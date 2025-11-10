# Local Development Setup

## Quick Start

1. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Run locally**
```bash
python agent/main.py
# Or
python -m agent.main
```

The server will run on `http://localhost:8080`

## Testing

Test the health endpoint:
```bash
curl http://localhost:8080/
```

Test the agent query:
```bash
curl -X POST http://localhost:8080/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Monitor shipment SHIP-001", "user_id": "test-user"}'
```

# Google Cloud Run Deployment

## Prerequisites

1. **Install Google Cloud SDK**
   - Download from: https://cloud.google.com/sdk/docs/install
   - Authenticate: `gcloud auth login`
   - Set project: `gcloud config set project arkham-ai-477701`

2. **Enable required APIs**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

3. **Set up service account** (if needed)
```bash
gcloud iam service-accounts create arkham-ai-agent \
    --display-name="Arkham AI Agent Service Account"

gcloud projects add-iam-policy-binding arkham-ai-477701 \
    --member="serviceAccount:arkham-ai@arkham-ai-477701.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

## Deploy Options

### Option 1: Using Deployment Script (Recommended)

```bash
./deploy.sh
```

### Option 2: Manual Deployment

1. **Build Docker image**
```bash
gcloud builds submit --tag gcr.io/arkham-ai-477701/arkham-ai-agent
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy arkham-ai-agent \
    --image gcr.io/arkham-ai-477701/arkham-ai-agent \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=arkham-ai-477701,GOOGLE_CLOUD_LOCATION=us-central1"
```

3. **Set environment variables** (after deployment)
```bash
gcloud run services update arkham-ai-agent \
    --region us-central1 \
    --update-env-vars "ACLED_USERNAME=your_email@example.com,ACLED_PASSWORD=your_password"
```

### Option 3: Using Docker Locally

1. **Build Docker image**
```bash
docker build -t arkham-ai-agent .
```

2. **Run container**
```bash
docker run -p 8080:8080 \
    -e GOOGLE_CLOUD_PROJECT=arkham-ai-477701 \
    -e GOOGLE_CLOUD_LOCATION=us-central1 \
    arkham-ai-agent
```

# Environment Variables

Set these in Cloud Run or your `.env` file:

**Required:**
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- `GOOGLE_CLOUD_LOCATION` - GCP region (e.g., us-central1)

**Optional (for real data sources):**
- `ACLED_USERNAME` - ACLED API username
- `ACLED_PASSWORD` - ACLED API password
- `NEWS_API_KEY` - News API key
- `PORT_API_KEY` - Port API key

**Service Account (for Vertex AI):**
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON key

# Post-Deployment

1. **Get service URL**
```bash
gcloud run services describe arkham-ai-agent \
    --region us-central1 \
    --format 'value(status.url)'
```

2. **Test deployment**
```bash
curl https://your-service-url.run.app/
```

3. **Monitor logs**
```bash
gcloud run services logs read arkham-ai-agent --region us-central1
```

# Troubleshooting

**Issue: Module not found**
- Ensure `agent/__init__.py` exists
- Check Python path

**Issue: Authentication errors**
- Verify service account has correct permissions
- Check `GOOGLE_APPLICATION_CREDENTIALS` is set correctly

**Issue: Port binding**
- Ensure `PORT` environment variable is set (Cloud Run sets this automatically)
- Check firewall rules if deploying to VM

**Issue: ACLED API errors**
- Verify credentials are correct
- Check token expiration (tokens expire after 24 hours)

