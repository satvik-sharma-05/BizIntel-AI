"""
Structured Output Formatter
Converts AI responses to clean, structured format
Removes markdown formatting and creates professional business reports
"""
from typing import Dict, Any
import re

def format_market_analysis(raw_response: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format market analysis into structured output
    
    Returns structured JSON that frontend can render cleanly
    """
    # Remove markdown formatting
    clean_text = remove_markdown(raw_response)
    
    # Extract sections
    sections = extract_sections(clean_text)
    
    return {
        "title": f"Market Analysis – {business_data.get('industry', 'Business')} in {business_data.get('city', 'Location')}",
        "summary": sections.get("summary", "Market analysis completed."),
        "key_insights": extract_bullet_points(sections.get("key_insights", "")),
        "data_analysis": extract_bullet_points(sections.get("data_analysis", "")),
        "risks": extract_bullet_points(sections.get("risks", "")),
        "opportunities": extract_bullet_points(sections.get("opportunities", "")),
        "recommendations": extract_bullet_points(sections.get("recommendations", "")),
        "action_plan": extract_numbered_list(sections.get("action_plan", "")),
        "conclusion": sections.get("conclusion", "Analysis complete."),
        "generated_at": "now"
    }

def format_location_analysis(raw_response: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format location analysis into structured output"""
    clean_text = remove_markdown(raw_response)
    sections = extract_sections(clean_text)
    
    return {
        "title": f"Location Intelligence – {business_data.get('city', 'Location')}",
        "summary": sections.get("summary", "Location analysis completed."),
        "current_location": {
            "city": business_data.get("city"),
            "state": business_data.get("state"),
            "analysis": sections.get("current_location", "")
        },
        "key_insights": extract_bullet_points(sections.get("key_insights", "")),
        "expansion_opportunities": extract_bullet_points(sections.get("opportunities", "")),
        "logistics_analysis": sections.get("logistics", ""),
        "recommendations": extract_bullet_points(sections.get("recommendations", "")),
        "action_plan": extract_numbered_list(sections.get("action_plan", "")),
        "conclusion": sections.get("conclusion", "Analysis complete.")
    }

def format_forecast(raw_response: str, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format forecast into structured output"""
    clean_text = remove_markdown(raw_response)
    sections = extract_sections(clean_text)
    
    return {
        "title": f"Revenue Forecast – {forecast_data.get('business_name', 'Business')}",
        "summary": sections.get("summary", "Forecast generated based on market data."),
        "financial_projections": {
            "annual_revenue": forecast_data.get("annual_revenue"),
            "annual_profit": forecast_data.get("annual_profit"),
            "monthly_revenue": forecast_data.get("monthly_revenue"),
            "roi": forecast_data.get("roi"),
            "breakeven_months": forecast_data.get("breakeven_months")
        },
        "key_insights": extract_bullet_points(sections.get("key_insights", "")),
        "growth_drivers": extract_bullet_points(sections.get("growth_drivers", "")),
        "risks": extract_bullet_points(sections.get("risks", "")),
        "recommendations": extract_bullet_points(sections.get("recommendations", "")),
        "action_plan": extract_numbered_list(sections.get("action_plan", "")),
        "conclusion": sections.get("conclusion", "Forecast complete.")
    }

def format_chat_response(raw_response: str) -> Dict[str, Any]:
    """Format chat response into structured output"""
    clean_text = remove_markdown(raw_response)
    sections = extract_sections(clean_text)
    
    return {
        "answer": sections.get("answer", clean_text),
        "summary": sections.get("summary", ""),
        "key_points": extract_bullet_points(sections.get("key_points", "")),
        "recommendations": extract_bullet_points(sections.get("recommendations", "")),
        "action_items": extract_numbered_list(sections.get("action_items", "")),
        "formatted": True
    }

def remove_markdown(text: str) -> str:
    """Remove markdown formatting from text"""
    # Remove bold/italic markers
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # ***text***
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # **text**
    text = re.sub(r'\*(.+?)\*', r'\1', text)          # *text*
    text = re.sub(r'__(.+?)__', r'\1', text)          # __text__
    text = re.sub(r'_(.+?)_', r'\1', text)            # _text_
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def extract_sections(text: str) -> Dict[str, str]:
    """Extract sections from text based on common headers"""
    sections = {}
    
    # Common section patterns
    patterns = {
        "summary": r"Summary:?\s*(.+?)(?=\n\n|\n[A-Z]|$)",
        "key_insights": r"Key Insights:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "data_analysis": r"Data Analysis:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "risks": r"Risks:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "opportunities": r"Opportunities:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "recommendations": r"Recommendations:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "action_plan": r"Action Plan:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "conclusion": r"Conclusion:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "answer": r"Answer:?\s*(.+?)(?=\n\n[A-Z]|$)",
        "key_points": r"Key Points:?\s*(.+?)(?=\n\n[A-Z]|$)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()
    
    return sections

def extract_bullet_points(text: str) -> list:
    """Extract bullet points from text"""
    if not text:
        return []
    
    # Find lines starting with -, *, or •
    lines = text.split('\n')
    bullets = []
    
    for line in lines:
        line = line.strip()
        if line.startswith(('-', '*', '•')):
            # Remove bullet marker
            clean_line = re.sub(r'^[-*•]\s*', '', line).strip()
            if clean_line:
                bullets.append(clean_line)
    
    return bullets

def extract_numbered_list(text: str) -> list:
    """Extract numbered list from text"""
    if not text:
        return []
    
    # Find lines starting with numbers
    lines = text.split('\n')
    numbered = []
    
    for line in lines:
        line = line.strip()
        match = re.match(r'^\d+[\.)]\s*(.+)', line)
        if match:
            numbered.append(match.group(1).strip())
    
    return numbered

def create_business_report_structure() -> Dict[str, Any]:
    """Create empty business report structure"""
    return {
        "title": "",
        "summary": "",
        "key_insights": [],
        "data_analysis": [],
        "risks": [],
        "opportunities": [],
        "recommendations": [],
        "action_plan": [],
        "conclusion": ""
    }
