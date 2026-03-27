<div align="center">

# 🚀 BizIntel AI

### *Intelligent Business Decision Platform*

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Visit_Now-blue?style=for-the-badge)](https://biz-intel-ai-two.vercel.app)
[![API Docs](https://img.shields.io/badge/📚_API_Docs-Swagger-green?style=for-the-badge)](https://bizintel-backend-xb1r.onrender.com/docs)
[![Backend](https://img.shields.io/badge/⚡_Backend-FastAPI-teal?style=for-the-badge)](https://bizintel-backend-xb1r.onrender.com)

*Empowering businesses with AI-driven insights, market analysis, and intelligent document processing*

[Features](#-features) • [Tech Stack](#-tech-stack) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API](#-api-endpoints)

</div>

---

## ✨ Features

### 🤖 **Hybrid RAG System**
- **Multi-Database Intelligence**: FAISS + BM25 + Neo4j + MongoDB working together
- **Smart Retrieval**: 40% semantic (FAISS) + 30% keyword (BM25) + 30% graph (Neo4j)
- **Knowledge Graph**: Entity extraction and relationship mapping
- **Document Modes**: Document-only or hybrid AI analysis

### 📊 **Business Intelligence**
- **Market Analysis**: Industry trends, competition, and opportunities
- **Location Intelligence**: GDP, demographics, and economic indicators
- **Revenue Forecasting**: AI-powered financial projections
- **Risk Assessment**: Comprehensive business risk analysis

### 📄 **Document Processing**
- **Multi-Format Support**: PDF, DOCX, TXT
- **Real-time Processing**: Background task with live status updates
- **Smart Chunking**: Optimized text splitting with overlap
- **Citation Tracking**: Source attribution for all answers

### 💬 **Intelligent Chat**
- **Context-Aware**: Remembers conversation history
- **Multi-Agent System**: Specialized agents for different tasks
- **Beautiful Responses**: Markdown formatting with code blocks
- **Source Citations**: Links to original documents

---

## 🛠️ Tech Stack

<div align="center">

### Frontend
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat-square&logo=tailwind-css)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-Animations-ff69b4?style=flat-square)

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-green?style=flat-square)

### Databases
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb)
![Neo4j](https://img.shields.io/badge/Neo4j-Aura-008CC1?style=flat-square&logo=neo4j)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=flat-square)

### AI & ML
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-purple?style=flat-square)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn)
![BM25](https://img.shields.io/badge/BM25-Search-red?style=flat-square)

</div>

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI[User Interface]
        Auth[Authentication]
        Chat[Chat Interface]
        Docs[Document Upload]
    end
    
    subgraph "Backend - FastAPI"
        API[REST API]
        Agents[AI Agents]
        RAG[Hybrid RAG]
    end
    
    subgraph "Databases"
        Mongo[(MongoDB<br/>Metadata)]
        Neo4j[(Neo4j<br/>Knowledge Graph)]
        FAISS[(FAISS<br/>Vectors)]
    end
    
    subgraph "External APIs"
        LLM[OpenRouter LLM]
        Weather[Weather API]
        News[News API]
        DataGov[Data.gov.in]
    end
    
    UI --> API
    Auth --> API
    Chat --> API
    Docs --> API
    
    API --> Agents
    API --> RAG
    
    RAG --> Mongo
    RAG --> Neo4j
    RAG --> FAISS
    
    Agents --> LLM
    Agents --> Weather
    Agents --> News
    Agents --> DataGov
```

### 🔄 Hybrid RAG Pipeline

```
Document Upload
    ↓
Text Extraction (PyPDF2, python-docx)
    ↓
Smart Chunking (500 chars, 50 overlap)
    ↓
Embedding Generation (HashingVectorizer)
    ↓
┌─────────────┬─────────────┬─────────────┐
│   FAISS     │    BM25     │   Neo4j     │
│  (Vectors)  │ (Keywords)  │   (Graph)   │
└─────────────┴─────────────┴─────────────┘
    ↓
MongoDB (Metadata)
    ↓
Query Processing
    ↓
┌─────────────────────────────────────────┐
│  Hybrid Search (40% + 30% + 30%)       │
│  • FAISS: Semantic similarity           │
│  • BM25: Keyword matching               │
│  • Neo4j: Entity relationships          │
└─────────────────────────────────────────┘
    ↓
Context Building
    ↓
LLM Generation (OpenRouter)
    ↓
Formatted Response + Citations
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB Atlas account
- Neo4j Aura account
- OpenRouter API key

### 1️⃣ Clone Repository
```bash
git clone https://github.com/satvik-sharma-05/BizIntel-AI.git
cd BizIntel-AI
```

### 2️⃣ Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
uvicorn app.main:app --reload --port 8000
```

### 3️⃣ Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with backend URL

# Run development server
npm run dev
```

### 4️⃣ Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📡 API Endpoints

### 🔐 Authentication
```http
POST   /api/register          # Register new user
POST   /api/login             # Login user
GET    /api/me                # Get current user
```

### 🏢 Business Management
```http
POST   /api/businesses        # Create business
GET    /api/businesses        # List businesses
GET    /api/businesses/{id}   # Get business details
PUT    /api/businesses/{id}   # Update business
DELETE /api/businesses/{id}   # Delete business
```

### 💬 Chat & RAG
```http
POST   /api/chat              # Send message
GET    /api/conversations     # List conversations
GET    /api/conversations/{id} # Get conversation
```

### 📄 Document Management
```http
POST   /api/documents/upload/{business_id}  # Upload document
GET    /api/documents/list/{business_id}    # List documents
GET    /api/documents/status/{doc_id}       # Check status
DELETE /api/documents/delete/{doc_id}       # Delete document
GET    /api/documents/stats/{business_id}   # Get statistics
```

### 🔧 Admin (RAG Management)
```http
GET    /api/admin/rag-status              # Check RAG status
POST   /api/admin/rebuild-rag-indexes     # Rebuild indexes
POST   /api/admin/clear-rag-indexes       # Clear indexes
```

### 📊 Analytics
```http
GET    /api/market/{business_id}          # Market analysis
GET    /api/location/{business_id}        # Location intelligence
GET    /api/forecast/{business_id}        # Revenue forecast
GET    /api/dashboard/{business_id}       # Dashboard data
```

---

## 🎯 Key Features Explained

### 🧠 Hybrid RAG System

**Why Hybrid?**
- **FAISS**: Understands semantic meaning ("activation function" ≈ "neural network layer")
- **BM25**: Finds exact keywords ("swish" matches "swish activation")
- **Neo4j**: Discovers relationships (documents mentioning same entities)

**Scoring Formula:**
```python
hybrid_score = 0.4 × faiss_score + 0.3 × bm25_score + 0.3 × neo4j_score
if entities_found:
    hybrid_score *= 1.1  # 10% boost
```

### 📊 Multi-Agent System

**Specialized Agents:**
- **Data Agent**: Fetches external data (weather, news, GDP)
- **Market Agent**: Analyzes market trends and competition
- **Location Agent**: Evaluates location suitability
- **Decision Agent**: Provides strategic recommendations
- **Graph Agent**: Queries Neo4j knowledge graph

### 🎨 Professional UI/UX

**Design Principles:**
- Clean, modern SaaS interface (inspired by Stripe, Vercel)
- Smooth animations with Framer Motion
- Responsive design for all devices
- Beautiful toast notifications
- Real-time status updates

---

## 🌐 Live Deployment

### Production URLs
- **Frontend**: https://biz-intel-ai-two.vercel.app
- **Backend**: https://bizintel-backend-xb1r.onrender.com
- **API Docs**: https://bizintel-backend-xb1r.onrender.com/docs

### Deployment Stack
- **Frontend**: Vercel (Free tier)
- **Backend**: Render (Free tier)
- **MongoDB**: Atlas (Free M0)
- **Neo4j**: Aura (Free tier)

---

## 📝 Environment Variables

### Backend (.env)
```env
# App
APP_NAME=BizIntel AI
DEBUG=False
FRONTEND_URL=https://biz-intel-ai-two.vercel.app
BACKEND_URL=https://bizintel-backend-xb1r.onrender.com

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/BizIntel

# Neo4j
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# OpenRouter (LLM)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=deepseek/deepseek-chat

# External APIs (Optional)
OPENWEATHER_API_KEY=xxxxx
NEWS_API_KEY=xxxxx
DATA_GOV_API_KEY=xxxxx

# RAG Configuration
VECTOR_DB_PATH=./vector_store
EMBEDDING_DIMENSION=384
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Satvik Sharma**

- GitHub: [@satvik-sharma-05](https://github.com/satvik-sharma-05)
- Project: [BizIntel AI](https://github.com/satvik-sharma-05/BizIntel-AI)

---

## 🙏 Acknowledgments

- **OpenRouter** for LLM API access
- **Render** for backend hosting
- **Vercel** for frontend hosting
- **MongoDB Atlas** for database
- **Neo4j Aura** for knowledge graph
- **FastAPI** for amazing Python framework
- **Next.js** for React framework

---

<div align="center">

### ⭐ Star this repo if you find it helpful!

[![GitHub stars](https://img.shields.io/github/stars/satvik-sharma-05/BizIntel-AI?style=social)](https://github.com/satvik-sharma-05/BizIntel-AI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/satvik-sharma-05/BizIntel-AI?style=social)](https://github.com/satvik-sharma-05/BizIntel-AI/network/members)

**Made with ❤️ and AI**

</div>
