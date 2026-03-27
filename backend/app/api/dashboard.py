"""
Dashboard API - MongoDB Only
Multi-tenant SaaS with business access verification
"""
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from ..services.data_pipeline import data_pipeline
from ..database.mongodb import collections
from ..api.auth import get_current_user_id
from ..api.business import verify_business_access

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    business_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get business-specific dashboard data with REAL data from APIs/MongoDB cache"""
    try:
        # Verify business access
        business = await verify_business_access(business_id, user_id)
        
        print(f"Fetching dashboard data for business: {business['business_name']}")
        
        # Fetch REAL data from data pipeline (with MongoDB caching)
        economic_data = await data_pipeline.get_economic_data()
        msme_total = await data_pipeline.get_msme_data_cached()
        msme_state = await data_pipeline.get_msme_data_cached(business["state"])
        weather = await data_pipeline.get_weather_cached(business["city"])
        news = await data_pipeline.get_news_cached(business["industry"], 5)
        
        # Build business-specific dashboard with REAL data
        data = {
            "business": {
                "id": str(business["_id"]),
                "name": business["business_name"],
                "industry": business["industry"],
                "city": business["city"],
                "state": business["state"],
                "investment": business["initial_investment"],
                "description": business.get("description", "")
            },
            "location": {
                "city": business["city"],
                "state": business["state"],
                "weather": weather,
                "msme_count": msme_state.get("count", 0)
            },
            "market": {
                "gdp": economic_data.get("gdp", {}),
                "msme": {"count": msme_total.get("total", 0)},
                "economic_indicators": economic_data.get("economic_indicators", {}),
                "industry": business["industry"]
            },
            "news": news,
            "timestamp": "2024-03-26T10:00:00Z"
        }
        
        return data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.get("/data/gdp")
async def get_gdp():
    """Get GDP data from cache/API"""
    try:
        economic_data = await data_pipeline.get_economic_data()
        return economic_data.get("gdp", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/msme")
async def get_msme():
    """Get MSME data from cache/API"""
    try:
        msme_data = await data_pipeline.get_msme_data_cached()
        return msme_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/economic-indicators")
async def get_indicators():
    """Get economic indicators from cache/API"""
    try:
        economic_data = await data_pipeline.get_economic_data()
        return economic_data.get("economic_indicators", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/weather/{city}")
async def get_weather(city: str):
    """Get weather data for city from cache/API"""
    try:
        return await data_pipeline.get_weather_cached(city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/news")
async def get_news(query: str = "business india", limit: int = 10):
    """Get news from cache/API"""
    try:
        return await data_pipeline.get_news_cached(query, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/industry-news/{industry}")
async def get_industry_specific_news(industry: str, limit: int = 5):
    """Get industry-specific news from cache/API"""
    try:
        return await data_pipeline.get_news_cached(industry, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
