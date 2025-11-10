# Cloud Infrastructure Usage

## ✅ Currently Deployed on Google Cloud

### Backend (Google Cloud Run)
- **Service URL**: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
- **Status**: ✅ Running and accessible
- **Region**: `us-central1`
- **Project**: `arkham-ai-477701`

### Cloud Services Being Used

1. **Google Cloud Run** (Backend Hosting)
   - Serverless container platform
   - Auto-scaling based on traffic
   - Pay-per-use pricing
   - Currently deployed and running

2. **Google Cloud Build** (CI/CD)
   - Builds Docker images
   - Used during deployment

3. **Google Vertex AI** (AI/ML)
   - Configured for Gemini 2.0 Flash
   - Used for predictive scoring and AI analysis
   - Service account configured

4. **MongoDB Atlas** (Database)
   - Cloud-hosted MongoDB
   - Stores risk data, routes, assessments, executions, logs
   - Connected and operational

5. **Google Maps Platform** (Frontend)
   - Maps JavaScript API
   - Geocoding API
   - Used for route visualization

### What's NOT Using Cloud (Yet)

- **Frontend**: Currently running locally or needs deployment
  - Can deploy to:
    - Vercel (recommended)
    - Netlify
    - Firebase Hosting
    - Google Cloud Storage + Cloud CDN

### Cloud Costs

**Current Usage:**
- Cloud Run: Pay per request (free tier: 2M requests/month)
- Vertex AI: Pay per API call
- MongoDB Atlas: Free tier available (512MB)
- Google Maps: $200 free credit/month

**Estimated Monthly Cost**: ~$0-50 (depending on usage)

### Deployment Status

✅ **Backend**: Deployed and running on Cloud Run
⏳ **Frontend**: Needs deployment (currently local)

### To Deploy Frontend to Cloud

**Option 1: Vercel (Easiest)**
```bash
cd frontend
npx vercel --prod
```

**Option 2: Firebase Hosting**
```bash
cd frontend
firebase init hosting
firebase deploy --only hosting
```

**Option 3: Google Cloud Storage + CDN**
```bash
gsutil -m cp -r frontend/dist/* gs://arkham-ai-frontend/
```

