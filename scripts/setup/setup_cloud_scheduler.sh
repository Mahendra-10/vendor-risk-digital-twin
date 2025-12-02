#!/bin/bash

# Setup Cloud Scheduler for Vendor Risk Digital Twin
# Creates scheduled jobs for automated discovery and reporting

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"
DISCOVERY_FUNCTION_URL="https://vendor-discovery-wearla5naa-uc.a.run.app"

echo "🚀 Setting up Cloud Scheduler for Vendor Risk Digital Twin"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Enable Cloud Scheduler API if not already enabled
echo "📋 Checking Cloud Scheduler API..."
if ! gcloud services list --enabled --project=$PROJECT_ID --filter="name:cloudscheduler.googleapis.com" | grep -q cloudscheduler; then
    echo "   Enabling Cloud Scheduler API..."
    gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID
    echo "   ✅ Cloud Scheduler API enabled"
else
    echo "   ✅ Cloud Scheduler API already enabled"
fi

echo ""

# Create daily discovery job
JOB_NAME="daily-vendor-discovery"
echo "📅 Creating daily discovery scheduler job..."

# Check if job already exists
if gcloud scheduler jobs describe $JOB_NAME --location=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo "   ⚠️  Job '$JOB_NAME' already exists. Updating..."
    gcloud scheduler jobs update http $JOB_NAME \
        --location=$REGION \
        --schedule="0 2 * * *" \
        --uri="$DISCOVERY_FUNCTION_URL" \
        --http-method=POST \
        --message-body='{"project_id": "'$PROJECT_ID'"}' \
        --headers="Content-Type=application/json" \
        --time-zone="America/Los_Angeles" \
        --description="Daily automated vendor dependency discovery scan" \
        --project=$PROJECT_ID
    echo "   ✅ Job '$JOB_NAME' updated"
else
    echo "   Creating new job '$JOB_NAME'..."
    gcloud scheduler jobs create http $JOB_NAME \
        --location=$REGION \
        --schedule="0 2 * * *" \
        --uri="$DISCOVERY_FUNCTION_URL" \
        --http-method=POST \
        --message-body='{"project_id": "'$PROJECT_ID'"}' \
        --headers="Content-Type=application/json" \
        --time-zone="America/Los_Angeles" \
        --description="Daily automated vendor dependency discovery scan at 2 AM" \
        --project=$PROJECT_ID
    echo "   ✅ Job '$JOB_NAME' created"
fi

echo ""
echo "✅ Cloud Scheduler setup complete!"
echo ""
echo "📊 Summary:"
echo "   - Daily discovery job: $JOB_NAME"
echo "   - Schedule: Daily at 2:00 AM (America/Los_Angeles)"
echo "   - Target: $DISCOVERY_FUNCTION_URL"
echo ""
echo "🔍 To verify:"
echo "   gcloud scheduler jobs list --location=$REGION --project=$PROJECT_ID"
echo ""
echo "🧪 To test immediately:"
echo "   gcloud scheduler jobs run $JOB_NAME --location=$REGION --project=$PROJECT_ID"
echo ""

