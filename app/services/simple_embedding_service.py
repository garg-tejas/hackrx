import numpy as np
import hashlib
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SimpleEmbeddingService:
    """Simple embedding service using hash-based embeddings for testing."""
    
    def __init__(self):
        self.dimension = 384  # Same dimension as sentence-transformers
        self.index = None
        self.chunks = []
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate simple hash-based embeddings for testing."""
        try:
            embeddings = []
            for text in texts:
                # Create a simple hash-based embedding
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                
                # Convert to 384-dimensional vector
                embedding = []
                for i in range(self.dimension):
                    byte_idx = i % len(hash_bytes)
                    embedding.append(float(hash_bytes[byte_idx]) / 255.0)
                
                embeddings.append(embedding)
            
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def build_faiss_index(self, embeddings: np.ndarray) -> None:
        """Build FAISS index from embeddings."""
        try:
            import faiss
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            self.index.add(embeddings.astype('float32'))
            logger.info(f"Built FAISS index with {len(embeddings)} vectors")
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {str(e)}")
            raise Exception(f"Index building failed: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar chunks using FAISS."""
        if self.index is None:
            raise Exception("FAISS index not built. Call build_faiss_index first.")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Return results with metadata
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks):
                    result = {
                        "chunk": self.chunks[idx],
                        "score": float(score),
                        "rank": i + 1
                    }
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    def add_to_index(self, embeddings: np.ndarray, chunks: List[Any]) -> None:
        """Add new embeddings and chunks to the index."""
        try:
            import faiss
            if self.index is None:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.chunks = []
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Add to chunks list
            self.chunks.extend(chunks)
            
            logger.info(f"Added {len(embeddings)} new vectors to index")
        except Exception as e:
            logger.error(f"Failed to add to index: {str(e)}")
            raise Exception(f"Index addition failed: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        if self.index is None:
            return {"index_built": False}
        
        return {
            "index_built": True,
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d,
            "total_chunks": len(self.chunks)
        }
    
    def clear_index(self) -> None:
        """Clear the current index and chunks."""
        self.index = None
        self.chunks = []
        logger.info("Cleared index and chunks") 