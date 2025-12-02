#!/bin/bash

# Phase 8: CI/CD Pipeline Setup Script
# Sets up Cloud Build for automated deployments

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"

echo "🚀 Setting up CI/CD Pipeline for Vendor Risk Digital Twin"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📋 Project Number: $PROJECT_NUMBER"
echo "📋 Cloud Build Service Account: $CLOUD_BUILD_SA"
echo ""

# Enable required APIs
echo "📋 Enabling required APIs..."
APIS=(
    "cloudbuild.googleapis.com"
    "cloudfunctions.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    if ! gcloud services list --enabled --project=$PROJECT_ID --filter="name:$api" | grep -q "$api"; then
        echo "   Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
        echo "   ✅ $api enabled"
    else
        echo "   ✅ $api already enabled"
    fi
done

echo ""

# Grant Cloud Build service account necessary permissions
echo "🔐 Granting Cloud Build service account permissions..."

# Roles needed for Cloud Build to deploy services
ROLES=(
    "roles/cloudfunctions.developer"      # Deploy Cloud Functions
    "roles/run.admin"                      # Deploy Cloud Run services
    "roles/iam.serviceAccountUser"         # Use service accounts
    "roles/secretmanager.secretAccessor"   # Access secrets
    "roles/storage.admin"                  # Push images to Container Registry
    "roles/artifactregistry.writer"       # Push images to Artifact Registry
)

for role in "${ROLES[@]}"; do
    echo "   Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="$role" \
        --condition=None \
        --quiet 2>/dev/null || echo "   ⚠️  Role may already be granted or needs manual setup"
done

echo ""
echo "✅ Cloud Build service account permissions configured"
echo ""

# Verify cloudbuild.yaml exists
if [ ! -f "cloudbuild.yaml" ]; then
    echo "❌ Error: cloudbuild.yaml not found in project root"
    echo "   Please ensure cloudbuild.yaml exists"
    exit 1
fi

echo "✅ Found cloudbuild.yaml in project root"
echo ""

# Test build (optional - can be skipped)
read -p "Do you want to test the build now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Testing Cloud Build configuration..."
    gcloud builds submit \
        --config cloudbuild.yaml \
        --project $PROJECT_ID \
        --no-source || echo "⚠️  Build test failed - check configuration"
else
    echo "⏭️  Skipping build test"
fi

echo ""
echo "✅ CI/CD Pipeline setup complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Set up GitHub/GitLab trigger (optional but recommended):"
echo "   - Go to: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
echo "   - Click 'Create Trigger'"
echo "   - Connect your repository"
echo "   - Configure trigger settings:"
echo "     * Event: Push to branch"
echo "     * Branch: ^main$ (or your main branch)"
echo "     * Configuration: cloudbuild.yaml"
echo ""
echo "2. Test manual build:"
echo "   gcloud builds submit --config cloudbuild.yaml --project $PROJECT_ID"
echo ""
echo "3. View build history:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""
echo "📖 Documentation:"
echo "   - Implementation guide: docs/gcp-integration/phase8/"
echo ""

