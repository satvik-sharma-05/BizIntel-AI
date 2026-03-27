"""
Market Agent - Enhanced with Competition Analysis
Analyzes market conditions, opportunities, and competition
"""
from .base_agent import BaseAgent
from typing import Dict, Any
from ..services.competition_service import competition_service

class MarketAgent(BaseAgent):
    """Agent responsible for market analysis with competition data"""
    
    def __init__(self):
        super().__init__(
            agent_id="market_agent",
            name="Market Agent",
            description="Analyzes market conditions, demand, competition, and opportunities"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions with competition"""
        
        industry = context.get("industry")
        city = context.get("city")
        state = context.get("state")
        data = context.get("data", {})
        
        self.log(f"Analyzing market for {industry} in {city}, {state}")
        
        # Get data from Data Agent
        gdp = data.get("gdp", {})
        msme = data.get("msme", {})
        economic = data.get("economic_indicators", {})
        news = data.get("news", [])
        
        # Get competition data
        competition_data = await competition_service.get_competitors_nearby(
            city=city,
            state=state,
            industry=industry,
            radius_km=5.0
        )
        
        # Calculate market scores
        gdp_growth = gdp.get("growth", 7.2)
        msme_count = msme.get("state", 0)
        inflation = economic.get("inflation", 5.4)
        competitor_count = competition_data.get("count", 0)
        competitor_density = competition_data.get("density", "Medium")
        
        # Market demand score (0-100)
        demand_score = min(100, (gdp_growth * 10) + (msme_count / 10000))
        
        # Market opportunity (High/Medium/Low)
        if demand_score > 75:
            opportunity = "High"
        elif demand_score > 50:
            opportunity = "Medium"
        else:
            opportunity = "Low"
        
        # Competition level (enhanced with real data)
        if competitor_density in ["Very High", "High"] or msme_count > 500000:
            competition = "High"
        elif competitor_density == "Medium" or msme_count > 100000:
            competition = "Medium"
        else:
            competition = "Low"
        
        # Market saturation
        saturation_ratio = competitor_count / (demand_score / 10) if demand_score > 0 else 0
        if saturation_ratio > 5:
            saturation = "Oversaturated"
        elif saturation_ratio > 3:
            saturation = "High"
        elif saturation_ratio > 1:
            saturation = "Moderate"
        else:
            saturation = "Low"
        
        # Market growth trend
        if gdp_growth > 7:
            growth_trend = "Growing"
        elif gdp_growth > 5:
            growth_trend = "Stable"
        else:
            growth_trend = "Declining"
        
        # Entry difficulty
        if competition == "High" and saturation in ["Oversaturated", "High"]:
            entry_difficulty = "Very Hard"
        elif competition == "High" or saturation == "High":
            entry_difficulty = "Hard"
        elif competition == "Medium":
            entry_difficulty = "Moderate"
        else:
            entry_difficulty = "Easy"
        
        # Profit potential
        if opportunity == "High" and competition == "Low":
            profit_potential = "Very High"
        elif opportunity == "High" and competition == "Medium":
            profit_potential = "High"
        elif opportunity == "Medium" and competition == "Low":
            profit_potential = "High"
        elif opportunity == "Medium" and competition == "Medium":
            profit_potential = "Medium"
        else:
            profit_potential = "Low"
        
        # News sentiment
        news_sentiment = "Positive" if len(news) > 0 else "Neutral"
        
        # Build structured markdown analysis
        markdown_analysis = self._build_markdown_analysis(
            industry=industry,
            city=city,
            state=state,
            demand_score=demand_score,
            opportunity=opportunity,
            competition=competition,
            competitor_count=competitor_count,
            competitor_density=competitor_density,
            saturation=saturation,
            growth_trend=growth_trend,
            gdp_growth=gdp_growth,
            msme_count=msme_count,
            inflation=inflation,
            entry_difficulty=entry_difficulty,
            profit_potential=profit_potential,
            news_sentiment=news_sentiment
        )
        
        analysis = {
            "demand_score": round(demand_score, 1),
            "opportunity": opportunity,
            "competition": competition,
            "competitor_count": competitor_count,
            "competitor_density": competitor_density,
            "saturation": saturation,
            "growth_trend": growth_trend,
            "gdp_growth": gdp_growth,
            "msme_count": msme_count,
            "inflation": inflation,
            "news_sentiment": news_sentiment,
            "news_count": len(news) if isinstance(news, list) else 0,
            "market_size": "Large" if msme_count > 300000 else "Medium" if msme_count > 100000 else "Small",
            "entry_difficulty": entry_difficulty,
            "profit_potential": profit_potential,
            "markdown_analysis": markdown_analysis,
            "competition_source": competition_data.get("source", "Estimated")
        }
        
        self.log(f"Market analysis complete: {opportunity} opportunity, {competition} competition, {competitor_count} competitors")
        
        return {
            "success": True,
            "data": analysis,
            "message": f"Market analysis complete for {industry} in {state}",
            "errors": []
        }
    
    def _build_markdown_analysis(
        self,
        industry: str,
        city: str,
        state: str,
        demand_score: float,
        opportunity: str,
        competition: str,
        competitor_count: int,
        competitor_density: str,
        saturation: str,
        growth_trend: str,
        gdp_growth: float,
        msme_count: int,
        inflation: float,
        entry_difficulty: str,
        profit_potential: str,
        news_sentiment: str
    ) -> str:
        """Build structured markdown analysis"""
        
        return f"""## Market Analysis: {industry} in {city}, {state}

### 📊 Summary
- **Market Opportunity**: {opportunity}
- **Competition Level**: {competition}
- **Profit Potential**: {profit_potential}
- **Entry Difficulty**: {entry_difficulty}

### 🎯 Market Overview
- **Market Size**: Based on {msme_count:,} MSMEs in {state}
- **Growth Trend**: {growth_trend} ({gdp_growth}% GDP growth)
- **Demand Score**: {demand_score:.1f}/100

### 📈 Demand Analysis
- **GDP Growth**: {gdp_growth}% (State level)
- **Economic Trend**: {growth_trend}
- **Market Sentiment**: {news_sentiment}
- **Inflation Rate**: {inflation}%

### 🏢 Competition Analysis
- **Competitor Count**: {competitor_count} businesses within 5km
- **Competitor Density**: {competitor_density}
- **Market Saturation**: {saturation}
- **Competition Level**: {competition}

### 💰 Market Saturation
- **Status**: {saturation}
- **Demand vs Competition**: {"Favorable" if saturation in ["Low", "Moderate"] else "Challenging"}

### 🚀 Opportunities
{"- High demand with manageable competition" if opportunity == "High" and competition != "High" else ""}
{"- Growing market with expansion potential" if growth_trend == "Growing" else ""}
{"- Lower competition density" if competitor_density in ["Low", "Very Low"] else ""}

### ⚠️ Risks
{"- High competition in the area" if competition == "High" else ""}
{"- Market saturation concerns" if saturation in ["High", "Oversaturated"] else ""}
{"- Economic headwinds" if gdp_growth < 5 else ""}

### 💡 Recommendations
{"- **Strong Entry**: Market conditions are favorable for entry" if profit_potential in ["Very High", "High"] else ""}
{"- **Differentiation Required**: Focus on unique value proposition" if competition == "High" else ""}
{"- **Strategic Positioning**: Identify underserved segments" if saturation in ["High", "Oversaturated"] else ""}

### 📍 Action Plan
1. Conduct detailed competitor analysis
2. Identify market gaps and opportunities
3. Develop differentiation strategy
4. Plan marketing and customer acquisition
5. Monitor market trends continuously
"""
