"""
Data Agent
Fetches data from various APIs and databases using data pipeline
NO MOCK DATA - All data from real sources with caching
"""
from .base_agent import BaseAgent
from typing import Dict, Any
from ..services.data_pipeline import data_pipeline

class DataAgent(BaseAgent):
    """Agent responsible for fetching data from external sources"""
    
    def __init__(self):
        super().__init__(
            agent_id="data_agent",
            name="Data Agent",
            description="Fetches real data from APIs and databases with caching"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch all relevant data for the business"""
        
        business_id = context.get("business_id")
        industry = context.get("industry")
        city = context.get("city")
        state = context.get("state")
        
        self.log(f"Fetching data for business {business_id} in {city}, {state}")
        
        data = {}
        errors = []
        
        # Fetch economic data (GDP, inflation) from cache/API
        try:
            self.log("Fetching economic data from data pipeline...")
            economic_data = await data_pipeline.get_economic_data()
            data["gdp"] = economic_data.get("gdp", {})
            data["economic_indicators"] = economic_data.get("economic_indicators", {})
            self.log("Economic data fetched successfully")
        except Exception as e:
            self.add_error(f"Economic data fetch failed: {str(e)}")
            errors.append(f"Economic: {str(e)}")
            data["gdp"] = {"growth": 0, "error": str(e)}
            data["economic_indicators"] = {"inflation": 0, "error": str(e)}
        
        # Fetch MSME data from cache/API
        try:
            self.log("Fetching MSME data from data pipeline...")
            msme_total = await data_pipeline.get_msme_data_cached()
            msme_state = await data_pipeline.get_msme_data_cached(state)
            data["msme"] = {
                "total": msme_total.get("total", 0),
                "state": msme_state.get("count", 0)
            }
            self.log(f"MSME data fetched: {msme_state.get('count', 0)} MSMEs in {state}")
        except Exception as e:
            self.add_error(f"MSME fetch failed: {str(e)}")
            errors.append(f"MSME: {str(e)}")
            data["msme"] = {"total": 0, "state": 0, "error": str(e)}
        
        # Fetch weather data from cache/API
        try:
            self.log(f"Fetching weather for {city} from data pipeline...")
            weather = await data_pipeline.get_weather_cached(city)
            data["weather"] = weather
            self.log(f"Weather fetched: {weather.get('temp', 'N/A')}°C")
        except Exception as e:
            self.add_error(f"Weather fetch failed: {str(e)}")
            errors.append(f"Weather: {str(e)}")
            data["weather"] = {"temp": 0, "description": "Data unavailable", "error": str(e)}
        
        # Fetch industry news from cache/API
        try:
            self.log(f"Fetching news for {industry} from data pipeline...")
            news = await data_pipeline.get_news_cached(industry, 5)
            data["news"] = news
            self.log(f"News fetched: {len(news) if isinstance(news, list) else 0} articles")
        except Exception as e:
            self.add_error(f"News fetch failed: {str(e)}")
            errors.append(f"News: {str(e)}")
            data["news"] = []
        
        return {
            "success": len(errors) < 5,  # Success if less than 5 errors
            "data": data,
            "message": f"Data fetched with {len(errors)} errors" if errors else "All data fetched successfully from cache/APIs",
            "errors": errors
        }
