# 🚀 BizIntel AI - Free Tier Deployment Guide

Deploy your entire BizIntel AI platform for **FREE** using:
- **Render** (Backend) - Free tier
- **Vercel** (Frontend) - Free tier  
- **MongoDB Atlas** (Database) - Free tier (512MB)
- **Neo4j Aura** (Graph DB) - Free tier (50MB)

---

## 📋 Prerequisites

- GitHub account
- OpenRouter API key (get free credits at https://openrouter.ai)
- OpenAI API key (for embeddings - $5 credit on signup)

---

## Step 1: Setup Databases (15 minutes)

### A. MongoDB Atlas (Free 512MB)

1. **Sign up:** https://www.mongodb.com/cloud/atlas/register
2. **Create Free Cluster:**
   - Click "Build a Database"
   - Choose "M0 FREE" tier
   - Select region closest to you
   - Cluster name: `bizintel-cluster`
   - Click "Create"

3. **Create Database User:**
   - Security → Database Access → Add New User
   - Username: `bizintel`
   - Password: Click "Autogenerate Secure Password" (save it!)
   - Database User Privileges: "Read and write to any database"
   - Click "Add User"

4. **Allow Network Access:**
   - Security → Network Access → Add IP Address
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

5. **Get Connection String:**
   - Database → Connect → Drivers
   - Copy connection string
   - Replace `<password>` with your saved password
   - Example: `mongodb+srv://bizintel:YOUR_PASSWORD@bizintel-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - **Save this!** You'll need it later

### B. Neo4j Aura (Free 50MB)

1. **Sign up:** https://neo4j.com/cloud/aura-free/
2. **Create Free Instance:**
   - Click "Create Instance"
   - Instance name: `bizintel-graph`
   - Region: Same as MongoDB
   - Click "Create"

3. **Save Credentials:**
   - **IMPORTANT:** Download the credentials file immediately
   - Save the password - you can't retrieve it later!
   - Connection URI: `neo4j+s://xxxxx.databases.neo4j.io`
   - Username: `neo4j`
   - Password: (from downloaded file)

---

## Step 2: Deploy Backend to Render (10 minutes)

### A. Create Render Account

1. Go to: https://render.com
2. Sign up with GitHub

### B. Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `BizIntel-AI`
3. Configure:
   ```
   Name: bizintel-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Free Plan** (scroll down)

### C. Add Environment Variables

Click "Advanced" → Add Environment Variables:

```bash
# MongoDB (from Step 1A)
MONGODB_URL=mongodb+srv://bizintel:YOUR_PASSWORD@bizintel-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Neo4j (from Step 1B)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# OpenRouter (get from https://openrouter.ai)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# OpenAI (get from https://platform.openai.com)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# JWT Secret (generate random string)
JWT_SECRET=your_random_secret_key_here_make_it_long_and_secure

# Optional APIs (can skip for now)
WEATHER_API_KEY=
NEWS_API_KEY=

# App Settings
DEBUG=False
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://bizintel-backend.onrender.com
```

**Generate JWT Secret:**
```bash
# Run this in terminal:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment
7. **Save your backend URL:** `https://bizintel-backend.onrender.com`

### D. Test Backend

Once deployed, visit:
- Health check: `https://bizintel-backend.onrender.com/health`
- API docs: `https://bizintel-backend.onrender.com/docs`

---

## Step 3: Deploy Frontend to Vercel (5 minutes)

### A. Create Vercel Account

1. Go to: https://vercel.com
2. Sign up with GitHub

### B. Import Project

1. Click "Add New..." → "Project"
2. Import `BizIntel-AI` repository
3. Configure:
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

### C. Add Environment Variable

Click "Environment Variables":

```bash
NEXT_PUBLIC_API_URL=https://bizintel-backend.onrender.com
```

**IMPORTANT:** Use your actual Render backend URL from Step 2!

4. Click "Deploy"
5. Wait 2-3 minutes
6. **Save your frontend URL:** `https://your-app.vercel.app`

### D. Update Backend Environment

Go back to Render → bizintel-backend → Environment:
- Update `FRONTEND_URL` to your Vercel URL
- Click "Save Changes"
- Backend will auto-redeploy

---

## Step 4: Test Your Deployment (5 minutes)

### A. Open Your App

Visit your Vercel URL: `https://your-app.vercel.app`

### B. Create Account

1. Click "Register"
2. Enter email and password
3. Create account

### C. Create Business

1. Click "Create Business"
2. Fill in details:
   - Name: Test Business
   - Industry: Food & Beverage
   - City: Bangalore
   - State: Karnataka
   - Investment: 500000

### D. Test Features

1. **Dashboard** - Should load business overview
2. **Market Analysis** - Click "Analyze Market"
3. **Chat** - Ask: "What is my business?"
4. **Documents** - Upload a PDF (optional)

---

## 🎉 Success!

Your BizIntel AI is now live on free tier!

**Your URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://bizintel-backend.onrender.com`
- API Docs: `https://bizintel-backend.onrender.com/docs`

---

## ⚠️ Free Tier Limitations

### Render Free Tier:
- ✅ 750 hours/month (enough for 24/7)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes 30-60 seconds
- ✅ 512MB RAM
- ✅ Shared CPU

### Vercel Free Tier:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Always fast (no spin-down)
- ✅ Automatic HTTPS

### MongoDB Atlas Free:
- ✅ 512MB storage
- ✅ Shared cluster
- ✅ Enough for ~1000 businesses

### Neo4j Aura Free:
- ✅ 50MB storage
- ✅ 50,000 nodes
- ✅ Enough for testing

---

## 🔧 Troubleshooting

### Backend Not Working

**Check Render Logs:**
1. Render Dashboard → bizintel-backend → Logs
2. Look for errors

**Common Issues:**
- MongoDB connection failed → Check connection string
- Neo4j connection failed → Check URI format (must be `neo4j+s://`)
- OpenRouter API error → Check API key and credits

### Frontend Not Connecting

**Check Environment Variable:**
1. Vercel Dashboard → Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Redeploy if changed

### Slow First Load

This is normal on Render free tier:
- Backend spins down after 15 min inactivity
- First request wakes it up (30-60 seconds)
- Subsequent requests are fast

**Solution:** Keep backend alive with uptime monitor (optional):
- Use https://uptimerobot.com (free)
- Ping your backend every 5 minutes

---

## 📊 Monitor Your App

### Render Dashboard
- View logs
- Monitor CPU/Memory
- Check deployment status

### Vercel Dashboard  
- View deployment logs
- Monitor bandwidth usage
- Check build times

### MongoDB Atlas
- Database → Metrics
- Monitor storage usage
- View connection count

### Neo4j Aura
- Instance → Metrics
- Monitor query performance
- Check storage usage

---

## 🚀 Upgrade Later (Optional)

When you need more:

**Render Pro ($7/month):**
- No spin-down
- More RAM
- Faster CPU

**MongoDB Atlas Shared ($9/month):**
- 2GB-5GB storage
- Better performance

**Neo4j Aura Pro ($65/month):**
- More storage
- Better performance

---

## 📝 Important Notes

1. **Keep API Keys Secret:**
   - Never commit `.env` to GitHub
   - Use environment variables only

2. **Backup Your Data:**
   - MongoDB Atlas has automatic backups
   - Export important data regularly

3. **Monitor Usage:**
   - Check MongoDB storage
   - Monitor API costs (OpenRouter/OpenAI)
   - Watch Vercel bandwidth

4. **Free Tier is Perfect For:**
   - Testing
   - Portfolio projects
   - Small user base (<100 users)
   - Demos

---

## 🎯 Next Steps

1. **Add Custom Domain (Optional):**
   - Vercel: Settings → Domains
   - Add your domain (free HTTPS)

2. **Share Your Project:**
   - Add to portfolio
   - Share on LinkedIn
   - Tweet about it

3. **Monitor Performance:**
   - Set up uptime monitoring
   - Check error logs regularly

4. **Improve Features:**
   - Add more agents
   - Enhance UI
   - Add analytics

---

## 💡 Tips for Free Tier

1. **Optimize Backend:**
   - Use caching (already implemented)
   - Minimize API calls
   - Optimize database queries

2. **Reduce Costs:**
   - Use cheaper LLM models
   - Cache API responses
   - Limit document uploads

3. **Keep It Running:**
   - Use uptime monitor
   - Or accept 30s cold start

4. **Monitor Limits:**
   - MongoDB: 512MB storage
   - Vercel: 100GB bandwidth/month
   - OpenRouter: Check credits

---

## 🆘 Need Help?

**Check Logs:**
- Render: Dashboard → Logs
- Vercel: Deployments → View Logs
- Browser: F12 → Console

**Common Solutions:**
- Clear browser cache
- Redeploy services
- Check environment variables
- Verify API keys

---

## ✅ Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Neo4j Aura instance created
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set
- [ ] Backend URL updated in frontend
- [ ] Frontend URL updated in backend
- [ ] Test account created
- [ ] Test business created
- [ ] All features tested

---

**Congratulations! Your BizIntel AI is live on free tier! 🎊**

**Total Cost: $0/month** (except API usage)

**Estimated API Costs:**
- OpenRouter: ~$1-5/month (light usage)
- OpenAI Embeddings: ~$0.50-2/month

**Total: ~$1.50-7/month for API usage only!**
