"""
Neo4j Graph Database Client
Stores business relationships and enables graph-based queries
"""
from neo4j import GraphDatabase
from ..config.settings import settings
from typing import Dict, List, Any, Optional

class Neo4jClient:
    """Neo4j database client for graph relationships"""
    
    def __init__(self):
        self.driver = None
        self.connected = False
    
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.connected = True
            print("✅ Neo4j connected")
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            self.connected = False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("👋 Neo4j disconnected")
    
    def create_business_node(self, business_data: Dict[str, Any]):
        """Create business node in graph"""
        if not self.connected:
            return
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (b:Business {id: $business_id})
                SET b.name = $name,
                    b.industry = $industry,
                    b.investment = $investment,
                    b.created_at = datetime()
                RETURN b
                """
                session.run(query, 
                    business_id=business_data.get("business_id"),
                    name=business_data.get("name"),
                    industry=business_data.get("industry"),
                    investment=business_data.get("investment", 0)
                )
        except Exception as e:
            print(f"Error creating business node: {e}")
    
    def create_location_relationship(self, business_id: str, city: str, state: str):
        """Create business -> city relationship"""
        if not self.connected:
            return
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (b:Business {id: $business_id})
                MERGE (c:City {name: $city, state: $state})
                MERGE (b)-[r:LOCATED_IN]->(c)
                RETURN b, c, r
                """
                session.run(query, business_id=business_id, city=city, state=state)
        except Exception as e:
            print(f"Error creating location relationship: {e}")
    
    def create_industry_relationship(self, business_id: str, industry: str):
        """Create business -> industry relationship"""
        if not self.connected:
            return
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (b:Business {id: $business_id})
                MERGE (i:Industry {name: $industry})
                MERGE (b)-[r:OPERATES_IN]->(i)
                RETURN b, i, r
                """
                session.run(query, business_id=business_id, industry=industry)
        except Exception as e:
            print(f"Error creating industry relationship: {e}")
    
    def create_market_relationship(self, business_id: str, market_data: Dict[str, Any]):
        """Create business -> market relationship"""
        if not self.connected:
            return
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (b:Business {id: $business_id})
                MERGE (m:Market {
                    industry: $industry,
                    city: $city
                })
                SET m.demand_score = $demand_score,
                    m.competition = $competition,
                    m.opportunity = $opportunity,
                    m.updated_at = datetime()
                MERGE (b)-[r:TARGETS]->(m)
                RETURN b, m, r
                """
                session.run(query,
                    business_id=business_id,
                    industry=market_data.get("industry"),
                    city=market_data.get("city"),
                    demand_score=market_data.get("demand_score", 0),
                    competition=market_data.get("competition", "Unknown"),
                    opportunity=market_data.get("opportunity", "Unknown")
                )
        except Exception as e:
            print(f"Error creating market relationship: {e}")
    
    def create_risk_nodes(self, business_id: str, risks: List[str]):
        """Create risk nodes and relationships"""
        if not self.connected or not risks:
            return
        
        try:
            with self.driver.session() as session:
                for risk in risks:
                    query = """
                    MATCH (b:Business {id: $business_id})
                    MERGE (r:Risk {description: $risk})
                    MERGE (b)-[rel:HAS_RISK]->(r)
                    RETURN b, r, rel
                    """
                    session.run(query, business_id=business_id, risk=risk)
        except Exception as e:
            print(f"Error creating risk nodes: {e}")
    
    def create_opportunity_nodes(self, business_id: str, opportunities: List[str]):
        """Create opportunity nodes and relationships"""
        if not self.connected or not opportunities:
            return
        
        try:
            with self.driver.session() as session:
                for opp in opportunities:
                    query = """
                    MATCH (b:Business {id: $business_id})
                    MERGE (o:Opportunity {description: $opportunity})
                    MERGE (b)-[rel:HAS_OPPORTUNITY]->(o)
                    RETURN b, o, rel
                    """
                    session.run(query, business_id=business_id, opportunity=opp)
        except Exception as e:
            print(f"Error creating opportunity nodes: {e}")
    
    def get_similar_businesses(self, industry: str, city: str, limit: int = 5) -> List[Dict]:
        """Find similar businesses in same industry/city"""
        if not self.connected:
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (b:Business)-[:OPERATES_IN]->(i:Industry {name: $industry})
                MATCH (b)-[:LOCATED_IN]->(c:City {name: $city})
                RETURN b.id as business_id, b.name as name, b.investment as investment
                LIMIT $limit
                """
                result = session.run(query, industry=industry, city=city, limit=limit)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Error getting similar businesses: {e}")
            return []
    
    def get_market_insights(self, industry: str, city: str) -> Dict[str, Any]:
        """Get market insights from graph"""
        if not self.connected:
            return {}
        
        try:
            with self.driver.session() as session:
                # Count businesses in same market
                query = """
                MATCH (b:Business)-[:OPERATES_IN]->(i:Industry {name: $industry})
                MATCH (b)-[:LOCATED_IN]->(c:City {name: $city})
                RETURN count(b) as business_count
                """
                result = session.run(query, industry=industry, city=city)
                record = result.single()
                
                business_count = record["business_count"] if record else 0
                
                # Get common risks
                risk_query = """
                MATCH (b:Business)-[:OPERATES_IN]->(i:Industry {name: $industry})
                MATCH (b)-[:HAS_RISK]->(r:Risk)
                RETURN r.description as risk, count(r) as frequency
                ORDER BY frequency DESC
                LIMIT 5
                """
                risk_result = session.run(risk_query, industry=industry)
                common_risks = [dict(record) for record in risk_result]
                
                # Get common opportunities
                opp_query = """
                MATCH (b:Business)-[:OPERATES_IN]->(i:Industry {name: $industry})
                MATCH (b)-[:HAS_OPPORTUNITY]->(o:Opportunity)
                RETURN o.description as opportunity, count(o) as frequency
                ORDER BY frequency DESC
                LIMIT 5
                """
                opp_result = session.run(opp_query, industry=industry)
                common_opportunities = [dict(record) for record in opp_result]
                
                return {
                    "business_count": business_count,
                    "competition_level": "High" if business_count > 10 else "Medium" if business_count > 5 else "Low",
                    "common_risks": common_risks,
                    "common_opportunities": common_opportunities
                }
        except Exception as e:
            print(f"Error getting market insights: {e}")
            return {}
    
    def get_expansion_cities(self, industry: str, current_city: str, limit: int = 5) -> List[Dict]:
        """Get recommended cities for expansion"""
        if not self.connected:
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:City)<-[:LOCATED_IN]-(b:Business)-[:OPERATES_IN]->(i:Industry {name: $industry})
                WHERE c.name <> $current_city
                WITH c, count(b) as business_count
                RETURN c.name as city, c.state as state, business_count
                ORDER BY business_count ASC
                LIMIT $limit
                """
                result = session.run(query, industry=industry, current_city=current_city, limit=limit)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Error getting expansion cities: {e}")
            return []
    
    def create_full_business_graph(self, business_data: Dict[str, Any], 
                                   market_data: Dict[str, Any],
                                   risks: List[str],
                                   opportunities: List[str]):
        """Create complete business graph with all relationships"""
        business_id = business_data.get("business_id")
        
        # Create business node
        self.create_business_node(business_data)
        
        # Create location relationship
        self.create_location_relationship(
            business_id,
            business_data.get("city"),
            business_data.get("state")
        )
        
        # Create industry relationship
        self.create_industry_relationship(
            business_id,
            business_data.get("industry")
        )
        
        # Create market relationship
        self.create_market_relationship(business_id, market_data)
        
        # Create risk nodes
        self.create_risk_nodes(business_id, risks)
        
        # Create opportunity nodes
        self.create_opportunity_nodes(business_id, opportunities)

# Global Neo4j client instance
neo4j_client = Neo4jClient()
