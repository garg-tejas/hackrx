from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_processor import QueryProcessor
from app.api.auth import verify_token
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global query processor instance (lazy initialization)
query_processor = None

def get_query_processor():
    """Get or create the query processor instance."""
    global query_processor
    if query_processor is None:
        query_processor = QueryProcessor()
    return query_processor

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest, token: str = Depends(verify_token)) -> QueryResponse:
    """
    Main endpoint for processing document queries using BATCH PDF processing.
    
    This endpoint:
    1. Downloads the PDF from the provided URL
    2. Uploads it directly to Gemini using the File API
    3. Processes ALL questions in a SINGLE batch request to the LLM
    4. Returns structured answers with improved efficiency
    
    OPTIMIZED: Reduces API calls from N to 1 for N questions
    """
    try:
        logger.info(f"Received BATCH query request with {len(request.questions)} questions")
        
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions or len(request.questions) == 0:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        if len(request.questions) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 questions allowed per batch")
        
        # Process the queries in BATCH mode
        response = await get_query_processor().process_queries(
            documents=request.documents,
            questions=request.questions
        )
        
        logger.info(f"Successfully processed {len(request.questions)} questions in batch mode")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get processing statistics."""
    try:
        return {
            "processing_method": "Direct PDF processing via Gemini File API",
            "timestamp": datetime.utcnow(),
            "status": "Simplified processing active"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@router.post("/clear")
async def clear_session():
    """Clear the current processing session."""
    try:
        return {"message": "Session cleared successfully (simplified processing)"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@router.post("/test")
async def test_single_query(request: QueryRequest, token: str = Depends(verify_token)):
    """Test endpoint for single query processing."""
    try:
        if len(request.questions) != 1:
            raise HTTPException(status_code=400, detail="Test endpoint requires exactly one question")
        
        result = await get_query_processor().process_queries(
            documents=request.documents,
            questions=request.questions
        )
        
        return {
            "test_result": result,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test query failed: {str(e)}")

@router.get("/rate-limit-status")
async def get_rate_limit_status(token: str = Depends(verify_token)):
    """Get current rate limit status."""
    try:
        # Get rate limit status from the LLM service
        processor = get_query_processor()
        rate_limit_status = processor.llm_service.rate_limiter.get_status()
        key_status = processor.llm_service.get_key_status()
        return {
            "rate_limit_status": rate_limit_status,
            "key_rotation_status": key_status,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving rate limit status: {str(e)}")