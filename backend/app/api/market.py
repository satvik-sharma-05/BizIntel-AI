"""
Market Analysis API
Provides comprehensive market intelligence and analysis
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends
from ..api.auth import get_current_user_id
from ..api.business import verify_business_access
from ..agents.market_agent import MarketAgent
from ..agents.data_agent import DataAgent
from ..agents.graph_agent import graph_agent
from ..services.llm_service import call_openrouter
from ..database.mongodb import collections
from ..database.neo4j_client import neo4j_client
from ..utils.structured_output import format_market_analysis, remove_markdown
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/analyze/{business_id}")
async def analyze_market(
    business_id: str,
    user_id: str = Depends(get_current_user_id),
    force_refresh: bool = False
):
    """
    Comprehensive market analysis for a business
    Uses cached data if available (< 24 hours old) unless force_refresh=True
    
    Returns:
    - Market demand score
    - Competition analysis
    - Growth trends
    - Market opportunities
    - AI-generated strategic recommendations
    """
    try:
        # Verify business access
        business = await verify_business_access(business_id, user_id)
        
        # Check for cached analysis (< 24 hours old)
        if not force_refresh:
            cached = await collections.market_analysis().find_one(
                {"business_id": business_id},
                sort=[("created_at", -1)]
            )
            
            if cached:
                # Check if less than 24 hours old
                age_hours = (datetime.utcnow() - cached["created_at"]).total_seconds() / 3600
                if age_hours < 24:
                    print(f"✅ Using cached market analysis ({age_hours:.1f} hours old)")
                    return {
                        "success": True,
                        "business_id": business_id,
                        "business_name": business.get("name"),
                        "industry": business.get("industry"),
                        "location": f"{business.get('city')}, {business.get('state')}",
                        "market_analysis": cached.get("market_analysis", {}),
                        "structured_analysis": cached.get("structured_analysis", {}),
                        "graph_insights": cached.get("graph_insights", {}),
                        "data_sources": cached.get("data_sources", {}),
                        "cached": True,
                        "cache_age_hours": round(age_hours, 1),
                        "message": "Market analysis (cached)"
                    }
        
        print(f"🔄 Generating fresh market analysis for {business.get('name')}")
        
        # Initialize agents
        market_agent = MarketAgent()
        data_agent = DataAgent()
        
        # Build context
        context = {
            "business_id": business_id,
            "business_name": business.get("name"),
            "industry": business.get("industry"),
            "city": business.get("city"),
            "state": business.get("state"),
            "investment": business.get("investment")
        }
        
        # Fetch data first
        data_result = await data_agent.run(context)
        
        # Add data to context
        context["data"] = data_result.get("data", {})
        
        # Run market analysis
        market_result = await market_agent.run(context)
        
        if not market_result.get("success"):
            raise HTTPException(status_code=500, detail="Market analysis failed")
        
        market_data = market_result.get("data", {})
        
        # Run graph agent to get relationship insights
        graph_result = await graph_agent.run(context)
        graph_data = graph_result.get("data", {})
        
        # Generate AI insights with structured output
        ai_insights_raw = await _generate_market_insights(
            business, 
            market_data, 
            data_result.get("data", {}),
            graph_data
        )
        
        # Format to structured output
        structured_analysis = format_market_analysis(ai_insights_raw, {
            "industry": business.get("industry"),
            "city": business.get("city"),
            "state": business.get("state")
        })
        
        # Store business graph in Neo4j
        if neo4j_client.connected and structured_analysis:
            try:
                neo4j_client.create_full_business_graph(
                    business_data={
                        "business_id": business_id,
                        "name": business.get("name"),
                        "industry": business.get("industry"),
                        "city": business.get("city"),
                        "state": business.get("state"),
                        "investment": business.get("investment", 0)
                    },
                    market_data={
                        "industry": business.get("industry"),
                        "city": business.get("city"),
                        "demand_score": market_data.get("demand_score", 0),
                        "competition": market_data.get("competition", "Unknown"),
                        "opportunity": market_data.get("opportunity", "Unknown")
                    },
                    risks=structured_analysis.get("risks", []),
                    opportunities=structured_analysis.get("opportunities", [])
                )
            except Exception as e:
                print(f"Neo4j graph creation error: {e}")
        
        # Store in MongoDB
        analysis_doc = {
            "business_id": business_id,
            "user_id": user_id,
            "market_analysis": market_data,
            "structured_analysis": structured_analysis,
            "graph_insights": graph_data,
            "data_sources": data_result.get("data", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await collections.market_analysis().insert_one(analysis_doc)
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": business.get("name"),
            "industry": business.get("industry"),
            "location": f"{business.get('city')}, {business.get('state')}",
            "market_analysis": market_data,
            "structured_analysis": structured_analysis,
            "graph_insights": graph_data,
            "data_sources": data_result.get("data", {}),
            "cached": False,
            "message": "Market analysis complete"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Market Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market analysis error: {str(e)}")

async def _generate_market_insights(business: dict, market_data: dict, raw_data: dict, graph_data: dict) -> str:
    """Generate AI insights for market analysis - returns clean text without markdown"""
    try:
        # Extract graph insights
        competition_analysis = graph_data.get("competition_analysis", {})
        similar_businesses_count = len(graph_data.get("similar_businesses", []))
        market_insights = graph_data.get("market_insights", {})
        common_risks = [r.get("risk") for r in market_insights.get("common_risks", [])][:3]
        common_opportunities = [o.get("opportunity") for o in market_insights.get("common_opportunities", [])][:3]
        
        prompt = f"""Analyze this market data and provide strategic recommendations in a structured format.

Business: {business.get('name')}
Industry: {business.get('industry')}
Location: {business.get('city')}, {business.get('state')}
Investment: ₹{business.get('investment', 0):,.0f}

Market Analysis:
- Demand Score: {market_data.get('demand_score', 'N/A')}/100
- Market Opportunity: {market_data.get('opportunity', 'N/A')}
- Competition Level: {market_data.get('competition', 'N/A')}
- Growth Trend: {market_data.get('growth_trend', 'N/A')}
- Market Size: {market_data.get('market_size', 'N/A')}
- Entry Barrier: {market_data.get('entry_barrier', 'N/A')}

Economic Data:
- GDP Growth: {raw_data.get('gdp', {}).get('growth', 'N/A')}%
- MSME Count: {raw_data.get('msme', {}).get('state', 'N/A')}
- Inflation: {raw_data.get('economic_indicators', {}).get('inflation', 'N/A')}%

Graph Intelligence (Neo4j):
- Similar Businesses in Market: {similar_businesses_count}
- Competition Level: {competition_analysis.get('competition_level', 'Unknown')}
- Market Saturation: {competition_analysis.get('market_saturation', 'Unknown')}
- Common Industry Risks: {', '.join(common_risks) if common_risks else 'None identified'}
- Common Opportunities: {', '.join(common_opportunities) if common_opportunities else 'None identified'}

Provide analysis in this exact structure (NO markdown formatting like *** or **):

Summary: [Brief 2-3 sentence overview]

Key Insights:
- [Insight 1]
- [Insight 2]
- [Insight 3]

Data Analysis:
- [Data point 1]
- [Data point 2]
- [Data point 3]

Risks:
- [Risk 1]
- [Risk 2]
- [Risk 3]

Opportunities:
- [Opportunity 1]
- [Opportunity 2]
- [Opportunity 3]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

Action Plan:
1. [Action 1]
2. [Action 2]
3. [Action 3]

Conclusion: [Final summary]

Be specific, actionable, and use Indian market context. Do NOT use markdown formatting."""

        messages = [
            {"role": "system", "content": "You are a market strategy expert. Provide clean, structured analysis without markdown formatting."},
            {"role": "user", "content": prompt}
        ]
        
        insights_text = call_openrouter(messages, max_tokens=1500)
        
        return insights_text
    
    except Exception as e:
        return f"Unable to generate AI insights: {str(e)}"
