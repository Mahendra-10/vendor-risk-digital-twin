#!/bin/bash
# Store Neo4j Aura credentials in GCP Secret Manager

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"

echo "🔐 Storing Neo4j Aura credentials in GCP Secret Manager..."
echo "Project: ${PROJECT_ID}"
echo ""

# Get credentials from environment variables or prompt for input
# NEVER hardcode credentials in this file!

if [ -n "$1" ]; then
    NEO4J_URI="$1"
elif [ -n "$NEO4J_URI" ]; then
    # Use environment variable if set
    NEO4J_URI="$NEO4J_URI"
else
    echo "❌ Error: NEO4J_URI not provided"
    echo "Usage: $0 <neo4j-uri>"
    echo "   OR: export NEO4J_URI='neo4j+s://your-instance.databases.neo4j.io'"
    exit 1
fi

# Get username from environment or use default
NEO4J_USER="${NEO4J_USER:-neo4j}"

# Get password from environment (required)
if [ -z "$NEO4J_PASSWORD" ]; then
    echo "❌ Error: NEO4J_PASSWORD environment variable not set"
    echo "Please set it before running this script:"
    echo "  export NEO4J_PASSWORD='your-password'"
    exit 1
fi

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

