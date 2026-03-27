"""
Test all API endpoints to verify data flow
"""
import asyncio
import sys
from app.services.data_pipeline import data_pipeline
from app.services.gdp_service import get_gdp_data, get_economic_indicators
from app.services.msme_service import get_msme_data, get_msme_by_state
from app.services.weather_service import get_weather_data
from app.services.news_service import get_industry_news

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_data(label, data):
    print(f"{YELLOW}📊 {label}:{RESET}")
    if isinstance(data, dict):
        for key, value in list(data.items())[:5]:  # Show first 5 items
            print(f"   {key}: {value}")
        if len(data) > 5:
            print(f"   ... and {len(data) - 5} more fields")
    else:
        print(f"   {data}")
    print()

async def test_all_apis():
    """Test all API endpoints"""
    
    print("\n" + "="*60)
    print("🧪 BizIntel AI - API Testing")
    print("="*60 + "\n")
    
    errors = []
    
    # 1. Test GDP Service
    print("1️⃣  Testing GDP Service...")
    try:
        gdp_data = get_gdp_data()
        if gdp_data and 'growth' in gdp_data:
            print_success(f"GDP Service Working - Growth: {gdp_data['growth']}%")
            print_data("GDP Data", gdp_data)
        else:
            print_error("GDP Service returned invalid data")
            print_data("GDP Data", gdp_data)
            errors.append("GDP Service")
    except Exception as e:
        print_error(f"GDP Service Failed: {str(e)}")
        errors.append("GDP Service")
    
    # 2. Test Economic Indicators
    print("2️⃣  Testing Economic Indicators...")
    try:
        indicators = get_economic_indicators()
        if indicators and 'inflation' in indicators:
            print_success(f"Economic Indicators Working - Inflation: {indicators['inflation']}%")
            print_data("Economic Indicators", indicators)
        else:
            print_error("Economic Indicators returned invalid data")
            errors.append("Economic Indicators")
    except Exception as e:
        print_error(f"Economic Indicators Failed: {str(e)}")
        errors.append("Economic Indicators")
    
    # 3. Test MSME Service
    print("3️⃣  Testing MSME Service...")
    try:
        msme_total = get_msme_data()
        msme_punjab = get_msme_by_state("Punjab")
        print_success(f"MSME Service Working - Total: {msme_total:,}")
        print_success(f"MSME Punjab: {msme_punjab:,}")
        print()
    except Exception as e:
        print_error(f"MSME Service Failed: {str(e)}")
        errors.append("MSME Service")
    
    # 4. Test Weather Service
    print("4️⃣  Testing Weather Service...")
    try:
        weather = get_weather_data("Mumbai")
        if weather and 'temp' in weather:
            print_success(f"Weather Service Working - Mumbai: {weather['temp']}°C")
            print_data("Weather Data", weather)
        else:
            print_error("Weather Service returned invalid data")
            errors.append("Weather Service")
    except Exception as e:
        print_error(f"Weather Service Failed: {str(e)}")
        errors.append("Weather Service")
    
    # 5. Test News Service
    print("5️⃣  Testing News Service...")
    try:
        news = get_industry_news("technology", limit=3)
        if news and len(news) > 0:
            print_success(f"News Service Working - Found {len(news)} articles")
            if news:
                print_info(f"Latest: {news[0].get('title', 'N/A')[:60]}...")
        else:
            print_error("News Service returned no articles")
            errors.append("News Service")
        print()
    except Exception as e:
        print_error(f"News Service Failed: {str(e)}")
        errors.append("News Service")
    
    # 6. Test Data Pipeline
    print("6️⃣  Testing Data Pipeline...")
    try:
        from app.database.mongodb import connect_mongodb, close_mongodb
        await connect_mongodb()
        
        economic_data = await data_pipeline.get_economic_data(force_refresh=True)
        if economic_data and 'gdp' in economic_data:
            gdp = economic_data['gdp']
            indicators = economic_data['economic_indicators']
            print_success("Data Pipeline Working")
            print_info(f"GDP Growth: {gdp.get('growth', 'N/A')}%")
            print_info(f"Inflation: {indicators.get('inflation', 'N/A')}%")
            print_data("Pipeline Data", economic_data)
        else:
            print_error("Data Pipeline returned invalid data")
            print_data("Pipeline Data", economic_data)
            errors.append("Data Pipeline")
        
        await close_mongodb()
    except Exception as e:
        print_error(f"Data Pipeline Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        errors.append("Data Pipeline")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60 + "\n")
    
    if not errors:
        print_success("🎉 All API tests passed!")
        print_info("\nAll services are working correctly:")
        print("  ✅ GDP Service")
        print("  ✅ Economic Indicators")
        print("  ✅ MSME Service")
        print("  ✅ Weather Service")
        print("  ✅ News Service")
        print("  ✅ Data Pipeline")
        return True
    else:
        print_error(f"❌ {len(errors)} service(s) failed:")
        for error in errors:
            print(f"  - {error}")
        print_info("\nPlease check:")
        print("  1. API keys in .env file")
        print("  2. Internet connection")
        print("  3. MongoDB running")
        print("  4. Service implementations")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_all_apis())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Testing cancelled")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nTesting failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
