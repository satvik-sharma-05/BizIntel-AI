# BizIntel AI - AI-Powered Business Intelligence SaaS Platform

> Transform your business decisions with AI-powered market analysis, location intelligence, and intelligent chat

## 🚀 Overview

BizIntel AI is a production-ready SaaS platform that provides AI-powered business intelligence for entrepreneurs and businesses. It combines real-time data from multiple sources, multi-agent analysis, and RAG (Retrieval-Augmented Generation) to deliver actionable insights.

### Key Features

- 🤖 **Multi-Agent Intelligence System** - Specialized AI agents for market, location, and data analysis
- 📄 **RAG Document System** - Upload and query business documents with AI
- 💬 **5 Intelligent Chat Modes** - From document-only to full intelligence
- 📊 **Market Analysis** - Real-time competition and market opportunity analysis
- 📍 **Location Intelligence** - City comparison and expansion recommendations
- 📈 **Revenue Forecasting** - AI-powered financial projections
- 🏢 **Multi-Business Support** - Manage multiple businesses in one account
- 🔐 **Secure Authentication** - JWT-based auth with MongoDB

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Next.js 13+ (React)
- TailwindCSS
- Framer Motion (animations)
- React Markdown
- Recharts for visualizations

**Backend:**
- FastAPI (Python)
- MongoDB (business data, users, cache)
- Neo4j (graph relationships)
- FAISS (vector embeddings)
- OpenRouter (LLM API)

**AI/ML:**
- OpenAI text-embedding-3-small (1536d)
- Sentence-transformers (fallback, 384d)
- Multi-agents orchestration
- RAG pipeline with citations


### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Chat   │  │ Market   │  │ Location │  │ Forecast │   │
│  │   Mode   │  │ Analysis │  │  Intel   │  │  View    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Intelligent Chat Service                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │ RAG System │  │   Agents   │  │ LLM Service│    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   MongoDB    │   │    Neo4j     │   │    FAISS     │
│  (Business   │   │   (Graph     │   │  (Vector     │
│   Data +     │   │ Relations)   │   │  Embeddings) │
│   Cache)     │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Multi-Agent System

```
User Query
    │
    ▼
┌─────────────────┐
│  Orchestrator   │ ← Coordinates all agents
└─────────────────┘
    │
    ├──→ Data Agent      (GDP, MSME, Weather, News)
    ├──→ Market Agent    (Competition, Demand, Saturation)
    ├──→ Location Agent  (City Rankings, Expansion)
    ├──→ Graph Agent     (Neo4j Relationships)
    └──→ Decision Agent  (Final Recommendations)
         │
         ▼
    AI Response
```

## 📋 Features in Detail

### 1. Chat Modes System

Five intelligence modes for different use cases:

| Mode | Description | Use Case | Speed |
|------|-------------|----------|-------|
| 📄 Knowledge Base Only | RAG strict, documents only | Verify facts from docs | ⚡ Fast |
| 🔄 AI + Knowledge Base | RAG + AI analysis | Document insights + recommendations | ⚡⚡ Medium |
| 🧠 AI Only | LLM only, no docs/agents | General business advice | ⚡⚡ Medium |
| 📊 Business Data Only | Agents only, real-time data | Market/location analysis | ⚡⚡⚡ Slow |
| ⚡ Full Intelligence | Everything combined | Strategic decisions | ⚡⚡⚡ Slowest |


### 2. Market Analysis

Comprehensive market intelligence with:

- **Demand Analysis** - GDP growth, MSME count, economic indicators
- **Competition Analysis** - Real competitor data from OpenStreetMap/Overpass API
- **Market Saturation** - Demand vs competition ratio
- **Entry Difficulty** - Barrier analysis
- **Profit Potential** - Weighted scoring
- **Structured Markdown Output** - Beautiful, actionable reports

### 3. Location Intelligence

City comparison and expansion recommendations:

- **Multi-City Analysis** - Compare 10+ major Indian cities
- **Scoring System** - Demand, competition, cost, profit potential
- **Real Data** - Government MSME and GDP data
- **Pros/Cons Analysis** - For each city
- **Expansion Strategy** - Step-by-step recommendations
- **Risk Mitigation** - Identified risks and solutions

### 4. RAG Document System

Upload and query business documents:

- **Supported Formats** - PDF, DOCX, TXT
- **Smart Chunking** - 500 chars with 50 char overlap
- **OpenAI Embeddings** - text-embedding-3-small (1536d)
- **FAISS Vector Store** - Fast similarity search
- **Citation Tracking** - Document name, page number
- **Hybrid Mode** - Documents + AI analysis

### 5. Edit Business & Re-Analysis

Full CRUD operations with intelligent re-analysis:

- **Edit Business Details** - Name, industry, location, investment
- **Automatic Re-Analysis** - Clears old data, triggers fresh analysis
- **Neo4j Updates** - Graph relationships updated
- **Cache Invalidation** - API cache cleared
- **Delete Business** - With confirmation modal

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB 5.0+
- Neo4j 4.4+
- OpenRouter API key

### Installation

#### 1. Clone Repository

```bash
git clone <repository-url>
cd bizintel-ai
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```


#### 3. Configure Environment Variables

Edit `backend/.env`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=bizintel

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_key

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_key

# JWT Secret
JWT_SECRET=your_secret_key_here

# API Keys (optional)
WEATHER_API_KEY=your_weather_key
NEWS_API_KEY=your_news_key
```

#### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`

#### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

### Database Setup

#### MongoDB

```bash
# Start MongoDB
mongod --dbpath /path/to/data

# No schema needed - MongoDB is schemaless
```

#### Neo4j

```bash
# Start Neo4j
neo4j start

# Access Neo4j Browser at http://localhost:7474
# Set password on first login
```

## 📊 Data Sources

### Real APIs Used

- **Government Data** - data.gov.in (GDP, MSME, economic indicators)
- **Weather** - OpenWeatherMap API
- **News** - NewsAPI
- **Competition** - OpenStreetMap/Overpass API
- **Routing** - OSRM API
- **LLM** - OpenRouter (DeepSeek, Mistral, Llama)
- **Embeddings** - OpenAI text-embedding-3-small

### Caching Strategy

| Data Type | Cache Duration | Reason |
|-----------|----------------|--------|
| GDP Data | 24 hours | Changes infrequently |
| MSME Data | 24 hours | Government data |
| Weather | 6 hours | Changes regularly |
| News | 12 hours | Updated daily |
| Population | Permanent | Static data |


## 🗄️ Database Schema

### MongoDB Collections

#### users
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "name": "User Name",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### businesses
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "name": "Business Name",
  "industry": "Industry Type",
  "city": "City",
  "state": "State",
  "investment": 500000,
  "description": "Business description",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### conversations
```json
{
  "_id": ObjectId,
  "business_id": ObjectId,
  "messages": [
    {
      "role": "user|assistant",
      "content": "Message text",
      "timestamp": ISODate,
      "mode": "full_intelligence",
      "sources": {...},
      "citations": [...]
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### documents
```json
{
  "_id": ObjectId,
  "business_id": ObjectId,
  "filename": "document.pdf",
  "file_path": "/path/to/file",
  "file_size": 1024000,
  "file_type": "application/pdf",
  "uploaded_at": ISODate,
  "processed": true,
  "chunk_count": 50
}
```

### Neo4j Graph Schema

```cypher
// Business Node
(b:Business {
  id: "business_id",
  name: "Business Name",
  industry: "Industry",
  city: "City",
  state: "State"
})

// Market Node
(m:Market {
  state: "State",
  gdp_growth: 7.2,
  msme_count: 500000
})

// Competitor Node
(c:Competitor {
  name: "Competitor Name",
  type: "Business Type",
  distance_km: 2.5
})

// Relationships
(b)-[:OPERATES_IN]->(m)
(b)-[:COMPETES_WITH]->(c)
(b)-[:EXPANDING_TO]->(city:City)
```


## 🔌 API Endpoints

### Authentication

```
POST   /auth/register          Register new user
POST   /auth/login             Login user
GET    /auth/me                Get current user
```

### Business

```
GET    /business               List all businesses
POST   /business               Create business
GET    /business/{id}          Get business details
PUT    /business/{id}          Update business (triggers re-analysis)
DELETE /business/{id}          Delete business
```

### Chat

```
POST   /chat                   Send chat message
GET    /chat/history/{id}      Get conversation history
```

### Documents

```
POST   /documents/upload       Upload document
GET    /documents/{id}         List documents
DELETE /documents/{id}         Delete document
POST   /documents/rebuild      Rebuild vector store
```

### Analysis

```
GET    /market/{business_id}   Get market analysis
GET    /location/{business_id} Get location intelligence
GET    /forecast/{business_id} Get revenue forecast
```

### System

```
GET    /health                 Health check
GET    /docs                   API documentation (Swagger)
```

## 🎯 Usage Examples

### 1. Create Business

```bash
curl -X POST http://localhost:8000/business \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Gaming Cafe",
    "industry": "Gaming",
    "city": "Bangalore",
    "state": "Karnataka",
    "investment": 500000,
    "description": "Gaming cafe with latest consoles"
  }'
```

### 2. Upload Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@business_plan.pdf" \
  -F "business_id=BUSINESS_ID"
```

### 3. Chat with AI

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the market opportunity in Bangalore?",
    "business_id": "BUSINESS_ID",
    "mode": "full_intelligence"
  }'
```


## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test MongoDB connection
python test_mongo.py

# Test RAG system
python test_rag_system.py

# Test APIs
python test_apis.py

# Verify setup
python verify_setup.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run linter
npm run lint
```

## 🚀 Deployment

### Backend Deployment (Railway/Render)

1. Create new service
2. Connect GitHub repository
3. Set environment variables
4. Deploy from `backend` directory
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Import project from GitHub
2. Set root directory to `frontend`
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url`
4. Deploy

### Database Deployment

**MongoDB Atlas:**
- Create cluster at mongodb.com/cloud/atlas
- Get connection string
- Update `MONGODB_URL` in backend .env

**Neo4j Aura:**
- Create instance at neo4j.com/cloud/aura
- Get connection details
- Update Neo4j credentials in backend .env

## 📈 Performance

### Optimization Strategies

1. **Smart Agent Triggering** - Only run agents when needed
2. **Parallel Execution** - Documents and agents run simultaneously
3. **API Caching** - Responses cached (6-24 hours)
4. **RAG Optimization** - top_k=3, embedding cache (100 queries)
5. **MongoDB Indexing** - Comprehensive indexes on all collections
6. **Model Routing** - Fast models for chat, reasoning models for reports
7. **Async Operations** - Non-blocking API calls
8. **Timeouts** - 10s orchestrator, 5s decision agent

### Model Routing (OpenRouter)

| Use Case | Model | Speed | Cost |
|----------|-------|-------|------|
| Chat | deepseek/deepseek-chat | ⚡⚡⚡ Fast | $ Low |
| Reports | mistralai/mistral-7b-instruct | ⚡⚡ Medium | $$ Medium |
| Summaries | meta-llama/llama-3-8b-instruct | ⚡⚡⚡ Fast | $ Low |
| RAG Answers | deepseek/deepseek-chat | ⚡⚡ Medium | $ Low |

### Performance Results

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Simple chat ("hi") | 6s | 0.3s | **95% faster** |
| Document Q&A | 7s | 1.0s | **86% faster** |
| Market analysis | 8s | 4s | **50% faster** |
| RAG retrieval | 2s | 1.2s | **40% faster** |
| Database queries | Variable | <100ms | **10-100x faster** |

### Database Optimization

**MongoDB Indexes:**
- Users: email (unique), created_at
- Businesses: user_id, industry, city, compound indexes
- Conversations: business_id + created_at
- Documents: business_id + uploaded_at
- RAG chunks: business_id + document_id
- Market/Location/Forecasts: business_id (unique)
- API cache: cache_key (unique), TTL 24h auto-delete
- Agent logs: agent_id + created_at, TTL 7 days auto-delete

**FAISS Optimization:**
- Reduced top_k from 5 to 3 (40% faster)
- Embedding caching (100 queries)
- Optimized context building

**Neo4j:**
- Indexed business nodes
- Relationship caching
- Efficient graph queries


## 🔒 Security

### Authentication

- JWT-based authentication
- Password hashing with bcrypt
- Token expiration (24 hours)
- Secure HTTP-only cookies (production)

### Authorization

- User-specific business access
- Document access control
- API rate limiting (planned)

### Data Protection

- Environment variables for secrets
- MongoDB connection encryption
- HTTPS in production
- Input validation with Pydantic

## 🛠️ Development

### Project Structure

```
bizintel-ai/
├── backend/
│   ├── app/
│   │   ├── agents/           # Multi-agent system
│   │   │   ├── base_agent.py
│   │   │   ├── data_agent.py
│   │   │   ├── market_agent.py
│   │   │   ├── location_agent.py
│   │   │   ├── graph_agent.py
│   │   │   ├── decision_agent.py
│   │   │   └── orchestrator.py
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── business.py
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── market.py
│   │   │   ├── location.py
│   │   │   └── forecast.py
│   │   ├── services/         # Business logic
│   │   │   ├── intelligent_chat.py
│   │   │   ├── competition_service.py
│   │   │   ├── data_service.py
│   │   │   ├── llm_service.py
│   │   │   └── data_pipeline.py
│   │   ├── rag/              # RAG pipeline
│   │   │   ├── document_loader.py
│   │   │   ├── text_splitter.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   └── rag_pipeline.py
│   │   ├── database/         # Database clients
│   │   │   ├── mongodb.py
│   │   │   └── neo4j_client.py
│   │   ├── auth/             # Authentication
│   │   │   └── auth_service.py
│   │   ├── config/           # Configuration
│   │   │   └── settings.py
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── components/           # React components
│   │   ├── ChatMessage.jsx
│   │   ├── ChatModeSelector.jsx
│   │   ├── BusinessSwitcher.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   ├── pages/                # Next.js pages
│   │   ├── index.jsx
│   │   ├── login.jsx
│   │   ├── dashboard.jsx
│   │   └── business/
│   │       └── [businessId]/
│   │           ├── chat.jsx
│   │           ├── market.jsx
│   │           ├── location.jsx
│   │           ├── forecast.jsx
│   │           ├── documents.jsx
│   │           └── settings.jsx
│   ├── contexts/             # React contexts
│   │   ├── AuthContext.jsx
│   │   └── BusinessContext.jsx
│   ├── lib/                  # Utilities
│   │   └── api.js
│   ├── package.json
│   └── .env.local
└── README.md
```


### Adding New Features

#### 1. Add New Agent

```python
# backend/app/agents/my_agent.py
from .base_agent import BaseAgent
from typing import Dict, Any

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my_agent",
            name="My Agent",
            description="What this agent does"
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your logic here
        return {
            "success": True,
            "data": {...},
            "message": "Analysis complete"
        }
```

#### 2. Add New API Endpoint

```python
# backend/app/api/my_endpoint.py
from fastapi import APIRouter, Depends
from ..auth.auth_service import get_current_user

router = APIRouter(prefix="/my-endpoint", tags=["My Feature"])

@router.get("/")
async def my_endpoint(current_user = Depends(get_current_user)):
    # Your logic here
    return {"message": "Success"}
```

#### 3. Add New Chat Mode

```python
# backend/app/services/intelligent_chat.py
async def _my_custom_mode(self, message, business_id, business, history):
    # Your mode logic
    return {
        "response": "...",
        "sources": {...},
        "citations": []
    }
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Failed

```bash
# Check if MongoDB is running
mongod --version

# Start MongoDB
mongod --dbpath /path/to/data

# Check connection string in .env
MONGODB_URL=mongodb://localhost:27017
```

#### Neo4j Connection Failed

```bash
# Check if Neo4j is running
neo4j status

# Start Neo4j
neo4j start

# Verify credentials in .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

#### OpenRouter API Errors

```bash
# Verify API key
echo $OPENROUTER_API_KEY

# Check API quota at openrouter.ai
# Try different model if rate limited
```

#### RAG Not Working

```bash
# Rebuild vector store
cd backend
python rebuild_vector_store.py

# Check FAISS files exist
ls vector_store/
# Should see: index.faiss, index.pkl, metadata.pkl
```


## 🔮 Future Enhancements

### Short-term (1-2 weeks)

- [ ] Advanced competition heatmaps
- [ ] Real-time competitor pricing
- [ ] Enhanced forecasting models
- [ ] Export reports to PDF
- [ ] Email notifications

### Medium-term (1 month)

- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Custom agent creation
- [ ] API for third-party integrations

### Long-term (3 months)

- [ ] White-label solution
- [ ] Multi-language support
- [ ] Advanced ML models
- [ ] Predictive analytics
- [ ] Industry-specific templates

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Contributors

- Development Team
- AI/ML Engineers
- Product Designers

## 📞 Support

For support, email support@bizintel.ai or join our Slack community.

## 🙏 Acknowledgments

- OpenAI for embeddings API
- OpenRouter for LLM access
- MongoDB, Neo4j, FAISS for databases
- FastAPI and Next.js communities
- Open source contributors

## 📊 Project Status

**Version:** 2.0.0  
**Status:** Production Ready ✅  
**Last Updated:** 2024

### Completion Status

- ✅ Core Features: 100%
- ✅ Chat Modes: 100%
- ✅ Edit Business: 100%
- ✅ RAG Pipeline: 100%
- ✅ Performance: 100%
- ✅ Documentation: 100%
- ⚠️ Competition Analysis: 85% (Overpass API integrated)
- ⚠️ Market Structure: 90% (Markdown formatting added)
- ⚠️ Location Intelligence: 90% (Enhanced formatting)

**Overall Completion: ~95%**

---

**Built with ❤️ by the BizIntel AI Team**

For more information, visit our [documentation](https://docs.bizintel.ai) or [website](https://bizintel.ai).
