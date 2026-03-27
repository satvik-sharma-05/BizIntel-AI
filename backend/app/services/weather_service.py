import os
import requests
from typing import Dict, Any

def get_weather_data(city: str) -> Dict[str, Any]:
    """Fetch real weather data from OpenWeather API"""
    try:
        api_key = os.getenv('OPENWEATHER_API_KEY', '')
        
        if not api_key:
            return get_fallback_weather(city)
        
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},IN",
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "city": data.get("name"),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0) / 1000,  # km
                "source": "OpenWeather API"
            }
        else:
            return get_fallback_weather(city)
            
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return get_fallback_weather(city)

def get_fallback_weather(city: str) -> Dict[str, Any]:
    """Fallback weather data"""
    # Typical weather for major Indian cities
    weather_data = {
        "Mumbai": {"temp": 28, "humidity": 75, "description": "partly cloudy"},
        "Delhi": {"temp": 25, "humidity": 60, "description": "clear sky"},
        "Bangalore": {"temp": 24, "humidity": 65, "description": "pleasant"},
        "Kolkata": {"temp": 30, "humidity": 80, "description": "humid"},
        "Chennai": {"temp": 32, "humidity": 70, "description": "hot"},
        "Hyderabad": {"temp": 29, "humidity": 55, "description": "warm"},
        "Pune": {"temp": 26, "humidity": 60, "description": "pleasant"},
        "Ahmedabad": {"temp": 31, "humidity": 50, "description": "hot and dry"}
    }
    
    city_weather = weather_data.get(city, {"temp": 27, "humidity": 65, "description": "moderate"})
    
    return {
        "success": True,
        "city": city,
        "temperature": city_weather["temp"],
        "feels_like": city_weather["temp"] + 2,
        "humidity": city_weather["humidity"],
        "pressure": 1013,
        "description": city_weather["description"],
        "wind_speed": 3.5,
        "visibility": 10,
        "source": "Fallback Data"
    }
