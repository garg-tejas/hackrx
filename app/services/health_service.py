"""
Health service for monitoring system components.
"""

import asyncio
import time
from typing import Dict, Any, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class HealthService:
    """Service for monitoring system health and dependencies."""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def check_llm_service(self) -> Dict[str, Any]:
        """Check LLM service health."""
        try:
            from app.services.llm_service import LLMService
            llm_service = LLMService()
            
            # Test a simple call
            test_response = await llm_service._make_llm_call(
                "You are a helpful assistant.",
                "Say 'OK'"
            )
            
            return {
                "status": "healthy",
                "model": settings.LLM_MODEL,
                "rate_limit_status": llm_service.get_rate_limit_status(),
                "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
            }
        except Exception as e:
            logger.error(f"LLM service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": settings.LLM_MODEL
            }
    
    async def check_document_processor(self) -> Dict[str, Any]:
        """Check document processor health."""
        try:
            from app.services.document_processor import DocumentProcessor
            doc_processor = DocumentProcessor()
            
            # Test text cleaning
            test_text = "Test document content with some artifacts /Title(test) endobj"
            cleaned_text = doc_processor.clean_text(test_text)
            
            return {
                "status": "healthy",
                "text_cleaning_working": len(cleaned_text) > 0,
                "chunk_size": doc_processor.chunk_size,
                "chunk_overlap": doc_processor.chunk_overlap
            }
        except Exception as e:
            logger.error(f"Document processor health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_embedding_service(self) -> Dict[str, Any]:
        """Check embedding service health."""
        try:
            from app.services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            
            # Test embedding generation
            test_texts = ["Test document", "Another test"]
            embeddings = embedding_service.generate_embeddings(test_texts)
            
            return {
                "status": "healthy",
                "embedding_model": settings.EMBEDDING_MODEL,
                "embeddings_generated": len(embeddings),
                "embedding_dimension": embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings[0])
            }
        except Exception as e:
            logger.error(f"Embedding service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "embedding_model": settings.EMBEDDING_MODEL
            }
    
    async def check_environment(self) -> Dict[str, Any]:
        """Check environment configuration."""
        required_vars = [
            "GOOGLE_API_KEY",
            "PINECONE_API_KEY", 
            "PINECONE_ENVIRONMENT"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(settings, var, None):
                missing_vars.append(var)
        
        return {
            "status": "healthy" if not missing_vars else "unhealthy",
            "missing_variables": missing_vars,
            "api_host": settings.API_HOST,
            "api_port": settings.API_PORT,
            "llm_model": settings.LLM_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL
        }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available // (1024 * 1024),  # MB
                "disk_percent": disk.percent,
                "disk_free": disk.free // (1024 * 1024 * 1024)  # GB
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for resource monitoring"
            }
        except Exception as e:
            logger.error(f"System resources health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components."""
        start_time = time.time()
        
        # Run all health checks concurrently
        tasks = [
            self.check_llm_service(),
            self.check_document_processor(),
            self.check_embedding_service(),
            self.check_environment(),
            self.check_system_resources()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_checks = {
            "llm_service": results[0] if not isinstance(results[0], Exception) else {"status": "unhealthy", "error": str(results[0])},
            "document_processor": results[1] if not isinstance(results[1], Exception) else {"status": "unhealthy", "error": str(results[1])},
            "embedding_service": results[2] if not isinstance(results[2], Exception) else {"status": "unhealthy", "error": str(results[2])},
            "environment": results[3] if not isinstance(results[3], Exception) else {"status": "unhealthy", "error": str(results[3])},
            "system_resources": results[4] if not isinstance(results[4], Exception) else {"status": "unhealthy", "error": str(results[4])}
        }
        
        # Determine overall status
        unhealthy_checks = [check for check in health_checks.values() if check.get("status") == "unhealthy"]
        overall_status = "healthy" if not unhealthy_checks else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.start_time,
            "health_checks": health_checks,
            "summary": {
                "total_checks": len(health_checks),
                "healthy_checks": len(health_checks) - len(unhealthy_checks),
                "unhealthy_checks": len(unhealthy_checks),
                "response_time_ms": (time.time() - start_time) * 1000
            }
        } 