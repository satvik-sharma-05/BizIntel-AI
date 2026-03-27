from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.neo4j_client import neo4j_client
from app.api import chat, dashboard, business, auth, system, agents, location, market, forecast, documents
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("=" * 80)
    print(f"🚀 {settings.APP_NAME} Backend Starting...")
    print(f"📍 Backend URL: {settings.BACKEND_URL}")
    print(f"📍 Frontend URL: {settings.FRONTEND_URL}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print("=" * 80)
    
    # Connect to databases
    try:
        await connect_mongodb()
        print("✅ MongoDB Connected")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed (will retry): {e}")
    
    try:
        neo4j_client.connect()
        if neo4j_client.connected:
            print("✅ Neo4j Connected")
    except Exception as e:
        print(f"⚠️  Neo4j connection failed (optional feature): {e}")
    
    print("=" * 80)
    print(f"✅ Server ready and listening")
    print(f"💾 Databases: MongoDB + Neo4j + FAISS")
    print(f"📡 Health check: {settings.BACKEND_URL}/health")
    print("=" * 80)
    
    yield  # Server runs here
    
    # Shutdown
    print("=" * 80)
    print("👋 Backend Shutting Down...")
    print("=" * 80)
    await close_mongodb()
    neo4j_client.close()
    print("✅ Shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    description="Business Decision Intelligence Platform - MongoDB Only",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow all origins for now (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(business.router, prefix="/api", tags=["Business"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(location.router, prefix="/api/location", tags=["Location"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "database": "MongoDB Only",
        "docs": f"{settings.BACKEND_URL}/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "MongoDB"}

# This block is only for local development
# On Render, uvicorn is started via the start command in render.yaml
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
