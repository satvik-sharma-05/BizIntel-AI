"""
Admin API - Administrative endpoints for maintenance
"""
from fastapi import APIRouter, HTTPException, Depends
from ..api.auth import get_current_user_id
from ..database.mongodb import collections
from ..rag.embeddings import generate_embeddings
from ..rag.vector_store import vector_store
from ..rag.neo4j_rag import neo4j_rag
from ..database.neo4j_client import neo4j_client
import asyncio

router = APIRouter()

@router.post("/rebuild-rag-indexes")
async def rebuild_rag_indexes(
    user_id: str = Depends(get_current_user_id)
):
    """
    Rebuild FAISS and Neo4j indexes from MongoDB chunks
    Use this if you have chunks in MongoDB but FAISS/Neo4j are empty
    """
    try:
        print("\n" + "=" * 80)
        print("🔄 REBUILDING RAG INDEXES")
        print("=" * 80)
        
        # Get all completed documents
        print("\n📄 Fetching documents...")
        documents = await collections.documents().find({"status": "completed"}).to_list(length=None)
        print(f"✅ Found {len(documents)} completed documents")
        
        if not documents:
            return {
                "success": False,
                "message": "No completed documents found. Upload documents first.",
                "stats": {}
            }
        
        total_chunks_processed = 0
        documents_processed = 0
        
        # Process each document
        for doc_idx, document in enumerate(documents, 1):
            document_id = document["document_id"]
            business_id = document["business_id"]
            filename = document["filename"]
            
            print(f"\n{'='*80}")
            print(f"📄 Processing document {doc_idx}/{len(documents)}: {filename}")
            print(f"{'='*80}")
            
            # Get chunks for this document
            chunks = await collections.rag_chunks().find({
                "document_id": document_id
            }).sort("chunk_index", 1).to_list(length=None)
            
            if not chunks:
                print(f"⚠️  No chunks found for {filename}")
                continue
            
            print(f"✅ Found {len(chunks)} chunks")
            
            # Prepare chunk data
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_list = [
                {
                    "text": chunk["text"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "char_count": chunk.get("char_count", len(chunk["text"]))
                }
                for chunk in chunks
            ]
            
            # Generate embeddings
            print(f"🧠 Generating embeddings for {len(chunk_texts)} chunks...")
            embeddings = generate_embeddings(chunk_texts)
            print(f"✅ Generated embeddings: {embeddings.shape}")
            
            # Add to FAISS
            print(f"💾 Adding to FAISS...")
            vector_store.add_chunks(
                chunks=chunk_list,
                embeddings=embeddings,
                document_id=document_id,
                business_id=business_id,
                filename=filename
            )
            print(f"✅ Added to FAISS")
            
            # Add to Neo4j
            if neo4j_client.connected:
                print(f"🕸️  Adding to Neo4j...")
                
                # Create document node
                neo4j_rag.add_document(
                    document_id=document_id,
                    business_id=business_id,
                    filename=filename,
                    file_type=document.get("file_type", "unknown"),
                    total_pages=document.get("total_pages", 1),
                    metadata={"user_id": document.get("user_id")}
                )
                
                # Create chunk nodes
                for chunk in chunks:
                    neo4j_rag.add_chunk(
                        chunk_id=chunk["chunk_id"],
                        document_id=document_id,
                        business_id=business_id,
                        text=chunk["text"],
                        page_number=chunk["page_number"],
                        chunk_index=chunk["chunk_index"]
                    )
                
                print(f"✅ Added to Neo4j")
            
            total_chunks_processed += len(chunks)
            documents_processed += 1
        
        # Get final stats
        print(f"\n{'='*80}")
        print("📊 FINAL STATISTICS")
        print(f"{'='*80}")
        
        faiss_stats = vector_store.get_stats()
        print(f"\n💾 FAISS:")
        print(f"   - Total chunks: {faiss_stats['total_chunks']}")
        print(f"   - Total documents: {faiss_stats['total_documents']}")
        print(f"   - Dimension: {faiss_stats['dimension']}")
        print(f"   - Has BM25: {faiss_stats['has_bm25']}")
        
        neo4j_stats = {}
        if neo4j_client.connected:
            # Get Neo4j stats for each business
            business_ids = set(doc["business_id"] for doc in documents)
            neo4j_stats = {}
            for business_id in business_ids:
                stats = neo4j_rag.get_business_knowledge_graph(business_id)
                neo4j_stats[business_id] = stats
                print(f"\n🕸️  Neo4j - Business {business_id}:")
                print(f"      - Documents: {stats.get('document_count', 0)}")
                print(f"      - Chunks: {stats.get('chunk_count', 0)}")
                print(f"      - Entities: {stats.get('entity_count', 0)}")
        
        print(f"\n{'='*80}")
        print("✅ REBUILD COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "message": f"Successfully rebuilt indexes for {documents_processed} documents",
            "stats": {
                "documents_processed": documents_processed,
                "total_chunks": total_chunks_processed,
                "faiss": faiss_stats,
                "neo4j": neo4j_stats
            }
        }
    
    except Exception as e:
        print(f"\n❌ Rebuild failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

@router.get("/rag-status")
async def get_rag_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get status of all RAG indexes"""
    try:
        # MongoDB stats
        total_documents = await collections.documents().count_documents({})
        total_chunks = await collections.rag_chunks().count_documents({})
        
        # FAISS stats
        faiss_stats = vector_store.get_stats()
        
        # Neo4j stats
        neo4j_connected = neo4j_client.connected
        
        return {
            "success": True,
            "mongodb": {
                "documents": total_documents,
                "chunks": total_chunks
            },
            "faiss": faiss_stats,
            "neo4j": {
                "connected": neo4j_connected
            },
            "needs_rebuild": total_chunks > 0 and faiss_stats["total_chunks"] == 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-rag-indexes")
async def clear_rag_indexes(
    user_id: str = Depends(get_current_user_id)
):
    """Clear all RAG indexes (FAISS and Neo4j) - use with caution!"""
    try:
        print("\n⚠️  CLEARING ALL RAG INDEXES")
        
        # Clear FAISS
        import faiss
        from pathlib import Path
        
        store_path = Path(vector_store.store_path)
        
        # Delete FAISS files
        for file in ["index.faiss", "metadata.pkl", "bm25.pkl"]:
            file_path = store_path / file
            if file_path.exists():
                file_path.unlink()
                print(f"✅ Deleted {file}")
        
        # Reinitialize FAISS
        vector_store._initialized = False
        vector_store._ensure_initialized()
        print("✅ FAISS cleared and reinitialized")
        
        # Clear Neo4j
        if neo4j_client.connected:
            query = """
            MATCH (n)
            WHERE n:Document OR n:Chunk OR n:Entity
            DETACH DELETE n
            """
            neo4j_client.run_query(query)
            print("✅ Neo4j graph cleared")
        
        return {
            "success": True,
            "message": "All RAG indexes cleared successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")
