import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import pickle
import os

# Import sentence_transformers with error handling
try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logging.error(f"Failed to import SentenceTransformer: {e}")
    logging.error("Please install sentence-transformers with: pip install sentence-transformers==2.2.2 huggingface-hub==0.16.4")
    raise

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings and performing vector search."""
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.index = None
        self.chunks = []
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def build_faiss_index(self, embeddings: np.ndarray) -> None:
        """Build FAISS index from embeddings."""
        try:
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
            query_embedding = self.model.encode([query])
            
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
    
    def save_index(self, filepath: str) -> None:
        """Save FAISS index and chunks to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.faiss")
            
            # Save chunks
            with open(f"{filepath}.chunks", 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logger.info(f"Saved index to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            raise Exception(f"Index save failed: {str(e)}")
    
    def load_index(self, filepath: str) -> None:
        """Load FAISS index and chunks from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{filepath}.faiss")
            
            # Load chunks
            with open(f"{filepath}.chunks", 'rb') as f:
                self.chunks = pickle.load(f)
            
            logger.info(f"Loaded index from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            raise Exception(f"Index load failed: {str(e)}")
    
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