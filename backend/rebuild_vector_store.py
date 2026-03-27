"""
Rebuild Vector Store - Regenerate embeddings for all documents
Use this if you switch embedding providers (e.g., from sentence-transformers to OpenAI)
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.mongodb import collections, connect_to_mongodb, close_mongodb_connection
from app.rag.document_loader import load_document
from app.rag.text_splitter import split_document_into_chunks
from app.rag.embeddings import generate_embeddings, get_embedding_dimension
from app.rag.vector_store import vector_store

async def rebuild_vector_store():
    """Rebuild entire vector store from documents in MongoDB"""
    print("🔄 Rebuilding Vector Store...")
    print(f"📊 Using embedding dimension: {get_embedding_dimension()}")
    
    # Connect to MongoDB
    await connect_to_mongodb()
    
    try:
        # Get all documents
        documents = await collections.documents().find({}).to_list(length=None)
        
        if not documents:
            print("⚠️  No documents found in database")
            return
        
        print(f"📚 Found {len(documents)} documents to process")
        
        # Clear existing vector store
        print("🗑️  Clearing existing vector store...")
        vector_store.metadata = []
        import faiss
        vector_store.index = faiss.IndexFlatL2(vector_store.dimension)
        
        # Process each document
        processed = 0
        failed = 0
        
        for doc in documents:
            try:
                document_id = doc["document_id"]
                business_id = doc["business_id"]
                filename = doc["filename"]
                file_path = doc["file_path"]
                
                print(f"\n📄 Processing: {filename}")
                
                # Check if file exists
                if not Path(file_path).exists():
                    print(f"   ⚠️  File not found: {file_path}")
                    failed += 1
                    continue
                
                # Load document
                document_data = load_document(file_path)
                
                # Split into chunks
                chunks = split_document_into_chunks(document_data, chunk_size=500, chunk_overlap=50)
                
                if not chunks:
                    print(f"   ⚠️  No chunks extracted")
                    failed += 1
                    continue
                
                print(f"   ✂️  Split into {len(chunks)} chunks")
                
                # Generate embeddings
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = generate_embeddings(chunk_texts)
                
                print(f"   🧠 Generated embeddings")
                
                # Add to vector store
                vector_store.add_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    document_id=document_id,
                    business_id=business_id,
                    filename=filename
                )
                
                print(f"   ✅ Added to vector store")
                processed += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {doc.get('filename', 'unknown')}: {str(e)}")
                failed += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Rebuild complete!")
        print(f"   Processed: {processed}")
        print(f"   Failed: {failed}")
        print(f"   Total chunks: {len(vector_store.metadata)}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error rebuilding vector store: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongodb_connection()

if __name__ == "__main__":
    print("="*60)
    print("Vector Store Rebuild Tool")
    print("="*60)
    print("\nThis will regenerate all embeddings from your documents.")
    print("Use this when switching embedding providers or fixing issues.")
    print("\nPress Ctrl+C to cancel, or wait 3 seconds to continue...")
    
    try:
        import time
        time.sleep(3)
        asyncio.run(rebuild_vector_store())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
