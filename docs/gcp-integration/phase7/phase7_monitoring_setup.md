# Phase 7: Monitoring & Observability - Setup & Usage Guide

**Status:** ✅ Operational  
**Date Completed:** 2025-11-30  
**Last Updated:** 2025-11-30

---

## Table of Contents

1. [Overview](#overview)
2. [What Was Set Up](#what-was-set-up)
3. [Accessing the Dashboard](#accessing-the-dashboard)
4. [Understanding the Metrics](#understanding-the-metrics)
5. [Using the Dashboard](#using-the-dashboard)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Maintenance](#maintenance)

---

## Overview

Phase 7 implements comprehensive monitoring and observability for the Vendor Risk Digital Twin system. This enables real-time visibility into:

- **Service Health**: Execution counts, success rates, and performance metrics
- **System Performance**: Latency, throughput, and resource utilization
- **Error Tracking**: Failed executions and error patterns
- **Automation Status**: Discovery and data loading workflows

### Key Components

1. **Cloud Monitoring Dashboards**: Visual representation of key metrics
2. **Log-Based Metrics**: Custom metrics derived from Cloud Logging
3. **Alerting Policies**: Automated notifications for critical issues
4. **Service Metrics**: Built-in GCP metrics for Cloud Functions and Cloud Run

---

## What Was Set Up

### 1. Cloud Monitoring Dashboard

**Dashboard Name:** `Vendor Risk Digital Twin - Service Health`

**Location:** [Cloud Console - Monitoring Dashboards](https://console.cloud.google.com/monitoring/dashboards)

**Charts Included:**

1. **Discovery Function - Execution Count**
   - Metric: `cloudfunctions.googleapis.com/function/execution_count`
   - Shows: Number of times Discovery Function executed
   - Time Range: Last 1 hour (configurable)

2. **Discovery Function - Execution Time (P50)**
   - Metric: `cloudfunctions.googleapis.com/function/execution_times`
   - Shows: Median execution time in milliseconds
   - Aggregation: 50th percentile

3. **Simulation Service - Request Count**
   - Metric: `run.googleapis.com/request_count`
   - Shows: Number of simulation requests
   - Time Range: Last 1 hour (configurable)

4. **Simulation Service - Request Latency**
   - Metric: `run.googleapis.com/request_latencies`
   - Shows: Request latency in milliseconds
   - Aggregation: 95th percentile

5. **Graph Loader - Execution Count**
   - Metric: `cloudfunctions.googleapis.com/function/execution_count`
   - Shows: Number of times Graph Loader executed
   - Trigger: Pub/Sub events from Discovery

6. **BigQuery Loader - Execution Count**
   - Metric: `cloudfunctions.googleapis.com/function/execution_count`
   - Shows: Number of times BigQuery Loader executed
   - Trigger: Pub/Sub events from Simulation Service

### 2. Log-Based Metrics

Created via `scripts/setup_monitoring.sh`:

- `discovery_success_rate`: Success rate of Discovery Function
- `simulation_error_rate`: Error rate of Simulation Service
- `graph_loader_processing_time`: Processing time for Graph Loader

### 3. Alerting Policies

Basic alerting policies created for:
- High error rates
- Service unavailability
- Performance degradation

**Note:** Alerting policies require notification channels (email/Slack) to be configured.

### 4. Setup Script

**File:** `scripts/setup_monitoring.sh`

**What it does:**
- Enables Monitoring and Logging APIs
- Creates log-based metrics
- Sets up basic alerting policies
- Configures foundation for monitoring

---

## Accessing the Dashboard

### Method 1: Cloud Console (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Monitoring** → **Dashboards**
3. Find **"Vendor Risk Digital Twin - Service Health"**
4. Click to open

**Direct Link:**
```
https://console.cloud.google.com/monitoring/dashboards?project=vendor-risk-digital-twin
```

### Method 2: Using Dashboard JSON

1. Download the dashboard JSON: `docs/gcp-integration/dashboard_simple.json`
2. Go to [Cloud Console - Dashboards](https://console.cloud.google.com/monitoring/dashboards)
3. Click **"Create Dashboard"**
4. Click **"..."** (three dots) → **"Import Dashboard"**
5. Upload the JSON file

### Method 3: gcloud CLI

```bash
# List dashboards
gcloud monitoring dashboards list --project=vendor-risk-digital-twin

# Get dashboard details
gcloud monitoring dashboards describe DASHBOARD_ID --project=vendor-risk-digital-twin
```

---

## Understanding the Metrics

### Service Metrics Explained

#### Discovery Function Metrics

**Execution Count:**
- **What it shows:** Number of times the Discovery Function ran
- **Expected values:** 1 per day (from Cloud Scheduler) or manual triggers
- **What to look for:** 
  - ✅ Consistent daily executions
  - ⚠️ Missing executions (check Cloud Scheduler)
  - ⚠️ Unexpected spikes (may indicate issues)

**Execution Time (P50):**
- **What it shows:** Median time to complete discovery
- **Expected values:** 15-30 seconds
- **What to look for:**
  - ✅ Consistent execution times
  - ⚠️ Increasing times (may indicate performance issues)
  - ⚠️ Very long times (>60s) may indicate errors

#### Simulation Service Metrics

**Request Count:**
- **What it shows:** Number of simulation requests
- **Expected values:** Varies based on usage
- **What to look for:**
  - ✅ Normal traffic patterns
  - ⚠️ Sudden drops (may indicate service issues)
  - ⚠️ Unexpected spikes (may indicate load issues)

**Request Latency (P95):**
- **What it shows:** 95th percentile request latency
- **Expected values:** < 5 seconds for most requests
- **What to look for:**
  - ✅ Consistent low latency
  - ⚠️ Increasing latency (may indicate performance issues)
  - ⚠️ Very high latency (>10s) may indicate errors

#### Graph Loader Metrics

**Execution Count:**
- **What it shows:** Number of times Graph Loader processed discovery events
- **Expected values:** Should match Discovery Function executions
- **What to look for:**
  - ✅ Matches Discovery Function count
  - ⚠️ Missing executions (check Pub/Sub and Eventarc)
  - ⚠️ More executions than Discovery (may indicate duplicate events)

#### BigQuery Loader Metrics

**Execution Count:**
- **What it shows:** Number of times BigQuery Loader processed simulation results
- **Expected values:** Should match Simulation Service requests
- **What to look for:**
  - ✅ Matches Simulation Service count
  - ⚠️ Missing executions (check Pub/Sub)
  - ⚠️ Errors in logs (check function logs)

### Metric Types

- **GAUGE**: Current value (e.g., active instances)
- **DELTA**: Change over time (e.g., execution count)
- **CUMULATIVE**: Total since start (e.g., total requests)

---

## Using the Dashboard

### Viewing Metrics

1. **Select Time Range:**
   - Click the time range selector (top right)
   - Choose: Last 1 hour, Last 6 hours, Last 24 hours, Custom range
   - **Tip:** Use "Last 24 hours" to see daily patterns

2. **Zoom into Specific Periods:**
   - Click and drag on a chart to zoom
   - Use the time range selector to reset

3. **Compare Metrics:**
   - View multiple charts side-by-side
   - Look for correlations (e.g., Discovery → Graph Loader)

### Interpreting Data

#### Normal Operation

**What you should see:**
- ✅ Discovery Function: 1 execution per day (from Cloud Scheduler)
- ✅ Graph Loader: 1 execution per day (triggered by Discovery)
- ✅ Simulation Service: Executions when simulations are run
- ✅ BigQuery Loader: Executions matching Simulation Service

**Example Timeline:**
```
00:00 - Cloud Scheduler triggers Discovery
00:01 - Discovery Function executes (15-30 seconds)
00:02 - Discovery publishes to Pub/Sub
00:02 - Graph Loader triggered via Eventarc
00:03 - Graph Loader executes (5-10 seconds)
```

#### Troubleshooting with Dashboard

**Issue: Graph Loader shows no data**
- **Check:** Discovery Function execution count
- **If Discovery ran:** Check Pub/Sub and Eventarc triggers
- **If Discovery didn't run:** Check Cloud Scheduler

**Issue: High latency in Simulation Service**
- **Check:** Request count (may indicate high load)
- **Check:** Error logs for specific failures
- **Action:** May need to scale Cloud Run service

**Issue: Missing executions**
- **Check:** All service charts for gaps
- **Check:** Cloud Scheduler logs
- **Check:** Pub/Sub subscription status

### Exporting Data

1. **Export Chart as Image:**
   - Click **"..."** (three dots) on chart
   - Select **"Download as PNG"**

2. **Export Metrics Data:**
   - Use Cloud Monitoring API
   - Or use `gcloud monitoring` commands

---

## Troubleshooting

### Common Issues

#### 1. "No data is available for the selected time frame"

**Possible Causes:**
- Services haven't run recently
- Time range is too narrow
- Metrics haven't propagated yet (wait 1-2 minutes)

**Solutions:**
1. Expand time range to "Last 24 hours"
2. Manually trigger a service to generate data
3. Wait 1-2 minutes for metrics to appear

**Example:**
```bash
# Manually trigger Discovery Function
gcloud scheduler jobs run daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin
```

#### 2. Graph Loader Not Showing Data

**Possible Causes:**
- Discovery Function didn't publish to Pub/Sub
- Eventarc trigger not configured correctly
- Graph Loader function failed

**Solutions:**
1. Check Discovery Function logs for Pub/Sub publishing
2. Verify Eventarc trigger exists:
   ```bash
   gcloud eventarc triggers list --location=us-central1
   ```
3. Check Graph Loader logs:
   ```bash
   gcloud functions logs read graph-loader --gen2 --region=us-central1
   ```
4. Manually trigger Graph Loader (see below)

**Manual Trigger:**
```bash
# Publish test message to Pub/Sub
cat > /tmp/discovery_event.json << EOF
{
  "project_id": "vendor-risk-digital-twin",
  "storage_path": "gs://vendor-risk-digital-twin-discovery-results/discoveries/LATEST_FILE.json",
  "discovery_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": {
    "cloud_functions": 2,
    "cloud_run_services": 2,
    "vendors_found": 4
  }
}
EOF

gcloud pubsub topics publish vendor-discovery-events \
  --message="$(cat /tmp/discovery_event.json)" \
  --project=vendor-risk-digital-twin
```

#### 3. Dashboard Charts Not Loading

**Possible Causes:**
- Dashboard JSON has errors
- Metric filters are incorrect
- Permissions issues

**Solutions:**
1. Check dashboard JSON syntax
2. Verify metric names are correct
3. Check IAM permissions for Monitoring API

#### 4. Metrics Delayed or Missing

**Possible Causes:**
- Metrics take 1-2 minutes to propagate
- Service didn't execute
- Metric collection disabled

**Solutions:**
1. Wait 1-2 minutes after service execution
2. Verify service actually ran (check logs)
3. Check Monitoring API is enabled

### Getting Help

**Check Logs:**
```bash
# Discovery Function
gcloud functions logs read vendor-discovery --gen2 --region=us-central1

# Graph Loader
gcloud functions logs read graph-loader --gen2 --region=us-central1

# Simulation Service
gcloud run services logs read simulation-service --region=us-central1
```

**Check Metrics Directly:**
```bash
# List available metrics
gcloud monitoring metrics list --project=vendor-risk-digital-twin

# Query specific metric
gcloud monitoring time-series list \
  --filter='metric.type="cloudfunctions.googleapis.com/function/execution_count"' \
  --project=vendor-risk-digital-twin
```

---

## Best Practices

### 1. Regular Monitoring

- **Daily:** Check dashboard for service health
- **Weekly:** Review trends and patterns
- **Monthly:** Analyze performance and optimize

### 2. Setting Up Alerts

1. **Create Notification Channels:**
   - Email: For critical alerts
   - Slack: For team notifications
   - PagerDuty: For on-call escalation

2. **Configure Alerting Policies:**
   - High error rates (>5%)
   - Service unavailability
   - Performance degradation (>2x normal latency)

3. **Test Alerts:**
   - Verify alerts fire correctly
   - Ensure notification channels work
   - Document alert response procedures

### 3. Dashboard Maintenance

- **Update Metrics:** Add new metrics as services evolve
- **Review Charts:** Remove unused or redundant charts
- **Optimize Layout:** Organize charts by service or function

### 4. Documentation

- **Document Custom Metrics:** Explain what each metric means
- **Update Runbooks:** Include dashboard links in troubleshooting guides
- **Share Dashboards:** Make dashboards accessible to team members

---

## Maintenance

### Regular Tasks

#### Weekly

- Review dashboard for anomalies
- Check alerting policies are working
- Verify all services are being monitored

#### Monthly

- Review and optimize dashboard layout
- Update alerting thresholds based on trends
- Document any new metrics or services

#### Quarterly

- Review monitoring costs
- Optimize log-based metrics (remove unused ones)
- Update documentation

### Updating the Dashboard

1. **Edit in Cloud Console:**
   - Go to Dashboard → Edit
   - Add/remove/modify charts
   - Save changes

2. **Update JSON File:**
   - Edit `docs/gcp-integration/dashboard_simple.json`
   - Import updated JSON to Cloud Console
   - Document changes

### Adding New Metrics

1. **Identify Metric:**
   - Determine what you want to monitor
   - Check if metric exists in GCP
   - Create log-based metric if needed

2. **Add to Dashboard:**
   - Edit dashboard JSON
   - Add new chart configuration
   - Import to Cloud Console

3. **Document:**
   - Update this guide
   - Explain what the metric shows
   - Document expected values

---

## Quick Reference

### Dashboard Access

- **URL:** https://console.cloud.google.com/monitoring/dashboards?project=vendor-risk-digital-twin
- **Dashboard Name:** Vendor Risk Digital Twin - Service Health

### Key Metrics

| Service | Metric | Expected Value |
|---------|--------|----------------|
| Discovery Function | Execution Count | 1/day |
| Discovery Function | Execution Time | 15-30 seconds |
| Simulation Service | Request Count | Varies |
| Simulation Service | Latency (P95) | < 5 seconds |
| Graph Loader | Execution Count | Matches Discovery |
| BigQuery Loader | Execution Count | Matches Simulation |

### Useful Commands

```bash
# View dashboard
gcloud monitoring dashboards list --project=vendor-risk-digital-twin

# Check metrics
gcloud monitoring metrics list --project=vendor-risk-digital-twin

# View logs
gcloud functions logs read FUNCTION_NAME --gen2 --region=us-central1

# Trigger Discovery manually
gcloud scheduler jobs run daily-vendor-discovery --location=us-central1
```

---

## Summary

Phase 7 Monitoring & Observability provides:

✅ **Real-time visibility** into all services  
✅ **Performance tracking** for optimization  
✅ **Error detection** for quick troubleshooting  
✅ **Automation monitoring** for reliability  

The dashboard is operational and showing metrics for all major services. Regular monitoring helps ensure system reliability and performance.

---

**Last Updated:** 2025-11-30  
**Status:** ✅ Operational  
**Next Steps:** Configure alerting policies and notification channels for proactive monitoring

