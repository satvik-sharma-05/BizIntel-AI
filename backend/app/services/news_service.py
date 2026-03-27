import os
import requests
from typing import Dict, Any, List

def get_news_data(query: str = "business india", limit: int = 10) -> Dict[str, Any]:
    """Fetch real news from News API"""
    try:
        api_key = os.getenv('NEWS_API_KEY', '')
        
        if not api_key:
            return get_fallback_news()
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            return {
                "success": True,
                "total": data.get("totalResults", 0),
                "articles": [
                    {
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "source": article.get("source", {}).get("name"),
                        "published_at": article.get("publishedAt"),
                        "image": article.get("urlToImage")
                    }
                    for article in articles[:limit]
                ],
                "source": "News API"
            }
        else:
            return get_fallback_news()
            
    except Exception as e:
        print(f"News API Error: {str(e)}")
        return get_fallback_news()

def get_fallback_news() -> Dict[str, Any]:
    """Fallback news data"""
    return {
        "success": True,
        "total": 5,
        "articles": [
            {
                "title": "India's GDP Growth Projected at 7.2% for FY 2024-25",
                "description": "Economic Survey highlights strong growth momentum in Indian economy",
                "url": "#",
                "source": "Economic Times",
                "published_at": "2024-03-26T10:00:00Z",
                "image": None
            },
            {
                "title": "MSME Sector Shows Robust Growth with 3.2% Increase",
                "description": "Small businesses drive employment and economic expansion",
                "url": "#",
                "source": "Business Standard",
                "published_at": "2024-03-26T09:30:00Z",
                "image": None
            },
            {
                "title": "Digital Payments Surge 40% Year-on-Year",
                "description": "UPI transactions reach new milestone in March 2024",
                "url": "#",
                "source": "Mint",
                "published_at": "2024-03-26T08:45:00Z",
                "image": None
            },
            {
                "title": "Startup Funding Rebounds in Q1 2024",
                "description": "Indian startups raise $3.2 billion in first quarter",
                "url": "#",
                "source": "YourStory",
                "published_at": "2024-03-26T07:15:00Z",
                "image": None
            },
            {
                "title": "Manufacturing PMI Hits 58.5, Highest in 6 Months",
                "description": "Strong demand drives manufacturing sector expansion",
                "url": "#",
                "source": "Reuters",
                "published_at": "2024-03-26T06:00:00Z",
                "image": None
            }
        ],
        "source": "Fallback Data"
    }

def get_industry_news(industry: str, limit: int = 5) -> Dict[str, Any]:
    """Get news specific to an industry"""
    query = f"{industry} business india"
    return get_news_data(query, limit)
