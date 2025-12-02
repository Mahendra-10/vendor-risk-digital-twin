#!/bin/bash

# Grant Cloud Build permissions to Compute Engine default service account
# Use this if Cloud Build service account is not available in trigger setup

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
COMPUTE_SA="16418516910-compute@developer.gserviceaccount.com"

echo "🔧 Configuring Compute Engine default service account for Cloud Build"
echo "   Service Account: ${COMPUTE_SA}"
echo "   Project: ${PROJECT_ID}"
echo ""

# Grant Cloud Functions Developer role
echo "   Granting roles/cloudfunctions.developer..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/cloudfunctions.developer" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

# Grant Cloud Run Admin role
echo "   Granting roles/run.admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/run.admin" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

# Grant Service Account User role
echo "   Granting roles/iam.serviceAccountUser..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

# Grant Secret Manager Secret Accessor role
echo "   Granting roles/secretmanager.secretAccessor..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

# Grant Storage Admin role (for Container Registry)
echo "   Granting roles/storage.admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/storage.admin" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

# Grant Cloud Build Service Account role (so it can act as Cloud Build)
echo "   Granting roles/cloudbuild.builds.editor..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/cloudbuild.builds.editor" \
    --condition=None \
    --quiet || echo "   ⚠️  Role may already be granted"

echo ""
echo "✅ Compute Engine default service account configured for Cloud Build"
echo "   You can now use: 16418516910-compute@developer.gserviceaccount.com"
echo "   in your Cloud Build trigger setup"
echo ""

