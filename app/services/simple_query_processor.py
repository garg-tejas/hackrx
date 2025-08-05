import logging
from typing import List, Dict, Any
from app.services.simple_llm_service import SimpleLLMService
from app.config import settings

logger = logging.getLogger(__name__)

class SimpleQueryProcessor:
    """Simplified query processor using direct PDF processing with Gemini."""
    
    def __init__(self):
        self.llm_service = SimpleLLMService(api_key=settings.GOOGLE_API_KEY)
        logger.info("Simple Query Processor initialized")
    
    async def process_queries(self, documents: str, questions: List[str]) -> Dict[str, Any]:
        """Process queries using direct PDF processing with Gemini File API."""
        try:
            logger.info(f"Starting simple document processing for URL: {documents}")
            
            # Process all questions directly with the PDF
            results = await self.llm_service.process_multiple_questions(
                pdf_url=documents,
                questions=questions
            )
            
            logger.info(f"Successfully processed {len(questions)} questions")
            
            return {
                "status": "success",
                "answers": results["answers"],
                "total_questions": results["total_questions"],
                "successful_questions": results["successful_questions"],
                "processing_method": "Direct PDF processing via Gemini File API"
            }
            
        except Exception as e:
            logger.error(f"Failed to process queries: {str(e)}")
            
            # Return error responses for all questions
            error_response = {
                "status": "error",
                "answers": [f"Processing failed: {str(e)}"] * len(questions),
                "total_questions": len(questions),
                "successful_questions": 0,
                "processing_method": "Direct PDF processing via Gemini File API",
                "error": str(e)
            }
            
            return error_response 