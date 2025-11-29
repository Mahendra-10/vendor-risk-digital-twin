# Phase 2: Serverless Discovery - Cloud Functions

## Overview

Convert the GCP discovery script into a serverless Cloud Function that can be triggered on-demand via HTTP or scheduled via Pub/Sub.

## Goal

Deploy a Cloud Function that:
- Discovers vendor dependencies from GCP infrastructure
- Stores results in Cloud Storage
- Can be triggered manually (HTTP) or automatically (Pub/Sub)
- Logs to Cloud Logging

## Prerequisites

✅ Phase 1 complete (Secret Manager setup)  
✅ GCP project created  
✅ Cloud Functions API enabled  
✅ Cloud Storage API enabled  
✅ Service account with necessary permissions

## Step 1: Review Cloud Function Structure

The Cloud Function has been created in:
```
cloud_functions/
└── discovery/
    ├── main.py          # Cloud Function entry point
    ├── requirements.txt # Function dependencies
    └── .gcloudignore    # Files to exclude from deployment
```

## Step 2: Create Cloud Storage Bucket

```bash
# Create bucket for storing discovery results
gsutil mb -p vendor-risk-digital-twin -l us-central1 gs://vendor-risk-digital-twin-discovery-results

# Or let the function create it automatically (it will try)
```

## Step 3: Deploy Cloud Function

### Option A: HTTP Trigger (Manual Invocation)

```bash
cd cloud_functions/discovery

gcloud functions deploy vendor-discovery \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source . \
  --entry-point discover_vendors \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=vendor-risk-digital-twin \
  --set-env-vars STORAGE_BUCKET=vendor-risk-digital-twin-discovery-results \
  --memory 512MB \
  --timeout 540s \
  --max-instances 10
```

### Option B: Pub/Sub Trigger (Scheduled Scans)

First, create a Pub/Sub topic:
```bash
gcloud pubsub topics create vendor-discovery-trigger
```

Then deploy with Pub/Sub trigger:
```bash
gcloud functions deploy vendor-discovery-scheduled \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source . \
  --entry-point discover_vendors_pubsub \
  --trigger-topic vendor-discovery-trigger \
  --set-env-vars GCP_PROJECT_ID=vendor-risk-digital-twin \
  --set-env-vars STORAGE_BUCKET=vendor-risk-digital-twin-discovery-results \
  --memory 512MB \
  --timeout 540s
```

## Step 4: Test the Cloud Function

### Test HTTP Trigger

```bash
# Get the function URL
FUNCTION_URL=$(gcloud functions describe vendor-discovery \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)")

# Invoke the function
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}'
```

Or test via gcloud:
```bash
gcloud functions call vendor-discovery \
  --gen2 \
  --region us-central1 \
  --data '{"project_id": "vendor-risk-digital-twin"}'
```

### Test Pub/Sub Trigger

```bash
# Publish a message to trigger the function
gcloud pubsub topics publish vendor-discovery-trigger \
  --message '{"project_id": "vendor-risk-digital-twin"}'
```

## Step 5: View Results

### Check Cloud Storage

```bash
# List discovery results
gsutil ls gs://vendor-risk-digital-twin-discovery-results/discoveries/

# View latest result
gsutil cat $(gsutil ls -t gs://vendor-risk-digital-twin-discovery-results/discoveries/ | head -1)
```

### Check Cloud Logging

```bash
# View function logs
gcloud functions logs read vendor-discovery \
  --gen2 \
  --region us-central1 \
  --limit 50
```

## Step 6: Set Up Scheduled Discovery (Optional)

Use Cloud Scheduler to trigger discovery automatically:

```bash
# Create a scheduled job (runs daily at 2 AM)
gcloud scheduler jobs create pubsub daily-vendor-discovery \
  --schedule="0 2 * * *" \
  --topic=vendor-discovery-trigger \
  --message-body='{"project_id": "vendor-risk-digital-twin"}' \
  --time-zone="America/New_York"
```

## Function Features

### HTTP Endpoint
- **URL:** `https://us-central1-vendor-risk-digital-twin.cloudfunctions.net/vendor-discovery`
- **Method:** POST
- **Body:** `{"project_id": "vendor-risk-digital-twin"}` (optional if set in env)

### Response Format
```json
{
  "success": true,
  "project_id": "vendor-risk-digital-twin",
  "discovery_timestamp": "2025-11-27T04:30:00",
  "summary": {
    "cloud_functions": 5,
    "cloud_run_services": 3,
    "vendors_found": 4
  },
  "storage_path": "gs://bucket/discoveries/20251127_043000_discovery.json"
}
```

## Troubleshooting

### Error: "Permission denied"
**Solution:** Grant Cloud Functions service account necessary permissions:
```bash
PROJECT_NUMBER=$(gcloud projects describe vendor-risk-digital-twin --format="value(projectNumber)")

gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"

gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"
```

### Error: "Function deployment failed"
**Solution:** Check logs:
```bash
gcloud functions logs read vendor-discovery --gen2 --region us-central1 --limit 20
```

### Error: "Bucket not found"
**Solution:** The function will try to create the bucket automatically. If it fails, create manually:
```bash
gsutil mb -p vendor-risk-digital-twin -l us-central1 gs://vendor-risk-digital-twin-discovery-results
```

## Learning Outcomes

✅ Cloud Functions development lifecycle  
✅ HTTP vs Pub/Sub triggers  
✅ Function deployment and versioning  
✅ Cloud Storage integration  
✅ Cloud Logging integration  
✅ Serverless architecture patterns  

## Next Steps

After completing Phase 2:

✅ Cloud Function deployed  
✅ Discovery can be triggered on-demand  
✅ Results stored in Cloud Storage  
✅ Logs available in Cloud Logging  

**Ready for Phase 3:** Containerized Services - Cloud Run

## Files Created

- ✅ `cloud_functions/discovery/main.py` - Cloud Function code
- ✅ `cloud_functions/discovery/requirements.txt` - Function dependencies
- ✅ `cloud_functions/discovery/.gcloudignore` - Deployment exclusions

