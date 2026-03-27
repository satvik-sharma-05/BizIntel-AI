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

def process_document_background_sync(
    file_path: str,
    document_id: str,
    business_id: str,
    filename: str,
    user_id: str
):
    """Background task to process document - SYNC wrapper for async operations"""
    import asyncio
    
    print(f"=" * 80)
    print(f"🚀 BACKGROUND TASK STARTED (SYNC WRAPPER)")
    print(f"📄 Filename: {filename}")
    print(f"📄 Document ID: {document_id}")
    print(f"=" * 80)
    
    # Run the async version
    try:
        asyncio.run(process_document_background_async(
            file_path, document_id, business_id, filename, user_id
        ))
    except Exception as e:
        print(f"❌ Background task wrapper error: {str(e)}")
        import traceback
        traceback.print_exc()

async def process_document_background_async(
    file_path: str,
    document_id: str,
    business_id: str,
    filename: str,
    user_id: str
):
    """Background task to process document - ASYNC implementation"""
    print(f"=" * 80)
    print(f"🚀 BACKGROUND TASK STARTED")
    print(f"📄 Filename: {filename}")
    print(f"📄 Document ID: {document_id}")
    print(f"📄 File path: {file_path}")
    print(f"📄 Business ID: {business_id}")
    print(f"📄 User ID: {user_id}")
    print(f"=" * 80)
    
    try:
        # Step 1: Extract text
        print(f"\n[STEP 1/6] 📖 Extracting text from {filename}...")
        try:
            document_data = load_document(file_path)
            print(f"✅ [STEP 1/6] Extracted text from {document_data.get('total_pages', 1)} pages")
            print(f"   - Total pages: {document_data.get('total_pages', 1)}")
            print(f"   - Document data keys: {list(document_data.keys())}")
        except Exception as e:
            print(f"❌ [STEP 1/6] FAILED: {str(e)}")
            raise
        
        # Step 2: Split into chunks
        print(f"\n[STEP 2/6] ✂️ Splitting document into chunks...")
        try:
            chunks = split_document_into_chunks(document_data, chunk_size=300, chunk_overlap=30)
            print(f"✅ [STEP 2/6] Created {len(chunks)} chunks")
            
            # Limit chunks
            if len(chunks) > 100:
                print(f"⚠️ [STEP 2/6] Limiting to 100 chunks (from {len(chunks)}) for performance")
                chunks = chunks[:100]
        except Exception as e:
            print(f"❌ [STEP 2/6] FAILED: {str(e)}")
            raise
        
        # Step 3: Generate embeddings
        print(f"\n[STEP 3/6] 🧠 Generating embeddings for {len(chunks)} chunks...")
        try:
            chunk_texts = [chunk["text"] for chunk in chunks]
            print(f"   - Chunk texts prepared: {len(chunk_texts)} texts")
            embeddings = generate_embeddings(chunk_texts)
            print(f"✅ [STEP 3/6] Generated {len(embeddings)} embeddings")
            print(f"   - Embedding shape: {embeddings.shape if hasattr(embeddings, 'shape') else 'N/A'}")
        except Exception as e:
            print(f"❌ [STEP 3/6] FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # Step 4: Store in vector store
        print(f"\n[STEP 4/6] 💾 Storing in vector database...")
        try:
            vector_store.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                business_id=business_id,
                filename=filename
            )
            print(f"✅ [STEP 4/6] Stored in vector database")
        except Exception as e:
            print(f"❌ [STEP 4/6] FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # Step 5: Store chunk metadata in MongoDB
        print(f"\n[STEP 5/6] 💾 Storing chunk metadata in MongoDB...")
        try:
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
            
            print(f"   - Prepared {len(chunk_metadata_list)} metadata entries")
            
            if chunk_metadata_list:
                await collections.rag_chunks().insert_many(chunk_metadata_list)
                print(f"✅ [STEP 5/6] Stored {len(chunk_metadata_list)} chunk metadata entries")
        except Exception as e:
            print(f"❌ [STEP 5/6] FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # Step 6: Update document status
        print(f"\n[STEP 6/6] 📝 Updating document status to completed...")
        try:
            result = await collections.documents().update_one(
                {"document_id": document_id},
                {"$set": {
                    "status": "completed",
                    "chunk_count": len(chunks),
                    "total_pages": document_data.get("total_pages", 1),
                    "processed_at": datetime.utcnow()
                }}
            )
            print(f"✅ [STEP 6/6] Document status updated")
            print(f"   - Matched: {result.matched_count}, Modified: {result.modified_count}")
        except Exception as e:
            print(f"❌ [STEP 6/6] FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        print(f"\n" + "=" * 80)
        print(f"🎉 BACKGROUND PROCESSING COMPLETE")
        print(f"📊 Final stats: {len(chunks)} chunks, {document_data.get('total_pages', 1)} pages")
        print(f"=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n" + "=" * 80)
        print(f"❌ BACKGROUND PROCESSING FAILED")
        print(f"❌ Error: {str(e)}")
        print(f"=" * 80)
        import traceback
        traceback.print_exc()
        print(f"=" * 80 + "\n")
        
        # Update status to failed
        try:
            print(f"📝 Updating document status to failed...")
            await collections.documents().update_one(
                {"document_id": document_id},
                {"$set": {
                    "status": "failed",
                    "error": str(e),
                    "processed_at": datetime.utcnow()
                }}
            )
            print(f"✅ Document status updated to failed")
        except Exception as update_error:
            print(f"❌ Failed to update error status: {str(update_error)}")
            import traceback
            traceback.print_exc()

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
    print(f"\n{'='*80}")
    print(f"📤 UPLOAD REQUEST RECEIVED")
    print(f"   - Filename: {file.filename}")
    print(f"   - Business ID: {business_id}")
    print(f"   - User ID: {user_id}")
    print(f"{'='*80}\n")
    
    try:
        # Verify business access
        print(f"🔐 Verifying business access...")
        business = await verify_business_access(business_id, user_id)
        print(f"✅ Business access verified: {business.get('name')}")
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        print(f"📝 File extension: {file_ext}")
        
        if file_ext not in ALLOWED_EXTENSIONS:
            print(f"❌ Unsupported file type: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        print(f"📖 Reading file content...")
        content = await file.read()
        file_size = len(content)
        print(f"✅ File read: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            print(f"❌ File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        print(f"🆔 Generated document ID: {document_id}")
        
        # Save file to disk (async to avoid blocking)
        file_path = UPLOAD_DIR / f"{document_id}{file_ext}"
        print(f"💾 Saving file to: {file_path}")
        
        import aiofiles
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        print(f"✅ File saved successfully")
        
        # Store initial metadata in MongoDB
        print(f"📝 Storing metadata in MongoDB...")
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
        print(f"✅ Metadata saved to MongoDB")
        
        # Add background task for processing
        print(f"🔄 Queuing background task...")
        print(f"   - Function: process_document_background_sync")
        print(f"   - File path: {str(file_path)}")
        print(f"   - Document ID: {document_id}")
        
        background_tasks.add_task(
            process_document_background_sync,
            str(file_path),
            document_id,
            business_id,
            file.filename,
            user_id
        )
        print(f"✅ Background task queued successfully")
        
        response_data = {
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
        
        print(f"\n{'='*80}")
        print(f"✅ UPLOAD ENDPOINT RETURNING SUCCESS")
        print(f"   - Document ID: {document_id}")
        print(f"   - Status: processing")
        print(f"   - Background task: queued")
        print(f"{'='*80}\n")
        
        # Return immediately with document_id for status polling
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ UPLOAD ERROR")
        print(f"   - Error: {str(e)}")
        print(f"{'='*80}\n")
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
