"""
Embeddings - Fast, lightweight embeddings using HashingVectorizer
No heavy ML models - perfect for free tier deployment
"""
from typing import List
import numpy as np
import os
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import HashingVectorizer

# Global vectorizer instance
_vectorizer = None

def _get_vectorizer():
    """Get or create HashingVectorizer"""
    global _vectorizer
    if _vectorizer is None:
        # Get dimension from .env
        n_features = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        
        print(f"🔄 Initializing HashingVectorizer (dimension: {n_features})")
        _vectorizer = HashingVectorizer(
            n_features=n_features,
            alternate_sign=False,  # All positive values
            norm='l2'  # L2 normalization for better similarity
        )
        print(f"✅ HashingVectorizer ready")
    return _vectorizer

def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings using HashingVectorizer
    Fast, lightweight, no training required
    
    Args:
        texts: List of text chunks
        batch_size: Not used (kept for compatibility)
    
    Returns:
        Numpy array of embeddings
    """
    try:
        print(f"🧠 Generating embeddings for {len(texts)} texts using HashingVectorizer...")
        
        # Get vectorizer
        vectorizer = _get_vectorizer()
        
        # Generate embeddings (very fast)
        embeddings = vectorizer.transform(texts).toarray()
        
        print(f"✅ Generated {len(embeddings)} embeddings (shape: {embeddings.shape})")
        return embeddings
    
    except Exception as e:
        print(f"❌ Embedding generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def generate_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for single text"""
    return generate_embeddings([text])[0]

def get_embedding_dimension() -> int:
    """Get the dimension of embeddings from .env"""
    embedding_dim = os.getenv("EMBEDDING_DIMENSION", "384")
    return int(embedding_dim)
