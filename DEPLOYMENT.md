# 🚀 BizIntel AI - Deployment Guide

## Quick Start - Push to GitHub

### 1. Initialize Git Repository

```bash
# Navigate to your project root
cd C:\satvik\hackethons\business

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: BizIntel AI - Multi-Agent Business Intelligence Platform"
```

### 2. Connect to GitHub

```bash
# Add GitHub remote
git remote add origin https://github.com/satvik-sharma-05/BizIntel-AI.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify Push

Visit: https://github.com/satvik-sharma-05/BizIntel-AI

---

## 📋 Pre-Deployment Checklist

### ✅ Security Check

- [x] `.env` added to `.gitignore`
- [x] No API keys in code
- [x] No passwords in code
- [x] `node_modules/` excluded
- [x] `venv/` excluded
- [x] `__pycache__/` excluded
- [x] Uploads folder excluded
- [x] Vector store excluded

### ✅ Files to Include

- [x] README.md (comprehensive documentation)
- [x] requirements.txt (Python dependencies)
- [x] package.json (Node dependencies)
- [x] .gitignore (exclusion rules)
- [x] Source code (backend + frontend)
- [x] Configuration examples

### ✅ Files to Exclude

- [x] .env (contains secrets)
- [x] node_modules/ (too large)
- [x] venv/ (environment specific)
- [x] uploads/ (user data)
- [x] vector_store/ (generated files)
- [x] __pycache__/ (Python cache)

---

## 🌐 Deploy to Production

### Option 1: Deploy Backend to Railway

1. **Create Railway Account**
   - Visit: https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `BizIntel-AI` repository

3. **Configure Backend Service**
   ```
   Root Directory: backend
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   ```
   MONGODB_URL=your_mongodb_atlas_url
   NEO4J_URI=your_neo4j_aura_url
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   OPENROUTER_API_KEY=your_key
   OPENAI_API_KEY=your_key
   JWT_SECRET=your_secret_key
   WEATHER_API_KEY=your_key (optional)
   NEWS_API_KEY=your_key (optional)
   ```

5. **Deploy**
   - Railway will auto-deploy
   - Get your backend URL: `https://your-app.railway.app`

### Option 2: Deploy Backend to Render

1. **Create Render Account**
   - Visit: https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repository

3. **Configure Service**
   ```
   Name: bizintel-backend
   Root Directory: backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables** (same as Railway)

5. **Deploy**
   - Click "Create Web Service"
   - Get your backend URL

### Deploy Frontend to Vercel

1. **Create Vercel Account**
   - Visit: https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New..."
   - Select "Project"
   - Import `BizIntel-AI` repository

3. **Configure Project**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Add Environment Variable**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

5. **Deploy**
   - Click "Deploy"
   - Get your frontend URL: `https://your-app.vercel.app`

---

## 🗄️ Database Setup

### MongoDB Atlas (Free Tier)

1. **Create Account**
   - Visit: https://www.mongodb.com/cloud/atlas
   - Sign up for free

2. **Create Cluster**
   - Choose M0 (Free tier)
   - Select region closest to your users
   - Name: `bizintel-cluster`

3. **Create Database User**
   - Database Access → Add New User
   - Username: `bizintel`
   - Password: Generate secure password
   - Role: Read and write to any database

4. **Whitelist IP**
   - Network Access → Add IP Address
   - Allow access from anywhere: `0.0.0.0/0`
   - (For production, use specific IPs)

5. **Get Connection String**
   - Clusters → Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your password
   - Example: `mongodb+srv://bizintel:<password>@cluster0.xxxxx.mongodb.net/BizIntel?retryWrites=true&w=majority`

### Neo4j Aura (Free Tier)

1. **Create Account**
   - Visit: https://neo4j.com/cloud/aura
   - Sign up for free

2. **Create Instance**
   - Click "Create Instance"
   - Choose Free tier
   - Name: `bizintel-graph`
   - Region: Same as MongoDB

3. **Save Credentials**
   - Download credentials file
   - Save password securely

4. **Get Connection Details**
   ```
   URI: neo4j+s://xxxxx.databases.neo4j.io
   Username: neo4j
   Password: your_generated_password
   ```

---

## 🔑 API Keys Setup

### OpenRouter (LLM)

1. Visit: https://openrouter.ai
2. Sign up / Login
3. Go to Keys section
4. Create new API key
5. Copy key: `sk-or-v1-xxxxx`

### OpenAI (Embeddings)

1. Visit: https://platform.openai.com
2. Sign up / Login
3. Go to API Keys
4. Create new secret key
5. Copy key: `sk-xxxxx`

### OpenWeatherMap (Optional)

1. Visit: https://openweathermap.org/api
2. Sign up for free
3. Get API key from dashboard
4. Copy key

### NewsAPI (Optional)

1. Visit: https://newsapi.org
2. Sign up for free
3. Get API key
4. Copy key

---

## 🧪 Testing Deployment

### Test Backend

```bash
# Health check
curl https://your-backend-url.railway.app/health

# API docs
open https://your-backend-url.railway.app/docs
```

### Test Frontend

```bash
# Open in browser
open https://your-app.vercel.app

# Test login
# Test business creation
# Test chat
```

---

## 📊 Monitoring

### Railway Monitoring

- View logs in Railway dashboard
- Monitor CPU/Memory usage
- Check deployment status

### Vercel Monitoring

- View deployment logs
- Monitor build times
- Check analytics

### Database Monitoring

**MongoDB Atlas:**
- Metrics → View cluster metrics
- Monitor connections, operations, storage

**Neo4j Aura:**
- Metrics → View graph metrics
- Monitor queries, relationships

---

## 🔄 Continuous Deployment

### Automatic Deployment

Both Railway and Vercel support automatic deployment:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Auto-Deploy**
   - Railway detects changes → Builds → Deploys backend
   - Vercel detects changes → Builds → Deploys frontend

### Manual Deployment

**Railway:**
- Dashboard → Deployments → Redeploy

**Vercel:**
- Dashboard → Deployments → Redeploy

---

## 🐛 Troubleshooting

### Backend Issues

**MongoDB Connection Failed:**
```bash
# Check connection string
# Verify IP whitelist
# Check database user permissions
```

**Neo4j Connection Failed:**
```bash
# Verify URI format: neo4j+s://
# Check credentials
# Ensure instance is running
```

**OpenRouter API Errors:**
```bash
# Verify API key
# Check quota/credits
# Try different model
```

### Frontend Issues

**API Connection Failed:**
```bash
# Verify NEXT_PUBLIC_API_URL
# Check CORS settings in backend
# Ensure backend is running
```

**Build Errors:**
```bash
# Check Node version (16+)
# Clear .next folder
# npm install --force
```

---

## 📈 Scaling

### Backend Scaling

**Railway:**
- Upgrade to Pro plan
- Increase resources
- Add replicas

**Render:**
- Upgrade instance type
- Enable auto-scaling

### Database Scaling

**MongoDB Atlas:**
- Upgrade to M10+ cluster
- Enable sharding
- Add read replicas

**Neo4j Aura:**
- Upgrade instance size
- Optimize queries
- Add indexes

---

## 🔒 Security Best Practices

### Production Checklist

- [ ] Use HTTPS only
- [ ] Enable CORS properly
- [ ] Rate limit APIs
- [ ] Validate all inputs
- [ ] Use secure JWT secrets
- [ ] Rotate API keys regularly
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use environment variables
- [ ] Enable database encryption

### Environment Variables

**Never commit:**
- API keys
- Database passwords
- JWT secrets
- Service credentials

**Always use:**
- `.env` files locally
- Platform environment variables in production

---

## 📝 Post-Deployment

### Update README

Add deployment URLs to README:

```markdown
## 🌐 Live Demo

- **Frontend:** https://your-app.vercel.app
- **Backend API:** https://your-backend.railway.app
- **API Docs:** https://your-backend.railway.app/docs
```

### Share Project

1. Update GitHub repository description
2. Add topics/tags
3. Create releases
4. Share on social media
5. Add to portfolio

---

## 🎉 Success!

Your BizIntel AI platform is now live! 🚀

**Next Steps:**
1. Test all features in production
2. Monitor performance
3. Gather user feedback
4. Plan new features
5. Scale as needed

---

**Need Help?**
- Check logs in Railway/Vercel dashboard
- Review MongoDB Atlas metrics
- Test API endpoints with Postman
- Check browser console for errors

**Happy Deploying! 🎊**
