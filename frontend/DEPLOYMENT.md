# Frontend Deployment Guide

## Quick Demo Options

### Option 1: Vercel (Recommended - Easiest)

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```
   
   Follow the prompts:
   - Link to existing project? No
   - Project name: arkham-ai-frontend
   - Directory: `./dist`
   - Override settings? No

3. **Set Environment Variable**:
   After deployment, go to Vercel dashboard → Settings → Environment Variables:
   - Add `VITE_API_URL` = `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`

4. **Redeploy** to apply environment variables:
   ```bash
   vercel --prod
   ```

### Option 2: Netlify

1. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy**:
   ```bash
   cd frontend
   netlify deploy --prod --dir=dist
   ```

3. **Set Environment Variable** in Netlify dashboard:
   - Site settings → Environment variables
   - Add `VITE_API_URL` = `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`

### Option 3: Firebase Hosting (Google Cloud)

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Initialize Firebase**:
   ```bash
   cd frontend
   firebase init hosting
   ```
   - Select existing project or create new
   - Public directory: `dist`
   - Single-page app: Yes
   - Overwrite index.html: No

3. **Create firebase.json**:
   ```json
   {
     "hosting": {
       "public": "dist",
       "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
       "rewrites": [
         {
           "source": "**",
           "destination": "/index.html"
         }
       ],
       "headers": [
         {
           "source": "**/*.@(js|css)",
           "headers": [
             {
               "key": "Cache-Control",
               "value": "max-age=31536000"
             }
           ]
         }
       ]
     }
   }
   ```

4. **Deploy**:
   ```bash
   firebase deploy --only hosting
   ```

5. **Set Environment Variables**:
   Since Firebase Hosting is static, you'll need to rebuild with env vars:
   ```bash
   # Update .env with production URL
   echo "VITE_API_URL=https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app" > .env
   npm run build
   firebase deploy --only hosting
   ```

### Option 4: Serve from Backend (Simple for Demo)

Add static file serving to Flask backend:

1. **Update backend** to serve frontend:
   ```python
   # In agent/main.py, add:
   from flask import send_from_directory
   import os
   
   @app.route('/', defaults={'path': ''})
   @app.route('/<path:path>')
   def serve_frontend(path):
       if path != "" and os.path.exists(os.path.join('frontend/dist', path)):
           return send_from_directory('frontend/dist', path)
       else:
           return send_from_directory('frontend/dist', 'index.html')
   ```

2. **Copy frontend build to backend**:
   ```bash
   cp -r frontend/dist agent/static
   ```

## Quick Local Demo

For immediate testing:

```bash
cd frontend
npm run preview
```

This serves the built files on `http://localhost:4173`

## Environment Variables

Make sure `VITE_API_URL` is set to your backend URL:
- Production: `https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app`
- Local: `http://localhost:8080`

## Testing the Demo

1. Open the deployed frontend URL
2. Go through onboarding/setup
3. Navigate to Dashboard
4. Click "Simulate Disruption Event"
5. Watch the AI analyze routes and recommend alternatives

## Troubleshooting

- **CORS errors**: Backend already has CORS enabled
- **API not connecting**: Check `VITE_API_URL` environment variable
- **Build errors**: Run `npm run build` locally to debug

