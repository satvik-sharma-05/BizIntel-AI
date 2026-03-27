from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.neo4j_client import neo4j_client
from app.api import chat, dashboard, business, auth, system, agents, location, market, forecast, documents
import uvicorn

app = FastAPI(
    title=settings.APP_NAME,
    description="Business Decision Intelligence Platform - MongoDB Only",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup_event():
    try:
        await connect_mongodb()
        print("✅ MongoDB Connected")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
    
    try:
        neo4j_client.connect()
        print("✅ Neo4j Connected")
    except Exception as e:
        print(f"⚠️  Neo4j connection failed: {e}")
    
    print(f"🚀 {settings.APP_NAME} Backend Started")
    print(f"📍 Backend URL: {settings.BACKEND_URL}")
    print(f"📍 Frontend URL: {settings.FRONTEND_URL}")
    print(f"💾 Databases: MongoDB + Neo4j + FAISS")

# Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb()
    neo4j_client.close()
    print("👋 Backend Shutdown")

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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
