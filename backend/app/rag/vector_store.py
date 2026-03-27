"""
Vector Store - FAISS vector database with BM25 hybrid search
Lightweight, fast, perfect for free tier deployment
"""
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi

class VectorStore:
    """FAISS-based vector store with BM25 hybrid search"""
    
    def __init__(self, store_path: str = None):
        """
        Initialize vector store
        
        Args:
            store_path: Path to store FAISS index and metadata (from .env if not provided)
        """
        # Use .env configuration
        if store_path is None:
            store_path = os.getenv("VECTOR_DB_PATH", "./vector_store")
        
        self.store_path = Path(store_path)
        self.store_path.mkdir(exist_ok=True)
        
        self.index = None
        self.metadata = []
        self.dimension = None
        self.bm25 = None  # BM25 index for hybrid search
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
            bm25_path = self.store_path / "bm25.pkl"
            
            if index_path.exists() and metadata_path.exists():
                # Load existing
                self.index = faiss.read_index(str(index_path))
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                # Load BM25 if exists
                if bm25_path.exists():
                    with open(bm25_path, 'rb') as f:
                        self.bm25 = pickle.load(f)
                
                print(f"✅ Loaded vector store with {len(self.metadata)} chunks")
            else:
                # Create new
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
                self.bm25 = None
                print("✅ Created new vector store")
        
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
        Add document chunks to vector store with BM25 indexing
        
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
        
        # Rebuild BM25 index with all texts
        self._rebuild_bm25()
        
        # Save to disk
        self._save_index()
    
    def _rebuild_bm25(self):
        """Rebuild BM25 index from all metadata"""
        if not self.metadata:
            self.bm25 = None
            return
        
        # Tokenize all texts for BM25
        tokenized_corpus = [meta["text"].lower().split() for meta in self.metadata]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"✅ BM25 index rebuilt with {len(tokenized_corpus)} documents")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        business_id: str = None,
        query_text: str = None,
        use_hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search using FAISS + BM25
        
        Args:
            query_embedding: Query embedding for FAISS search
            top_k: Number of results to return
            business_id: Filter by business ID
            query_text: Query text for BM25 search
            use_hybrid: Use hybrid search (FAISS + BM25)
        
        Returns:
            List of matching chunks with scores
        """
        self._ensure_initialized()  # Lazy init
        
        if len(self.metadata) == 0:
            return []
        
        # FAISS vector search
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, min(top_k * 3, len(self.metadata)))
        
        # Get FAISS results
        faiss_results = {}
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                chunk = self.metadata[idx].copy()
                
                # Filter by business_id if provided
                if business_id and chunk["business_id"] != business_id:
                    continue
                
                faiss_score = 1 / (1 + float(dist))  # Convert distance to similarity
                faiss_results[idx] = {
                    "chunk": chunk,
                    "faiss_score": faiss_score,
                    "bm25_score": 0.0
                }
        
        # BM25 search if query text provided and hybrid enabled
        if use_hybrid and query_text and self.bm25:
            tokenized_query = query_text.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Add BM25 scores to results
            for idx, score in enumerate(bm25_scores):
                if idx in faiss_results:
                    faiss_results[idx]["bm25_score"] = float(score)
                elif score > 0:  # Add high BM25 matches even if not in FAISS top results
                    chunk = self.metadata[idx].copy()
                    
                    # Filter by business_id
                    if business_id and chunk["business_id"] != business_id:
                        continue
                    
                    faiss_results[idx] = {
                        "chunk": chunk,
                        "faiss_score": 0.0,
                        "bm25_score": float(score)
                    }
        
        # Combine scores (weighted average)
        results = []
        for idx, data in faiss_results.items():
            # Hybrid score: 60% FAISS + 40% BM25
            hybrid_score = 0.6 * data["faiss_score"] + 0.4 * data["bm25_score"]
            
            chunk = data["chunk"]
            chunk["score"] = hybrid_score
            chunk["faiss_score"] = data["faiss_score"]
            chunk["bm25_score"] = data["bm25_score"]
            chunk["similarity"] = hybrid_score
            results.append(chunk)
        
        # Sort by hybrid score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
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
            self.bm25 = None
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
        
        # Rebuild BM25
        self._rebuild_bm25()
        
        self._save_index()
    
    def _save_index(self):
        """Save index, metadata, and BM25 to disk"""
        import faiss
        
        index_path = self.store_path / "index.faiss"
        metadata_path = self.store_path / "metadata.pkl"
        bm25_path = self.store_path / "bm25.pkl"
        
        faiss.write_index(self.index, str(index_path))
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        if self.bm25:
            with open(bm25_path, 'wb') as f:
                pickle.dump(self.bm25, f)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        self._ensure_initialized()  # Lazy init
        
        return {
            "total_chunks": len(self.metadata),
            "total_documents": len(set(m["document_id"] for m in self.metadata)),
            "dimension": self.dimension,
            "has_bm25": self.bm25 is not None
        }

# Global vector store instance
vector_store = VectorStore()
