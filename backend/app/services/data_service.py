import requests
from typing import Dict, Any, Optional
from ..config.settings import settings
import json

class DataService:
    def __init__(self):
        self.base_url = settings.DATA_GOV_BASE_URL
        self.api_key = settings.DATA_GOV_API_KEY
    
    def _fetch_data(self, resource_id: str, filters: Optional[Dict] = None, limit: int = 100):
        """Fetch data from data.gov.in API"""
        params = {
            "api-key": self.api_key,
            "format": "json",
            "limit": limit
        }
        
        if filters:
            params["filters"] = json.dumps(filters)
        
        url = f"{self.base_url}/{resource_id}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_gdp_data(self, filters: Optional[Dict] = None):
        """Fetch GDP data"""
        return self._fetch_data(settings.GDP_RESOURCE_ID, filters)
    
    def get_msme_data(self, filters: Optional[Dict] = None):
        """Fetch MSME data"""
        return self._fetch_data(settings.MSME_RESOURCE_ID, filters)
    
    def get_fuel_prices(self, filters: Optional[Dict] = None):
        """Fetch fuel price data"""
        return self._fetch_data(settings.FUEL_PRICE_RESOURCE_ID, filters)
    
    def get_commodity_prices(self, filters: Optional[Dict] = None):
        """Fetch commodity price data"""
        return self._fetch_data(settings.COMMODITY_PRICE_RESOURCE_ID, filters)
    
    def get_unemployment_data(self, filters: Optional[Dict] = None):
        """Fetch unemployment data"""
        return self._fetch_data(settings.UNEMPLOYMENT_RESOURCE_ID, filters)
    
    def get_weather_data(self, city: str):
        """Fetch weather data from OpenWeather"""
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": "Weather data not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_news(self, query: str = "business india", page_size: int = 10):
        """Fetch news from NewsAPI"""
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": settings.NEWS_API_KEY,
            "pageSize": page_size,
            "language": "en"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": "News data not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_nearby_businesses(self, lat: float, lon: float, radius: int = 1000, business_type: str = "shop"):
        """Fetch nearby businesses using Overpass API"""
        query = f"""
        [out:json];
        (
          node["shop"](around:{radius},{lat},{lon});
          way["shop"](around:{radius},{lat},{lon});
        );
        out body;
        """
        
        try:
            response = requests.post(settings.PLACES_API, data={"data": query}, timeout=30)
            if response.status_code == 200:
                return response.json()
            return {"error": "Places data not available"}
        except Exception as e:
            return {"error": str(e)}

data_service = DataService()
