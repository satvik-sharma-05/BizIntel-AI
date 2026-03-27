"""
Test MongoDB Connection
Run this to verify MongoDB Atlas connection works
"""
import certifi
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB_NAME")

print("Testing MongoDB Connection...")
print(f"URI: {uri[:50]}...")
print(f"Database: {db_name}")
print("-" * 50)

try:
    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    
    # Test connection
    result = client.admin.command("ping")
    print("✅ MongoDB Connected Successfully!")
    print(f"Ping result: {result}")
    
    # Test database access
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"✅ Database accessible: {db_name}")
    print(f"Collections: {collections if collections else 'No collections yet'}")
    
    client.close()
    print("\n✅ All tests passed! MongoDB is working correctly.")
    
except Exception as e:
    print(f"\n❌ MongoDB connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check MongoDB Atlas Network Access (whitelist 0.0.0.0/0)")
    print("2. Verify connection string in .env")
    print("3. Install: pip install certifi dnspython")
    print("4. Check MongoDB Atlas cluster is running")
