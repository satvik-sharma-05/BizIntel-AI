"""
Embeddings - Generate embeddings for text chunks using sentence-transformers
"""
from typing import List
import numpy as np
import os

# Global model instance (lazy loaded)
_model = None

def _get_model():
    """Lazy load the sentence-transformers model"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"🔄 Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
        print(f"✅ Model loaded successfully")
    return _model

def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings for text chunks using sentence-transformers
    
    Args:
        texts: List of text chunks
        batch_size: Number of texts to process at once
    
    Returns:
        Numpy array of embeddings
    """
    try:
        print(f"🧠 Generating embeddings for {len(texts)} texts...")
        
        # Get model (lazy loaded)
        model = _get_model()
        
        # Generate embeddings in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(texts) + batch_size - 1)//batch_size
            
            print(f"   Batch {batch_num}/{total_batches}: {len(batch)} texts")
            batch_embeddings = model.encode(batch, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        embeddings = np.vstack(all_embeddings)
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
