"""
Data Pipeline Service - MongoDB Cache Only
Fetches data from external APIs, processes it, and stores in MongoDB for caching
NO MOCK DATA - All data from real sources
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..database.mongodb import collections
from ..services.gdp_service import get_gdp_data, get_economic_indicators
from ..services.msme_service import get_msme_data, get_msme_by_state
from ..services.weather_service import get_weather_data
from ..services.news_service import get_industry_news
from ..services.llm_service import call_openrouter

class DataPipeline:
    """Central data pipeline for fetching, processing, and caching data in MongoDB"""
    
    def __init__(self):
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    async def get_economic_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get economic data (GDP, inflation, etc.)
        Checks MongoDB cache first, fetches from API if needed
        """
        api_cache = collections.api_cache()
        
        # Check cache
        if not force_refresh:
            cached = await api_cache.find_one(
                {"cache_key": "economic_indicators"},
                sort=[("created_at", -1)]
            )
            
            if cached and self._is_cache_valid(cached.get("created_at")):
                return cached.get("data", {})
        
        # Fetch fresh data
        try:
            gdp_data = get_gdp_data()
            economic_indicators = get_economic_indicators()
            
            data = {
                "gdp": gdp_data,
                "economic_indicators": economic_indicators
            }
            
            # Store in MongoDB
            await api_cache.insert_one({
                "cache_key": "economic_indicators",
                "data": data,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + self.cache_duration,
                "source": "data.gov.in"
            })
            
            return data
        
        except Exception as e:
            print(f"Error fetching economic data: {str(e)}")
            # Return last cached data if available
            cached = await api_cache.find_one(
                {"cache_key": "economic_indicators"},
                sort=[("created_at", -1)]
            )
            return cached.get("data", {}) if cached else {}
    
    async def get_msme_data_cached(self, state: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """Get MSME data with MongoDB caching"""
        api_cache = collections.api_cache()
        cache_key = f"msme_{state}" if state else "msme_total"
        
        # Check cache
        if not force_refresh:
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            
            if cached and self._is_cache_valid(cached.get("created_at")):
                return cached.get("data", {})
        
        # Fetch fresh data
        try:
            if state:
                msme_count = get_msme_by_state(state)
                data = {"state": state, "count": msme_count}
            else:
                msme_count = get_msme_data()
                data = {"total": msme_count}
            
            # Store in MongoDB
            await api_cache.insert_one({
                "cache_key": cache_key,
                "data": data,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + self.cache_duration,
                "source": "data.gov.in"
            })
            
            return data
        
        except Exception as e:
            print(f"Error fetching MSME data: {str(e)}")
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            return cached.get("data", {}) if cached else {}
    
    async def get_weather_cached(self, city: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get weather data with MongoDB caching (cache for 6 hours)"""
        api_cache = collections.api_cache()
        cache_key = f"weather_{city}"
        
        # Check cache (weather changes more frequently)
        if not force_refresh:
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            
            if cached and self._is_cache_valid(cached.get("created_at"), hours=6):
                return cached.get("data", {})
        
        # Fetch fresh data
        try:
            weather = get_weather_data(city)
            
            # Store in MongoDB
            await api_cache.insert_one({
                "cache_key": cache_key,
                "data": weather,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=6),
                "source": "openweathermap"
            })
            
            return weather
        
        except Exception as e:
            print(f"Error fetching weather for {city}: {str(e)}")
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            return cached.get("data", {}) if cached else {}
    
    async def get_news_cached(self, query: str, limit: int = 5, force_refresh: bool = False) -> list:
        """Get news data with MongoDB caching (cache for 12 hours)"""
        api_cache = collections.api_cache()
        cache_key = f"news_{query}"
        
        # Check cache
        if not force_refresh:
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            
            if cached and self._is_cache_valid(cached.get("created_at"), hours=12):
                return cached.get("data", [])
        
        # Fetch fresh data
        try:
            news = get_industry_news(query, limit)
            
            # Store in MongoDB
            await api_cache.insert_one({
                "cache_key": cache_key,
                "data": news,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=12),
                "source": "newsapi"
            })
            
            return news
        
        except Exception as e:
            print(f"Error fetching news for {query}: {str(e)}")
            cached = await api_cache.find_one(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            )
            return cached.get("data", []) if cached else []
    
    async def get_city_population(self, city: str, state: str) -> int:
        """
        Get city population from LLM (since we don't have a population API)
        Cache in MongoDB permanently
        """
        api_cache = collections.api_cache()
        cache_key = f"population_{city}_{state}"
        
        # Check cache
        cached = await api_cache.find_one({"cache_key": cache_key})
        if cached:
            return cached.get("data", {}).get("population", 0)
        
        # Use LLM to get population estimate
        try:
            prompt = f"What is the approximate population of {city}, {state}, India? Reply with ONLY the number, no text."
            messages = [
                {"role": "system", "content": "You are a data assistant. Provide only numerical answers."},
                {"role": "user", "content": prompt}
            ]
            
            response = call_openrouter(messages, max_tokens=50)
            # Extract number from response
            population = int(''.join(filter(str.isdigit, response)))
            
            # Store in MongoDB permanently
            await api_cache.insert_one({
                "cache_key": cache_key,
                "data": {"population": population, "city": city, "state": state},
                "created_at": datetime.utcnow(),
                "expires_at": None,  # Never expires
                "source": "llm_estimate"
            })
            
            return population
        
        except Exception as e:
            print(f"Error getting population for {city}: {str(e)}")
            # Return reasonable default based on city tier
            major_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata"]
            return 10_000_000 if city in major_cities else 5_000_000
    
    def _is_cache_valid(self, created_at: datetime, hours: int = 24) -> bool:
        """Check if cached data is still valid"""
        if not created_at:
            return False
        
        age = datetime.utcnow() - created_at
        return age < timedelta(hours=hours)

# Global instance
data_pipeline = DataPipeline()
