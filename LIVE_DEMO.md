# 🎬 Arkham AI - Live Demo

## ✅ Integration Status

- ✅ **Backend**: Deployed to Cloud Run
  - URL: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
  - Status: Running
  - Health: ✅ Healthy

- ✅ **Frontend**: Running locally
  - URL: `http://localhost:5173`
  - Status: Running
  - Backend Integration: ✅ Connected

## 🚀 Quick Start Demo

### Step 1: Open Frontend
```
http://localhost:5173
```

### Step 2: Complete Onboarding
1. **Product**: "High-Performance Semiconductors"
2. **Origin Port**: "Port of Taipei, Taiwan"
3. **Destination Port**: "Port of Los Angeles, USA"
4. Click **"Save & Go to Dashboard"**

### Step 3: View Initial State
- All routes show **low risk** (~10-15%)
- Route map displays all routes
- System is monitoring in real-time

### Step 4: Simulate Disruption
1. Click the red **"Simulate Disruption Event"** button
2. Watch the system:
   - ✅ Fetch real-time risk data
   - ✅ Assess primary route (risk increases to ~78%)
   - ✅ Optimize alternative routes
   - ✅ Get AI recommendation
   - ✅ Auto-select best route

### Step 5: View Results
- **Primary Route**: 🔴 **HIGH RISK** (78%)
- **Alternative Routes**: Different risk scores:
  - Vietnam: 🟡 ~32% (LOW RISK) ✅
  - Japan: 🟡 ~45% (MEDIUM RISK)
  - Singapore: 🟡 ~50% (MEDIUM RISK)
  - Shanghai: 🟡 ~35% (LOW RISK)
- **AI Recommendation**: Appears in disruption analysis
- **Best Route**: Automatically selected (Vietnam)

## 🎯 Key Features Demonstrated

### 1. Real-Time Risk Assessment
- Each route assessed with actual data
- Different scores based on waypoints/regions
- Risk breakdown: Congestion, Tariffs, Political Unrest

### 2. AI-Powered Recommendations
- Google ADK Agent (Gemini 2.0 Flash)
- Intelligent route analysis
- Clear, actionable recommendations

### 3. Automatic Route Selection
- System selects best route automatically
- Shows risk reduction percentage
- Updates ETA dynamically

### 4. Visual Route Map
- Google Maps integration
- All routes with waypoints
- Active route highlighted
- Risk markers displayed

## 📊 Expected Demo Flow

### Before Disruption:
```
Primary Route:        10-15% risk (🟢 LOW)
Vietnam Route:        10-15% risk (🟢 LOW)
Japan Route:          10-15% risk (🟢 LOW)
Singapore Route:      10-15% risk (🟢 LOW)
Shanghai Route:       10-15% risk (🟢 LOW)
```

### After Disruption:
```
Primary Route:        70-80% risk (🔴 HIGH) ⚠️
Vietnam Route:        30-35% risk (🟡 LOW) ✅ BEST
Japan Route:          40-50% risk (🟡 MEDIUM)
Singapore Route:      45-55% risk (🟡 MEDIUM)
Shanghai Route:       30-40% risk (🟡 LOW)
```

### AI Recommendation:
"Based on the risk assessment, I recommend rerouting via Vietnam. This route offers a significant risk reduction from 78% to 32% (46% reduction) while maintaining reasonable cost and time impacts. The Vietnam route avoids the high tariff risk affecting the direct Taiwan route and benefits from lower port congestion."

## 🔧 Troubleshooting

### If routes show same risk:
- Check browser console for errors
- Verify backend is responding
- Check network tab for API calls

### If AI recommendation doesn't appear:
- Check backend logs: `gcloud run services logs read arkham-ai-agent --region us-central1`
- Verify ADK agent is initialized
- Fallback recommendation should still appear

### If map doesn't load:
- Check `VITE_GOOGLE_MAPS_API_KEY` in `.env`
- Verify Google Maps API is enabled
- Check browser console for API errors

## 📝 Demo Script

**Opening (30s)**: "Today I'll demonstrate Arkham AI, an autonomous supply chain rerouting agent that monitors geopolitical risks and automatically reroutes shipments to safer routes in real-time."

**Setup (30s)**: "I've configured a shipment from Taiwan to Los Angeles, representing a typical semiconductor supply chain route."

**Normal Operation (1m)**: "Initially, all routes show low risk. The system is monitoring trade news, political instability, and port congestion data in real-time."

**Disruption (2m)**: "I'll simulate a disruption - new tariffs on Taiwan exports. Watch as the system detects the disruption, assesses risk for all routes, uses AI to analyze alternatives, and automatically selects the best route."

**Results (1m)**: "Notice how each route now has different risk scores based on their waypoints. The AI agent recommended rerouting through Vietnam, reducing risk from 78% to 32%. The system automatically updated the route and adjusted the ETA."

**Closing (30s)**: "This demonstrates how Arkham AI provides autonomous, intelligent supply chain management with real-time risk monitoring and automatic rerouting capabilities."

## 🎉 Success Indicators

✅ Routes show **different** risk scores (not all 10%)
✅ AI recommendation appears in disruption analysis
✅ Best route is automatically selected
✅ Risk reduction percentage is displayed
✅ Route map updates with new active route
✅ ETA updates based on route change

## 📞 Support

- Backend Logs: `gcloud run services logs read arkham-ai-agent --region us-central1 --follow`
- Frontend Console: Open browser DevTools (F12)
- API Health: `curl https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/health`

