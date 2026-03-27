"""
Vector Store - FAISS vector database for similarity search
"""
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pathlib import Path

class VectorStore:
    """FAISS-based vector store for document chunks"""
    
    def __init__(self, store_path: str = "vector_store"):
        """
        Initialize vector store
        
        Args:
            store_path: Path to store FAISS index and metadata
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(exist_ok=True)
        
        self.index = None
        self.metadata = []
        self.dimension = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization - only initialize when first used"""
        if self._initialized:
            return
        
        # Get dimension from embeddings module
        from .embeddings import get_embedding_dimension
        self.dimension = get_embedding_dimension()
        
        self._load_or_create_index()
        self._initialized = True
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            import faiss
            
            index_path = self.store_path / "index.faiss"
            metadata_path = self.store_path / "metadata.pkl"
            
            if index_path.exists() and metadata_path.exists():
                # Load existing
                self.index = faiss.read_index(str(index_path))
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded existing vector store with {len(self.metadata)} chunks")
            else:
                # Create new
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
                print("Created new vector store")
        
        except ImportError:
            raise Exception("faiss-cpu not installed. Install with: pip install faiss-cpu")
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: np.ndarray,
        document_id: str,
        business_id: str,
        filename: str
    ):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks with metadata
            embeddings: Numpy array of embeddings
            document_id: Document ID
            business_id: Business ID
            filename: Source filename
        """
        self._ensure_initialized()  # Lazy init
        
        # Add embeddings to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Add metadata
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                "document_id": document_id,
                "business_id": business_id,
                "filename": filename,
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "vector_id": len(self.metadata)
            })
        
        # Save to disk
        self._save_index()
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        business_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results to return
            business_id: Filter by business ID
        
        Returns:
            List of matching chunks with scores
        """
        self._ensure_initialized()  # Lazy init
        
        if len(self.metadata) == 0:
            return []
        
        # Search FAISS index
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, min(top_k * 3, len(self.metadata)))
        
        # Filter and format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                chunk = self.metadata[idx].copy()
                
                # Filter by business_id if provided
                if business_id and chunk["business_id"] != business_id:
                    continue
                
                chunk["score"] = float(dist)
                chunk["similarity"] = 1 / (1 + float(dist))  # Convert distance to similarity
                results.append(chunk)
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        self._ensure_initialized()  # Lazy init
        
        # Remove from metadata
        self.metadata = [m for m in self.metadata if m["document_id"] != document_id]
        
        # Rebuild index (FAISS doesn't support deletion)
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild FAISS index from scratch"""
        self._ensure_initialized()  # Lazy init
        
        import faiss
        from .embeddings import generate_embeddings
        
        if not self.metadata:
            self.index = faiss.IndexFlatL2(self.dimension)
            self._save_index()
            return
        
        # Generate embeddings for all chunks
        texts = [m["text"] for m in self.metadata]
        embeddings = generate_embeddings(texts)
        
        # Create new index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Update vector IDs
        for i, meta in enumerate(self.metadata):
            meta["vector_id"] = i
        
        self._save_index()
    
    def _save_index(self):
        """Save index and metadata to disk"""
        import faiss
        
        index_path = self.store_path / "index.faiss"
        metadata_path = self.store_path / "metadata.pkl"
        
        faiss.write_index(self.index, str(index_path))
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        self._ensure_initialized()  # Lazy init
        
        return {
            "total_chunks": len(self.metadata),
            "total_documents": len(set(m["document_id"] for m in self.metadata)),
            "dimension": self.dimension
        }

# Global vector store instance
vector_store = VectorStore()
