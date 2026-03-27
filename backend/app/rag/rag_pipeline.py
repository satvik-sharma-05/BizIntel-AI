"""
RAG Pipeline - Hybrid multi-database retrieval system
Uses FAISS + Neo4j + MongoDB + BM25 for optimal retrieval
"""
from typing import List, Dict, Any, Optional
from .embeddings import generate_single_embedding
from .vector_store import vector_store
from .neo4j_rag import neo4j_rag
from ..services.llm_service import call_openrouter
from ..database.mongodb import collections
import os

class RAGPipeline:
    """Hybrid RAG pipeline using FAISS + Neo4j + MongoDB + BM25"""
    
    def __init__(self):
        self.vector_store = vector_store  # FAISS + BM25
        self.neo4j_rag = neo4j_rag  # Neo4j knowledge graph
        self._embedding_cache = {}  # Cache embeddings for common queries
        
        # Load configuration from .env
        self.top_k = int(os.getenv("RAG_TOP_K", "5"))
        self.score_threshold = float(os.getenv("RAG_SCORE_THRESHOLD", "0.7"))
    
    async def query(
        self,
        question: str,
        business_id: str,
        mode: str = "hybrid",  # "document_only" or "hybrid"
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Hybrid query using all databases:
        1. FAISS vector search (semantic similarity)
        2. BM25 keyword search (exact matches)
        3. Neo4j graph search (relationships & entities)
        4. MongoDB metadata enrichment
        
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
        
        print(f"\n{'='*80}")
        print(f"🔍 HYBRID RAG QUERY")
        print(f"   Question: {question}")
        print(f"   Business ID: {business_id}")
        print(f"   Mode: {mode}")
        print(f"{'='*80}\n")
        
        # Check embedding cache
        cache_key = f"{question}:{business_id}"
        if cache_key in self._embedding_cache:
            query_embedding = self._embedding_cache[cache_key]
            print("✅ Using cached embedding")
        else:
            # Generate query embedding
            print("🧠 Generating query embedding...")
            query_embedding = generate_single_embedding(question)
            # Cache it (limit cache size)
            if len(self._embedding_cache) > 100:
                self._embedding_cache.clear()
            self._embedding_cache[cache_key] = query_embedding
            print("✅ Query embedding generated")
        
        # Step 1: FAISS + BM25 hybrid search
        print("\n[STEP 1/4] 🔎 FAISS + BM25 vector search...")
        faiss_results = self.vector_store.search(
            query_embedding,
            top_k=top_k * 2,  # Get more results for merging
            business_id=business_id,
            query_text=question,  # For BM25 search
            use_hybrid=True  # Enable FAISS + BM25 hybrid
        )
        print(f"✅ Found {len(faiss_results)} results from FAISS+BM25")
        
        # Step 2: Neo4j graph search
        print("\n[STEP 2/4] 🕸️  Neo4j knowledge graph search...")
        neo4j_results = neo4j_rag.search_chunks(
            query_text=question,
            business_id=business_id,
            limit=top_k
        )
        print(f"✅ Found {len(neo4j_results)} results from Neo4j")
        
        # Step 3: Merge all results with intelligent scoring
        print("\n[STEP 3/4] 🔀 Merging results from all sources...")
        merged_results = self._merge_hybrid_results(
            faiss_results=faiss_results,
            neo4j_results=neo4j_results,
            top_k=top_k
        )
        print(f"✅ Merged to {len(merged_results)} top results")
        
        # Step 4: Enrich with MongoDB metadata
        print("\n[STEP 4/4] 💾 Enriching with MongoDB metadata...")
        enriched_results = await self._enrich_with_mongodb(merged_results, business_id)
        print(f"✅ Enriched {len(enriched_results)} results")
        
        if not enriched_results:
            print("\n⚠️  No relevant documents found")
            return {
                "answer": "No relevant documents found. Please upload documents first.",
                "mode": mode,
                "has_documents": False,
                "citations": [],
                "sources": {
                    "faiss": 0,
                    "neo4j": 0,
                    "mongodb": 0
                }
            }
        
        # Build context from enriched chunks
        print("\n📝 Building context from results...")
        context = self._build_context_optimized(enriched_results)
        
        # Generate answer based on mode
        print(f"\n🤖 Generating {mode} answer...")
        if mode == "document_only":
            answer = self._generate_document_only_answer(question, context, enriched_results)
        else:  # hybrid
            answer = self._generate_hybrid_answer(question, context, enriched_results)
        
        # Build citations
        citations = self._build_citations(enriched_results)
        
        print(f"\n{'='*80}")
        print(f"✅ HYBRID RAG QUERY COMPLETE")
        print(f"{'='*80}\n")
        
        return {
            "answer": answer,
            "mode": mode,
            "has_documents": True,
            "citations": citations,
            "chunks_used": len(enriched_results),
            "sources": {
                "faiss_bm25": len(faiss_results),
                "neo4j": len(neo4j_results),
                "mongodb": len(enriched_results)
            }
        }
    
    def _merge_hybrid_results(
        self,
        faiss_results: List[Dict[str, Any]],
        neo4j_results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Merge results from FAISS+BM25 and Neo4j with intelligent scoring
        
        Scoring weights:
        - FAISS semantic: 40%
        - BM25 keyword: 30%
        - Neo4j graph: 30%
        """
        merged = {}
        
        # Add FAISS+BM25 results
        for result in faiss_results:
            chunk_id = result.get("chunk_id", f"{result.get('document_id', 'unknown')}_chunk_{result.get('chunk_index', 0)}")
            merged[chunk_id] = {
                **result,
                "faiss_score": result.get("faiss_score", 0),
                "bm25_score": result.get("bm25_score", 0),
                "neo4j_score": 0,
                "entities": [],
                "related_chunks": []
            }
        
        # Add Neo4j results
        for result in neo4j_results:
            chunk_id = result.get("chunk_id", "")
            neo4j_score = result.get("score", 0)
            entities = result.get("entities", [])
            
            if chunk_id in merged:
                # Enhance existing result
                merged[chunk_id]["neo4j_score"] = neo4j_score
                merged[chunk_id]["entities"] = entities
            else:
                # Add new result from Neo4j
                merged[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": result.get("text", ""),
                    "page_number": result.get("page_number", 1),
                    "chunk_index": result.get("chunk_index", 0),
                    "filename": result.get("filename", ""),
                    "document_id": result.get("document_id", ""),
                    "faiss_score": 0,
                    "bm25_score": 0,
                    "neo4j_score": neo4j_score,
                    "entities": entities,
                    "related_chunks": []
                }
        
        # Calculate hybrid score (40% FAISS + 30% BM25 + 30% Neo4j)
        for chunk_id, data in merged.items():
            data["hybrid_score"] = (
                0.4 * data["faiss_score"] +
                0.3 * data["bm25_score"] +
                0.3 * data["neo4j_score"]
            )
            
            # Boost score if entities found
            if data["entities"]:
                data["hybrid_score"] *= 1.1  # 10% boost for entity-rich chunks
        
        # Sort by hybrid score
        results = sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)
        
        return results[:top_k]
    
    async def _enrich_with_mongodb(
        self,
        results: List[Dict[str, Any]],
        business_id: str
    ) -> List[Dict[str, Any]]:
        """Enrich results with additional metadata from MongoDB"""
        enriched = []
        
        for result in results:
            chunk_id = result.get("chunk_id")
            
            # Get additional metadata from MongoDB
            try:
                mongo_chunk = await collections.rag_chunks().find_one({
                    "chunk_id": chunk_id,
                    "business_id": business_id
                })
                
                if mongo_chunk:
                    result["char_count"] = mongo_chunk.get("char_count", 0)
                    result["created_at"] = mongo_chunk.get("created_at")
                
                enriched.append(result)
            except Exception as e:
                print(f"⚠️  MongoDB enrichment failed for {chunk_id}: {e}")
                enriched.append(result)
        
        return enriched
    
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
