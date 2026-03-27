"""
MongoDB Database Client - ONLY DATABASE
All data stored in MongoDB collections
"""
from motor.motor_asyncio import AsyncIOMotorClient
from ..config.settings import settings
import certifi

# Global MongoDB client
mongodb_client = None
mongodb_database = None

async def connect_mongodb():
    """Connect to MongoDB with proper SSL/TLS configuration"""
    global mongodb_client, mongodb_database
    
    try:
        # Use certifi for proper SSL certificates
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        mongodb_database = mongodb_client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        print(f"✅ MongoDB connected: {settings.MONGODB_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  Check: 1) Atlas IP whitelist, 2) Connection string, 3) certifi installed")
        raise  # Raise error so we know MongoDB is not working

async def close_mongodb():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("👋 MongoDB disconnected")

def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb_database

async def create_indexes():
    """Create indexes for better query performance"""
    db = mongodb_database
    
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        
        # Businesses collection indexes
        await db.businesses.create_index("user_id")
        await db.businesses.create_index([("user_id", 1), ("created_at", -1)])
        await db.businesses.create_index("industry")  # For filtering by industry
        await db.businesses.create_index("city")  # For filtering by city
        await db.businesses.create_index([("industry", 1), ("city", 1)])  # Compound index
        
        # Conversations collection indexes
        await db.conversations.create_index([("business_id", 1), ("created_at", -1)])
        await db.conversations.create_index("user_id")
        await db.conversations.create_index([("business_id", 1), ("updated_at", -1)])
        
        # Documents collection indexes
        await db.documents.create_index([("business_id", 1), ("uploaded_at", -1)])
        await db.documents.create_index("business_id")
        await db.documents.create_index("filename")
        
        # RAG chunks collection indexes
        await db.rag_chunks.create_index([("business_id", 1), ("document_id", 1)])
        await db.rag_chunks.create_index("document_id")
        
        # Market analysis collection indexes (NOT unique - allow multiple analyses)
        await db.market_analysis.create_index([("business_id", 1), ("created_at", -1)])
        
        # Location analysis collection indexes (NOT unique - allow multiple analyses)
        await db.location_analysis.create_index([("business_id", 1), ("created_at", -1)])
        
        # Forecasts collection indexes (NOT unique - allow multiple forecasts)
        await db.forecasts.create_index([("business_id", 1), ("created_at", -1)])
        
        # API cache collection indexes
        await db.api_cache.create_index([("cache_key", 1), ("created_at", -1)])
        await db.api_cache.create_index("created_at", expireAfterSeconds=86400)  # Auto-delete after 24h
        try:
            await db.api_cache.create_index("cache_key", unique=True)  # Unique cache keys
        except Exception as e:
            print(f"⚠️  API cache unique index already exists or has duplicates: {e}")
        
        # Agent logs collection indexes
        await db.agent_logs.create_index([("business_id", 1), ("created_at", -1)])
        await db.agent_logs.create_index("agent_id")
        await db.agent_logs.create_index([("agent_id", 1), ("created_at", -1)])
        await db.agent_logs.create_index("created_at", expireAfterSeconds=604800)  # Auto-delete after 7 days
        
        print("✅ MongoDB indexes created for optimal performance")
    except Exception as e:
        print(f"⚠️  Some indexes may already exist: {e}")

# Collections helper
class Collections:
    """MongoDB collections"""
    
    @staticmethod
    def users():
        return mongodb_database.users
    
    @staticmethod
    def businesses():
        return mongodb_database.businesses
    
    @staticmethod
    def conversations():
        return mongodb_database.conversations
    
    @staticmethod
    def market_analysis():
        return mongodb_database.market_analysis
    
    @staticmethod
    def location_analysis():
        return mongodb_database.location_analysis
    
    @staticmethod
    def forecasts():
        return mongodb_database.forecasts
    
    @staticmethod
    def reports():
        return mongodb_database.reports
    
    @staticmethod
    def documents():
        return mongodb_database.documents
    
    @staticmethod
    def rag_chunks():
        return mongodb_database.rag_chunks
    
    @staticmethod
    def api_cache():
        return mongodb_database.api_cache
    
    @staticmethod
    def agent_logs():
        return mongodb_database.agent_logs
    
    @staticmethod
    def insights():
        return mongodb_database.insights
    
    @staticmethod
    def system_logs():
        return mongodb_database.system_logs

collections = Collections()
