from fastapi import APIRouter, HTTPException
from ..config.settings import settings
from ..database.mongodb import get_mongodb
from ..database.neo4j_client import neo4j_client
from ..rag.vector_store import vector_store
import requests
from datetime import datetime

router = APIRouter()

@router.get("/system/check-apis")
async def check_all_apis():
    """Check status of all external APIs and databases"""
    
    status = {}
    
    # Check MongoDB
    try:
        mongo_db = get_mongodb()
        await mongo_db.command("ping")
        status["mongodb"] = "OK"
    except Exception as e:
        status["mongodb"] = f"Error: {str(e)}"
    
    # Check Neo4j
    try:
        if neo4j_client.connected:
            status["neo4j"] = "OK"
        else:
            status["neo4j"] = "Not Connected"
    except Exception as e:
        status["neo4j"] = f"Error: {str(e)}"
    
    # Check FAISS
    try:
        if vector_store.index is not None:
            status["faiss"] = "OK"
        else:
            status["faiss"] = "Not Initialized"
    except Exception as e:
        status["faiss"] = f"Error: {str(e)}"
    
    # Check OpenRouter
    try:
        url = f"{settings.OPENROUTER_BASE_URL}/models"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
        }
        response = requests.get(url, headers=headers, timeout=5)
        status["openrouter"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["openrouter"] = f"Error: {str(e)}"
    
    # Check Data.gov.in API
    try:
        url = f"{settings.DATA_GOV_BASE_URL}/{settings.GDP_RESOURCE_ID}"
        params = {
            "api-key": settings.DATA_GOV_API_KEY,
            "format": "json",
            "limit": 1
        }
        response = requests.get(url, params=params, timeout=5)
        status["data_gov"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["data_gov"] = f"Error: {str(e)}"
    
    # Check Weather API
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": "Mumbai",
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=5)
        status["weather_api"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["weather_api"] = f"Error: {str(e)}"
    
    # Check News API
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "business",
            "apiKey": settings.NEWS_API_KEY,
            "pageSize": 1
        }
        response = requests.get(url, params=params, timeout=5)
        status["news_api"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["news_api"] = f"Error: {str(e)}"
    
    # Check Overpass API (OpenStreetMap)
    try:
        url = "https://overpass-api.de/api/status"
        response = requests.get(url, timeout=5)
        status["overpass"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["overpass"] = f"Error: {str(e)}"
    
    # Check OSRM API
    try:
        url = "http://router.project-osrm.org/route/v1/driving/77.5946,12.9716;77.6412,13.0827"
        response = requests.get(url, timeout=5)
        status["osrm"] = "OK" if response.status_code == 200 else f"Error: {response.status_code}"
    except Exception as e:
        status["osrm"] = f"Error: {str(e)}"
    
    # Calculate overall status
    all_ok = all(v == "OK" for v in status.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "services": status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }
