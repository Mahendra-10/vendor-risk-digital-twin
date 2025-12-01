# Cloud Scheduler Logs Troubleshooting

## Issue: Empty Logs When Querying Discovery Function

### Problem
When running:
```bash
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=vendor-discovery"
```

You get an empty array `[]`.

### Root Cause
The `vendor-discovery` function is a **Cloud Functions Gen2**, which runs on **Cloud Run** infrastructure. Therefore, logs are stored under `cloud_run_revision` resource type, not `cloud_function`.

---

## ✅ Correct Log Queries

### For Cloud Functions Gen2 (Cloud Run)

```bash
# View Discovery Function logs (Gen2)
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=vendor-discovery" \
  --limit=10 \
  --format="table(timestamp,severity,textPayload)"

# View with JSON format
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=vendor-discovery" \
  --limit=10 \
  --format=json
```

### For Cloud Scheduler Execution Logs

```bash
# View Cloud Scheduler job execution logs
gcloud logging read \
  "resource.type=cloud_scheduler_job AND resource.labels.job_id=daily-vendor-discovery" \
  --limit=10 \
  --format="table(timestamp,severity,textPayload,jsonPayload.status.code)"
```

### For Graph Loader Function (Gen2)

```bash
# View Graph Loader logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=graph-loader" \
  --limit=10 \
  --format="table(timestamp,severity,textPayload)"
```

---

## 📊 Verification Commands

### 1. Check Function Type

```bash
# List Cloud Functions (shows both Gen1 and Gen2)
gcloud functions list --filter="name:vendor-discovery"

# List Cloud Run services (Gen2 functions appear here)
gcloud run services list --filter="metadata.name:vendor-discovery"
```

### 2. Check Latest Execution

```bash
# Check Cloud Scheduler job status
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --format="value(state,lastAttemptTime)"

# Check function logs (Gen2)
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=vendor-discovery" \
  --limit=5 \
  --freshness=1d \
  --format="table(timestamp,severity,textPayload)"
```

### 3. Verify Results in Cloud Storage

```bash
# List discovery results
gsutil ls -l gs://vendor-risk-digital-twin-discovery-results/discoveries/

# View latest discovery file
gsutil ls -t gs://vendor-risk-digital-twin-discovery-results/discoveries/ | head -1 | xargs gsutil cat
```

---

## 🔍 Understanding the Logs

### Successful Execution Logs

When the Discovery Function runs successfully, you'll see logs like:

```
2025-11-30 10:00:07,088 - main - INFO - Starting vendor discovery for project: vendor-risk-digital-twin
2025-11-30 10:00:07,158 - main - INFO - Discovering Cloud Functions...
2025-11-30 10:00:07,573 - main - INFO - Discovering Cloud Run services...
2025-11-30 10:00:07,950 - main - INFO - Analyzing vendor dependencies...
2025-11-30 10:00:07,950 - main - INFO - Discovery complete. Found 4 vendors
2025-11-30 10:00:08,206 - main - INFO - Results stored in Cloud Storage: gs://vendor-risk-digital-twin-discovery-results/discoveries/20251130_100007_discovery.json
```

### Cloud Scheduler Execution Logs

Cloud Scheduler logs show:
- Job trigger time
- HTTP response status
- Success/failure codes

---

## 📋 Resource Type Reference

| Function Type | Resource Type | Service Label |
|--------------|---------------|---------------|
| Cloud Functions Gen1 | `cloud_function` | `function_name` |
| Cloud Functions Gen2 | `cloud_run_revision` | `service_name` |
| Cloud Run Service | `cloud_run_revision` | `service_name` |

---

## 🎯 Quick Reference Commands

### Check if Job Ran Today

```bash
# Get last execution time
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --format="value(lastAttemptTime)"
```

### View Latest Function Logs

```bash
# Discovery Function (Gen2)
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=vendor-discovery" \
  --limit=10 \
  --freshness=1d \
  --format="table(timestamp,severity,textPayload)"
```

### Check for Errors

```bash
# Discovery Function errors
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=vendor-discovery AND severity>=ERROR" \
  --limit=10 \
  --freshness=7d
```

---

## ✅ Verification Checklist

After Cloud Scheduler runs, verify:

- [ ] Cloud Scheduler shows last execution time
- [ ] Discovery Function logs show successful execution
- [ ] Cloud Storage has new discovery file
- [ ] Graph Loader was triggered (check its logs)
- [ ] Neo4j has updated data (optional)

---

## 🐛 Common Issues

### Issue 1: No Logs Found
**Solution:** Use `cloud_run_revision` instead of `cloud_function` for Gen2 functions.

### Issue 2: Logs Too Old
**Solution:** Use `--freshness=1d` or `--freshness=7d` to limit time range.

### Issue 3: Too Many Logs
**Solution:** Add `--limit=10` and filter by severity or text.

---

**Last Updated:** 2025-11-30  
**Status:** ✅ Working

