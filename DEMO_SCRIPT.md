# 🎬 Arkham AI - Live Demo Script

## ✅ Pre-Demo Checklist

- [x] Frontend running at http://localhost:3000
- [x] Backend deployed at https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app
- [x] Backend health check passing
- [x] Integration tested and working

## 🎯 Demo Flow

### Step 1: Open Frontend (30 seconds)
**Action:** Open browser to `http://localhost:3000`

**What to say:**
> "Welcome to Arkham AI, an autonomous supply chain rerouting agent. This system monitors geopolitical risks and trade disruptions in real-time, then automatically reroutes shipments to safer routes."

**What you'll see:**
- Landing page or onboarding screen
- Clean, modern interface

---

### Step 2: Complete Onboarding (1 minute)
**Action:** Fill out the onboarding form

**Fill in:**
- **Product:** "High-Performance Semiconductors"
- **Origin Port:** Select "Port of Taipei, Taiwan"
- **Destination Port:** Select "Port of Los Angeles, USA"
- Click **"Save & Go to Dashboard"**

**What to say:**
> "I'm configuring a shipment from Taiwan to Los Angeles, representing a typical semiconductor supply chain route. This is a critical trade route that's vulnerable to geopolitical tensions."

**What you'll see:**
- Dashboard loads
- Shipment details displayed
- Route map showing all routes
- All routes showing low risk (~10-15%)

---

### Step 3: Initial State (30 seconds)
**Action:** Point out the dashboard features

**What to say:**
> "Initially, all routes show low risk levels. The system is monitoring trade news, political instability, and port congestion data in real-time. Notice the route map showing our primary route and several alternatives."

**What you'll see:**
- Route Analysis section
- All routes: 10-15% risk (green badges)
- Route map with all routes displayed
- Shipment details panel

---

### Step 4: Simulate Disruption (2 minutes)
**Action:** Click the red **"Simulate Disruption Event"** button

**What to say:**
> "Now I'll simulate a disruption - new tariffs on Taiwan exports. Watch as the system automatically responds: it detects the disruption, assesses risk for all routes, uses AI to analyze alternatives, and automatically selects the best route."

**What happens:**
1. ✅ System fetches real-time risk data from backend
2. ✅ Primary route risk increases to ~78% (HIGH RISK)
3. ✅ Alternative routes get assessed with different scores
4. ✅ AI agent analyzes routes and provides recommendation
5. ✅ Best route automatically selected

**What you'll see:**
- Loading indicator
- Risk scores updating
- Routes changing colors (green → yellow → red)
- Notification appearing

---

### Step 5: View Results (2 minutes)
**Action:** Point out the results

**What to say:**
> "Notice how each route now has different risk scores based on their waypoints and regions. The primary route shows 78% risk - that's critical. The AI agent analyzed all alternatives and recommended rerouting through Vietnam, which reduces risk to 32% - a 46% reduction!"

**What you'll see:**

**Route Analysis:**
- **Primary Route:** 🔴 **78% RISK** (HIGH RISK - red badge)
- **Vietnam Route:** 🟡 **32% RISK** (LOW RISK - yellow/green badge) ✅ SELECTED
- **Japan Route:** 🟡 **45% RISK** (MEDIUM RISK - yellow badge)
- **Singapore Route:** 🟡 **50% RISK** (MEDIUM RISK - yellow badge)
- **Shanghai Route:** 🟡 **35% RISK** (LOW RISK - yellow/green badge)

**AI Recommendation:**
- Appears in "Disruption Analysis" section
- Intelligent explanation of why Vietnam route is best
- Mentions risk reduction, cost/time tradeoffs

**Route Map:**
- Active route highlighted in cyan
- Risk markers displayed
- Route automatically switched to Vietnam

**Risk Breakdown:**
- Congestion: X%
- Tariffs: X%
- Political Unrest: X%

---

### Step 6: Highlight Key Features (1 minute)
**Action:** Point out the key features

**What to say:**
> "This demonstrates several key capabilities: First, real-time risk assessment - each route gets evaluated with actual data from multiple sources. Second, AI-powered recommendations - the system uses Google's Gemini 2.0 Flash model to analyze routes intelligently. Third, automatic route selection - the system automatically chooses the best route without manual intervention. And finally, dynamic updates - notice how the ETA adjusted based on the route change."

**Features to highlight:**
1. ✅ **Different Risk Scores** - Each route has unique risk based on waypoints
2. ✅ **AI Recommendations** - Intelligent analysis from backend
3. ✅ **Automatic Selection** - Best route chosen automatically
4. ✅ **Real-Time Data** - Actual risk data from APIs
5. ✅ **Visual Map** - Google Maps integration
6. ✅ **Dynamic Updates** - ETA and route updates automatically

---

### Step 7: Closing (30 seconds)
**Action:** Summarize the demo

**What to say:**
> "This demonstrates how Arkham AI provides autonomous, intelligent supply chain management. The system continuously monitors risks, uses AI to make decisions, and automatically reroutes shipments when necessary - all in real-time. This reduces supply chain disruptions and protects critical shipments from geopolitical risks."

---

## 🎯 Key Points to Emphasize

1. **Autonomous Operation** - System works automatically
2. **AI-Powered** - Uses Google Gemini for intelligent analysis
3. **Real-Time** - Monitors and responds to disruptions immediately
4. **Intelligent Routing** - Considers risk, cost, and time
5. **Visual Dashboard** - Easy to understand and monitor

## 📊 Expected Results

### Before Disruption:
```
Primary Route:        10-15% risk (🟢 LOW)
Vietnam Route:       10-15% risk (🟢 LOW)
Japan Route:         10-15% risk (🟢 LOW)
Singapore Route:     10-15% risk (🟢 LOW)
Shanghai Route:      10-15% risk (🟢 LOW)
```

### After Disruption:
```
Primary Route:        70-80% risk (🔴 HIGH) ⚠️
Vietnam Route:        30-35% risk (🟡 LOW) ✅ BEST
Japan Route:          40-50% risk (🟡 MEDIUM)
Singapore Route:      45-55% risk (🟡 MEDIUM)
Shanghai Route:       30-40% risk (🟡 LOW)
```

## 🔧 Troubleshooting

### If routes show same risk:
- Wait a few seconds for backend to process
- Check browser console for errors
- Verify backend is responding

### If AI recommendation doesn't appear:
- Check it appears in "Disruption Analysis" section
- May show fallback recommendation if AI unavailable
- Check backend logs for AI agent status

### If map doesn't load:
- Check Google Maps API key is configured
- May take a few seconds to load
- Check browser console for errors

## 🎉 Success Indicators

✅ Routes show **different** risk scores (not all 10%)
✅ Primary route shows **HIGH RISK** (red badge)
✅ Alternative routes show **varying** risk scores
✅ AI recommendation appears in disruption analysis
✅ Best route is **automatically selected**
✅ Route map updates with new active route
✅ ETA updates based on route change
✅ Risk reduction percentage displayed

---

## 🚀 Ready to Demo!

Open **http://localhost:3000** and follow the steps above!

