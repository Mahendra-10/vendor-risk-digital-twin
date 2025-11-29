#!/bin/bash
# Store Neo4j Aura credentials in GCP Secret Manager

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"

echo "🔐 Storing Neo4j Aura credentials in GCP Secret Manager..."
echo "Project: ${PROJECT_ID}"
echo ""

# Use provided URI or default to your Aura instance
if [ -n "$1" ]; then
    NEO4J_URI="$1"
else
    # Default to your Aura instance
    NEO4J_URI="neo4j+s://d29c0138.databases.neo4j.io"
fi

# Credentials (from Neo4j Aura)
NEO4J_USER="neo4j"
NEO4J_PASSWORD="lFzlLLu_hf8h_Hg0JHb5dtIAGNTq8_AZlLEpcV9LG-4"

echo "Storing credentials..."

# Store URI
if gcloud secrets describe neo4j-uri --project=${PROJECT_ID} &>/dev/null; then
    echo "Updating existing neo4j-uri secret..."
    echo -n "${NEO4J_URI}" | gcloud secrets versions add neo4j-uri --data-file=- --project=${PROJECT_ID}
else
    echo "Creating neo4j-uri secret..."
    echo -n "${NEO4J_URI}" | gcloud secrets create neo4j-uri \
        --data-file=- \
        --project=${PROJECT_ID} \
        --replication-policy=automatic
fi

# Store username
if gcloud secrets describe neo4j-user --project=${PROJECT_ID} &>/dev/null; then
    echo "Updating existing neo4j-user secret..."
    echo -n "${NEO4J_USER}" | gcloud secrets versions add neo4j-user --data-file=- --project=${PROJECT_ID}
else
    echo "Creating neo4j-user secret..."
    echo -n "${NEO4J_USER}" | gcloud secrets create neo4j-user \
        --data-file=- \
        --project=${PROJECT_ID} \
        --replication-policy=automatic
fi

# Store password
if gcloud secrets describe neo4j-password --project=${PROJECT_ID} &>/dev/null; then
    echo "Updating existing neo4j-password secret..."
    echo -n "${NEO4J_PASSWORD}" | gcloud secrets versions add neo4j-password --data-file=- --project=${PROJECT_ID}
else
    echo "Creating neo4j-password secret..."
    echo -n "${NEO4J_PASSWORD}" | gcloud secrets create neo4j-password \
        --data-file=- \
        --project=${PROJECT_ID} \
        --replication-policy=automatic
fi

echo ""
echo "✅ Credentials stored successfully!"
echo ""
echo "To verify:"
echo "  gcloud secrets versions access latest --secret=neo4j-uri --project=${PROJECT_ID}"
echo ""
echo "Next step: Load data into Aura, then deploy to Cloud Run"

