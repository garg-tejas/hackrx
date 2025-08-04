import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.query_processor import QueryProcessor
from app.models.schemas import DocumentChunk

class TestDocumentProcessor:
    """Test cases for DocumentProcessor service."""
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    @pytest.mark.asyncio
    async def test_download_document_success(self, processor):
        """Test successful document download."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.content = b"test document content"
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await processor.download_document("https://example.com/test.pdf")
            assert result == b"test document content"
    
    @pytest.mark.asyncio
    async def test_download_document_failure(self, processor):
        """Test document download failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
            
            with pytest.raises(Exception, match="Failed to download document"):
                await processor.download_document("https://example.com/test.pdf")
    
    def test_extract_text_from_pdf(self, processor):
        """Test PDF text extraction."""
        # Mock PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
            mock_reader.return_value.pages = [mock_page]
            
            result = processor.extract_text_from_pdf(pdf_content)
            assert "Test PDF content" in result
    
    def test_chunk_text(self, processor):
        """Test text chunking functionality."""
        text = "This is a test document. It contains multiple sentences. We want to chunk it properly."
        
        chunks = processor.chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.content for chunk in chunks)

class TestEmbeddingService:
    """Test cases for EmbeddingService."""
    
    @pytest.fixture
    def service(self):
        return EmbeddingService()
    
    def test_generate_embeddings(self, service):
        """Test embedding generation."""
        texts = ["This is a test sentence.", "Another test sentence."]
        
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            mock_model.return_value.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            
            embeddings = service.generate_embeddings(texts)
            assert len(embeddings) == 2
    
    def test_build_faiss_index(self, service):
        """Test FAISS index building."""
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        with patch('faiss.IndexFlatIP') as mock_index:
            service.build_faiss_index(embeddings)
            assert service.index is not None

class TestLLMService:
    """Test cases for LLMService."""
    
    @pytest.fixture
    def service(self):
        return LLMService()
    
    @pytest.mark.asyncio
    async def test_parse_query(self, service):
        """Test query parsing."""
        query = "What is the grace period for premium payment?"
        
        with patch.object(service, '_make_llm_call') as mock_call:
            mock_call.return_value = '{"main_question": "grace period", "information_type": "policy"}'
            
            result = await service.parse_query(query)
            assert "main_question" in result
    
    @pytest.mark.asyncio
    async def test_generate_answer(self, service):
        """Test answer generation."""
        query = "What is the grace period?"
        context_chunks = ["The grace period is 30 days.", "Premium payments are due monthly."]
        
        with patch.object(service, '_make_llm_call') as mock_call:
            mock_call.return_value = '{"answer": "30 days", "confidence": 0.9}'
            
            result = await service.generate_answer(query, context_chunks)
            assert "answer" in result
    
    def test_optimize_context(self, service):
        """Test context optimization."""
        chunks = ["Short chunk", "Long chunk " * 100, "Another short chunk"]
        
        result = service.optimize_context(chunks, max_tokens=50)
        assert len(result) > 0

class TestRetrievalService:
    """Test cases for RetrievalService."""
    
    @pytest.fixture
    def service(self):
        return RetrievalService()
    
    @pytest.mark.asyncio
    async def test_build_document_index(self, service):
        """Test document index building."""
        chunks = [
            DocumentChunk(id="1", content="Test content 1", metadata={}),
            DocumentChunk(id="2", content="Test content 2", metadata={})
        ]
        
        with patch.object(service.embedding_service, 'generate_embeddings') as mock_embeddings:
            mock_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
            
            await service.build_document_index(chunks)
            assert service.embedding_service.index is not None
    
    @pytest.mark.asyncio
    async def test_search_relevant_chunks(self, service):
        """Test chunk search functionality."""
        query = "test query"
        
        with patch.object(service.embedding_service, 'search_similar') as mock_search:
            mock_search.return_value = [
                {"chunk": DocumentChunk(id="1", content="test", metadata={}), "score": 0.8}
            ]
            
            results = await service.search_relevant_chunks(query)
            assert len(results) > 0

class TestQueryProcessor:
    """Test cases for QueryProcessor."""
    
    @pytest.fixture
    def processor(self):
        return QueryProcessor()
    
    @pytest.mark.asyncio
    async def test_process_document_queries(self, processor):
        """Test complete document query processing."""
        document_url = "https://example.com/test.pdf"
        questions = ["What is the grace period?", "Does this cover maternity?"]
        
        with patch.object(processor.doc_processor, 'process_document') as mock_process:
            mock_process.return_value = [
                DocumentChunk(id="1", content="Grace period is 30 days", metadata={})
            ]
            
            with patch.object(processor.retrieval_service, 'build_document_index') as mock_build:
                with patch.object(processor.retrieval_service, 'get_context_for_query') as mock_context:
                    mock_context.return_value = ["Grace period is 30 days"]
                    
                    with patch.object(processor.llm_service, 'generate_answer') as mock_answer:
                        mock_answer.return_value = {
                            "answer": "30 days",
                            "confidence": 0.9,
                            "sources": [],
                            "reasoning": "Found in document"
                        }
                        
                        result = await processor.process_document_queries(document_url, questions)
                        assert len(result.answers) == 2
                        assert result.answers[0] == "30 days"
    
    def test_get_processing_stats(self, processor):
        """Test processing statistics retrieval."""
        stats = processor.get_processing_stats()
        assert "total_chunks" in stats
        assert "index_stats" in stats
        assert "llm_info" in stats

if __name__ == "__main__":
    pytest.main([__file__]) 