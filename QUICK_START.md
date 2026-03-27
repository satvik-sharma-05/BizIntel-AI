# ⚡ BizIntel AI - Quick Start

## 🎯 Deploy in 30 Minutes (FREE)

### Step 1: Databases (15 min)
```
MongoDB Atlas → Sign up → Create M0 FREE cluster → Get connection string
Neo4j Aura → Sign up → Create FREE instance → Save credentials
```

### Step 2: Backend (10 min)
```
Render.com → New Web Service → Connect GitHub → Select BizIntel-AI
Root: backend | Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Add environment variables → Deploy
```

### Step 3: Frontend (5 min)
```
Vercel.com → Import Project → Select BizIntel-AI
Root: frontend | Framework: Next.js
Add: NEXT_PUBLIC_API_URL=your_render_url
Deploy
```

## 📋 Environment Variables Needed

**Backend (Render):**
```bash
MONGODB_URL=mongodb+srv://...
NEO4J_URI=neo4j+s://...
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_API_KEY=sk-...
JWT_SECRET=random_secret_key
```

**Frontend (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

## 🔑 Get API Keys

1. **OpenRouter:** https://openrouter.ai (Free credits)
2. **OpenAI:** https://platform.openai.com ($5 free credit)

## ✅ Test Deployment

1. Visit your Vercel URL
2. Register account
3. Create business
4. Test chat: "What is my business?"

## 💰 Cost

**FREE** except API usage (~$2-5/month)

## 📖 Full Guide

See **FREE_DEPLOYMENT.md** for detailed step-by-step instructions.

---

**Your app will be live at:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.onrender.com`
