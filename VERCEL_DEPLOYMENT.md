# Deploying Arkham AI Frontend to Vercel

This guide will walk you through deploying the React frontend to Vercel.

## Prerequisites

- A GitHub account (your code is already at https://github.com/KrishD11/Arkham-AI.git)
- A Vercel account (sign up at https://vercel.com)
- Google Maps API Key (for the route map feature)

## Step-by-Step Deployment

### Step 1: Sign Up / Sign In to Vercel

1. Go to https://vercel.com
2. Click "Sign Up" or "Log In"
3. Sign in with your GitHub account (recommended for easy integration)

### Step 2: Import Your Project

1. Once logged in, click **"Add New..."** → **"Project"**
2. You'll see a list of your GitHub repositories
3. Find **"Arkham-AI"** and click **"Import"**

### Step 3: Configure Project Settings

Vercel will auto-detect your Vite project. Configure these settings:

#### Root Directory
- Set **Root Directory** to: `frontend`
- This tells Vercel to build from the `frontend/` folder

#### Build Settings (should auto-detect):
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### Environment Variables

Click **"Environment Variables"** and add:

1. **VITE_API_URL**
   - Value: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
   - This is your backend API URL (already deployed on Cloud Run)

2. **VITE_GOOGLE_MAPS_API_KEY** (Required for map functionality)
   - Value: Your Google Maps API Key
   - Get one at: https://console.cloud.google.com/google/maps-apis/credentials
   - Make sure to enable "Maps JavaScript API" and "Geocoding API"

3. **PERPLEXITY_API_KEY** (Optional - for AI analysis)
   - Value: Your Perplexity API key (if you have one)
   - Get one at: https://www.perplexity.ai/settings/api

### Step 4: Deploy

1. Click **"Deploy"** button
2. Wait for the build to complete (usually 1-2 minutes)
3. Once deployed, you'll get a URL like: `https://arkham-ai-xxxxx.vercel.app`

### Step 5: Verify Deployment

1. Visit your deployment URL
2. Test the application:
   - Login/Onboarding flow
   - Dashboard loads correctly
   - Route map displays (if Google Maps API key is set)
   - Backend API calls work

## Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Click **"Domains"**
3. Add your custom domain (e.g., `arkham-ai.com`)
4. Follow DNS configuration instructions

### Environment Variables for Production

Make sure all environment variables are set for **Production**, **Preview**, and **Development** environments:

- In Vercel Dashboard → Your Project → Settings → Environment Variables
- Set each variable for all environments

## Troubleshooting

### Build Fails

**Error: Module not found**
- Make sure `Root Directory` is set to `frontend`
- Check that `package.json` exists in the frontend folder

**Error: Build command failed**
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`

### Map Not Showing

- Verify `VITE_GOOGLE_MAPS_API_KEY` is set in Vercel environment variables
- Check browser console for API key errors
- Make sure Google Maps API is enabled in Google Cloud Console

### API Calls Failing

- Verify `VITE_API_URL` is correct
- Check CORS settings on your backend (should allow Vercel domain)
- Check browser console for CORS errors

### CORS Issues

If you see CORS errors, update your backend (`agent/main.py`) to allow Vercel domain:

```python
from flask_cors import CORS

# Allow Vercel domains
CORS(app, origins=[
    "https://your-app.vercel.app",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
    "http://localhost:3000"   # For local development
])
```

## Continuous Deployment

Once connected to GitHub, Vercel will automatically:
- Deploy on every push to `main` branch
- Create preview deployments for pull requests
- Rebuild on every commit

## Manual Deployment via CLI (Alternative)

If you prefer using the CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Project Structure for Vercel

```
frontend/
├── vercel.json          # Vercel configuration ✅
├── package.json         # Dependencies ✅
├── vite.config.ts       # Vite configuration ✅
├── index.html           # Entry point ✅
├── src/                 # Source files ✅
└── dist/                # Build output (generated)
```

## Quick Checklist

- [ ] Vercel account created
- [ ] GitHub repository connected
- [ ] Root directory set to `frontend`
- [ ] Environment variables configured:
  - [ ] `VITE_API_URL`
  - [ ] `VITE_GOOGLE_MAPS_API_KEY`
  - [ ] `PERPLEXITY_API_KEY` (optional)
- [ ] Build successful
- [ ] Site accessible at Vercel URL
- [ ] Map displays correctly
- [ ] API calls working

## Support

- Vercel Docs: https://vercel.com/docs
- Vite Deployment: https://vitejs.dev/guide/static-deploy.html#vercel
- Project Issues: Check GitHub repository issues

