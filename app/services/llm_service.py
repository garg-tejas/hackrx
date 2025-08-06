from google import genai
from google.genai import types
import httpx
import io
import asyncio
import time
import json
import logging
from typing import List, Dict, Any, Optional
from collections import deque
from app.services.key_rotator import APIKeyRotator

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for Gemini API."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            
            # Remove old requests outside the window
            while self.requests and now - self.requests[0] > self.window_seconds:
                self.requests.popleft()
            
            # Check if we can make a request
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_time = self.window_seconds - (now - oldest_request) + 0.1
                if wait_time > 0:
                    logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # Add current request
            self.requests.append(now)
    
    def get_status(self):
        """Get current rate limit status."""
        now = time.time()
        active_requests = [req for req in self.requests if now - req <= self.window_seconds]
        
        return {
            "requests_in_window": len(active_requests),
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "remaining_requests": max(0, self.max_requests - len(active_requests)),
            "window_resets_in": max(0, self.window_seconds - (now - active_requests[0])) if active_requests else 0
        }

class LLMService:
    """LLM service using Gemini's File API for direct PDF processing."""
    
    def __init__(self, api_key: str = None):
        # Initialize key rotator
        self.key_rotator = APIKeyRotator()
        
        # Use provided key or get from rotator
        if api_key:
            self.current_key = api_key
        else:
            self.current_key = self.key_rotator.get_next_key()
        
        # Initialize client with current key
        self.client = genai.Client(api_key=self.current_key)
        self.model = "gemini-2.5-flash"
        self.rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        logger.info(f"LLM Service initialized with {self.model} and {self.key_rotator.get_key_status()['total_keys']} API keys")
    
    async def download_pdf(self, url: str) -> bytes:
        """Download PDF from URL."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {str(e)}")
            raise Exception(f"Failed to download PDF: {str(e)}")
    
    async def upload_pdf_to_gemini(self, pdf_content: bytes) -> Any:
        """Upload PDF to Gemini with current API key."""
        pdf_io = io.BytesIO(pdf_content)
        uploaded_file = self.client.files.upload(
            file=pdf_io,
            config=dict(mime_type='application/pdf')
        )
        logger.info(f"PDF uploaded to Gemini with key {self.current_key[:10]}...")
        return uploaded_file

    async def process_pdf_with_gemini(self, pdf_url: str, questions: List[str]) -> List[Dict[str, Any]]:
        """Process PDF directly with Gemini using File API."""
        try:
            # Download PDF once
            pdf_content = await self.download_pdf(pdf_url)
            
            # Upload PDF to Gemini using File API
            uploaded_file = await self.upload_pdf_to_gemini(pdf_content)
            
            # Process each question
            results = []
            for i, question in enumerate(questions, 1):
                logger.info(f"Processing question {i}/{len(questions)}: {question}")
                
                try:
                    # Acquire rate limit permission
                    await self.rate_limiter.acquire()
                    
                    # Get a fresh API key for this request
                    api_key = self.key_rotator.get_available_key()
                    if api_key and api_key != self.current_key:
                        # Update client with new key
                        self.current_key = api_key
                        self.client = genai.Client(api_key=self.current_key)
                        logger.info(f"Rotated to API key: {api_key[:10]}...")
                        
                        # CRITICAL: Re-upload PDF with new API key
                        uploaded_file = await self.upload_pdf_to_gemini(pdf_content)
                    
                    # Generate answer using Gemini with the uploaded PDF
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=[uploaded_file, question]
                    )
                    
                    # Parse response
                    answer_text = response.text.strip()
                    
                    # Create structured response
                    result = {
                        "question": question,
                        "answer": answer_text,
                    }
                    
                    results.append(result)
                    logger.info(f"Successfully processed question {i}")
                    
                except Exception as e:
                    error_str = str(e)
                    logger.error(f"Failed to process question {i}: {error_str}")
                    
                    # Check if it's a rate limit error
                    if "429" in error_str or "quota" in error_str.lower():
                        # Mark current key as rate limited
                        self.key_rotator.mark_key_rate_limited(self.current_key)
                        logger.warning(f"Rate limit hit for key {self.current_key[:10]}..., trying next key")
                        
                        # Try with a different key
                        try:
                            new_key = self.key_rotator.get_available_key()
                            if new_key and new_key != self.current_key:
                                self.current_key = new_key
                                self.client = genai.Client(api_key=self.current_key)
                                logger.info(f"Switched to API key: {new_key[:10]}...")
                                
                                # CRITICAL: Re-upload PDF with new API key
                                uploaded_file = await self.upload_pdf_to_gemini(pdf_content)
                                
                                # Retry the request
                                response = self.client.models.generate_content(
                                    model=self.model,
                                    contents=[uploaded_file, question]
                                )
                                
                                answer_text = response.text.strip()
                                result = {
                                    "question": question,
                                    "answer": answer_text
                                }
                                results.append(result)
                                logger.info(f"Successfully processed question {i} with rotated key")
                                continue
                        except Exception as retry_error:
                            logger.error(f"Retry also failed: {str(retry_error)}")
                    
                    results.append({
                        "question": question,
                        "answer": f"Error processing question: {str(e)}",
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process PDF with Gemini: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")
    
    async def process_multiple_questions(self, pdf_url: str, questions: List[str]) -> Dict[str, Any]:
        """Process multiple questions on a single PDF."""
        try:
            results = await self.process_pdf_with_gemini(pdf_url, questions)
            
            # Extract only answers
            answers = [result["answer"] for result in results]
            
            return {
                "answers": answers,
                "total_questions": len(questions),
                "successful_questions": len([r for r in results if "Error" not in r["answer"]])
            }
            
        except Exception as e:
            logger.error(f"Failed to process multiple questions: {str(e)}")
            # Return error responses for all questions
            error_response = {
                "answers": [f"Processing failed: {str(e)}"] * len(questions),
                "total_questions": len(questions),
                "successful_questions": 0
            }
            return error_response
    
    def get_key_status(self) -> dict:
        """Get status of API key rotation."""
        return self.key_rotator.get_key_status() 