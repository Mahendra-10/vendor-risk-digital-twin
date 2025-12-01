# Phase 2 Enhancements: Sample Services & Discovery Integration

This document describes the enhancements made to Phase 2 (Serverless Discovery) to support:
1. Deploying sample Cloud Functions/Cloud Run services with vendor environment variables
2. Fetching discovery results from Cloud Storage
3. Converting discovery results to Neo4j format
4. Loading discovery results into Neo4j graph database
5. Dashboard integration for discovery results

## Overview

These enhancements complete the discovery-to-simulation pipeline:
```
GCP Discovery → Cloud Storage → Neo4j → Simulation
```

## Components

### 1. Sample Service Deployment Script

**File:** `scripts/deploy_sample_services.sh`

**Purpose:** Deploys sample Cloud Functions and Cloud Run services with vendor environment variables to demonstrate vendor discovery.

**Services Deployed:**
- `payment-service` (Cloud Function) - Stripe integration
- `auth-service` (Cloud Function) - Auth0 integration
- `email-service` (Cloud Function) - SendGrid integration
- `checkout-service` (Cloud Run) - Stripe + Twilio integration

**Usage:**
```bash
cd vendor-risk-digital-twin
export GCP_PROJECT_ID=your-project-id
export GCP_REGION=us-central1
./scripts/deploy_sample_services.sh
```

**What it does:**
1. Creates temporary directories for each service
2. Generates minimal Python code for each service
3. Deploys to GCP with vendor-specific environment variables
4. Cleans up temporary files

**Environment Variables Set:**
- `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET` (payment-service)
- `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` (auth-service)
- `SENDGRID_API_KEY` (email-service)
- `STRIPE_PUBLISHABLE_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` (checkout-service)

### 2. Discovery Results Fetcher

**File:** `scripts/fetch_discovery_results.py`

**Purpose:** Fetches the latest discovery results from Cloud Storage and converts them to Neo4j format.

**Usage:**
```bash
# Fetch and save to file
python scripts/fetch_discovery_results.py --project-id PROJECT_ID

# Fetch and automatically load into Neo4j
python scripts/fetch_discovery_results.py --project-id PROJECT_ID --load-to-neo4j

# Specify custom bucket
python scripts/fetch_discovery_results.py --project-id PROJECT_ID --bucket custom-bucket-name

# Custom output file
python scripts/fetch_discovery_results.py --project-id PROJECT_ID --output-file data/outputs/my_discovery.json
```

**What it does:**
1. Connects to Cloud Storage
2. Finds the latest discovery file (by timestamp in filename)
3. Downloads and parses the JSON
4. Converts to Neo4j format (adds vendor metadata, service IDs, etc.)
5. Optionally loads directly into Neo4j

**Output Format:**
The script converts raw discovery results to the format expected by `load_graph.py`:
```json
{
  "vendors": [
    {
      "vendor_id": "vendor_001",
      "name": "Stripe",
      "category": "payment_processor",
      "criticality": "critical",
      "services": [
        {
          "service_id": "svc_001",
          "name": "payment-service",
          "type": "cloud_function",
          "gcp_resource": "projects/.../functions/payment-service",
          "environment_variables": ["STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET"],
          "business_processes": ["checkout", "refunds", "subscription_billing"],
          "rpm": 500,
          "customers_affected": 50000
        }
      ]
    }
  ],
  "discovery_metadata": {
    "discovery_timestamp": "2024-01-15T10:30:00Z",
    "project_id": "vendor-risk-digital-twin",
    "source": "gcp_discovery"
  }
}
```

**Vendor Metadata:**
The script includes metadata for common vendors:
- Stripe, Auth0, SendGrid, Twilio, Datadog, MongoDB, PayPal, Okta
- Each vendor has default: category, criticality, business processes, RPM, customers affected

### 3. Enhanced Graph Loader

**File:** `scripts/load_graph.py`

**New Features:**
- `--from-gcp` flag to load directly from Cloud Storage
- `--project-id` parameter for GCP project

**Usage:**
```bash
# Load from Cloud Storage (latest discovery)
python scripts/load_graph.py --from-gcp --project-id PROJECT_ID --clear

# Traditional file-based loading (still works)
python scripts/load_graph.py --data-file data/sample/sample_dependencies.json
```

**What it does:**
1. If `--from-gcp` is used:
   - Fetches latest discovery from Cloud Storage
   - Converts to Neo4j format
   - Loads into graph database
2. Otherwise, works as before with local JSON files

### 4. Dashboard API Endpoints

**File:** `dashboard/server.js`

**New Endpoints:**

#### GET `/api/discovery/latest`
Fetches the latest discovery results from Cloud Storage.

**Query Parameters:**
- `project_id` (optional, uses `GCP_PROJECT_ID` env var if not provided)

**Response:**
```json
{
  "success": true,
  "project_id": "vendor-risk-digital-twin",
  "discovery": {
    "vendors": [...],
    "discovery_metadata": {...}
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST `/api/discovery/load`
Fetches discovery results and loads them into Neo4j.

**Request Body:**
```json
{
  "project_id": "vendor-risk-digital-twin"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Discovery results loaded into Neo4j successfully",
  "output": "..."
}
```

## Complete Workflow

### Step 1: Deploy Sample Services
```bash
cd vendor-risk-digital-twin
export GCP_PROJECT_ID=your-project-id
./scripts/deploy_sample_services.sh
```

### Step 2: Run Discovery
```bash
# Trigger the Cloud Function
gcloud functions call discover-vendors \
  --region=us-central1 \
  --project=your-project-id
```

### Step 3: Fetch and Load into Neo4j
```bash
# Option A: Fetch and load in one step
python scripts/fetch_discovery_results.py \
  --project-id your-project-id \
  --load-to-neo4j

# Option B: Use enhanced load_graph.py
python scripts/load_graph.py \
  --from-gcp \
  --project-id your-project-id \
  --clear
```

### Step 4: Verify in Neo4j
```cypher
// View discovered vendors
MATCH (v:Vendor)
RETURN v.name, v.category, v.criticality

// View services and their vendors
MATCH (s:Service)-[:DEPENDS_ON]->(v:Vendor)
RETURN s.name, v.name, s.type
```

### Step 5: Run Simulation
```bash
# Via command line
python scripts/simulate_failure.py --vendor "Stripe" --duration 4

# Via dashboard
# Open http://localhost:5000 and use the UI
```

## Dashboard Integration

The dashboard now supports:
1. **Viewing Discovery Results:** Use the `/api/discovery/latest` endpoint to display discovered vendors
2. **Loading Discovery:** Use the `/api/discovery/load` endpoint to sync discovery results to Neo4j
3. **Running Simulations:** After loading, you can run simulations on discovered vendors

## Troubleshooting

### Issue: No vendors found in discovery
**Solution:** 
- Verify sample services are deployed: `gcloud functions list --project=PROJECT_ID`
- Check environment variables: `gcloud functions describe payment-service --region=us-central1`
- Re-run discovery after deploying sample services

### Issue: Failed to fetch from Cloud Storage
**Solution:**
- Verify bucket exists: `gsutil ls gs://PROJECT_ID-discovery-results/`
- Check service account permissions
- Ensure discovery has been run at least once

### Issue: Neo4j load fails
**Solution:**
- Verify Neo4j is running: `docker ps` (if using Docker)
- Check credentials in `.env` file
- Verify network connectivity to Neo4j

## Next Steps

After completing these enhancements:
1. ✅ Sample services deployed with vendor env vars
2. ✅ Discovery results fetched from Cloud Storage
3. ✅ Results converted to Neo4j format
4. ✅ Results loaded into Neo4j
5. ✅ Dashboard integrated with discovery

**Ready for Phase 3:** Containerized Simulation on Cloud Run

