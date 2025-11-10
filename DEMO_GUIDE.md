# Arkham AI - Demo Guide

## 🎯 Quick Start Demo

### Prerequisites
- Backend deployed to Cloud Run: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
- Frontend built and ready to run

### Step 1: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal)

### Step 2: Demo Flow

#### 1. **Onboarding** (First Time)
- Open `http://localhost:5173`
- You'll see the onboarding page
- Select:
  - **Product**: "High-Performance Semiconductors" (or any product)
  - **Origin Port**: "Port of Taipei, Taiwan"
  - **Destination Port**: "Port of Los Angeles, USA"
- Click "Save & Go to Dashboard"

#### 2. **Dashboard View**
- You'll see:
  - Shipment details (ID, contents, origin, destination, ETA)
  - Route map showing all routes
  - Route Analysis section with all routes and their risk scores
  - Initially, all routes show low risk (~10-15%)

#### 3. **Simulate Disruption**
- Click the red **"Simulate Disruption Event"** button
- Watch the system:
  1. ✅ Fetch real-time risk data from backend
  2. ✅ Assess primary route risk (will increase to ~78%)
  3. ✅ Optimize all alternative routes
  4. ✅ Get AI recommendation from backend
  5. ✅ Automatically select best route
  6. ✅ Update risk profiles with different scores for each route

#### 4. **View Results**
- **Route Analysis** shows:
  - Primary route: **HIGH RISK** (78% - red badge)
  - Alternative routes with **DIFFERENT** risk scores:
    - Vietnam route: ~32% (yellow/green)
    - Japan route: ~45% (yellow)
    - Singapore route: ~50% (yellow)
    - Shanghai route: ~35% (yellow/green)
  
- **AI Recommendation** appears in the "Disruption Analysis" section
- **Best Route** is automatically selected (lowest risk)
- **Notification** shows risk reduction percentage

### Step 3: Key Features to Highlight

#### ✅ **Real-Time Risk Assessment**
- Each route gets assessed with real data
- Different risk scores based on waypoints/regions
- Risk breakdown: Congestion, Tariffs, Political Unrest

#### ✅ **AI-Powered Recommendations**
- Backend uses Google ADK Agent (Gemini 2.0 Flash)
- Analyzes route comparisons
- Provides intelligent recommendations

#### ✅ **Automatic Route Selection**
- System automatically selects best route
- Shows risk reduction
- Updates ETA based on route changes

#### ✅ **Visual Route Map**
- Google Maps integration
- Shows all routes with waypoints
- Highlights active route
- Displays risk markers

### Step 4: Test Different Scenarios

#### Test Route Assessment API Directly:
```bash
# Assess primary route
curl -X POST "https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/routes/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Port of Taipei, Taiwan",
    "destination": "Port of Los Angeles, USA",
    "route_id": "TW-LA-DIRECT"
  }'

# Optimize routes
curl -X POST "https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/routes/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Port of Taipei, Taiwan",
    "destination": "Port of Los Angeles, USA",
    "priority": "balanced"
  }'
```

### Step 5: Verify Backend Integration

#### Check Backend Health:
```bash
curl https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/health
```

#### Check MongoDB Connection:
```bash
curl https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/db/health
```

#### View Backend Logs:
```bash
gcloud run services logs read arkham-ai-agent --region us-central1 --limit 50
```

## 🎬 Demo Script

### Opening (30 seconds)
"Today I'll demonstrate Arkham AI, an autonomous supply chain rerouting agent that monitors geopolitical risks and automatically reroutes shipments to safer routes in real-time."

### Setup (30 seconds)
"Let me configure a shipment from Taiwan to Los Angeles. This represents a typical semiconductor supply chain route."

### Normal Operation (1 minute)
"Initially, all routes show low risk. The system is monitoring trade news, political instability, and port congestion data in real-time."

### Disruption Simulation (2 minutes)
"Now I'll simulate a disruption - new tariffs on Taiwan exports. Watch as the system:
1. Detects the disruption
2. Assesses risk for all routes
3. Uses AI to analyze alternatives
4. Automatically selects the best route"

### Results (1 minute)
"Notice how each route now has different risk scores based on their waypoints. The AI agent recommended rerouting through Vietnam, reducing risk from 78% to 32%. The system automatically updated the route and adjusted the ETA."

### Closing (30 seconds)
"This demonstrates how Arkham AI provides autonomous, intelligent supply chain management with real-time risk monitoring and automatic rerouting capabilities."

## 🔍 Troubleshooting

### Frontend not connecting to backend:
1. Check `.env` file has correct `VITE_API_URL`
2. Rebuild frontend: `npm run build`
3. Check browser console for CORS errors

### Routes showing same risk:
1. Check backend logs for errors
2. Verify route optimization endpoint is working
3. Check that waypoints are being passed correctly

### AI recommendation not showing:
1. Check backend logs for ADK agent errors
2. Verify Google Cloud credentials are set
3. Check fallback recommendation is working

### Map not loading:
1. Check `VITE_GOOGLE_MAPS_API_KEY` is set in `.env`
2. Verify Google Maps API is enabled
3. Check browser console for API errors

## 📊 Expected Results

### Before Disruption:
- Primary Route: 10-15% risk (green)
- All Alternative Routes: 10-15% risk (green)

### After Disruption:
- Primary Route: 70-80% risk (red) - HIGH RISK
- Vietnam Route: 30-35% risk (yellow/green) - LOW RISK ✅
- Japan Route: 40-50% risk (yellow) - MEDIUM RISK
- Singapore Route: 45-55% risk (yellow) - MEDIUM RISK
- Shanghai Route: 30-40% risk (yellow/green) - LOW RISK

### AI Recommendation:
Should provide a clear, intelligent recommendation explaining:
- Which route to use
- Why (risk reduction, cost/time tradeoffs)
- Key considerations

## 🚀 Production Deployment

### Frontend Deployment (Vercel):
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

### Or serve from backend:
The backend already serves static files from `frontend/dist` when deployed.

## 📝 Notes

- The demo uses real backend APIs
- Risk scores are calculated from real data sources (Trade.gov, ACLED, Port APIs)
- AI recommendations use Google ADK Agent (Gemini 2.0 Flash)
- All data is stored in MongoDB Atlas
- Routes are assessed with region-specific risk data

