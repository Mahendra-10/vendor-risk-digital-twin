#!/bin/bash
# Deploy Graph Loader Cloud Function
# This function subscribes to vendor-discovery-events and loads data into Neo4j

set -e

PROJECT_ID=${GCP_PROJECT_ID:-vendor-risk-digital-twin}
REGION=${GCP_REGION:-us-central1}
FUNCTION_NAME="graph-loader"
TOPIC_NAME="vendor-discovery-events"

echo "🚀 Deploying Graph Loader Cloud Function..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Function: $FUNCTION_NAME"
echo "   Topic: $TOPIC_NAME"
echo ""

# Navigate to function directory
cd "$(dirname "$0")"

# Get Neo4j credentials from Secret Manager
echo "🔐 Fetching Neo4j credentials from Secret Manager..."
NEO4J_URI=$(gcloud secrets versions access latest --secret=neo4j-uri --project=$PROJECT_ID 2>/dev/null || echo "")
NEO4J_USER=$(gcloud secrets versions access latest --secret=neo4j-user --project=$PROJECT_ID 2>/dev/null || echo "neo4j")
NEO4J_PASSWORD=$(gcloud secrets versions access latest --secret=neo4j-password --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$NEO4J_URI" ] || [ -z "$NEO4J_PASSWORD" ]; then
    echo "⚠️  Warning: Could not fetch Neo4j credentials from Secret Manager"
    echo "   The function will try to access Secret Manager at runtime"
else
    echo "✅ Neo4j credentials fetched successfully"
fi

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime python311 \
  --region $REGION \
  --source . \
  --entry-point load_discovery_to_neo4j \
  --trigger-topic $TOPIC_NAME \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID \
  --set-secrets NEO4J_URI=neo4j-uri:latest,NEO4J_USER=neo4j-user:latest,NEO4J_PASSWORD=neo4j-password:latest \
  --timeout 540s \
  --memory 512MB \
  --max-instances 10 \
  --allow-unauthenticated

echo ""
echo "✅ Graph Loader Cloud Function deployed successfully!"
echo ""
echo "📋 Function Details:"
echo "   Name: $FUNCTION_NAME"
echo "   Trigger: Pub/Sub topic '$TOPIC_NAME'"
echo "   Entry Point: load_discovery_to_neo4j"
echo ""
echo "🔍 View logs:"
echo "   gcloud functions logs read $FUNCTION_NAME --region $REGION --limit 50"
echo ""

