"""
Embeddings - Generate embeddings for text chunks using OpenAI
"""
from typing import List
import numpy as np
import os

def generate_embeddings(texts: List[str], batch_size: int = 50) -> np.ndarray:
    """
    Generate embeddings for text chunks using OpenAI's text-embedding-3-small
    Falls back to sentence-transformers if OpenAI is not available
    Processes in batches for better performance
    
    Args:
        texts: List of text chunks
        batch_size: Number of texts to process at once
    
    Returns:
        Numpy array of embeddings
    """
    # Try OpenAI first
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                print(f"🧠 Generating embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            embeddings = np.array(all_embeddings)
            print(f"✅ Generated {len(embeddings)} embeddings using OpenAI")
            return embeddings
        
        except Exception as e:
            print(f"OpenAI embedding error: {str(e)}, falling back to sentence-transformers")
    
    # Fallback to sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        
        print("🧠 Loading sentence-transformers model...")
        # Load model (cached after first load)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"🧠 Generating embeddings for {len(texts)} chunks...")
        # Generate embeddings in batches
        embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        
        print(f"✅ Generated {len(embeddings)} embeddings using sentence-transformers")
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
