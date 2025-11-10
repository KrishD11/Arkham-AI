# Quick Demo Guide

## 🚀 Frontend is Running!

### Option 1: Local Preview (Currently Running)
The frontend preview server is running at:
**http://localhost:4173**

Open this URL in your browser to see the demo!

### Option 2: Deploy to Vercel (Production)

1. **Login to Vercel**:
   ```bash
   cd frontend
   npx vercel login
   ```

2. **Deploy**:
   ```bash
   npx vercel --prod
   ```

3. **Set Environment Variable** in Vercel Dashboard:
   - Go to your project → Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
   - Redeploy

### Option 3: Serve from Backend (Single Domain)

The backend has been updated to serve the frontend. To use this:

1. **Copy frontend build to backend**:
   ```bash
   cp -r frontend/dist agent/static
   ```

2. **Update backend to serve from static folder**:
   The backend will automatically serve the frontend from `/agent/static/`

3. **Deploy backend** (frontend will be included):
   ```bash
   ./deploy.sh
   ```

## 🎯 Demo Steps

1. **Open the frontend** (localhost:4173 or deployed URL)
2. **Go through onboarding**:
   - Enter product name
   - Select origin port
   - Select destination port
3. **Navigate to Dashboard**
4. **Click "Simulate Disruption Event"**
5. **Watch the AI**:
   - Fetch risk data from backend
   - Assess route risks
   - Optimize routes
   - Provide AI recommendations
   - Automatically reroute to safer path

## 🔗 Backend API

Backend is running at: **https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app**

Test endpoints:
- Health: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/health`
- Agent Info: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/agent/info`

## 📝 Notes

- Frontend connects to backend automatically via `VITE_API_URL`
- CORS is enabled on backend
- Frontend falls back to mock data if backend is unavailable
- All API calls are logged in browser console

