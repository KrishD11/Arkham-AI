# Frontend Fixes & Google Maps Integration

## ✅ Fixed Issues

### 1. Frontend Now Pulls Data from Backend
- **Problem**: Frontend was only using mock data and only fetched from backend when disruption was triggered
- **Solution**: 
  - Added `useEffect` hook in `DashboardPage.tsx` that fetches data on component mount
  - Fetches risk data, assesses all routes, and updates risk profiles automatically
  - Shows connection status in event log

### 2. Google Maps Integration
- **Added**: `RouteMap` component using `@react-google-maps/api`
- **Features**:
  - Visualizes all routes (primary + alternatives)
  - Shows active route in cyan, alternatives in gray
  - Displays port markers with labels
  - Shows risk data points as markers on the map
  - Interactive map with zoom, satellite view, terrain options

### 3. Real-time Data Fetching
- Dashboard now automatically:
  - Checks backend health on load
  - Fetches risk data from backend
  - Assesses all route risks using backend API
  - Updates risk profiles with real data
  - Falls back gracefully to mock data if backend unavailable

## 🗺️ Google Maps Setup

### Get Google Maps API Key

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**: Use your existing `arkham-ai-477701` project
3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Enable "Maps JavaScript API"
   - Enable "Geocoding API" (for converting addresses to coordinates)
4. **Create API Key**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Restrict the key to:
     - Application restrictions: HTTP referrers
     - Add your domain: `localhost:3000`, `localhost:4173`, and your production domain
     - API restrictions: Restrict to "Maps JavaScript API" and "Geocoding API"

### Add API Key to Frontend

1. **Update `.env` file**:
   ```bash
   cd frontend
   echo "VITE_GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE" >> .env
   ```

2. **Or set in Vercel/Netlify**:
   - Add `VITE_GOOGLE_MAPS_API_KEY` as environment variable

## 📍 Port Coordinates

Currently using hardcoded coordinates for major ports:
- Port of Taipei, Taiwan: `25.0330, 121.5654`
- Port of Ho Chi Minh City, Vietnam: `10.7769, 106.7009`
- Port of Tokyo, Japan: `35.6762, 139.6503`
- Port of Los Angeles, USA: `33.7490, -118.2648`

**Future Enhancement**: Use Geocoding API to convert port names to coordinates dynamically.

## 🎯 Risk Data Visualization

Risk data points from backend are displayed as markers on the map:
- **Red markers**: High risk (severity > 0.7)
- **Orange markers**: Medium risk (severity 0.4-0.7)
- **Yellow markers**: Low risk (severity < 0.4)

Risk data includes:
- Location (latitude/longitude)
- Severity score
- Category (trade disruption, political unrest, etc.)
- Title/description

## 🔄 Data Flow

1. **On Dashboard Load**:
   ```
   DashboardPage mounts
   → Checks backend health
   → Fetches risk data (getAllRiskData)
   → Assesses primary route (assessRoute)
   → Assesses alternative routes (assessRoute for each)
   → Updates risk profiles
   → Displays on map
   ```

2. **On Disruption Trigger**:
   ```
   User clicks "Simulate Disruption"
   → Fetches latest risk data
   → Re-assesses routes
   → Optimizes routes (optimizeRoute)
   → Gets AI analysis
   → Updates map with new routes
   ```

## 🚀 Testing

1. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Check browser console** for:
   - Backend connection status
   - API calls being made
   - Risk data being loaded
   - Map rendering

3. **Verify**:
   - Map displays routes
   - Risk markers appear on map
   - Route risks update from backend
   - Active route highlighted in cyan

## 📝 Notes

- Map requires Google Maps API key to function
- Without API key, shows placeholder message
- Backend data fetching happens automatically on mount
- All API calls have error handling and fallbacks
- Map updates when route changes or disruption is triggered

