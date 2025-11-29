#!/bin/bash
# Deployment script for Vendor Discovery Cloud Function

set -e

PROJECT_ID="vendor-risk-digital-twin"
REGION="us-central1"
FUNCTION_NAME="vendor-discovery"
BUCKET_NAME="${PROJECT_ID}-discovery-results"

echo "🚀 Deploying Vendor Discovery Cloud Function..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "📋 Setting GCP project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Create Cloud Storage bucket if it doesn't exist
echo "🪣 Checking Cloud Storage bucket..."
if ! gsutil ls -b gs://${BUCKET_NAME} &> /dev/null; then
    echo "   Creating bucket: ${BUCKET_NAME}"
    gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}
    echo "   ✅ Bucket created"
else
    echo "   ✅ Bucket already exists"
fi

# Deploy Cloud Function
echo "☁️  Deploying Cloud Function..."
cd "$(dirname "$0")"

gcloud functions deploy ${FUNCTION_NAME} \
  --gen2 \
  --runtime python311 \
  --region ${REGION} \
  --source . \
  --entry-point discover_vendors \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID} \
  --set-env-vars STORAGE_BUCKET=${BUCKET_NAME} \
  --memory 512MB \
  --timeout 540s \
  --max-instances 10

# Get function URL
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} \
  --gen2 \
  --region ${REGION} \
  --format="value(serviceConfig.uri)")

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📡 Function URL: ${FUNCTION_URL}"
echo ""
echo "🧪 Test the function:"
echo "   curl -X POST \"${FUNCTION_URL}\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"project_id\": \"${PROJECT_ID}\"}'"
echo ""
echo "📊 View logs:"
echo "   gcloud functions logs read ${FUNCTION_NAME} --gen2 --region ${REGION} --limit 20"
echo ""

