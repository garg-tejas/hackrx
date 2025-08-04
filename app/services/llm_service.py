import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM interactions using Google Gemini 2.5 Flash."""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
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
            - confidence: float (0-1)
            - sources: list of relevant text snippets
            - reasoning: string (brief explanation of your reasoning)
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
                    "confidence": 0.0,
                    "sources": context_chunks[:2],
                    "reasoning": "Failed to parse LLM response"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "reasoning": "LLM service error"
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
        """Make a call to the Google Gemini API."""
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
            logger.error(f"Gemini API call failed: {str(e)}")
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text string."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current LLM model."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        } 