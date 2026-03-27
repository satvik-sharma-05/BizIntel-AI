import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Any, List

class RevenueForecast:
    def __init__(self):
        self.model = LinearRegression()
    
    def forecast_revenue(self, 
                        industry: str,
                        location: str,
                        investment: float,
                        market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast revenue based on industry, location, and market data"""
        
        # Simple forecasting logic (can be enhanced with Prophet/ARIMA)
        base_revenue = investment * 0.3  # 30% of investment as base
        
        # Adjust based on market factors
        demand_score = market_data.get("demand_score", 70) / 100
        competition_score = market_data.get("competition_score", 50) / 100
        
        # Calculate monthly revenue
        monthly_revenue = base_revenue * demand_score * (1 - competition_score * 0.5)
        
        # Generate 12-month forecast
        forecast = []
        for month in range(1, 13):
            growth_factor = 1 + (month * 0.05)  # 5% monthly growth
            revenue = monthly_revenue * growth_factor
            forecast.append({
                "month": month,
                "revenue": round(revenue, 2),
                "profit": round(revenue * 0.2, 2)  # 20% profit margin
            })
        
        total_annual_revenue = sum(f["revenue"] for f in forecast)
        total_annual_profit = sum(f["profit"] for f in forecast)
        
        return {
            "monthly_forecast": forecast,
            "annual_revenue": round(total_annual_revenue, 2),
            "annual_profit": round(total_annual_profit, 2),
            "roi": round((total_annual_profit / investment) * 100, 2),
            "breakeven_months": round(investment / monthly_revenue, 1)
        }
    
    def demand_forecast(self, historical_data: List[float], periods: int = 6) -> List[float]:
        """Forecast demand for next periods"""
        if len(historical_data) < 3:
            return [historical_data[-1]] * periods if historical_data else [0] * periods
        
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array(historical_data)
        
        self.model.fit(X, y)
        
        future_X = np.array(range(len(historical_data), len(historical_data) + periods)).reshape(-1, 1)
        predictions = self.model.predict(future_X)
        
        return [max(0, p) for p in predictions.tolist()]

revenue_forecast = RevenueForecast()
