import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import QueryRequest, QueryResponse

client = TestClient(app)

class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_stats_endpoint(self):
        """Test stats endpoint."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "processing_stats" in data
        assert "timestamp" in data
    
    def test_clear_session(self):
        """Test clear session endpoint."""
        response = client.post("/api/v1/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session cleared successfully"
    
    def test_process_queries_valid_request(self):
        """Test main query processing endpoint with valid request."""
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": [
                "What is the grace period for premium payment?",
                "Does this policy cover maternity expenses?"
            ]
        }
        
        response = client.post("/api/v1/hackrx/run", json=request_data)
        
        # Should return 200 or 500 depending on whether external services are available
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "answers" in data
            assert len(data["answers"]) == 2
    
    def test_process_queries_missing_documents(self):
        """Test query processing with missing document URL."""
        request_data = {
            "documents": "",
            "questions": ["What is the grace period?"]
        }
        
        response = client.post("/api/v1/hackrx/run", json=request_data)
        assert response.status_code == 400
        data = response.json()
        assert "Document URL is required" in data["detail"]
    
    def test_process_queries_missing_questions(self):
        """Test query processing with missing questions."""
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": []
        }
        
        response = client.post("/api/v1/hackrx/run", json=request_data)
        assert response.status_code == 400
        data = response.json()
        assert "At least one question is required" in data["detail"]
    
    def test_test_single_query(self):
        """Test single query test endpoint."""
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": ["What is the grace period?"]
        }
        
        response = client.post("/api/v1/test", json=request_data)
        
        # Should return 200 or 500 depending on whether external services are available
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "test_result" in data
            assert "timestamp" in data
    
    def test_test_single_query_multiple_questions(self):
        """Test single query endpoint with multiple questions (should fail)."""
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": [
                "What is the grace period?",
                "Does this cover maternity?"
            ]
        }
        
        response = client.post("/api/v1/test", json=request_data)
        assert response.status_code == 400
        data = response.json()
        assert "exactly one question" in data["detail"]

class TestAPIValidation:
    """Test cases for API input validation."""
    
    def test_query_request_validation(self):
        """Test QueryRequest model validation."""
        # Valid request
        valid_request = QueryRequest(
            documents="https://example.com/test.pdf",
            questions=["What is the grace period?"]
        )
        assert valid_request.documents == "https://example.com/test.pdf"
        assert len(valid_request.questions) == 1
    
    def test_query_response_validation(self):
        """Test QueryResponse model validation."""
        # Valid response
        valid_response = QueryResponse(
            answers=["30 days"],
        )
        assert len(valid_response.answers) == 1
        assert valid_response.confidence_scores[0] == 0.9

class TestAPIErrorHandling:
    """Test cases for API error handling."""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request."""
        response = client.post("/api/v1/hackrx/run", data="invalid json")
        assert response.status_code == 422
    
    def test_malformed_request(self):
        """Test handling of malformed request."""
        request_data = {
            "documents": "https://example.com/test.pdf"
            # Missing questions field
        }
        
        response = client.post("/api/v1/hackrx/run", json=request_data)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__]) 