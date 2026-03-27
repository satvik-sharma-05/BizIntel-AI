"""
Orchestrator Agent
Coordinates all agents and manages the multi-agent workflow
"""
from .base_agent import BaseAgent
from .data_agent import DataAgent
from .market_agent import MarketAgent
from .location_agent import LocationAgent
from typing import Dict, Any
from datetime import datetime

class OrchestratorAgent(BaseAgent):
    """Orchestrator coordinates all agents in the system"""
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator Agent",
            description="Coordinates multi-agent workflow and manages agent communication"
        )
        
        # Initialize agents
        self.data_agent = DataAgent()
        self.market_agent = MarketAgent()
        self.location_agent = LocationAgent()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multi-agent workflow
        
        Context should contain:
        - business_id: int
        - business_name: str
        - industry: str
        - city: str
        - state: str
        - investment: float
        - query: str (optional)
        """
        
        business_id = context.get("business_id")
        query = context.get("query", "")
        
        self.log(f"Starting orchestration for business {business_id}")
        self.log(f"Query: {query}")
        
        results = {
            "orchestration_id": f"orch_{business_id}_{int(datetime.utcnow().timestamp())}",
            "business_id": business_id,
            "query": query,
            "agents_executed": [],
            "execution_time": datetime.utcnow().isoformat()
        }
        
        # Step 1: Data Agent - Fetch all data
        self.log("Executing Data Agent...")
        data_result = await self.data_agent.run(context)
        results["agents_executed"].append("data_agent")
        results["data"] = data_result.get("data", {})
        
        if not data_result.get("success"):
            self.log("Data Agent failed, continuing with available data", "warning")
        
        # Step 2: Market Agent - Analyze market
        self.log("Executing Market Agent...")
        market_context = {**context, "data": results["data"]}
        market_result = await self.market_agent.run(market_context)
        results["agents_executed"].append("market_agent")
        results["market_analysis"] = market_result.get("data", {})
        
        # Step 3: Location Agent - Analyze locations
        self.log("Executing Location Agent...")
        location_result = await self.location_agent.run(context)
        results["agents_executed"].append("location_agent")
        results["location_analysis"] = location_result.get("data", {})
        
        # Compile agent statuses
        results["agent_statuses"] = {
            "data_agent": self.data_agent.get_status(),
            "market_agent": self.market_agent.get_status(),
            "location_agent": self.location_agent.get_status()
        }
        
        self.log(f"Orchestration complete. Executed {len(results['agents_executed'])} agents")
        
        return {
            "success": True,
            "data": results,
            "message": f"Orchestration complete for business {business_id}",
            "errors": []
        }
    
    def get_all_agent_statuses(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "orchestrator": self.get_status(),
            "data_agent": self.data_agent.get_status(),
            "market_agent": self.market_agent.get_status(),
            "location_agent": self.location_agent.get_status()
        }

# Global orchestrator instance
orchestrator = OrchestratorAgent()
