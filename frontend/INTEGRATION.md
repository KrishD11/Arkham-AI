# Frontend-Backend Integration Guide

## Overview
The frontend React application is now connected to the Arkham AI backend API running on Google Cloud Run.

## Setup

### 1. Environment Variables
Create a `.env` file in the `frontend/` directory:

```bash
# Backend API URL
VITE_API_URL=https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app

# For local development:
# VITE_API_URL=http://localhost:8080

# Optional: Perplexity API Key
# PERPLEXITY_API_KEY=your_key_here
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Run Development Server
```bash
npm run dev
```

The frontend will run on `http://localhost:3000` (or the next available port).

## API Integration

### Services
- **`services/apiService.ts`**: Main API service with all backend endpoints
- **`services/perplexityService.ts`**: AI analysis service (uses backend agent or Perplexity API)

### Key Features
1. **Risk Assessment**: Fetches real-time risk data from backend
2. **Route Optimization**: Uses backend to find optimal routes
3. **AI Analysis**: Uses backend agent for route recommendations
4. **Fallback Support**: Gracefully falls back to mock data if backend is unavailable

### API Endpoints Used
- `/api/health` - Health check
- `/api/data/all` - Fetch risk data
- `/api/routes/assess` - Assess route risk
- `/api/routes/optimize` - Optimize routes
- `/api/agent/query` - Query AI agent

## Development

### Backend Connection
The frontend automatically connects to the backend API configured in `VITE_API_URL`. If the backend is unavailable, the app will:
- Log warnings to console
- Use mock/fallback data
- Continue functioning with limited features

### Testing Backend Connection
You can test the backend connection by:
1. Opening browser DevTools console
2. Triggering a disruption event in the dashboard
3. Checking console logs for API calls

## Production Build

```bash
npm run build
```

The built files will be in `frontend/dist/`. You can deploy these to any static hosting service (Vercel, Netlify, etc.) or serve them alongside your backend.

## CORS
The backend has CORS enabled, so the frontend can make requests from any origin. For production, consider restricting CORS to your frontend domain.

