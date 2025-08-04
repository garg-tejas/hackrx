from typing import List, Dict, Any, Optional
from app.models.schemas import DocumentChunk
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    """Service for retrieving relevant document chunks based on queries."""
    
    def __init__(self):
        # Try to use the full embedding service, fallback to simple one
        try:
            from app.services.embedding_service import EmbeddingService
            self.embedding_service = EmbeddingService()
            logger.info("Using full embedding service with sentence-transformers")
        except ImportError:
            from app.services.simple_embedding_service import SimpleEmbeddingService
            self.embedding_service = SimpleEmbeddingService()
            logger.info("Using simple embedding service (fallback mode)")
    
    async def build_document_index(self, chunks: List[DocumentChunk]) -> None:
        """Build search index from document chunks."""
        try:
            # Extract text content from chunks
            texts = [chunk.content for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_service.generate_embeddings(texts)
            
            # Build FAISS index
            self.embedding_service.build_faiss_index(embeddings)
            
            # Store chunks for retrieval
            self.embedding_service.chunks = chunks
            
            logger.info(f"Built search index with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to build document index: {str(e)}")
            raise Exception(f"Index building failed: {str(e)}")
    
    async def search_relevant_chunks(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant chunks based on query."""
        try:
            # Search using embedding service
            search_results = self.embedding_service.search_similar(query, top_k)
            
            # Filter and rank results
            filtered_results = []
            for result in search_results:
                if result["score"] > 0.1:  # Minimum similarity threshold
                    filtered_results.append(result)
            
            logger.info(f"Found {len(filtered_results)} relevant chunks for query: {query}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to search relevant chunks: {str(e)}")
            return []
    
    async def get_context_for_query(self, query: str, max_chunks: int = 5) -> List[str]:
        """Get context chunks for a specific query."""
        try:
            # Search for relevant chunks
            search_results = await self.search_relevant_chunks(query, max_chunks * 2)
            
            # Extract content from top results
            context_chunks = []
            for result in search_results[:max_chunks]:
                if hasattr(result["chunk"], "content"):
                    context_chunks.append(result["chunk"].content)
                else:
                    context_chunks.append(str(result["chunk"]))
            
            return context_chunks
            
        except Exception as e:
            logger.error(f"Failed to get context for query: {str(e)}")
            return []
    
    async def rank_results_by_relevance(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank search results by relevance to query."""
        try:
            # Sort by similarity score (higher is better)
            ranked_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
            
            # Add relevance metadata
            for i, result in enumerate(ranked_results):
                result["relevance_rank"] = i + 1
                result["relevance_score"] = result.get("score", 0)
            
            return ranked_results
            
        except Exception as e:
            logger.error(f"Failed to rank results: {str(e)}")
            return results
    
    async def get_source_citations(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source citations from search results."""
        citations = []
        
        for result in search_results:
            chunk = result.get("chunk")
            if chunk and hasattr(chunk, "metadata"):
                citation = {
                    "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "metadata": chunk.metadata,
                    "relevance_score": result.get("score", 0),
                    "rank": result.get("rank", 0)
                }
                citations.append(citation)
        
        return citations
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current search index."""
        return self.embedding_service.get_index_stats()
    
    def clear_index(self) -> None:
        """Clear the current search index."""
        self.embedding_service.clear_index()
        logger.info("Cleared search index") 