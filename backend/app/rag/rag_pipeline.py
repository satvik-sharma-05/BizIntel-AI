"""
RAG Pipeline - Optimized retrieval-augmented generation pipeline
Uses configuration from .env
"""
from typing import List, Dict, Any, Optional
from .embeddings import generate_single_embedding
from .vector_store import vector_store
from ..services.llm_service import call_openrouter
import os

class RAGPipeline:
    """Optimized RAG pipeline for document-based Q&A"""
    
    def __init__(self):
        self.vector_store = vector_store
        self._embedding_cache = {}  # Cache embeddings for common queries
        
        # Load configuration from .env
        self.top_k = int(os.getenv("RAG_TOP_K", "5"))
        self.score_threshold = float(os.getenv("RAG_SCORE_THRESHOLD", "0.7"))
    
    def query(
        self,
        question: str,
        business_id: str,
        mode: str = "hybrid",  # "document_only" or "hybrid"
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Query RAG system with optimized retrieval
        
        Args:
            question: User question
            business_id: Business ID for filtering
            mode: "document_only" or "hybrid"
            top_k: Number of chunks to retrieve (from .env if not provided)
        
        Returns:
            Structured response with answer and citations
        """
        # Use .env configuration if not provided
        if top_k is None:
            top_k = self.top_k
        
        # Check embedding cache
        cache_key = f"{question}:{business_id}"
        if cache_key in self._embedding_cache:
            query_embedding = self._embedding_cache[cache_key]
        else:
            # Generate query embedding
            query_embedding = generate_single_embedding(question)
            # Cache it (limit cache size)
            if len(self._embedding_cache) > 100:
                self._embedding_cache.clear()
            self._embedding_cache[cache_key] = query_embedding
        
        # Search vector store (FAISS is fast)
        relevant_chunks = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            business_id=business_id
        )
        
        if not relevant_chunks:
            return {
                "answer": "No relevant documents found. Please upload documents first.",
                "mode": mode,
                "has_documents": False,
                "citations": []
            }
        
        # Build context from chunks (optimized)
        context = self._build_context_optimized(relevant_chunks)
        
        # Generate answer based on mode
        if mode == "document_only":
            answer = self._generate_document_only_answer(question, context, relevant_chunks)
        else:  # hybrid
            answer = self._generate_hybrid_answer(question, context, relevant_chunks)
        
        # Build citations
        citations = self._build_citations(relevant_chunks)
        
        return {
            "answer": answer,
            "mode": mode,
            "has_documents": True,
            "citations": citations,
            "chunks_used": len(relevant_chunks)
        }
    
    def _build_context_optimized(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks - optimized version"""
        # Use list comprehension for speed
        context_parts = [
            f"[Doc {i}: {chunk['filename']}, P{chunk['page_number']}]\n{chunk['text']}"
            for i, chunk in enumerate(chunks, 1)
        ]
        return "\n\n".join(context_parts)
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Document {i}: {chunk['filename']}, Page {chunk['page_number']}]\n"
                f"{chunk['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_document_only_answer(
        self,
        question: str,
        context: str,
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Generate answer using only document content - uses hybrid model"""
        prompt = f"""Answer the question using ONLY the information from the provided documents.
Do not use any external knowledge.

Documents:
{context}

Question: {question}

Provide a clear, well-formatted answer based only on the document content.
If the documents don't contain the answer, say so clearly.

Use markdown formatting for better readability:
- Use **bold** for emphasis
- Use bullet points for lists
- Use proper headings (##, ###)
- Use code blocks if relevant

Structure your response clearly with sections."""

        messages = [
            {"role": "system", "content": "You are a document analysis assistant. Answer only based on provided documents. Use markdown formatting for clear, beautiful responses."},
            {"role": "user", "content": prompt}
        ]
        
        return call_openrouter(messages, max_tokens=1500, use_case="hybrid")
    
    def _generate_hybrid_answer(
        self,
        question: str,
        context: str,
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Generate answer combining document content and AI knowledge - uses hybrid model"""
        prompt = f"""Answer the question by combining information from the provided documents with your general knowledge.
Clearly separate document insights from AI analysis.

Documents:
{context}

Question: {question}

Provide a comprehensive, well-formatted answer using markdown:
- Use **bold** for emphasis
- Use bullet points and numbered lists
- Use proper headings (##, ###)
- Use tables if comparing data
- Use code blocks if relevant

Structure your response with clear sections:
## Answer
[Main answer here]

## Document Insights
[What the documents say]

## Analysis & Recommendations
[Your expert analysis and actionable recommendations]"""

        messages = [
            {"role": "system", "content": "You are a business intelligence assistant. Combine document insights with expert analysis. Use markdown formatting for clear, beautiful responses."},
            {"role": "user", "content": prompt}
        ]
        
        return call_openrouter(messages, max_tokens=2000, use_case="hybrid")
    
    def _build_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build citation list from chunks"""
        citations = []
        seen = set()
        
        for chunk in chunks:
            key = (chunk['filename'], chunk['page_number'])
            if key not in seen:
                citations.append({
                    "filename": chunk['filename'],
                    "page_number": chunk['page_number'],
                    "similarity": chunk.get('similarity', 0)
                })
                seen.add(key)
        
        return citations

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()
