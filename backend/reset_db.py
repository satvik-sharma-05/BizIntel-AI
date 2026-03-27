"""
Reset MongoDB database - drops all collections and recreates them
"""
import asyncio
from app.database.mongodb import connect_mongodb, close_mongodb, get_mongodb

async def reset_database():
    """Drop all collections and recreate fresh database"""
    try:
        print("🔄 Connecting to MongoDB...")
        await connect_mongodb()
        
        db = get_mongodb()
        
        # Get all collection names
        collections = await db.list_collection_names()
        
        if collections:
            print(f"\n📋 Found {len(collections)} collections:")
            for coll in collections:
                print(f"  - {coll}")
            
            # Drop all collections
            print("\n🗑️  Dropping all collections...")
            for coll in collections:
                await db[coll].drop()
                print(f"  ✅ Dropped: {coll}")
        else:
            print("\n📋 No collections found")
        
        print("\n✅ Database reset complete!")
        print("\nCollections will be created automatically when first used:")
        print("  - users")
        print("  - businesses")
        print("  - conversations")
        print("  - market_analysis")
        print("  - location_analysis")
        print("  - forecasts")
        print("  - api_cache")
        print("  - agent_logs")
        
        await close_mongodb()
        print("\n👋 MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_database())
