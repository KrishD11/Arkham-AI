#!/bin/bash
# Deployment script for Arkham AI Agent

set -e

echo "🚀 Deploying Arkham AI Agent to Google Cloud Run..."

# Set variables
PROJECT_ID="arkham-ai-477701"
SERVICE_NAME="arkham-ai-agent"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set the project
echo "📋 Setting Google Cloud project..."
gcloud config set project ${PROJECT_ID}

# Build and push Docker image
echo "🐳 Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --update-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},AGENT_NAME=Arkham AI,TRADE_NEWS_API_KEY=66f73ba2c57f456188799bc2f240ebe7,ACLED_USERNAME=kdandu3@charlotte.edu,ACLED_PASSWORD=Theater6#,MONGODB_URI=mongodb+srv://rakeshravi898_db_user:gXDAqFez1jk4f5gu@cluster0.aabxext.mongodb.net/?appName=Cluster0,MONGODB_DATABASE=arkham_ai"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo "📊 Health check: ${SERVICE_URL}/"
echo "📚 API docs: ${SERVICE_URL}/api/health"

