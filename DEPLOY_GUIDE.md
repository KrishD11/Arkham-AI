# Cloud Run Deployment Guide

## Quick Deploy

Run the deployment script:
```bash
./deploy.sh
```

This will:
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Set environment variables

## Manual Deployment Steps

### 1. Build and Push Docker Image
```bash
gcloud builds submit --tag gcr.io/arkham-ai-477701/arkham-ai-agent
```

### 2. Deploy to Cloud Run
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
    --set-env-vars "GOOGLE_CLOUD_PROJECT=arkham-ai-477701,GOOGLE_CLOUD_LOCATION=us-central1,AGENT_NAME=Arkham AI" \
    --update-env-vars "TRADE_NEWS_API_KEY=66f73ba2c57f456188799bc2f240ebe7,ACLED_USERNAME=kdandu3@charlotte.edu,ACLED_PASSWORD=Theater6#,MONGODB_URI=mongodb+srv://rakeshravi898_db_user:gXDAqFez1jk4f5gu@cluster0.aabxext.mongodb.net/?appName=Cluster0,MONGODB_DATABASE=arkham_ai"
```

### 3. Verify Deployment
```bash
# Get service URL
gcloud run services describe arkham-ai-agent --region us-central1 --format="value(status.url)"

# Test health endpoint
curl https://arkham-ai-agent-bzt66kt2sa-uc.a.run.app/api/health
```

## Environment Variables

The following are set in Cloud Run:
- `GOOGLE_CLOUD_PROJECT`: arkham-ai-477701
- `GOOGLE_CLOUD_LOCATION`: us-central1
- `AGENT_NAME`: Arkham AI
- `TRADE_NEWS_API_KEY`: (set)
- `ACLED_USERNAME`: (set)
- `ACLED_PASSWORD`: (set)
- `MONGODB_URI`: (set)
- `MONGODB_DATABASE`: arkham_ai

## View Logs

```bash
gcloud run services logs read arkham-ai-agent --region us-central1 --limit 50
```

## Update Environment Variables

```bash
gcloud run services update arkham-ai-agent \
    --region us-central1 \
    --update-env-vars "KEY=VALUE"
```

## Troubleshooting

**Build fails:**
- Check Dockerfile syntax
- Verify requirements.txt is correct
- Check Python version compatibility

**Deployment fails:**
- Verify gcloud is authenticated: `gcloud auth list`
- Check project is set: `gcloud config get-value project`
- Verify APIs are enabled: `gcloud services list --enabled`

**Service not responding:**
- Check logs: `gcloud run services logs read arkham-ai-agent --region us-central1`
- Verify environment variables are set correctly
- Check service status: `gcloud run services describe arkham-ai-agent --region us-central1`

