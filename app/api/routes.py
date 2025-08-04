from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_processor import QueryProcessor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global query processor instance
query_processor = QueryProcessor()

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest) -> QueryResponse:
    """
    Main endpoint for processing document queries.
    
    This endpoint:
    1. Downloads and processes the document from the provided URL
    2. Builds a search index from the document content
    3. Processes each question to find relevant information
    4. Returns structured answers with explanations and confidence scores
    """
    try:
        logger.info(f"Received query request with {len(request.questions)} questions")
        
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions or len(request.questions) == 0:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        # Process the queries
        response = await query_processor.process_document_queries(
            document_url=request.documents,
            questions=request.questions
        )
        
        logger.info(f"Successfully processed {len(request.questions)} questions")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "service": "HackRx 6.0 Query System"
    }

@router.get("/stats")
async def get_stats():
    """Get processing statistics."""
    try:
        stats = query_processor.get_processing_stats()
        return {
            "processing_stats": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@router.post("/clear")
async def clear_session():
    """Clear the current processing session."""
    try:
        query_processor.clear_session()
        return {"message": "Session cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@router.post("/test")
async def test_single_query(request: QueryRequest):
    """Test endpoint for single query processing."""
    try:
        if len(request.questions) != 1:
            raise HTTPException(status_code=400, detail="Test endpoint requires exactly one question")
        
        result = await query_processor.process_single_query(
            document_url=request.documents,
            question=request.questions[0]
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