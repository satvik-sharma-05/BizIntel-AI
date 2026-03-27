"""
Document Upload API for RAG System
Supports PDF, DOCX, TXT files
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
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
import asyncio

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def process_document_background(
    file_path: str,
    document_id: str,
    business_id: str,
    filename: str,
    user_id: str
):
    """Background task to process document"""
    try:
        print(f"🔄 Background processing started: {filename}")
        print(f"📄 Document ID: {document_id}")
        
        # Extract text from document (sync operation)
        print(f"📖 Extracting text from {filename}...")
        document_data = load_document(file_path)
        print(f"✅ Extracted text from {document_data.get('total_pages', 1)} pages")
        
        # Split into chunks (sync operation)
        print(f"✂️ Splitting document into chunks...")
        chunks = split_document_into_chunks(document_data, chunk_size=300, chunk_overlap=30)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Limit chunks for free tier (max 100 chunks = ~10 pages)
        if len(chunks) > 100:
            print(f"⚠️ Limiting to 100 chunks (from {len(chunks)}) for performance")
            chunks = chunks[:100]
        
        # Generate embeddings (sync operation)
        print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Store in vector store (sync operation)
        print(f"💾 Storing in vector database...")
        vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            business_id=business_id,
            filename=filename
        )
        print(f"✅ Stored in vector database")
        
        # Store chunk metadata (async operation)
        print(f"💾 Storing chunk metadata in MongoDB...")
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
        print(f"✅ Stored chunk metadata")
        
        # Update document status to completed (async operation)
        await collections.documents().update_one(
            {"document_id": document_id},
            {"$set": {
                "status": "completed",
                "chunk_count": len(chunks),
                "total_pages": document_data.get("total_pages", 1),
                "processed_at": datetime.utcnow()
            }}
        )
        
        print(f"✅ Background processing complete: {filename}")
        print(f"📊 Final stats: {len(chunks)} chunks, {document_data.get('total_pages', 1)} pages")
        
    except Exception as e:
        print(f"❌ Background processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Update status to failed (async operation)
        try:
            await collections.documents().update_one(
                {"document_id": document_id},
                {"$set": {
                    "status": "failed",
                    "error": str(e),
                    "processed_at": datetime.utcnow()
                }}
            )
        except Exception as update_error:
            print(f"❌ Failed to update error status: {str(update_error)}")

@router.post("/upload/{business_id}")
async def upload_document(
    business_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload document for RAG system - Returns immediately, processes in background
    Supports: PDF, DOCX, TXT
    """
    try:
        print(f"📤 Upload started: {file.filename}")
        
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
        file_size = len(content)
        print(f"📄 File read: {file_size} bytes")
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file to disk
        file_path = UPLOAD_DIR / f"{document_id}{file_ext}"
        with open(file_path, "wb") as f:
            f.write(content)
        print(f"💾 File saved: {file_path}")
        
        # Store initial metadata in MongoDB
        document_metadata = {
            "document_id": document_id,
            "user_id": user_id,
            "business_id": business_id,
            "filename": file.filename,
            "file_type": file_ext[1:],
            "file_size": file_size,
            "file_path": str(file_path),
            "chunk_count": 0,
            "total_pages": 0,
            "status": "processing",
            "upload_date": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await collections.documents().insert_one(document_metadata)
        print(f"✅ Metadata saved")
        
        # Add background task for processing
        background_tasks.add_task(
            process_document_background,
            str(file_path),
            document_id,
            business_id,
            file.filename,
            user_id
        )
        print(f"🔄 Background task queued")
        
        # Return immediately with document_id for status polling
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "file_type": file_ext[1:],
            "file_size": file_size,
            "status": "processing",
            "chunk_count": 0,
            "total_pages": 0,
            "message": "File uploaded successfully. Processing in background..."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
                    "status": doc.get("status", "completed"),
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

@router.get("/status/{document_id}")
async def get_document_status(
    document_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get processing status of a document"""
    try:
        document = await collections.documents().find_one({
            "document_id": document_id,
            "user_id": user_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document_id": document_id,
            "status": document.get("status", "completed"),
            "chunk_count": document.get("chunk_count", 0),
            "total_pages": document.get("total_pages", 0),
            "error": document.get("error")
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
