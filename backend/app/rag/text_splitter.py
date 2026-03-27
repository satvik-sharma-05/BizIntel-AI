"""
Text Splitter - Splits documents into chunks for embedding
"""
from typing import List, Dict, Any

def split_text_into_chunks(
    text: str,
    chunk_size: int = 300,  # Reduced from 500
    chunk_overlap: int = 30,  # Reduced from 50
    page_number: int = 1
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between chunks
        page_number: Page number for citation
    
    Returns:
        List of chunks with metadata
    """
    chunks = []
    
    # Clean text
    text = text.strip()
    if not text:
        return chunks
    
    # Split by sentences first
    sentences = text.replace('\n', ' ').split('. ')
    
    current_chunk = ""
    chunk_index = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Add period back if not present
        if not sentence.endswith('.'):
            sentence += '.'
        
        # Check if adding this sentence exceeds chunk size
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                "text": current_chunk.strip(),
                "page_number": page_number,
                "chunk_index": chunk_index,
                "char_count": len(current_chunk)
            })
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
            current_chunk = overlap_text + " " + sentence
            chunk_index += 1
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add last chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "page_number": page_number,
            "chunk_index": chunk_index,
            "char_count": len(current_chunk)
        })
    
    return chunks

def split_document_into_chunks(
    document_data: Dict[str, Any],
    chunk_size: int = 300,  # Reduced from 500
    chunk_overlap: int = 30  # Reduced from 50
) -> List[Dict[str, Any]]:
    """
    Split entire document into chunks
    
    Args:
        document_data: Document data from document_loader
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of all chunks from document
    """
    all_chunks = []
    
    pages = document_data.get("pages", [])
    
    for page in pages:
        page_number = page.get("page_number", 1)
        page_text = page.get("text", "")
        
        page_chunks = split_text_into_chunks(
            page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            page_number=page_number
        )
        
        all_chunks.extend(page_chunks)
    
    return all_chunks
