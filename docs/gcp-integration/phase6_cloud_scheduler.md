# Phase 6: Cloud Scheduler - Implementation Guide

**Status:** ✅ Complete  
**Date Completed:** 2025-11-29  
**Estimated Time:** 2-3 hours (Actual: ~30 minutes)

---

## Overview

Phase 6 implements automated scheduling using Google Cloud Scheduler to trigger periodic vendor dependency discovery scans without manual intervention.

---

## Implementation Summary

### What Was Created

1. **Daily Discovery Scheduler Job**
   - **Job Name:** `daily-vendor-discovery`
   - **Schedule:** Daily at 2:00 AM (America/Los_Angeles timezone)
   - **Target:** Discovery Cloud Function (`vendor-discovery`)
   - **Method:** HTTP POST
   - **Status:** ✅ Enabled and active

2. **Setup Script**
   - `scripts/setup_cloud_scheduler.sh` - Automated setup script
   - Handles API enabling, job creation/updates
   - Includes verification and testing commands

---

## How It Works

### Automation Flow

```
Cloud Scheduler (2 AM daily)
    ↓
Triggers Discovery Function (HTTP POST)
    ↓
Discovery Function runs GCP scan
    ↓
Publishes to Pub/Sub (vendor-discovery-events)
    ↓
Graph Loader Function automatically triggered
    ↓
Neo4j graph updated automatically
```

### Schedule Details

- **Cron Expression:** `0 2 * * *` (2:00 AM daily)
- **Timezone:** America/Los_Angeles
- **HTTP Method:** POST
- **Request Body:** `{"project_id": "vendor-risk-digital-twin"}`

---

## Setup Instructions

### Quick Setup

```bash
cd vendor-risk-digital-twin
./scripts/setup_cloud_scheduler.sh
```

### Manual Setup

```bash
# Enable Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com --project=vendor-risk-digital-twin

# Create daily discovery job
gcloud scheduler jobs create http daily-vendor-discovery \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri="https://vendor-discovery-wearla5naa-uc.a.run.app" \
  --http-method=POST \
  --message-body='{"project_id": "vendor-risk-digital-twin"}' \
  --headers="Content-Type=application/json" \
  --time-zone="America/Los_Angeles" \
  --description="Daily automated vendor dependency discovery scan" \
  --project=vendor-risk-digital-twin
```

---

## Verification

### Check Job Status

```bash
# List all scheduler jobs
gcloud scheduler jobs list --location=us-central1 --project=vendor-risk-digital-twin

# Describe specific job
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin
```

### Test Job Manually

```bash
# Run job immediately (for testing)
gcloud scheduler jobs run daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin
```

### Monitor Execution

```bash
# Check Cloud Function logs (after job runs)
gcloud functions logs read vendor-discovery --region=us-central1 --limit=20

# Check Pub/Sub message delivery
gcloud pubsub subscriptions describe discovery-to-neo4j-subscription \
  --format="value(numUndeliveredMessages)" \
  --project=vendor-risk-digital-twin
```

---

## Expected Behavior

### Daily Execution (2 AM)

1. **Cloud Scheduler triggers** discovery function at 2:00 AM
2. **Discovery Function** scans GCP resources
3. **Results stored** in Cloud Storage
4. **Pub/Sub event published** to `vendor-discovery-events`
5. **Graph Loader Function** automatically triggered
6. **Neo4j graph updated** with new dependencies

### Success Indicators

- ✅ Scheduler job shows `state: ENABLED`
- ✅ Discovery function logs show successful execution
- ✅ Pub/Sub messages delivered (0 undelivered)
- ✅ Neo4j graph contains updated vendor data

---

## Troubleshooting

### Job Not Running

```bash
# Check job state
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin \
  --format="value(state)"

# Check for errors
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin \
  --format="value(status)"
```

### Discovery Function Fails

```bash
# Check function logs
gcloud functions logs read vendor-discovery --region=us-central1 --limit=50

# Verify function is accessible
curl -X POST "https://vendor-discovery-wearla5naa-uc.a.run.app" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}'
```

### Timezone Issues

```bash
# Update timezone if needed
gcloud scheduler jobs update http daily-vendor-discovery \
  --location=us-central1 \
  --time-zone="America/New_York" \
  --project=vendor-risk-digital-twin
```

---

## Future Enhancements

### Additional Scheduled Jobs (Planned)

1. **Weekly Compliance Reports**
   - Schedule: Every Monday at 9 AM
   - Action: Generate compliance posture report
   - Deliverable: Email/Slack notification with report

2. **Monthly Vendor Risk Assessment**
   - Schedule: 1st of month at 8 AM
   - Action: Run comprehensive risk analysis
   - Deliverable: Executive summary report

3. **Quarterly Compliance Framework Review**
   - Schedule: Quarterly (Jan, Apr, Jul, Oct) at 10 AM
   - Action: Review all compliance frameworks
   - Deliverable: Compliance dashboard update

---

## Cost Considerations

**Cloud Scheduler Pricing:**
- **Free Tier:** 3 jobs free per month
- **Beyond Free Tier:** $0.10 per job execution
- **Estimated Cost:** ~$3/month (30 daily executions)

**Total Monthly Cost (Phase 6):**
- Daily discovery: ~$3/month
- Very cost-effective for continuous monitoring

---

## Integration with Other Phases

**Phase 6 depends on:**
- ✅ Phase 2: Discovery Function (deployed)
- ✅ Phase 5: Pub/Sub infrastructure (ready)

**Phase 6 enables:**
- ⏳ Phase 7: Monitoring (can monitor scheduler job execution)
- ⏳ Future: Automated compliance reporting

---

## Success Metrics

**Phase 6 is successful if:**
- ✅ Scheduler job created and enabled
- ✅ Job executes successfully on schedule
- ✅ Discovery function triggered automatically
- ✅ Neo4j graph updated without manual intervention
- ✅ Zero manual steps required for daily discovery

---

## Documentation

- **Setup Script:** `scripts/setup_cloud_scheduler.sh`
- **Roadmap Reference:** `docs/gcp_integration_roadmap.md` (Phase 6)
- **Related:** `docs/pubsub_automation.md` (event flow)

---

**Phase 6 Status: ✅ Complete and Operational**

