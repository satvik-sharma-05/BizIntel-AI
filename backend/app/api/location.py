"""
Location Intelligence API
Provides location analysis and expansion recommendations
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends
from ..api.auth import get_current_user_id
from ..api.business import verify_business_access
from ..agents.location_agent import LocationAgent
from ..agents.data_agent import DataAgent
from ..services.llm_service import call_openrouter
from ..database.mongodb import collections
from ..utils.structured_output import format_location_analysis
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/analyze/{business_id}")
async def analyze_location(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyze location intelligence for business expansion
    
    Returns:
    - Current location analysis
    - Top recommended cities for expansion
    - Detailed scores for each city
    - Pros/cons for each location
    """
    try:
        # Verify business access
        business = await verify_business_access(business_id, user_id)
        
        # Initialize agents
        location_agent = LocationAgent()
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
        
        # Run location analysis
        location_result = await location_agent.run(context)
        
        if not location_result.get("success"):
            raise HTTPException(status_code=500, detail="Location analysis failed")
        
        location_data = location_result.get("data", {})
        
        # Generate AI insights
        ai_insights_raw = await _generate_location_insights(business, location_data, data_result.get("data", {}))
        
        # Format to structured output
        structured_analysis = format_location_analysis(ai_insights_raw, {
            "city": business.get("city"),
            "state": business.get("state")
        })
        
        # Store in MongoDB
        await collections.location_analysis().insert_one({
            "business_id": business_id,
            "user_id": user_id,
            "current_location": location_data.get("current_location", {}),
            "recommendations": location_data.get("recommendations", []),
            "structured_analysis": structured_analysis,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": business.get("name"),
            "industry": business.get("industry"),
            "current_location": location_data.get("current_location", {}),
            "recommendations": location_data.get("recommendations", []),
            "structured_analysis": structured_analysis,
            "total_analyzed": location_data.get("total_analyzed", 0),
            "data_sources": {
                "gdp": data_result.get("data", {}).get("gdp", {}),
                "msme": data_result.get("data", {}).get("msme", {}),
                "economic_indicators": data_result.get("data", {}).get("economic_indicators", {})
            },
            "message": "Location analysis complete"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Location Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Location analysis error: {str(e)}")


async def _generate_location_insights(business: dict, location_data: dict, raw_data: dict) -> str:
    """Generate AI insights for location analysis - returns clean text without markdown"""
    try:
        current_loc = location_data.get("current_location", {})
        recommendations = location_data.get("recommendations", [])
        
        rec_text = "\n".join([f"- {rec.get('city')}: Score {rec.get('score')}/100" for rec in recommendations[:5]])
        
        prompt = f"""Analyze this location data and provide expansion recommendations in a structured format.

Business: {business.get('name')}
Industry: {business.get('industry')}
Current Location: {business.get('city')}, {business.get('state')}
Investment: ₹{business.get('investment', 0):,.0f}

Current Location Analysis:
- Score: {current_loc.get('score', 'N/A')}/100
- Population: {current_loc.get('population', 'N/A')}
- GDP Growth: {current_loc.get('gdp_growth', 'N/A')}%
- MSME Count: {current_loc.get('msme_count', 'N/A')}

Top Expansion Recommendations:
{rec_text}

Economic Data:
- GDP Growth: {raw_data.get('gdp', {}).get('growth', 'N/A')}%
- MSME Count: {raw_data.get('msme', {}).get('state', 'N/A')}

Provide analysis in this exact structure (NO markdown formatting like *** or **):

Summary: [Brief 2-3 sentence overview of location opportunities]

Key Insights:
- [Insight 1]
- [Insight 2]
- [Insight 3]

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

Be specific and actionable. Do NOT use markdown formatting."""

        messages = [
            {"role": "system", "content": "You are a location strategy expert. Provide clean, structured analysis without markdown formatting."},
            {"role": "user", "content": prompt}
        ]
        
        insights_text = call_openrouter(messages, max_tokens=1200)
        
        return insights_text
    
    except Exception as e:
        return f"Unable to generate location insights: {str(e)}"
