import os
import requests
from typing import Dict, Any, List
import asyncio
import httpx

# Model routing for different use cases
MODELS = {
    "fast": "deepseek/deepseek-chat",  # Fast for chat, analysis
    "reasoning": "mistralai/mistral-7b-instruct",  # For reports, complex analysis
    "cheap": "meta-llama/llama-3-8b-instruct",  # For summaries, simple tasks
    "hybrid": "deepseek/deepseek-chat"  # For RAG answers
}

def call_openrouter(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    use_case: str = "fast"  # "fast", "reasoning", "cheap", "hybrid"
) -> str:
    """
    Call OpenRouter API for LLM responses with optimized model routing
    
    Args:
        messages: Conversation messages
        model: Specific model (overrides use_case)
        temperature: Sampling temperature
        max_tokens: Max response tokens
        use_case: Type of task - "fast", "reasoning", "cheap", "hybrid"
    """
    try:
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        
        if not api_key:
            return "OpenRouter API key not configured. Please add OPENROUTER_API_KEY to .env file."
        
        # Select model based on use case
        if model is None:
            model = MODELS.get(use_case, MODELS["fast"])
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('APP_URL', 'http://localhost:3000'),
            "X-Title": "BizIntel AI"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            error_msg = f"OpenRouter API error: {response.status_code}"
            print(error_msg)
            return f"Error: {error_msg}"
            
    except Exception as e:
        print(f"LLM Service Error: {str(e)}")
        return f"Error calling AI service: {str(e)}"

async def call_openrouter_async(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    use_case: str = "fast"
) -> str:
    """Async version of call_openrouter for better performance"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        
        if not api_key:
            return "OpenRouter API key not configured."
        
        # Select model based on use case
        if model is None:
            model = MODELS.get(use_case, MODELS["fast"])
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('APP_URL', 'http://localhost:3000'),
            "X-Title": "BizIntel AI"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                error_msg = f"OpenRouter API error: {response.status_code}"
                print(error_msg)
                return f"Error: {error_msg}"
                
    except Exception as e:
        print(f"LLM Service Error: {str(e)}")
        return f"Error calling AI service: {str(e)}"

def chat_with_business_context(
    user_message: str,
    business_name: str,
    industry: str,
    city: str,
    state: str,
    investment: float,
    conversation_history: List[Dict[str, str]] = None
) -> str:
    """Chat with business context using fast model"""
    
    system_prompt = f"""You are an AI business intelligence assistant for BizIntel AI.

You are helping analyze a business with the following details:
- Business Name: {business_name}
- Industry: {industry}
- Location: {city}, {state}
- Initial Investment: ₹{investment:,.0f}

Your role is to:
1. Provide market analysis and insights
2. Evaluate business viability
3. Suggest strategies and recommendations
4. Analyze economic indicators
5. Forecast revenue and growth
6. Identify risks and opportunities

IMPORTANT: Format all responses using markdown for better readability:
- Use **bold** for emphasis and key terms
- Use bullet points (- or •) for lists
- Use proper headings (##, ###) for sections
- Use tables when comparing data
- Use code blocks for technical information
- Use > for important quotes or highlights

Be specific, data-driven, and actionable. Use Indian market context and currency (₹).
Make your responses visually appealing and easy to scan.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    if conversation_history:
        messages.extend(conversation_history[-5:])  # Last 5 messages
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    return call_openrouter(messages, max_tokens=1500, use_case="fast")

def analyze_business_opportunity(
    business_name: str,
    industry: str,
    city: str,
    state: str,
    investment: float,
    description: str = ""
) -> Dict[str, Any]:
    """Comprehensive business opportunity analysis using reasoning model"""
    
    prompt = f"""Analyze this business opportunity and provide a detailed assessment:

Business: {business_name}
Industry: {industry}
Location: {city}, {state}
Investment: ₹{investment:,.0f}
Description: {description}

Provide a comprehensive analysis using markdown formatting:

## Executive Summary
[Brief overview with key recommendation]

## Market Viability Score: X/10
[Detailed explanation]

## Location Suitability Score: X/10
[Detailed explanation]

## Investment Analysis Score: X/10
[Detailed explanation]

## Competition Level: [Low/Medium/High]
[Analysis of competitive landscape]

## Key Opportunities
- [Opportunity 1]
- [Opportunity 2]
- [Opportunity 3]

## Key Risks
- [Risk 1]
- [Risk 2]
- [Risk 3]

## Financial Projections
| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Revenue | ₹X | ₹X | ₹X |
| Profit | ₹X | ₹X | ₹X |

**Breakeven Timeline:** [X months]

## Overall Recommendation
**[Go/No-Go/Conditional]**

[Detailed reasoning]

## Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

Be specific and use Indian market data where possible. Use **bold** for emphasis.
"""

    messages = [
        {"role": "system", "content": "You are a business analysis expert specializing in Indian markets. Always use markdown formatting for clear, beautiful responses."},
        {"role": "user", "content": prompt}
    ]
    
    response = call_openrouter(messages, max_tokens=2000, use_case="reasoning")
    
    return {
        "analysis": response,
        "business_name": business_name,
        "industry": industry,
        "location": f"{city}, {state}",
        "investment": investment
    }
