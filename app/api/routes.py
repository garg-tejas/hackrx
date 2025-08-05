from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.services.simple_query_processor import SimpleQueryProcessor
from app.api.auth import verify_token
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global query processor instance
query_processor = SimpleQueryProcessor()

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest, token: str = Depends(verify_token)) -> QueryResponse:
    """
    Main endpoint for processing document queries using direct PDF processing.
    
    This endpoint:
    1. Downloads the PDF from the provided URL
    2. Uploads it directly to Gemini using the File API
    3. Processes each question directly with the PDF
    4. Returns structured answers with explanations and confidence scores
    """
    try:
        logger.info(f"Received query request with {len(request.questions)} questions")
        
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions or len(request.questions) == 0:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        # Process the queries using simplified approach
        response = await query_processor.process_queries(
            documents=request.documents,
            questions=request.questions
        )
        
        logger.info(f"Successfully processed {len(request.questions)} questions")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
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
        
        result = await query_processor.process_queries(
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
        rate_limit_status = query_processor.llm_service.rate_limiter.get_status()
        return {
            "rate_limit_status": rate_limit_status,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving rate limit status: {str(e)}")

@router.get("/api/v1/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "HackRx 6.0 - Simplified PDF Processing",
        "timestamp": datetime.utcnow(),
        "processing_method": "Direct PDF processing via Gemini File API"
    }

@router.get("/health/comprehensive")
async def comprehensive_health_check(token: str = Depends(verify_token)):
    """Comprehensive health check with detailed system status."""
    try:
        # Get rate limit status
        rate_limit_status = query_processor.llm_service.rate_limiter.get_status()
        
        return {
            "status": "healthy",
            "service": "HackRx 6.0 - Simplified PDF Processing",
            "timestamp": datetime.utcnow(),
            "processing_method": "Direct PDF processing via Gemini File API",
            "rate_limit_status": rate_limit_status,
            "features": [
                "Direct PDF processing",
                "Gemini File API integration",
                "Rate limiting",
                "Async processing"
            ]
        }
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        } 