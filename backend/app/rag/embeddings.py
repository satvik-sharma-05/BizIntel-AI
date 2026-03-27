"""
Embeddings - Generate embeddings for text chunks using OpenAI
"""
from typing import List
import numpy as np
import os

def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for text chunks using OpenAI's text-embedding-3-small
    Falls back to sentence-transformers if OpenAI is not available
    
    Args:
        texts: List of text chunks
    
    Returns:
        Numpy array of embeddings
    """
    # Try OpenAI first
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            # Generate embeddings using OpenAI
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            embeddings = np.array([item.embedding for item in response.data])
            return embeddings
        
        except Exception as e:
            print(f"OpenAI embedding error: {str(e)}, falling back to sentence-transformers")
    
    # Fallback to sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model (cached after first load)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=False)
        
        return embeddings
    
    except ImportError:
        raise Exception("Neither OpenAI nor sentence-transformers available. Install with: pip install openai OR pip install sentence-transformers")
    except Exception as e:
        raise Exception(f"Error generating embeddings: {str(e)}")

def generate_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for single text"""
    return generate_embeddings([text])[0]

def get_embedding_dimension() -> int:
    """Get the dimension of embeddings based on available provider"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return 1536  # text-embedding-3-small dimension
    else:
        return 384  # all-MiniLM-L6-v2 dimension
