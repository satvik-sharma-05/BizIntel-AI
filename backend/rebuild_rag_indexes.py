"""
Rebuild RAG Indexes - Rebuild FAISS and Neo4j from MongoDB chunks
Run this if you have chunks in MongoDB but FAISS/Neo4j are empty
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import vector_store
from app.rag.neo4j_rag import neo4j_rag
from app.database.neo4j_client import neo4j_client
import certifi
import numpy as np

async def rebuild_indexes():
    """Rebuild FAISS and Neo4j indexes from MongoDB chunks"""
    
    print("=" * 80)
    print("🔄 REBUILDING RAG INDEXES")
    print("=" * 80)
    
    # Connect to MongoDB
    print("\n📦 Connecting to MongoDB...")
    client = AsyncIOMotorClient(
        settings.mongodb_url,
        tls=True,
        tlsCAFile=certifi.where()
    )
    db = client[settings.MONGODB_DB_NAME]
    print("✅ MongoDB connected")
    
    # Connect to Neo4j
    print("\n🕸️  Connecting to Neo4j...")
    neo4j_client.connect()
    if neo4j_client.connected:
        print("✅ Neo4j connected")
        neo4j_rag.create_indexes()
    else:
        print("⚠️  Neo4j not connected - skipping Neo4j rebuild")
    
    # Get all documents
    print("\n📄 Fetching documents...")
    documents = await db.documents.find({"status": "completed"}).to_list(length=None)
    print(f"✅ Found {len(documents)} completed documents")
    
    if not documents:
        print("\n⚠️  No completed documents found. Upload documents first.")
        return
    
    # Process each document
    for doc_idx, document in enumerate(documents, 1):
        document_id = document["document_id"]
        business_id = document["business_id"]
        filename = document["filename"]
        
        print(f"\n{'='*80}")
        print(f"📄 Processing document {doc_idx}/{len(documents)}: {filename}")
        print(f"{'='*80}")
        
        # Get chunks for this document
        chunks = await db.rag_chunks.find({
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
    
    if neo4j_client.connected:
        # Get Neo4j stats for each business
        business_ids = set(doc["business_id"] for doc in documents)
        print(f"\n🕸️  Neo4j:")
        for business_id in business_ids:
            stats = neo4j_rag.get_business_knowledge_graph(business_id)
            print(f"   Business {business_id}:")
            print(f"      - Documents: {stats.get('document_count', 0)}")
            print(f"      - Chunks: {stats.get('chunk_count', 0)}")
            print(f"      - Entities: {stats.get('entity_count', 0)}")
    
    print(f"\n{'='*80}")
    print("✅ REBUILD COMPLETE")
    print(f"{'='*80}\n")
    
    # Close connections
    client.close()
    neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(rebuild_indexes())
