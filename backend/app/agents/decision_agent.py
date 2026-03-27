"""
Decision Agent
Aggregates results from all agents and generates final recommendations using LLM
"""
from .base_agent import BaseAgent
from typing import Dict, Any
import json
from ..services.llm_service import call_openrouter

class DecisionAgent(BaseAgent):
    """Agent responsible for making final decisions based on all agent outputs"""
    
    def __init__(self):
        super().__init__(
            agent_id="decision_agent",
            name="Decision Agent",
            description="Aggregates agent results and generates final recommendations"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final decision and recommendations
        
        Context should contain:
        - query: str
        - business_name: str
        - industry: str
        - city: str
        - state: str
        - investment: float
        - data: dict (from Data Agent)
        - market_analysis: dict (from Market Agent)
        - location_analysis: dict (from Location Agent)
        """
        
        query = context.get("query", "")
        business_name = context.get("business_name", "")
        industry = context.get("industry", "")
        city = context.get("city", "")
        state = context.get("state", "")
        investment = context.get("investment", 0)
        
        data = context.get("data", {})
        market_analysis = context.get("market_analysis", {})
        location_analysis = context.get("location_analysis", {})
        
        self.log(f"Generating decision for query: {query}")
        
        # Build comprehensive prompt for LLM
        prompt = f"""You are an expert business consultant analyzing a business opportunity.

Business Details:
- Name: {business_name}
- Industry: {industry}
- Location: {city}, {state}
- Investment: ₹{investment:,.0f}

User Query: {query}

Data Analysis:
- GDP Growth: {data.get('gdp', {}).get('growth', 'N/A')}%
- MSME Count in {state}: {data.get('msme', {}).get('state', 'N/A')}
- Inflation: {data.get('economic_indicators', {}).get('inflation', 'N/A')}%
- Weather: {data.get('weather', {}).get('temp', 'N/A')}°C, {data.get('weather', {}).get('description', 'N/A')}
- News Articles: {len(data.get('news', []))} recent articles

Market Analysis:
- Demand Score: {market_analysis.get('demand_score', 'N/A')}/100
- Market Opportunity: {market_analysis.get('opportunity', 'N/A')}
- Competition Level: {market_analysis.get('competition', 'N/A')}
- Growth Trend: {market_analysis.get('growth_trend', 'N/A')}
- Market Size: {market_analysis.get('market_size', 'N/A')}
- Entry Barrier: {market_analysis.get('entry_barrier', 'N/A')}

Location Intelligence:
- Current Location: {location_analysis.get('current_location', {}).get('city', city)}
- Top Expansion Cities: {', '.join([rec['city'] for rec in location_analysis.get('recommendations', [])[:3]])}
- Total Cities Analyzed: {location_analysis.get('total_analyzed', 0)}

Based on this comprehensive analysis, provide:

1. **Overall Recommendation**: Should they proceed? (Highly Recommended / Recommended / Consider / Not Recommended)
2. **Confidence Score**: 0-100 based on data quality and market conditions
3. **Key Strengths**: 3-5 specific advantages
4. **Key Risks**: 3-5 specific concerns
5. **Strategic Recommendations**: 3-5 actionable steps
6. **Financial Outlook**: Expected ROI timeline and revenue potential
7. **Next Steps**: Immediate actions to take

Be specific, data-driven, and actionable. Use Indian market context."""

        try:
            # Call LLM
            messages = [
                {"role": "system", "content": "You are an expert business consultant specializing in Indian markets. Provide clear, actionable recommendations based on data."},
                {"role": "user", "content": prompt}
            ]
            
            self.log("Calling LLM for decision generation...")
            llm_response = call_openrouter(messages, max_tokens=1500)
            
            self.log("LLM response received")
            
            # Try to extract structured data, but keep full response
            decision = {
                "recommendation": self._extract_recommendation(llm_response),
                "confidence": self._extract_confidence(llm_response),
                "full_analysis": llm_response,
                "query": query,
                "business_context": {
                    "name": business_name,
                    "industry": industry,
                    "location": f"{city}, {state}",
                    "investment": investment
                }
            }
            
            return {
                "success": True,
                "data": decision,
                "message": "Decision generated successfully",
                "errors": []
            }
            
        except Exception as e:
            self.add_error(f"LLM call failed: {str(e)}")
            
            # Fallback decision
            return {
                "success": False,
                "data": {
                    "recommendation": "Consider",
                    "confidence": 60,
                    "full_analysis": f"Unable to generate full analysis due to error: {str(e)}. Based on available data: Market shows {market_analysis.get('opportunity', 'moderate')} opportunity with {market_analysis.get('competition', 'moderate')} competition.",
                    "query": query
                },
                "message": "Decision generated with limited data",
                "errors": [str(e)]
            }
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract recommendation from LLM response"""
        text_lower = text.lower()
        if "highly recommended" in text_lower:
            return "Highly Recommended"
        elif "not recommended" in text_lower:
            return "Not Recommended"
        elif "recommended" in text_lower:
            return "Recommended"
        else:
            return "Consider"
    
    def _extract_confidence(self, text: str) -> int:
        """Extract confidence score from LLM response"""
        import re
        # Look for patterns like "confidence: 85" or "85%" or "score: 85"
        patterns = [
            r'confidence[:\s]+(\d+)',
            r'(\d+)%',
            r'score[:\s]+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    return score
        
        return 70  # Default confidence

# Global decision agent instance
decision_agent = DecisionAgent()
