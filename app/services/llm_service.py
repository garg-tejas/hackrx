import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import json
import asyncio
import time
from collections import deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter to respect Gemini API limits (10 RPM)."""
    
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
                # Calculate wait time - wait for the oldest request to expire
                oldest_request = self.requests[0]
                wait_time = self.window_seconds - (now - oldest_request) + 0.1  # Add small buffer
                if wait_time > 0:
                    logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds for next slot...")
                    await asyncio.sleep(wait_time)
                    # After waiting, remove expired requests and try again
                    return await self.acquire()  # Recursive call after waiting
            
            # Add current request
            self.requests.append(now)
            logger.debug(f"Request allowed. {len(self.requests)}/{self.max_requests} requests in window")
    
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
    """Service for LLM interactions using Google Gemini 2.0 Flash with rate limiting."""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
        # Initialize rate limiter (10 requests per minute)
        self.rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        logger.info(f"LLM Service initialized with {settings.LLM_MODEL}")
        logger.info(f"Rate limit: 10 requests per minute")
    
    async def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse and understand the query intent."""
        try:
            system_prompt = """You are an expert at analyzing insurance, legal, HR, and compliance documents. 
            Parse the given query and extract:
            1. The main question being asked
            2. The type of information being sought (policy details, coverage, terms, etc.)
            3. Any specific entities mentioned (dates, amounts, conditions, etc.)
            4. The expected answer format
            
            Return your analysis as a JSON object with these fields:
            - main_question: string
            - information_type: string
            - entities: list of strings
            - expected_format: string
            - keywords: list of strings for search
            """
            
            response = await self._make_llm_call(
                system_prompt=system_prompt,
                user_prompt=f"Query: {query}"
            )
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "main_question": query,
                    "information_type": "general",
                    "entities": [],
                    "expected_format": "text",
                    "keywords": query.lower().split()
                }
                
        except Exception as e:
            logger.error(f"Failed to parse query: {str(e)}")
            return {
                "main_question": query,
                "information_type": "general",
                "entities": [],
                "expected_format": "text",
                "keywords": query.lower().split()
            }
    
    async def generate_answer(self, query: str, context_chunks: List[str]) -> Dict[str, Any]:
        """Generate an answer based on query and context chunks."""
        try:
            # Optimize context to fit token limits
            optimized_context = self.optimize_context(context_chunks, self.max_tokens // 2)
            
            system_prompt = """You are an expert at answering questions about insurance, legal, HR, and compliance documents. 
            Based on the provided context, answer the question accurately and concisely.
            
            Guidelines:
            1. Only answer based on the information provided in the context
            2. If the information is not in the context, say "The information is not available in the provided document"
            3. Be specific and cite relevant sections when possible
            4. Use clear, professional language
            5. Provide a confidence score (0-1) based on how well the context answers the question
            
            Return your response as a JSON object with:
            - answer: string (the main answer)
            """
            
            user_prompt = f"""Context: {optimized_context}
            
            Question: {query}
            
            Please provide a JSON response with the answer, confidence score, sources, and reasoning."""
            
            response = await self._make_llm_call(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                # Fallback response
                return {
                    "answer": "Unable to generate a structured response. Please check the document content.",
                }
                
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
            }
    
    async def explain_reasoning(self, query: str, answer: str, sources: List[Dict]) -> str:
        """Generate an explanation for the reasoning process."""
        try:
            system_prompt = """You are an expert at explaining how answers were derived from document analysis.
            Provide a clear, concise explanation of how the answer was determined from the source material.
            Focus on the logical connection between the question, the relevant document sections, and the final answer."""
            
            sources_text = "\n".join([f"Source {i+1}: {source.get('content', '')}" for i, source in enumerate(sources[:3])])
            
            user_prompt = f"""Question: {query}
            Answer: {answer}
            Relevant Sources: {sources_text}
            
            Explain how the answer was derived from the sources."""
            
            response = await self._make_llm_call(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to explain reasoning: {str(e)}")
            return f"Explanation generation failed: {str(e)}"
    
    def optimize_context(self, chunks: List[str], max_tokens: int) -> str:
        """Optimize context to fit within token limits."""
        if not chunks:
            return ""
        
        # Simple token estimation (rough approximation)
        estimated_tokens = sum(len(chunk.split()) * 1.3 for chunk in chunks)
        
        if estimated_tokens <= max_tokens:
            return "\n\n".join(chunks)
        
        # Truncate to fit token limit
        optimized_chunks = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = len(chunk.split()) * 1.3
            if current_tokens + chunk_tokens <= max_tokens:
                optimized_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                break
        
        return "\n\n".join(optimized_chunks)
    
    async def _make_llm_call(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the Google Gemini API with rate limiting and retry logic."""
        
        # Acquire rate limit permission with timeout
        try:
            await asyncio.wait_for(self.rate_limiter.acquire(), timeout=120)  # 2 minute timeout
        except asyncio.TimeoutError:
            logger.error("Rate limiter timeout - too many requests")
            return "Rate limit timeout. Please try again later."
        
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Combine system and user prompts for Gemini
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                )
                
                return response.text.strip()
                
            except Exception as e:
                error_str = str(e)
                logger.warning(f"Gemini API call attempt {attempt + 1} failed: {error_str}")
                
                # Check if it's a rate limit error
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = base_delay * (2 ** attempt)
                        logger.info(f"Rate limited. Waiting {delay} seconds before retry...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error("Rate limit exceeded after all retries")
                        return "Rate limit exceeded. Please try again later."
                
                # For other errors, don't retry
                logger.error(f"Gemini API call failed: {error_str}")
                raise Exception(f"LLM API call failed: {error_str}")
        
        # This should never be reached, but just in case
        raise Exception("All retry attempts failed")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text string."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current LLM model."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "rate_limit": {
                "max_requests": self.rate_limiter.max_requests,
                "window_seconds": self.rate_limiter.window_seconds,
                "current_requests": len(self.rate_limiter.requests)
            }
        }
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_status() 