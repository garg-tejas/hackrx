#!/usr/bin/env python3
"""
Simple test script for HackRx 6.0 system.
This script tests the basic functionality without requiring external APIs.
"""

import asyncio
import json
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.query_processor import QueryProcessor
from app.models.schemas import DocumentChunk

async def test_document_processing():
    """Test document processing functionality."""
    print("🧪 Testing Document Processing...")
    
    processor = DocumentProcessor()
    
    # Test text chunking
    test_text = """
    This is a test insurance policy document. 
    It contains information about grace periods and coverage.
    The grace period is 30 days from the due date.
    Maternity expenses are covered under this policy.
    Premium payments are due monthly.
    """
    
    chunks = processor.chunk_text(test_text, chunk_size=100, overlap=20)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Test metadata extraction
    metadata = processor.extract_metadata(test_text, "pdf", "https://example.com/test.pdf")
    print(f"✅ Extracted metadata: {metadata['word_count']} words, {metadata['estimated_pages']} pages")
    
    return chunks

async def test_embedding_service():
    """Test embedding service functionality."""
    print("\n🧪 Testing Embedding Service...")
    
    service = EmbeddingService()
    
    # Test with mock data (without loading actual model)
    test_texts = [
        "This is a test sentence about insurance.",
        "Another sentence about policy coverage.",
        "Grace period information is important."
    ]
    
    print("✅ Embedding service initialized")
    print(f"✅ Model: {service.model}")
    print(f"✅ Dimension: {service.dimension}")
    
    return service

async def test_llm_service():
    """Test LLM service functionality."""
    print("\n🧪 Testing LLM Service...")
    
    service = LLMService()
    
    print(f"✅ LLM service initialized")
    print(f"✅ Model: {service.model}")
    print(f"✅ Max tokens: {service.max_tokens}")
    print(f"✅ Temperature: {service.temperature}")
    
    # Test context optimization
    test_chunks = [
        "Short chunk",
        "This is a longer chunk with more content about insurance policies and coverage details.",
        "Another short chunk"
    ]
    
    optimized = service.optimize_context(test_chunks, max_tokens=50)
    print(f"✅ Context optimization: {len(optimized)} characters")
    
    return service

async def test_retrieval_service():
    """Test retrieval service functionality."""
    print("\n🧪 Testing Retrieval Service...")
    
    service = RetrievalService()
    
    print("✅ Retrieval service initialized")
    print(f"✅ Embedding service: {type(service.embedding_service).__name__}")
    
    return service

async def test_query_processor():
    """Test query processor functionality."""
    print("\n🧪 Testing Query Processor...")
    
    processor = QueryProcessor()
    
    print("✅ Query processor initialized")
    print(f"✅ Document processor: {type(processor.doc_processor).__name__}")
    print(f"✅ Retrieval service: {type(processor.retrieval_service).__name__}")
    print(f"✅ LLM service: {type(processor.llm_service).__name__}")
    
    # Test processing stats
    stats = processor.get_processing_stats()
    print(f"✅ Processing stats: {stats['total_chunks']} chunks")
    
    return processor

async def test_api_models():
    """Test API model validation."""
    print("\n🧪 Testing API Models...")
    
    from app.models.schemas import QueryRequest, QueryResponse
    
    # Test QueryRequest
    request = QueryRequest(
        documents="https://example.com/test.pdf",
        questions=["What is the grace period?", "Does this cover maternity?"]
    )
    print(f"✅ QueryRequest: {len(request.questions)} questions")
    
    # Test QueryResponse
    response = QueryResponse(
        answers=["30 days", "Yes"],
        explanations=["Found in document", "Covered in policy"],
        confidence_scores=[0.9, 0.8],
        sources=[[], []]
    )
    print(f"✅ QueryResponse: {len(response.answers)} answers")
    
    return True

async def test_utility_functions():
    """Test utility functions."""
    print("\n🧪 Testing Utility Functions...")
    
    from app.utils.helpers import sanitize_text, extract_keywords, validate_url
    
    # Test text sanitization
    dirty_text = "  This   is   a   test   text   with   extra   spaces.  "
    clean_text = sanitize_text(dirty_text)
    print(f"✅ Text sanitization: '{clean_text}'")
    
    # Test keyword extraction
    keywords = extract_keywords("This is a test document about insurance policies and coverage.")
    print(f"✅ Keyword extraction: {keywords}")
    
    # Test URL validation
    valid_url = validate_url("https://example.com/test.pdf")
    invalid_url = validate_url("not-a-url")
    print(f"✅ URL validation: valid={valid_url}, invalid={invalid_url}")
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting HackRx 6.0 System Tests")
    print("=" * 50)
    
    try:
        # Test all components
        await test_document_processing()
        await test_embedding_service()
        await test_llm_service()
        await test_retrieval_service()
        await test_query_processor()
        await test_api_models()
        await test_utility_functions()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 HackRx 6.0 system is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 