"""
MongoDB migration script - creates indexes and validates schema
Run this to optimize MongoDB collections
"""
import asyncio
from app.database.mongodb import connect_mongodb, close_mongodb, get_mongodb

async def migrate_database():
    """Create indexes and optimize MongoDB collections"""
    try:
        print("🔄 Connecting to MongoDB...")
        await connect_mongodb()
        
        db = get_mongodb()
        
        print("\n📋 Creating indexes for optimal performance...")
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        print("  ✅ users: email (unique)")
        
        # Businesses collection indexes
        await db.businesses.create_index("user_id")
        await db.businesses.create_index([("user_id", 1), ("created_at", -1)])
        print("  ✅ businesses: user_id, user_id+created_at")
        
        # Conversations collection indexes
        await db.conversations.create_index("business_id")
        await db.conversations.create_index("user_id")
        await db.conversations.create_index([("business_id", 1), ("timestamp", -1)])
        print("  ✅ conversations: business_id, user_id, business_id+timestamp")
        
        # Market analysis collection indexes
        await db.market_analysis.create_index("business_id")
        await db.market_analysis.create_index([("business_id", 1), ("created_at", -1)])
        print("  ✅ market_analysis: business_id, business_id+created_at")
        
        # Location analysis collection indexes
        await db.location_analysis.create_index("business_id")
        await db.location_analysis.create_index([("business_id", 1), ("created_at", -1)])
        print("  ✅ location_analysis: business_id, business_id+created_at")
        
        # Forecasts collection indexes
        await db.forecasts.create_index("business_id")
        await db.forecasts.create_index([("business_id", 1), ("created_at", -1)])
        print("  ✅ forecasts: business_id, business_id+created_at")
        
        # API cache collection indexes
        await db.api_cache.create_index("cache_key", unique=True)
        await db.api_cache.create_index("expires_at")
        print("  ✅ api_cache: cache_key (unique), expires_at")
        
        # Agent logs collection indexes
        await db.agent_logs.create_index("business_id")
        await db.agent_logs.create_index("agent_id")
        await db.agent_logs.create_index([("business_id", 1), ("timestamp", -1)])
        print("  ✅ agent_logs: business_id, agent_id, business_id+timestamp")
        
        print("\n✅ Database migration completed successfully!")
        print("\nIndexes created for:")
        print("  - Fast user lookups by email")
        print("  - Fast business queries by user")
        print("  - Fast conversation history retrieval")
        print("  - Fast analysis data access")
        print("  - Efficient cache lookups")
        print("  - Quick agent log queries")
        
        await close_mongodb()
        print("\n👋 MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔄 Starting MongoDB migration...")
    print("⚠️  This will create indexes for better performance")
    asyncio.run(migrate_database())
