"""
Verification script to check if the MongoDB-only setup is complete
"""
import asyncio
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

async def verify_setup():
    """Verify the complete MongoDB-only setup"""
    
    print("\n" + "="*60)
    print("🔍 BizIntel AI - Setup Verification")
    print("="*60 + "\n")
    
    errors = []
    warnings = []
    
    # 1. Check Python version
    print("1️⃣  Checking Python version...")
    if sys.version_info >= (3, 9):
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        print_error(f"Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.9+)")
        errors.append("Python version too old")
    
    # 2. Check .env file
    print("\n2️⃣  Checking .env file...")
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print_success(".env file exists")
        
        # Check required variables
        with open(env_path) as f:
            env_content = f.read()
            required_vars = [
                "MONGODB_URI",
                "JWT_SECRET",
                "OPENROUTER_API_KEY",
                "OPENWEATHER_API_KEY",
                "NEWS_API_KEY",
                "DATA_GOV_API_KEY"
            ]
            
            for var in required_vars:
                if var in env_content:
                    print_success(f"  {var} found")
                else:
                    print_error(f"  {var} missing")
                    errors.append(f"Missing {var} in .env")
    else:
        print_error(".env file not found")
        errors.append(".env file missing")
    
    # 3. Check MongoDB connection
    print("\n3️⃣  Checking MongoDB connection...")
    try:
        from app.database.mongodb import connect_mongodb, close_mongodb, get_mongodb
        await connect_mongodb()
        db = get_mongodb()
        await db.command("ping")
        print_success("MongoDB connected")
        await close_mongodb()
    except Exception as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        errors.append("MongoDB not accessible")
    
    # 4. Check for old database files
    print("\n4️⃣  Checking for old database files...")
    old_files = [
        "app/database/postgres.py",
        "app/database/redis_client.py",
        "app/database/neo4j_client.py"
    ]
    
    found_old = False
    for file in old_files:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            print_error(f"  {file} still exists (should be deleted)")
            errors.append(f"Old file {file} exists")
            found_old = True
    
    if not found_old:
        print_success("No old database files found")
    
    # 5. Check imports
    print("\n5️⃣  Checking imports...")
    try:
        from app.config.settings import settings
        print_success("Settings imported")
        
        from app.database.mongodb import collections
        print_success("MongoDB collections imported")
        
        from app.api import auth, business, chat, dashboard, forecast, market, location, agents
        print_success("All API modules imported")
        
        from app.agents.orchestrator import orchestrator
        print_success("Orchestrator imported")
        
        from app.auth.auth_service import hash_password, verify_password
        print_success("Auth service imported")
        
    except Exception as e:
        print_error(f"Import failed: {str(e)}")
        errors.append("Import errors")
    
    # 6. Check documentation
    print("\n6️⃣  Checking documentation...")
    docs = [
        "README.md",
        "ARCHITECTURE.md",
        "STARTUP_GUIDE.md",
        "QUICK_START.md",
        "REFACTOR_COMPLETE.md"
    ]
    
    for doc in docs:
        doc_path = Path(__file__).parent.parent / doc
        if doc_path.exists():
            print_success(f"  {doc}")
        else:
            print_warning(f"  {doc} missing")
            warnings.append(f"Missing {doc}")
    
    # 7. Check requirements
    print("\n7️⃣  Checking requirements.txt...")
    req_path = Path(__file__).parent / "requirements.txt"
    if req_path.exists():
        print_success("requirements.txt exists")
        
        # Check key packages
        with open(req_path) as f:
            req_content = f.read()
            key_packages = ["fastapi", "motor", "bcrypt", "pyjwt", "pymongo"]
            
            for pkg in key_packages:
                if pkg in req_content.lower():
                    print_success(f"  {pkg}")
                else:
                    print_warning(f"  {pkg} not in requirements")
                    warnings.append(f"Missing {pkg} in requirements")
    else:
        print_error("requirements.txt not found")
        errors.append("requirements.txt missing")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Verification Summary")
    print("="*60 + "\n")
    
    if not errors and not warnings:
        print_success("🎉 All checks passed! Setup is complete!")
        print_info("\nNext steps:")
        print("  1. Start MongoDB: mongod")
        print("  2. Start backend: python -m uvicorn app.main:app --reload")
        print("  3. Start frontend: cd ../frontend && npm run dev")
        print("  4. Open browser: http://localhost:3000")
        return True
    
    if warnings:
        print_warning(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    
    if errors:
        print_error(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        print_info("\nPlease fix the errors above before starting the application.")
        return False
    
    print_warning("\n⚠️  Setup has warnings but should work.")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(verify_setup())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Verification cancelled")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nVerification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
