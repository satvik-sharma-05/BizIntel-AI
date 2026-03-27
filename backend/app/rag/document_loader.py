"""
Document Loader - Extracts text from PDF, DOCX, TXT files
"""
import os
from typing import Dict, Any
from pathlib import Path

def load_document(file_path: str) -> Dict[str, Any]:
    """
    Load and extract text from document
    Supports: PDF, DOCX, TXT
    """
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        return load_txt(file_path)
    elif file_ext == '.pdf':
        return load_pdf(file_path)
    elif file_ext == '.docx':
        return load_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

def load_txt(file_path: str) -> Dict[str, Any]:
    """Load text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "text": text,
            "pages": [{"page_number": 1, "text": text}],
            "total_pages": 1,
            "file_type": "txt"
        }
    except Exception as e:
        raise Exception(f"Error loading TXT file: {str(e)}")

def load_pdf(file_path: str) -> Dict[str, Any]:
    """Load PDF file"""
    try:
        import PyPDF2
        
        pages = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                pages.append({
                    "page_number": page_num + 1,
                    "text": text
                })
        
        full_text = "\n\n".join([p["text"] for p in pages])
        
        return {
            "text": full_text,
            "pages": pages,
            "total_pages": total_pages,
            "file_type": "pdf"
        }
    except ImportError:
        raise Exception("PyPDF2 not installed. Install with: pip install PyPDF2")
    except Exception as e:
        raise Exception(f"Error loading PDF file: {str(e)}")

def load_docx(file_path: str) -> Dict[str, Any]:
    """Load DOCX file"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        full_text = "\n\n".join(paragraphs)
        
        return {
            "text": full_text,
            "pages": [{"page_number": 1, "text": full_text}],
            "total_pages": 1,
            "file_type": "docx",
            "paragraphs": paragraphs
        }
    except ImportError:
        raise Exception("python-docx not installed. Install with: pip install python-docx")
    except Exception as e:
        raise Exception(f"Error loading DOCX file: {str(e)}")
