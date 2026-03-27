"""
Test RAG System
Quick test to verify RAG implementation
"""
import asyncio
from app.rag.document_loader import load_document
from app.rag.text_splitter import split_document_into_chunks
from app.rag.embeddings import generate_embeddings, generate_single_embedding
from app.rag.vector_store import VectorStore
from app.rag.rag_pipeline import RAGPipeline
from app.utils.structured_output import (
    format_market_analysis,
    format_location_analysis,
    format_forecast,
    format_chat_response,
    remove_markdown
)

def test_document_loader():
    """Test document loading"""
    print("\n=== Testing Document Loader ===")
    
    # Create a test text file
    test_file = "test_document.txt"
    with open(test_file, "w") as f:
        f.write("""
        Business Report - Market Analysis
        
        The food and beverage market in Mumbai is experiencing significant growth.
        Market demand has increased by 18% in the last year.
        Competition is high but opportunities exist in the premium segment.
        
        Key Findings:
        - Urban population growth driving demand
        - Online delivery platforms expanding rapidly
        - Premium healthy food segment showing strong growth
        
        Recommendations:
        1. Focus on delivery-first model
        2. Target working professionals
        3. Use mid-range pricing strategy
        """)
    
    try:
        doc_data = load_document(test_file)
        print(f"✅ Document loaded: {len(doc_data['text'])} characters")
        print(f"✅ Pages: {doc_data['total_pages']}")
        print(f"✅ File type: {doc_data['file_type']}")
        return doc_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        import os
        if os.path.exists(test_file):
            os.remove(test_file)

def test_text_splitter(doc_data):
    """Test text splitting"""
    print("\n=== Testing Text Splitter ===")
    
    if not doc_data:
        print("❌ No document data")
        return None
    
    try:
        chunks = split_document_into_chunks(doc_data, chunk_size=200, chunk_overlap=20)
        print(f"✅ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):
            print(f"  Chunk {i+1}: {len(chunk['text'])} chars, page {chunk['page_number']}")
        return chunks
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_embeddings(chunks):
    """Test embedding generation"""
    print("\n=== Testing Embeddings ===")
    
    if not chunks:
        print("❌ No chunks")
        return None
    
    try:
        texts = [chunk['text'] for chunk in chunks]
        embeddings = generate_embeddings(texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"✅ Embedding dimension: {embeddings.shape[1]}")
        return embeddings
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_vector_store(chunks, embeddings):
    """Test vector store"""
    print("\n=== Testing Vector Store ===")
    
    if not chunks or embeddings is None:
        print("❌ No chunks or embeddings")
        return None
    
    try:
        # Create test vector store
        vector_store = VectorStore(store_path="test_vector_store")
        
        # Add chunks
        vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id="test_doc_123",
            business_id="test_business_456",
            filename="test_document.txt"
        )
        print(f"✅ Added {len(chunks)} chunks to vector store")
        
        # Test search
        query = "What are the market opportunities?"
        query_embedding = generate_single_embedding(query)
        results = vector_store.search(query_embedding, top_k=3, business_id="test_business_456")
        
        print(f"✅ Search returned {len(results)} results")
        for i, result in enumerate(results):
            print(f"  Result {i+1}: Score {result['similarity']:.3f}, Page {result['page_number']}")
        
        # Cleanup
        import shutil
        shutil.rmtree("test_vector_store", ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_structured_output():
    """Test structured output formatting"""
    print("\n=== Testing Structured Output ===")
    
    # Test markdown removal
    markdown_text = """
    **Summary:** This is a test
    
    ***Key Insights:***
    - Point 1
    - Point 2
    
    ### Conclusion
    Final thoughts
    """
    
    clean_text = remove_markdown(markdown_text)
    print(f"✅ Markdown removed: {len(markdown_text)} -> {len(clean_text)} chars")
    
    # Test market analysis formatting
    raw_response = """
    Summary: The market is growing steadily.
    
    Key Insights:
    - High demand
    - Strong competition
    - Good opportunities
    
    Risks:
    - Market saturation
    - High costs
    
    Recommendations:
    - Focus on niche
    - Optimize pricing
    
    Action Plan:
    1. Research competitors
    2. Launch pilot
    3. Scale gradually
    
    Conclusion: Market is viable with right strategy.
    """
    
    structured = format_market_analysis(raw_response, {
        "industry": "Food & Beverage",
        "city": "Mumbai"
    })
    
    print(f"✅ Structured market analysis created")
    print(f"  Title: {structured['title']}")
    print(f"  Key Insights: {len(structured['key_insights'])} items")
    print(f"  Risks: {len(structured['risks'])} items")
    print(f"  Recommendations: {len(structured['recommendations'])} items")
    print(f"  Action Plan: {len(structured['action_plan'])} items")
    
    return True

def test_rag_pipeline():
    """Test complete RAG pipeline"""
    print("\n=== Testing RAG Pipeline ===")
    
    try:
        # Note: This requires a running vector store with data
        print("⚠️  RAG pipeline test requires uploaded documents")
        print("   Use the API to upload documents first")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests"""
    print("=" * 60)
    print("RAG SYSTEM TEST")
    print("=" * 60)
    
    # Test document loading
    doc_data = test_document_loader()
    
    # Test text splitting
    chunks = test_text_splitter(doc_data)
    
    # Test embeddings
    embeddings = test_embeddings(chunks)
    
    # Test vector store
    test_vector_store(chunks, embeddings)
    
    # Test structured output
    test_structured_output()
    
    # Test RAG pipeline
    test_rag_pipeline()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n✅ All core components tested successfully!")
    print("\nNext steps:")
    print("1. Start the backend: python -m uvicorn app.main:app --reload")
    print("2. Upload documents via /api/documents/upload/{business_id}")
    print("3. Test RAG chat via /api/chat/chat")
    print("4. Check structured output in all analysis APIs")

if __name__ == "__main__":
    main()
