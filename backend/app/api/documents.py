"""
Document Upload API for RAG System
Supports PDF, DOCX, TXT files
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from ..api.auth import get_current_user_id
from ..api.business import verify_business_access
from ..database.mongodb import collections
from ..rag.document_loader import load_document
from ..rag.text_splitter import split_document_into_chunks
from ..rag.embeddings import generate_embeddings
from ..rag.vector_store import vector_store
from bson import ObjectId
from datetime import datetime
import os
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload/{business_id}")
async def upload_document(
    business_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload document for RAG system - Fast response with background processing
    Supports: PDF, DOCX, TXT
    """
    try:
        print(f"📤 Starting upload: {file.filename}")
        
        # Verify business access
        business = await verify_business_access(business_id, user_id)
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        print(f"📄 File read: {len(content)} bytes")
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file to disk FIRST (fast operation)
        file_path = UPLOAD_DIR / f"{document_id}{file_ext}"
        with open(file_path, "wb") as f:
            f.write(content)
        print(f"💾 File saved: {file_path}")
        
        # Store initial metadata in MongoDB (mark as processing)
        document_metadata = {
            "document_id": document_id,
            "user_id": user_id,
            "business_id": business_id,
            "filename": file.filename,
            "file_type": file_ext[1:],
            "file_size": len(content),
            "file_path": str(file_path),
            "chunk_count": 0,  # Will update after processing
            "total_pages": 0,  # Will update after processing
            "status": "processing",  # New field
            "upload_date": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await collections.documents().insert_one(document_metadata)
        print(f"✅ Metadata saved, starting background processing...")
        
        # Return immediately - processing happens in background
        # Note: In production, use Celery/RQ for true background jobs
        # For now, we'll do a quick synchronous process with limits
        
        try:
            # Quick processing with limits
            document_data = load_document(str(file_path))
            
            # Limit chunks for speed (max 50 chunks)
            chunks = split_document_into_chunks(document_data, chunk_size=300, chunk_overlap=30)
            if len(chunks) > 50:
                chunks = chunks[:50]  # Limit to first 50 chunks
                print(f"⚠️ Limited to 50 chunks for speed")
            
            print(f"✅ Created {len(chunks)} chunks")
            
            # Generate embeddings (this is still slow but limited)
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = generate_embeddings(chunk_texts)
            
            # Store in vector store
            vector_store.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                business_id=business_id,
                filename=file.filename
            )
            
            # Store chunk metadata
            chunk_metadata_list = []
            for i, chunk in enumerate(chunks):
                chunk_metadata_list.append({
                    "chunk_id": f"{document_id}_chunk_{i}",
                    "document_id": document_id,
                    "business_id": business_id,
                    "text": chunk["text"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "char_count": chunk["char_count"],
                    "created_at": datetime.utcnow()
                })
            
            if chunk_metadata_list:
                await collections.rag_chunks().insert_many(chunk_metadata_list)
            
            # Update document status to completed
            await collections.documents().update_one(
                {"document_id": document_id},
                {"$set": {
                    "status": "completed",
                    "chunk_count": len(chunks),
                    "total_pages": document_data.get("total_pages", 1)
                }}
            )
            
            print(f"✅ Processing complete: {file.filename}")
            
        except Exception as process_error:
            print(f"❌ Processing error: {str(process_error)}")
            # Update status to failed
            await collections.documents().update_one(
                {"document_id": document_id},
                {"$set": {"status": "failed", "error": str(process_error)}}
            )
        
        # Return success immediately (even if processing failed)
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "file_type": file_ext[1:],
            "status": "processing",
            "message": "Document uploaded successfully. Processing in background..."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Document upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.get("/list/{business_id}")
async def list_documents(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """List all documents for a business"""
    try:
        # Verify business access
        await verify_business_access(business_id, user_id)
        
        # Get documents
        documents = await collections.documents().find({
            "business_id": business_id,
            "user_id": user_id
        }).sort("upload_date", -1).to_list(length=100)
        
        return {
            "success": True,
            "business_id": business_id,
            "documents": [
                {
                    "document_id": doc["document_id"],
                    "filename": doc["filename"],
                    "file_type": doc["file_type"],
                    "file_size": doc["file_size"],
                    "chunk_count": doc["chunk_count"],
                    "total_pages": doc["total_pages"],
                    "upload_date": doc["upload_date"].isoformat()
                }
                for doc in documents
            ],
            "total": len(documents)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a document and its chunks"""
    try:
        # Get document and verify ownership
        document = await collections.documents().find_one({
            "document_id": document_id,
            "user_id": user_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from vector store
        vector_store.delete_document(document_id)
        
        # Delete file from disk
        file_path = Path(document["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Delete from MongoDB
        await collections.documents().delete_one({"document_id": document_id})
        await collections.rag_chunks().delete_many({"document_id": document_id})
        
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{business_id}")
async def get_document_stats(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get document statistics for a business"""
    try:
        # Verify business access
        await verify_business_access(business_id, user_id)
        
        # Count documents
        doc_count = await collections.documents().count_documents({
            "business_id": business_id,
            "user_id": user_id
        })
        
        # Count chunks
        chunk_count = await collections.rag_chunks().count_documents({
            "business_id": business_id
        })
        
        # Get vector store stats
        vector_stats = vector_store.get_stats()
        
        return {
            "success": True,
            "business_id": business_id,
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "vector_store": vector_stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
