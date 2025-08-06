import logging
from typing import List, Dict, Any
from app.services.llm_service import LLMService
from app.config import settings

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Query processor using direct PDF processing with Gemini."""
    
    def __init__(self):
        self.llm_service = LLMService()  # Will use key rotator
        logger.info("Query Processor initialized")
    
    async def process_queries(self, documents: str, questions: List[str]) -> Dict[str, Any]:
        """Process queries using BATCH PDF processing with Gemini File API."""
        try:
            logger.info(f"Starting BATCH document processing for URL: {documents}")
            logger.info(f"Processing {len(questions)} questions in a single LLM call")
            
            # Process all questions in BATCH mode with the PDF
            results = await self.llm_service.process_multiple_questions(
                pdf_url=documents,
                questions=questions
            )
            
            logger.info(f"Successfully processed {len(questions)} questions in batch mode")
            
            return {
                "status": "success",
                "answers": results["answers"],
                "total_questions": results["total_questions"],
                "successful_questions": results["successful_questions"],
                "processing_method": "BATCH PDF processing via Gemini File API",
                "optimization": "Single LLM call for all questions"
            }
            
        except Exception as e:
            logger.error(f"Failed to process batch queries: {str(e)}")
            
            # Return error responses for all questions
            error_response = {
                "status": "error",
                "answers": [f"Processing failed: {str(e)}"] * len(questions),
                "total_questions": len(questions),
                "successful_questions": 0,
                "processing_method": "BATCH PDF processing via Gemini File API",
                "error": str(e)
            }
            
            return error_response 