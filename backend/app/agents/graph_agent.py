"""
Graph Agent - Queries Neo4j for relationship insights
"""
from .base_agent import BaseAgent
from ..database.neo4j_client import neo4j_client
from typing import Dict, Any

class GraphAgent(BaseAgent):
    """Agent that queries Neo4j graph database for relationship insights"""
    
    def __init__(self):
        super().__init__(
            agent_id="graph_agent",
            name="Graph Intelligence Agent",
            description="Queries Neo4j graph database for business relationships and market insights"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query Neo4j for business relationships and insights
        
        Args:
            context: {
                "business_id": str,
                "industry": str,
                "city": str,
                "state": str
            }
        
        Returns:
            {
                "success": bool,
                "data": {
                    "similar_businesses": list,
                    "market_insights": dict,
                    "expansion_cities": list,
                    "competition_analysis": dict
                }
            }
        """
        try:
            industry = context.get("industry")
            city = context.get("city")
            
            # Get similar businesses
            similar_businesses = neo4j_client.get_similar_businesses(
                industry=industry,
                city=city,
                limit=5
            )
            
            # Get market insights from graph
            market_insights = neo4j_client.get_market_insights(
                industry=industry,
                city=city
            )
            
            # Get expansion recommendations
            expansion_cities = neo4j_client.get_expansion_cities(
                industry=industry,
                current_city=city,
                limit=5
            )
            
            # Build competition analysis
            competition_analysis = {
                "competitor_count": len(similar_businesses),
                "competition_level": market_insights.get("competition_level", "Unknown"),
                "market_saturation": "High" if len(similar_businesses) > 10 else "Medium" if len(similar_businesses) > 5 else "Low"
            }
            
            return {
                "success": True,
                "data": {
                    "similar_businesses": similar_businesses,
                    "market_insights": market_insights,
                    "expansion_cities": expansion_cities,
                    "competition_analysis": competition_analysis,
                    "graph_available": neo4j_client.connected
                },
                "message": "Graph intelligence retrieved successfully"
            }
        
        except Exception as e:
            self.log(f"Graph Agent Error: {str(e)}", "error")
            return {
                "success": False,
                "data": {
                    "similar_businesses": [],
                    "market_insights": {},
                    "expansion_cities": [],
                    "competition_analysis": {},
                    "graph_available": False
                },
                "message": f"Graph query failed: {str(e)}",
                "errors": [str(e)]
            }

# Global instance
graph_agent = GraphAgent()
