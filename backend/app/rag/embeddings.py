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
    # Try OpenAI first (NO MEMORY OVERHEAD)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            import httpx
            
            # Create client with timeout
            client = OpenAI(
                api_key=openai_key,
                timeout=httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect
            )
            
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i//batch_size + 1
                total_batches = (len(texts) + batch_size - 1)//batch_size
                
                print(f"🧠 Generating embeddings for batch {batch_num}/{total_batches} ({len(batch)} texts)")
                
                try:
                    response = client.embeddings.create(
                        model="text-embedding-3-small",
                        input=batch
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    print(f"✅ Batch {batch_num}/{total_batches} complete")
                    
                except Exception as batch_error:
                    print(f"❌ Batch {batch_num} failed: {str(batch_error)}")
                    raise
            
            embeddings = np.array(all_embeddings)
            print(f"✅ Generated {len(embeddings)} embeddings using OpenAI")
            return embeddings
        
        except Exception as e:
            print(f"❌ OpenAI embedding error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Don't fallback to sentence-transformers on free tier - too much memory
            raise Exception(f"OpenAI embeddings failed: {str(e)}")
    
    # NO FALLBACK - sentence-transformers uses too much memory on free tier
    print(f"❌ OPENAI_API_KEY not set!")
    raise Exception("OPENAI_API_KEY not set. Sentence-transformers disabled on free tier due to memory constraints. Please set OPENAI_API_KEY environment variable.")

def generate_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for single text"""
    return generate_embeddings([text])[0]

def get_embedding_dimension() -> int:
    """Get the dimension of embeddings based on available provider"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return 1536  # text-embedding-3-small dimension
    else:
        # Default to OpenAI dimension even if key not set
        # Sentence-transformers disabled on free tier
        return 1536
