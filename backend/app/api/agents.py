"""
Agents API - Information about all AI agents
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from ..auth.auth_service import get_current_user
from ..database.mongodb import collections
from datetime import datetime

router = APIRouter(tags=["Agents"])

# Agent definitions
AGENTS_INFO = [
    {
        "id": "orchestrator",
        "name": "Orchestrator Agent",
        "role": "Coordinates all agents and manages workflow",
        "description": "The orchestrator agent is the central coordinator that manages the execution of all other agents. It determines which agents to run based on the user query and business context.",
        "data_sources": ["Agent responses", "Business context"],
        "databases": ["MongoDB (agent logs)"],
        "capabilities": [
            "Agent coordination",
            "Workflow management",
            "Task distribution",
            "Result aggregation"
        ],
        "icon": "🎯"
    },
    {
        "id": "data_agent",
        "name": "Data Agent",
        "role": "Fetches real-time data from external APIs",
        "description": "Collects real-time data from government APIs, weather services, news sources, and economic indicators to provide up-to-date market intelligence.",
        "data_sources": [
            "Government APIs (GDP, MSME)",
            "Weather API",
            "News API",
            "Economic indicators"
        ],
        "databases": ["MongoDB (API cache)"],
        "capabilities": [
            "GDP data retrieval",
            "MSME statistics",
            "Weather data",
            "News aggregation",
            "Economic indicators"
        ],
        "icon": "📊"
    },
    {
        "id": "market_agent",
        "name": "Market Agent",
        "role": "Analyzes market conditions and opportunities",
        "description": "Performs comprehensive market analysis including demand assessment, competition analysis, market saturation, and profit potential evaluation.",
        "data_sources": [
            "Data Agent output",
            "Competition Service",
            "OpenStreetMap/Overpass API"
        ],
        "databases": ["MongoDB (market analysis)", "Neo4j (market relationships)"],
        "capabilities": [
            "Market demand analysis",
            "Competition assessment",
            "Market saturation calculation",
            "Profit potential scoring",
            "Entry difficulty evaluation",
            "Structured markdown reports"
        ],
        "icon": "📈"
    },
    {
        "id": "location_agent",
        "name": "Location Agent",
        "role": "Provides location intelligence and expansion recommendations",
        "description": "Analyzes multiple cities for expansion opportunities, comparing demand, competition, costs, and profit potential across locations.",
        "data_sources": [
            "Data Agent output",
            "Government MSME data",
            "GDP statistics"
        ],
        "databases": ["MongoDB (location analysis)", "Neo4j (city relationships)"],
        "capabilities": [
            "Multi-city comparison",
            "Expansion recommendations",
            "City scoring (demand, competition, cost)",
            "Pros/cons analysis",
            "Risk assessment",
            "Structured markdown reports"
        ],
        "icon": "📍"
    },
    {
        "id": "graph_agent",
        "name": "Graph Agent",
        "role": "Manages Neo4j graph relationships",
        "description": "Creates and queries graph relationships between businesses, markets, competitors, and locations using Neo4j.",
        "data_sources": ["Business data", "Market data", "Competition data"],
        "databases": ["Neo4j (graph database)"],
        "capabilities": [
            "Business node creation",
            "Relationship mapping",
            "Competitor networks",
            "Market connections",
            "Graph queries"
        ],
        "icon": "🕸️"
    },
    {
        "id": "decision_agent",
        "name": "Decision Agent",
        "role": "Provides strategic recommendations and decisions",
        "description": "Synthesizes insights from all agents to provide strategic recommendations, risk assessments, and actionable next steps.",
        "data_sources": [
            "Market Agent output",
            "Location Agent output",
            "Data Agent output"
        ],
        "databases": ["MongoDB (decisions)"],
        "capabilities": [
            "Strategic recommendations",
            "Risk assessment",
            "Opportunity identification",
            "Action plan generation",
            "Confidence scoring"
        ],
        "icon": "🎲"
    },
    {
        "id": "rag_agent",
        "name": "RAG Agent",
        "role": "Document retrieval and question answering",
        "description": "Retrieves relevant information from uploaded documents using vector search and generates answers with citations.",
        "data_sources": ["Uploaded documents (PDF, DOCX, TXT)"],
        "databases": ["FAISS (vector embeddings)", "MongoDB (document metadata)"],
        "capabilities": [
            "Document embedding",
            "Vector similarity search",
            "Context retrieval",
            "Citation generation",
            "Hybrid Q&A (documents + AI)"
        ],
        "icon": "📄"
    },
    {
        "id": "forecast_agent",
        "name": "Forecast Agent",
        "role": "Revenue and growth forecasting",
        "description": "Generates financial forecasts including revenue projections, growth estimates, and breakeven analysis.",
        "data_sources": [
            "Business data",
            "Market analysis",
            "Economic indicators"
        ],
        "databases": ["MongoDB (forecasts)"],
        "capabilities": [
            "Revenue forecasting",
            "Growth projections",
            "Breakeven analysis",
            "Scenario modeling",
            "Financial metrics"
        ],
        "icon": "💰"
    },
    {
        "id": "competition_service",
        "name": "Competition Service",
        "role": "Real competitor data collection",
        "description": "Collects real competitor data from OpenStreetMap using Overpass API to provide accurate competition analysis.",
        "data_sources": ["OpenStreetMap", "Overpass API"],
        "databases": ["MongoDB (competition cache)"],
        "capabilities": [
            "Competitor location mapping",
            "Competitor density calculation",
            "Industry-specific search",
            "Real-time data collection",
            "Fallback estimates"
        ],
        "icon": "🏢"
    }
]

@router.get("/")
async def get_all_agents() -> Dict[str, Any]:
    """Get information about all agents"""
    return {
        "agents": AGENTS_INFO,
        "total_agents": len(AGENTS_INFO),
        "message": "All agents information retrieved"
    }

@router.get("/{agent_id}")
async def get_agent_info(agent_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific agent"""
    agent = next((a for a in AGENTS_INFO if a["id"] == agent_id), None)
    
    if not agent:
        return {"error": "Agent not found"}
    
    return agent

@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: str,
    limit: int = 50
) -> Dict[str, Any]:
    """Get recent logs for a specific agent"""
    logs = await collections.agent_logs().find(
        {"agent_id": agent_id}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Convert ObjectId to string
    for log in logs:
        log["_id"] = str(log["_id"])
        if "business_id" in log:
            log["business_id"] = str(log["business_id"])
    
    return {
        "agent_id": agent_id,
        "logs": logs,
        "count": len(logs)
    }

@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: str
) -> Dict[str, Any]:
    """Get statistics for a specific agent"""
    
    # Get total executions
    total_executions = await collections.agent_logs().count_documents(
        {"agent_id": agent_id}
    )
    
    # Get recent executions (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_executions = await collections.agent_logs().count_documents({
        "agent_id": agent_id,
        "created_at": {"$gte": yesterday}
    })
    
    # Get last execution time
    last_log = await collections.agent_logs().find_one(
        {"agent_id": agent_id},
        sort=[("created_at", -1)]
    )
    
    last_run = last_log["created_at"] if last_log else None
    
    return {
        "agent_id": agent_id,
        "total_executions": total_executions,
        "recent_executions_24h": recent_executions,
        "last_run": last_run,
        "status": "active" if recent_executions > 0 else "idle"
    }
