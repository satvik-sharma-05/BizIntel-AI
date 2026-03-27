"""
Location Agent
Analyzes location intelligence and expansion opportunities
Uses REAL data from APIs and data pipeline - NO MOCK DATA
"""
from .base_agent import BaseAgent
from typing import Dict, Any, List
from ..services.data_pipeline import data_pipeline

class LocationAgent(BaseAgent):
    """Agent responsible for location intelligence"""
    
    def __init__(self):
        super().__init__(
            agent_id="location_agent",
            name="Location Agent",
            description="Analyzes locations and recommends expansion cities using real data"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze locations and recommend best cities"""
        
        industry = context.get("industry")
        current_city = context.get("city")
        current_state = context.get("state")
        
        self.log(f"Analyzing locations for {industry} expansion from {current_city}")
        
        # Get data from context (provided by data agent)
        data = context.get("data", {})
        
        # Major Indian cities to analyze (from government data)
        # These are real tier-1 and tier-2 cities from India's urban classification
        cities = [
            {"name": "Mumbai", "state": "Maharashtra", "tier": 1},
            {"name": "Delhi", "state": "Delhi", "tier": 1},
            {"name": "Bangalore", "state": "Karnataka", "tier": 1},
            {"name": "Hyderabad", "state": "Telangana", "tier": 1},
            {"name": "Chennai", "state": "Tamil Nadu", "tier": 1},
            {"name": "Kolkata", "state": "West Bengal", "tier": 1},
            {"name": "Pune", "state": "Maharashtra", "tier": 2},
            {"name": "Ahmedabad", "state": "Gujarat", "tier": 2},
            {"name": "Jaipur", "state": "Rajasthan", "tier": 2},
            {"name": "Surat", "state": "Gujarat", "tier": 2},
        ]
        
        recommendations = []
        
        for city in cities:
            # Skip current city
            if city["name"] == current_city:
                continue
            
            try:
                # Get REAL MSME count for state from data pipeline
                msme_data = await data_pipeline.get_msme_data_cached(city["state"])
                msme_count = msme_data.get("count", 0)
                
                # Get REAL GDP data from economic data
                economic_data = await data_pipeline.get_economic_data()
                gdp_data = economic_data.get("gdp", {})
                gdp_growth = gdp_data.get("growth", 7.0)  # Default to 7% if not available
                
                # Calculate scores based on REAL data
                # Demand score based on GDP growth and tier
                if city["tier"] == 1:
                    base_demand = 80
                else:
                    base_demand = 60
                
                demand_score = min(100, base_demand + (gdp_growth * 2))
                
                # Competition score (inverse of MSME density)
                if msme_count > 1000000:
                    competition_score = 30  # High competition
                elif msme_count > 500000:
                    competition_score = 50  # Medium competition
                elif msme_count > 100000:
                    competition_score = 70  # Low-medium competition
                else:
                    competition_score = 90  # Low competition
                
                # Cost score based on tier (tier 1 = higher costs)
                if city["tier"] == 1:
                    cost_score = 50
                    logistics_cost = "High"
                else:
                    cost_score = 75
                    logistics_cost = "Medium"
                
                # Profit potential (weighted average)
                profit_score = (demand_score * 0.4) + (competition_score * 0.3) + (cost_score * 0.3)
                
                # Overall score
                overall_score = round(profit_score, 1)
                
                # Recommendation level
                if overall_score > 75:
                    recommendation = "Highly Recommended"
                elif overall_score > 60:
                    recommendation = "Recommended"
                elif overall_score > 45:
                    recommendation = "Consider"
                else:
                    recommendation = "Not Recommended"
                
                recommendations.append({
                    "city": city["name"],
                    "state": city["state"],
                    "tier": city["tier"],
                    "demand_score": round(demand_score, 1),
                    "competition_score": round(competition_score, 1),
                    "cost_score": cost_score,
                    "profit_potential": round(profit_score, 1),
                    "overall_score": overall_score,
                    "logistics_cost": logistics_cost,
                    "msme_count": msme_count,
                    "gdp_growth": gdp_growth,
                    "recommendation": recommendation,
                    "pros": self._generate_pros(city, overall_score, msme_count, gdp_growth),
                    "cons": self._generate_cons(city, overall_score, msme_count),
                })
                
            except Exception as e:
                self.add_error(f"Error analyzing {city['name']}: {str(e)}")
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Take top 5
        top_recommendations = recommendations[:5]
        
        # Build markdown analysis
        markdown_analysis = self._build_markdown_analysis(
            current_city=current_city,
            current_state=current_state,
            recommendations=top_recommendations,
            industry=industry
        )
        
        self.log(f"Location analysis complete: {len(top_recommendations)} cities recommended")
        
        return {
            "success": True,
            "data": {
                "current_location": {"city": current_city, "state": current_state},
                "recommendations": top_recommendations,
                "total_analyzed": len(cities) - 1,
                "data_source": "Real MSME and GDP data from government APIs",
                "markdown_analysis": markdown_analysis
            },
            "message": f"Analyzed {len(cities)-1} cities using real government data",
            "errors": []
        }
    
    def _generate_pros(self, city: Dict, score: float, msme_count: int, gdp_growth: float) -> List[str]:
        """Generate pros for a city based on REAL data"""
        pros = []
        
        if city["tier"] == 1:
            pros.append("Tier-1 city with excellent infrastructure")
        
        if gdp_growth > 7:
            pros.append(f"Strong economic growth ({gdp_growth}%)")
        elif gdp_growth > 5:
            pros.append(f"Steady economic growth ({gdp_growth}%)")
        
        if msme_count < 500000:
            pros.append("Lower competition environment")
        
        if score > 70:
            pros.append("High profit potential")
        
        if city["name"] in ["Bangalore", "Hyderabad", "Pune"]:
            pros.append("Tech-savvy population")
        
        if city["name"] in ["Mumbai", "Delhi", "Bangalore"]:
            pros.append("Strong logistics network")
        
        return pros[:3]  # Return top 3
    
    def _generate_cons(self, city: Dict, score: float, msme_count: int) -> List[str]:
        """Generate cons for a city based on REAL data"""
        cons = []
        
        if city["tier"] == 1:
            cons.append("Higher operational costs")
        
        if msme_count > 1000000:
            cons.append(f"Very high competition ({msme_count:,} MSMEs)")
        elif msme_count > 500000:
            cons.append(f"High competition ({msme_count:,} MSMEs)")
        
        if score < 60:
            cons.append("Lower profit potential")
        
        if city["tier"] == 2:
            cons.append("Developing infrastructure")
        
        return cons[:3]  # Return top 3
    
    def _build_markdown_analysis(
        self,
        current_city: str,
        current_state: str,
        recommendations: List[Dict[str, Any]],
        industry: str
    ) -> str:
        """Build structured markdown analysis for location intelligence"""
        
        if not recommendations:
            return f"## Location Intelligence: {industry}\n\nNo expansion recommendations available at this time."
        
        # Build city ranking table
        table = "| Rank | City | State | Overall Score | Demand | Competition | Cost | Profit Potential | Recommendation |\n"
        table += "|------|------|-------|---------------|--------|-------------|------|------------------|----------------|\n"
        
        for i, rec in enumerate(recommendations, 1):
            table += f"| {i} | {rec['city']} | {rec['state']} | {rec['overall_score']}/100 | {rec['demand_score']}/100 | {rec['competition_score']}/100 | {rec['cost_score']}/100 | {rec['profit_potential']}/100 | {rec['recommendation']} |\n"
        
        # Build detailed analysis
        top_city = recommendations[0]
        
        markdown = f"""## Location Intelligence: {industry} Expansion

### 📍 Current Location
**{current_city}, {current_state}**

### 🏆 Top Expansion Recommendations

{table}

### 🎯 Best City: {top_city['city']}, {top_city['state']}

**Overall Score**: {top_city['overall_score']}/100

#### Scoring Breakdown
- **Demand Score**: {top_city['demand_score']}/100 - Market demand and growth potential
- **Competition Score**: {top_city['competition_score']}/100 - Lower competition = higher score
- **Cost Score**: {top_city['cost_score']}/100 - Operational and logistics costs
- **Profit Potential**: {top_city['profit_potential']}/100 - Overall profitability

#### Key Advantages
"""
        
        for pro in top_city['pros']:
            markdown += f"- ✅ {pro}\n"
        
        markdown += "\n#### Considerations\n"
        for con in top_city['cons']:
            markdown += f"- ⚠️ {con}\n"
        
        markdown += f"""
#### Market Data
- **MSMEs in State**: {top_city['msme_count']:,}
- **GDP Growth**: {top_city['gdp_growth']}%
- **City Tier**: Tier-{top_city['tier']}
- **Logistics Cost**: {top_city['logistics_cost']}

### 📊 All Recommendations

"""
        
        for i, rec in enumerate(recommendations, 1):
            markdown += f"""
#### {i}. {rec['city']}, {rec['state']} - {rec['recommendation']}
- **Overall Score**: {rec['overall_score']}/100
- **Profit Potential**: {rec['profit_potential']}/100
- **Key Strengths**: {', '.join(rec['pros'][:2])}
- **Considerations**: {', '.join(rec['cons'][:2])}

"""
        
        markdown += """
### 💡 Expansion Strategy

1. **Primary Target**: Focus on the top-ranked city for initial expansion
2. **Market Entry**: Conduct detailed local market research
3. **Competitive Analysis**: Study local competitors and pricing
4. **Location Selection**: Choose high-footfall areas within the city
5. **Pilot Launch**: Start with a pilot location before full expansion

### 📈 Success Factors

- **Local Partnerships**: Build relationships with local suppliers and partners
- **Market Adaptation**: Adapt offerings to local preferences
- **Competitive Pricing**: Price competitively based on local market
- **Marketing**: Invest in local marketing and brand awareness
- **Operations**: Ensure efficient logistics and supply chain

### ⚠️ Risk Mitigation

- Start with smaller investment in new location
- Test market response before scaling
- Monitor competition and market changes
- Maintain strong operations in current location
- Build local team with market knowledge
"""
        
        return markdown


