#!/bin/bash
# Deploy BigQuery Loader Cloud Function
# This function subscribes to simulation-results and loads data into BigQuery

set -e

PROJECT_ID=${GCP_PROJECT_ID:-vendor-risk-digital-twin}
REGION=${GCP_REGION:-us-central1}
FUNCTION_NAME="bigquery-loader"
TOPIC_NAME="simulation-results"

echo "🚀 Deploying BigQuery Loader Cloud Function..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Function: $FUNCTION_NAME"
echo "   Topic: $TOPIC_NAME"
echo ""

# Navigate to function directory
cd "$(dirname "$0")"

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime python311 \
  --region $REGION \
  --source . \
  --entry-point load_simulation_result \
  --trigger-topic $TOPIC_NAME \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,BIGQUERY_DATASET_ID=vendor_risk \
  --timeout 300s \
  --memory 256MB \
  --max-instances 10 \
  --allow-unauthenticated

echo ""
echo "✅ BigQuery Loader Cloud Function deployed successfully!"
echo ""
echo "📋 Function Details:"
echo "   Name: $FUNCTION_NAME"
echo "   Trigger: Pub/Sub topic '$TOPIC_NAME'"
echo "   Entry Point: load_simulation_result"
echo ""
echo "🔍 View logs:"
echo "   gcloud functions logs read $FUNCTION_NAME --region $REGION --limit 50"
echo ""

