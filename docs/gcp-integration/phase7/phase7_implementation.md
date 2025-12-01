# Phase 7: Monitoring & Observability - Implementation Guide

**Status:** ✅ Complete  
**Date Started:** 2025-11-29  
**Date Completed:** 2025-11-30

> **📖 For detailed setup and usage instructions, see:** [Phase 7 Monitoring Setup Guide](./phase7_monitoring_setup.md)

---

## Overview

Phase 7 implements comprehensive monitoring and observability for the Vendor Risk Digital Twin system using Google Cloud Monitoring, Cloud Logging, and Alerting.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Steps](#setup-steps)
3. [Cloud Monitoring Dashboards](#cloud-monitoring-dashboards)
4. [Alerting Policies](#alerting-policies)
5. [Log-Based Metrics](#log-based-metrics)
6. [Verification](#verification)
7. [Usage Guide](#usage-guide)

---

## Prerequisites

### ✅ Completed Phases
- ✅ Phase 1: Secret Management
- ✅ Phase 2: Cloud Functions
- ✅ Phase 3: Cloud Run
- ✅ Phase 4: BigQuery
- ✅ Phase 5: Pub/Sub
- ✅ Phase 6: Cloud Scheduler

### Required Services
- Discovery Cloud Function (`vendor-discovery`)
- Simulation Cloud Run Service (`simulation-service`)
- Graph Loader Cloud Function (`graph-loader`)
- BigQuery Loader Cloud Function (`bigquery-loader`)
- Cloud Scheduler Job (`daily-vendor-discovery`)

---

## Setup Steps

### Step 1: Run Setup Script

```bash
cd vendor-risk-digital-twin
./scripts/setup_monitoring.sh
```

**What this does:**
- Enables Cloud Monitoring and Logging APIs
- Creates log-based metrics
- Creates basic alerting policies
- Sets up foundation for monitoring

### Step 2: Create Notification Channel

1. Go to [Cloud Console - Alerting](https://console.cloud.google.com/monitoring/alerting/notifications)
2. Click **"Add Notification Channel"**
3. Select **"Email"**
4. Enter your email address
5. Click **"Save"**

**Note:** You'll need the notification channel ID for alerting policies.

### Step 3: Create Custom Dashboards

See [Cloud Monitoring Dashboards](#cloud-monitoring-dashboards) section below for dashboard configurations.

---

## Cloud Monitoring Dashboards

### Dashboard 1: Service Health Overview

**Purpose:** High-level view of all services

**Metrics to Include:**
1. **Discovery Function**
   - Success rate (last 24h)
   - Error rate (last 24h)
   - Execution count (last 24h)
   - Average execution time

2. **Simulation Service**
   - Request rate (requests/min)
   - Error rate (%)
   - P50/P95/P99 latency
   - Active instances

3. **Graph Loader**
   - Processing success rate
   - Average processing time
   - Neo4j write operations

4. **Cloud Scheduler**
   - Job execution success rate
   - Last execution time
   - Execution duration

**Dashboard JSON:**
```json
{
  "displayName": "Vendor Risk Digital Twin - Service Health",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Discovery Function Success Rate",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_function\" AND resource.labels.function_name=\"vendor-discovery\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Simulation Service Latency (P95)",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"simulation-service\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_DELTA",
                    "crossSeriesReducer": "REDUCE_PERCENTILE_95"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

### Dashboard 2: Error Monitoring

**Purpose:** Track errors across all services

**Metrics:**
- Error rate by service
- Error count by type
- Failed request trends
- Error rate over time

### Dashboard 3: Performance Metrics

**Purpose:** Track performance and latency

**Metrics:**
- Request latency (P50, P95, P99)
- Throughput (requests/second)
- Resource utilization (CPU, memory)
- Response time trends

### Dashboard 4: Business Metrics

**Purpose:** Track business-relevant metrics

**Metrics:**
- Discovery scans completed
- Vendors discovered per scan
- Simulations executed
- Neo4j graph updates
- Cloud Scheduler job success rate

---

## Alerting Policies

### Alert 1: Discovery Function High Error Rate

**Trigger:** Error rate > 10% for 5 minutes

**Configuration:**
```yaml
displayName: "Discovery Function High Error Rate"
combiner: OR
conditions:
  - displayName: "Error rate > 10%"
    conditionThreshold:
      filter: 'resource.type="cloud_function" AND resource.labels.function_name="vendor-discovery"'
      aggregations:
        - alignmentPeriod: 300s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_SUM
      comparison: COMPARISON_GT
      thresholdValue: 0.1
      duration: 300s
notificationChannels:
  - "projects/vendor-risk-digital-twin/notificationChannels/YOUR_CHANNEL_ID"
```

### Alert 2: Simulation Service High Latency

**Trigger:** P95 latency > 5 seconds for 5 minutes

**Configuration:**
```yaml
displayName: "Simulation Service High Latency"
combiner: OR
conditions:
  - displayName: "P95 latency > 5s"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="simulation-service"'
      aggregations:
        - alignmentPeriod: 300s
          perSeriesAligner: ALIGN_DELTA
          crossSeriesReducer: REDUCE_PERCENTILE_95
      comparison: COMPARISON_GT
      thresholdValue: 5000
      duration: 300s
```

### Alert 3: Cloud Scheduler Job Failure

**Trigger:** Job execution fails

**Configuration:**
```yaml
displayName: "Cloud Scheduler Job Failure"
combiner: OR
conditions:
  - displayName: "Job execution failed"
    conditionThreshold:
      filter: 'resource.type="cloud_scheduler_job" AND resource.labels.job_id="daily-vendor-discovery"'
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
      comparison: COMPARISON_GT
      thresholdValue: 0
      duration: 60s
```

### Alert 4: Service Unavailable

**Trigger:** Service returns 5xx errors

**Configuration:**
```yaml
displayName: "Service Unavailable (5xx Errors)"
combiner: OR
conditions:
  - displayName: "5xx error rate > 0"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND httpRequest.status>=500'
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
      comparison: COMPARISON_GT
      thresholdValue: 0
      duration: 60s
```

---

## Log-Based Metrics

### Metric 1: Discovery Success Rate

**Purpose:** Track discovery function success rate

**Log Filter:**
```
resource.type="cloud_function"
resource.labels.function_name="vendor-discovery"
jsonPayload.message=~"Discovery complete"
```

**Extraction:**
- Count successful discoveries
- Calculate success rate over time

### Metric 2: Simulation Error Rate

**Purpose:** Track simulation service errors

**Log Filter:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="simulation-service"
severity>=ERROR
```

**Extraction:**
- Count errors by type
- Calculate error rate

### Metric 3: Graph Loader Processing Time

**Purpose:** Track graph loader performance

**Log Filter:**
```
resource.type="cloud_function"
resource.labels.function_name="graph-loader"
jsonPayload.message=~"Successfully loaded"
```

**Extraction:**
- Extract processing time from logs
- Track average processing time

---

## Verification

### Verify APIs Enabled

```bash
gcloud services list --enabled --project=vendor-risk-digital-twin \
  --filter="name:monitoring.googleapis.com OR name:logging.googleapis.com"
```

**Expected:** Both APIs should be enabled

### Verify Log-Based Metrics

```bash
gcloud logging metrics list --project=vendor-risk-digital-twin
```

**Expected:** Should see:
- `discovery_success_rate`
- `simulation_error_rate`
- `graph_loader_processing_time`

### Verify Alerting Policies

```bash
gcloud alpha monitoring policies list --project=vendor-risk-digital-twin
```

**Expected:** Should see alerting policies created

### Verify Dashboards

1. Go to [Cloud Console - Dashboards](https://console.cloud.google.com/monitoring/dashboards)
2. Verify custom dashboards are visible
3. Check that metrics are populating

---

## Usage Guide

### Viewing Logs

**Cloud Console:**
```
https://console.cloud.google.com/logs?project=vendor-risk-digital-twin
```

**gcloud CLI:**
```bash
# Discovery Function logs
gcloud functions logs read vendor-discovery \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=50

# Simulation Service logs
gcloud run services logs read simulation-service \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=50
```

### Viewing Metrics

**Cloud Console:**
```
https://console.cloud.google.com/monitoring?project=vendor-risk-digital-twin
```

**gcloud CLI:**
```bash
# List metrics
gcloud monitoring metrics list --project=vendor-risk-digital-twin
```

### Viewing Alerts

**Cloud Console:**
```
https://console.cloud.google.com/monitoring/alerting?project=vendor-risk-digital-twin
```

**gcloud CLI:**
```bash
# List alerting policies
gcloud alpha monitoring policies list --project=vendor-risk-digital-twin
```

### Creating Custom Queries

**Example: Discovery Function Success Rate**
```
resource.type="cloud_function"
resource.labels.function_name="vendor-discovery"
jsonPayload.message=~"Discovery complete"
```

**Example: Simulation Service Errors**
```
resource.type="cloud_run_revision"
resource.labels.service_name="simulation-service"
severity>=ERROR
```

---

## Best Practices

### 1. Structured Logging

Ensure all services use structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)

# Good: Structured logging
logger.info("Discovery complete", extra={
    "vendors_found": 4,
    "execution_time": 15.3,
    "project_id": "vendor-risk-digital-twin"
})

# Bad: Unstructured logging
logger.info("Discovery complete. Found 4 vendors in 15.3 seconds")
```

### 2. Meaningful Metrics

Track metrics that matter:
- Business metrics (discoveries, simulations)
- Performance metrics (latency, throughput)
- Error metrics (error rate, error types)
- Resource metrics (CPU, memory usage)

### 3. Appropriate Alert Thresholds

Set thresholds based on:
- Historical data
- Business requirements
- SLA targets
- User impact

### 4. Dashboard Organization

Organize dashboards by:
- Service (one dashboard per service)
- Purpose (health, performance, business)
- Audience (operational, business, technical)

---

## Troubleshooting

### Issue: Metrics Not Appearing

**Symptoms:** Dashboards show "No data"

**Solutions:**
1. Verify services are generating logs
2. Check log filters in metrics
3. Ensure time range is correct
4. Verify APIs are enabled

### Issue: Alerts Not Firing

**Symptoms:** Alerts configured but not triggering

**Solutions:**
1. Verify notification channels are configured
2. Check alert thresholds are appropriate
3. Verify metric filters are correct
4. Test alerts manually

### Issue: High Alert Volume

**Symptoms:** Too many alerts

**Solutions:**
1. Adjust alert thresholds
2. Increase alert duration
3. Use alert grouping
4. Filter out noise

---

## Next Steps

After Phase 7 is complete:

1. **Monitor for 1 week** to establish baselines
2. **Adjust thresholds** based on actual data
3. **Refine dashboards** based on usage
4. **Document runbooks** for common alerts
5. **Proceed to Phase 8** (CI/CD Pipeline)

---

## Related Documentation

- **Benefits**: `docs/gcp-integration/phase7/phase7_benefits.md`
- **Readiness Check**: `docs/gcp-integration/phase7/phase7_readiness_check.md`
- **GCP Integration Roadmap**: `docs/gcp-integration/gcp_integration_roadmap.md`

---

**Last Updated:** 2025-11-29  
**Status:** 🚧 In Progress

