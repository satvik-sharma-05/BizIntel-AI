"""
Neo4j RAG - Knowledge Graph-based Retrieval Augmented Generation
Stores documents, chunks, entities, and relationships in Neo4j
"""
from typing import List, Dict, Any, Optional
from ..database.neo4j_client import neo4j_client
import json

class Neo4jRAG:
    """Neo4j-based RAG system with knowledge graph"""
    
    def __init__(self):
        self.client = neo4j_client
    
    def create_indexes(self):
        """Create Neo4j indexes for better performance"""
        if not self.client.connected:
            return
        
        indexes = [
            "CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.document_id)",
            "CREATE INDEX business_id IF NOT EXISTS FOR (d:Document) ON (d.business_id)",
            "CREATE INDEX chunk_id IF NOT EXISTS FOR (c:Chunk) ON (c.chunk_id)",
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            "CREATE FULLTEXT INDEX chunk_text IF NOT EXISTS FOR (c:Chunk) ON EACH [c.text]",
        ]
        
        for index_query in indexes:
            try:
                self.client.run_query(index_query)
            except Exception as e:
                print(f"Index creation (may already exist): {e}")
        
        print("✅ Neo4j RAG indexes created")
    
    def add_document(
        self,
        document_id: str,
        business_id: str,
        filename: str,
        file_type: str,
        total_pages: int,
        metadata: Dict[str, Any] = None
    ):
        """Create document node in Neo4j"""
        if not self.client.connected:
            return
        
        query = """
        MERGE (d:Document {document_id: $document_id})
        SET d.business_id = $business_id,
            d.filename = $filename,
            d.file_type = $file_type,
            d.total_pages = $total_pages,
            d.metadata = $metadata,
            d.created_at = datetime()
        
        // Link to business
        MERGE (b:Business {id: $business_id})
        MERGE (d)-[:BELONGS_TO]->(b)
        
        RETURN d
        """
        
        self.client.run_query(query, {
            "document_id": document_id,
            "business_id": business_id,
            "filename": filename,
            "file_type": file_type,
            "total_pages": total_pages,
            "metadata": json.dumps(metadata or {})
        })
        
        print(f"✅ Document node created in Neo4j: {filename}")
    
    def add_chunk(
        self,
        chunk_id: str,
        document_id: str,
        business_id: str,
        text: str,
        page_number: int,
        chunk_index: int,
        embedding: List[float] = None
    ):
        """Create chunk node and link to document"""
        if not self.client.connected:
            return
        
        query = """
        MATCH (d:Document {document_id: $document_id})
        
        CREATE (c:Chunk {
            chunk_id: $chunk_id,
            text: $text,
            page_number: $page_number,
            chunk_index: $chunk_index,
            business_id: $business_id,
            created_at: datetime()
        })
        
        MERGE (c)-[:PART_OF]->(d)
        
        RETURN c
        """
        
        self.client.run_query(query, {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "business_id": business_id,
            "text": text,
            "page_number": page_number,
            "chunk_index": chunk_index
        })
    
    def add_entity(
        self,
        entity_name: str,
        entity_type: str,
        chunk_id: str,
        business_id: str
    ):
        """Extract and create entity nodes (people, organizations, concepts)"""
        if not self.client.connected:
            return
        
        query = """
        MATCH (c:Chunk {chunk_id: $chunk_id})
        
        MERGE (e:Entity {name: $entity_name, type: $entity_type})
        SET e.business_id = $business_id
        
        MERGE (c)-[:MENTIONS]->(e)
        
        RETURN e
        """
        
        self.client.run_query(query, {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "chunk_id": chunk_id,
            "business_id": business_id
        })
    
    def link_related_chunks(
        self,
        chunk_id_1: str,
        chunk_id_2: str,
        relationship_type: str = "RELATED_TO",
        similarity_score: float = 0.0
    ):
        """Create relationships between related chunks"""
        if not self.client.connected:
            return
        
        query = f"""
        MATCH (c1:Chunk {{chunk_id: $chunk_id_1}})
        MATCH (c2:Chunk {{chunk_id: $chunk_id_2}})
        
        MERGE (c1)-[r:{relationship_type}]->(c2)
        SET r.similarity = $similarity_score
        
        RETURN r
        """
        
        self.client.run_query(query, {
            "chunk_id_1": chunk_id_1,
            "chunk_id_2": chunk_id_2,
            "similarity_score": similarity_score
        })
    
    def search_chunks(
        self,
        query_text: str,
        business_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search chunks using Neo4j full-text search"""
        if not self.client.connected:
            return []
        
        # Full-text search query
        search_query = """
        CALL db.index.fulltext.queryNodes('chunk_text', $query_text)
        YIELD node, score
        
        MATCH (node:Chunk)-[:PART_OF]->(d:Document)
        WHERE node.business_id = $business_id
        
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        
        RETURN node.chunk_id as chunk_id,
               node.text as text,
               node.page_number as page_number,
               node.chunk_index as chunk_index,
               d.filename as filename,
               d.document_id as document_id,
               score,
               collect(DISTINCT e.name) as entities
        ORDER BY score DESC
        LIMIT $limit
        """
        
        results = self.client.run_query(search_query, {
            "query_text": query_text,
            "business_id": business_id,
            "limit": limit
        })
        
        return results or []
    
    def get_related_chunks(
        self,
        chunk_id: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get chunks related to a given chunk through graph relationships"""
        if not self.client.connected:
            return []
        
        query = """
        MATCH (c:Chunk {chunk_id: $chunk_id})-[r:RELATED_TO|MENTIONS]-(related:Chunk)
        MATCH (related)-[:PART_OF]->(d:Document)
        
        RETURN DISTINCT related.chunk_id as chunk_id,
               related.text as text,
               related.page_number as page_number,
               d.filename as filename,
               type(r) as relationship_type
        LIMIT $limit
        """
        
        results = self.client.run_query(query, {
            "chunk_id": chunk_id,
            "limit": limit
        })
        
        return results or []
    
    def get_document_graph(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """Get the knowledge graph for a document"""
        if not self.client.connected:
            return {}
        
        query = """
        MATCH (d:Document {document_id: $document_id})
        OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
        
        RETURN d.filename as filename,
               count(DISTINCT c) as chunk_count,
               collect(DISTINCT e.name) as entities,
               collect(DISTINCT e.type) as entity_types
        """
        
        result = self.client.run_query(query, {"document_id": document_id})
        return result[0] if result else {}
    
    def get_business_knowledge_graph(
        self,
        business_id: str
    ) -> Dict[str, Any]:
        """Get the complete knowledge graph for a business"""
        if not self.client.connected:
            return {}
        
        query = """
        MATCH (b:Business {id: $business_id})
        OPTIONAL MATCH (b)<-[:BELONGS_TO]-(d:Document)
        OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
        
        RETURN b.name as business_name,
               count(DISTINCT d) as document_count,
               count(DISTINCT c) as chunk_count,
               count(DISTINCT e) as entity_count,
               collect(DISTINCT e.name)[0..10] as top_entities
        """
        
        result = self.client.run_query(query, {"business_id": business_id})
        return result[0] if result else {}
    
    def delete_document(self, document_id: str):
        """Delete document and all related nodes"""
        if not self.client.connected:
            return
        
        query = """
        MATCH (d:Document {document_id: $document_id})
        OPTIONAL MATCH (d)<-[:PART_OF]-(c:Chunk)
        OPTIONAL MATCH (c)-[r:MENTIONS]->()
        
        DETACH DELETE c, d
        """
        
        self.client.run_query(query, {"document_id": document_id})
        print(f"✅ Document deleted from Neo4j: {document_id}")
    
    def hybrid_search(
        self,
        query_text: str,
        business_id: str,
        faiss_results: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Combine FAISS vector search with Neo4j graph search"""
        if not self.client.connected:
            return faiss_results[:limit]
        
        # Get Neo4j full-text search results
        neo4j_results = self.search_chunks(query_text, business_id, limit)
        
        # Merge results (combine scores)
        merged = {}
        
        # Add FAISS results
        for result in faiss_results:
            chunk_id = result.get("chunk_id", f"{result['document_id']}_chunk_{result['chunk_index']}")
            merged[chunk_id] = {
                **result,
                "faiss_score": result.get("score", 0),
                "neo4j_score": 0,
                "entities": []
            }
        
        # Add Neo4j results
        for result in neo4j_results:
            chunk_id = result["chunk_id"]
            if chunk_id in merged:
                merged[chunk_id]["neo4j_score"] = result["score"]
                merged[chunk_id]["entities"] = result.get("entities", [])
            else:
                merged[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": result["text"],
                    "page_number": result["page_number"],
                    "chunk_index": result["chunk_index"],
                    "filename": result["filename"],
                    "document_id": result["document_id"],
                    "faiss_score": 0,
                    "neo4j_score": result["score"],
                    "entities": result.get("entities", [])
                }
        
        # Calculate hybrid score (50% FAISS + 50% Neo4j)
        for chunk_id, data in merged.items():
            data["hybrid_score"] = 0.5 * data["faiss_score"] + 0.5 * data["neo4j_score"]
        
        # Sort by hybrid score
        results = sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)
        
        return results[:limit]

# Global instance
neo4j_rag = Neo4jRAG()
