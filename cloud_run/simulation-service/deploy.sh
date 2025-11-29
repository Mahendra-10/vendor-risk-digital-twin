#!/bin/bash
# Deployment script for Simulation Service on Cloud Run

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="simulation-service"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Simulation Service to Cloud Run..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "📋 Setting GCP project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Get Neo4j credentials from Secret Manager (if available)
echo "🔐 Fetching Neo4j credentials from Secret Manager..."
NEO4J_URI=$(gcloud secrets versions access latest --secret=neo4j-uri --project=${PROJECT_ID} 2>/dev/null || echo "")
NEO4J_USER=$(gcloud secrets versions access latest --secret=neo4j-user --project=${PROJECT_ID} 2>/dev/null || echo "neo4j")
NEO4J_PASSWORD=$(gcloud secrets versions access latest --secret=neo4j-password --project=${PROJECT_ID} 2>/dev/null || echo "")

# Build container image
echo "🏗️  Building container image..."
cd "$(dirname "$0")/../.."  # Go to project root
# Build using Cloud Build with the Dockerfile in subdirectory
gcloud builds submit \
    --config cloud_run/simulation-service/cloudbuild.yaml \
    --project ${PROJECT_ID} \
    --quiet

echo "✅ Image built successfully: ${IMAGE_NAME}"

# Prepare environment variables
ENV_VARS="GCP_PROJECT_ID=${PROJECT_ID}"
if [ -n "$NEO4J_URI" ]; then
    ENV_VARS="${ENV_VARS},NEO4J_URI=${NEO4J_URI}"
fi
if [ -n "$NEO4J_USER" ]; then
    ENV_VARS="${ENV_VARS},NEO4J_USER=${NEO4J_USER}"
fi
if [ -n "$NEO4J_PASSWORD" ]; then
    ENV_VARS="${ENV_VARS},NEO4J_PASSWORD=${NEO4J_PASSWORD}"
fi

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars ${ENV_VARS} \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --project ${PROJECT_ID} \
    --quiet

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📡 Service URL: ${SERVICE_URL}"
echo ""
echo "🧪 Test the service:"
echo "   curl ${SERVICE_URL}/health"
echo "   curl ${SERVICE_URL}/vendors"
echo "   curl -X POST ${SERVICE_URL}/simulate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"vendor\": \"Stripe\", \"duration\": 4}'"
echo ""
echo "📊 View logs:"
echo "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --limit 50"

