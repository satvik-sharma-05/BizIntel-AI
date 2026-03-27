"""
Competition Service - Real Competitor Data
Uses Overpass API to find real competitors nearby
"""
import httpx
from typing import Dict, Any, List, Optional
import asyncio

class CompetitionService:
    """Service to analyze competition using real data"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.timeout = 30.0
    
    async def get_competitors_nearby(
        self,
        city: str,
        state: str,
        industry: str,
        radius_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Get real competitors from OpenStreetMap using Overpass API
        
        Args:
            city: City name
            state: State name
            industry: Business industry/category
            radius_km: Search radius in kilometers
        
        Returns:
            Dict with competitor data
        """
        try:
            # Map industry to OSM tags
            osm_tags = self._map_industry_to_osm_tags(industry)
            
            # Get city coordinates (approximate)
            coords = self._get_city_coordinates(city, state)
            
            if not coords:
                return self._get_fallback_data(city, state, industry)
            
            # Build Overpass query
            query = self._build_overpass_query(
                lat=coords["lat"],
                lon=coords["lon"],
                radius_m=radius_km * 1000,
                tags=osm_tags
            )
            
            # Execute query
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.overpass_url,
                    data={"data": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    competitors = self._parse_overpass_response(data)
                    
                    return {
                        "success": True,
                        "competitors": competitors,
                        "count": len(competitors),
                        "density": self._calculate_density(len(competitors), radius_km),
                        "source": "OpenStreetMap/Overpass API",
                        "radius_km": radius_km,
                        "city": city,
                        "state": state
                    }
                else:
                    return self._get_fallback_data(city, state, industry)
        
        except Exception as e:
            print(f"Competition service error: {str(e)}")
            return self._get_fallback_data(city, state, industry)
    
    def _map_industry_to_osm_tags(self, industry: str) -> List[str]:
        """Map business industry to OpenStreetMap tags"""
        industry_lower = industry.lower()
        
        # Common industry mappings
        mappings = {
            "restaurant": ["amenity=restaurant", "amenity=fast_food", "amenity=cafe"],
            "cafe": ["amenity=cafe", "amenity=restaurant"],
            "retail": ["shop=*"],
            "grocery": ["shop=supermarket", "shop=convenience", "shop=grocery"],
            "pharmacy": ["amenity=pharmacy"],
            "hotel": ["tourism=hotel", "tourism=guest_house"],
            "gym": ["leisure=fitness_centre", "leisure=sports_centre"],
            "salon": ["shop=hairdresser", "shop=beauty"],
            "bakery": ["shop=bakery"],
            "clothing": ["shop=clothes", "shop=fashion"],
            "electronics": ["shop=electronics"],
            "bookstore": ["shop=books"],
            "medical": ["amenity=clinic", "amenity=hospital", "amenity=doctors"],
            "education": ["amenity=school", "amenity=college", "amenity=university"],
        }
        
        # Find matching tags
        for key, tags in mappings.items():
            if key in industry_lower:
                return tags
        
        # Default: search for shops
        return ["shop=*"]
    
    def _get_city_coordinates(self, city: str, state: str) -> Optional[Dict[str, float]]:
        """Get approximate coordinates for major Indian cities"""
        # Major Indian cities coordinates
        coordinates = {
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "delhi": {"lat": 28.7041, "lon": 77.1025},
            "bangalore": {"lat": 12.9716, "lon": 77.5946},
            "bengaluru": {"lat": 12.9716, "lon": 77.5946},
            "hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "chennai": {"lat": 13.0827, "lon": 80.2707},
            "kolkata": {"lat": 22.5726, "lon": 88.3639},
            "pune": {"lat": 18.5204, "lon": 73.8567},
            "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
            "jaipur": {"lat": 26.9124, "lon": 75.7873},
            "surat": {"lat": 21.1702, "lon": 72.8311},
            "lucknow": {"lat": 26.8467, "lon": 80.9462},
            "kanpur": {"lat": 26.4499, "lon": 80.3319},
            "nagpur": {"lat": 21.1458, "lon": 79.0882},
            "indore": {"lat": 22.7196, "lon": 75.8577},
            "thane": {"lat": 19.2183, "lon": 72.9781},
            "bhopal": {"lat": 23.2599, "lon": 77.4126},
            "visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
            "pimpri-chinchwad": {"lat": 18.6298, "lon": 73.7997},
            "patna": {"lat": 25.5941, "lon": 85.1376},
        }
        
        city_lower = city.lower()
        return coordinates.get(city_lower)
    
    def _build_overpass_query(
        self,
        lat: float,
        lon: float,
        radius_m: float,
        tags: List[str]
    ) -> str:
        """Build Overpass API query"""
        # Build tag filters
        tag_filters = " ".join([f'["{tag.split("=")[0]}"="{tag.split("=")[1]}"]' if "=" in tag else f'["{tag}"]' for tag in tags])
        
        query = f"""
        [out:json][timeout:25];
        (
          node{tag_filters}(around:{radius_m},{lat},{lon});
          way{tag_filters}(around:{radius_m},{lat},{lon});
        );
        out center;
        """
        
        return query
    
    def _parse_overpass_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Overpass API response"""
        competitors = []
        
        elements = data.get("elements", [])
        
        for element in elements:
            tags = element.get("tags", {})
            
            # Extract competitor info
            competitor = {
                "name": tags.get("name", "Unknown"),
                "type": tags.get("amenity") or tags.get("shop") or tags.get("tourism", "business"),
                "lat": element.get("lat") or element.get("center", {}).get("lat"),
                "lon": element.get("lon") or element.get("center", {}).get("lon"),
                "address": tags.get("addr:street", ""),
                "phone": tags.get("phone", ""),
                "website": tags.get("website", ""),
                "opening_hours": tags.get("opening_hours", ""),
            }
            
            competitors.append(competitor)
        
        return competitors
    
    def _calculate_density(self, count: int, radius_km: float) -> str:
        """Calculate competitor density"""
        area = 3.14159 * (radius_km ** 2)  # Area in sq km
        density_per_sqkm = count / area if area > 0 else 0
        
        if density_per_sqkm > 10:
            return "Very High"
        elif density_per_sqkm > 5:
            return "High"
        elif density_per_sqkm > 2:
            return "Medium"
        elif density_per_sqkm > 0.5:
            return "Low"
        else:
            return "Very Low"
    
    def _get_fallback_data(self, city: str, state: str, industry: str) -> Dict[str, Any]:
        """Fallback data when API fails"""
        # Estimate based on city tier
        tier1_cities = ["mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata"]
        tier2_cities = ["pune", "ahmedabad", "jaipur", "surat", "lucknow", "kanpur", "nagpur", "indore"]
        
        city_lower = city.lower()
        
        if city_lower in tier1_cities:
            count = 45
            density = "High"
        elif city_lower in tier2_cities:
            count = 28
            density = "Medium"
        else:
            count = 15
            density = "Low"
        
        return {
            "success": True,
            "competitors": [],
            "count": count,
            "density": density,
            "source": "Estimated (API unavailable)",
            "radius_km": 5.0,
            "city": city,
            "state": state,
            "note": "Using estimated data. Real competitor data requires Overpass API access."
        }

# Global instance
competition_service = CompetitionService()
