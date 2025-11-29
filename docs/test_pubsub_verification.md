# Quick Test Guide: Verify Pub/Sub Automation Works

**Purpose:** Simple steps to verify that your event-driven automation is working end-to-end.

---

## 🧪 Test 1: Simulation → BigQuery Flow

This tests: **Simulation completes → Publishes to Pub/Sub → BigQuery Loader automatically saves results**

### Step 1: Get baseline count
```bash
# Count existing simulations in BigQuery
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`'
```

**Note the number** (e.g., `5`)

### Step 2: Run a simulation via Cloud Run
```bash
# Run simulation (this should trigger Pub/Sub → BigQuery automatically)
curl -X POST "https://simulation-service-16418516910.us-central1.run.app/simulate" \
  -H "Content-Type: application/json" \
  -d '{"vendor": "auth0", "duration": 4}'
```

### Step 3: Wait 10-30 seconds
Pub/Sub delivery and BigQuery loading takes a few seconds.

### Step 4: Verify BigQuery count increased
```bash
# Count again - should be +1
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`'
```

**✅ Success if:** Count increased by 1

### Step 5: Check the new record
```bash
# View the latest simulation
bq query --use_legacy_sql=false \
  'SELECT * FROM `vendor-risk-digital-twin.vendor_risk.simulations` 
   ORDER BY timestamp DESC LIMIT 1'
```

**✅ Success if:** You see the simulation you just ran

### Step 6: Check Cloud Function logs
```bash
# Check if BigQuery Loader was triggered
gcloud functions logs read bigquery-loader --region=us-central1 --limit=20
```

**✅ Success if:** You see logs like:
- `📥 Received simulation result event`
- `✅ Loaded simulation result into BigQuery`

---

## 🧪 Test 2: Discovery → Neo4j Flow

This tests: **Discovery completes → Publishes to Pub/Sub → Graph Loader automatically loads into Neo4j**

### Step 1: Check current vendor count in Neo4j
```bash
# Connect to Neo4j and count vendors
# (Use Neo4j Browser or cypher-shell)
# Query: MATCH (v:Vendor) RETURN count(v) as vendor_count
```

Or use the dashboard to see current vendor count.

### Step 2: Trigger discovery (if you have discovery function deployed)
```bash
# Option A: If discovery Cloud Function is deployed
curl -X POST "https://us-central1-vendor-risk-digital-twin.cloudfunctions.net/vendor-discovery" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}'

# Option B: Run discovery locally (but it won't trigger Pub/Sub)
# python scripts/gcp_discovery.py --project-id vendor-risk-digital-twin
```

**Note:** If discovery function isn't deployed, you can manually publish a test event (see Test 3).

### Step 3: Wait 10-30 seconds
Pub/Sub delivery and Neo4j loading takes a few seconds.

### Step 4: Verify Graph Loader was triggered
```bash
# Check Graph Loader logs
gcloud functions logs read graph-loader --region=us-central1 --limit=20
```

**✅ Success if:** You see logs like:
- `📥 Received discovery event for project: vendor-risk-digital-twin`
- `✅ Successfully loaded discovery data into Neo4j`

### Step 5: Check Neo4j for new data
```bash
# In Neo4j Browser, run:
MATCH (v:Vendor) RETURN v.name, v.category LIMIT 10
```

**✅ Success if:** Vendors appear in Neo4j

---

## 🧪 Test 3: Manual Pub/Sub Message Test

Test Pub/Sub directly without running full discovery/simulation.

### Test BigQuery Loader
```bash
# Publish a test message to simulation-results topic
gcloud pubsub topics publish simulation-results \
  --message='{
    "project_id": "vendor-risk-digital-twin",
    "simulation_id": "test-manual-123",
    "vendor": "TestVendor",
    "duration_hours": 1,
    "overall_impact_score": 0.5,
    "operational_impact": {"impact_score": 0.4, "service_count": 1},
    "financial_impact": {"impact_score": 0.3, "revenue_loss": 1000},
    "compliance_impact": {"impact_score": 0.2},
    "timestamp": "2025-01-15T12:00:00Z",
    "full_result": {
      "simulation_id": "test-manual-123",
      "vendor": "TestVendor",
      "duration_hours": 1,
      "overall_impact_score": 0.5,
      "operational_impact": {"impact_score": 0.4, "service_count": 1, "customers_affected": 100},
      "financial_impact": {"impact_score": 0.3, "revenue_loss": 1000, "total_cost": 1500},
      "compliance_impact": {"impact_score": 0.2},
      "timestamp": "2025-01-15T12:00:00Z"
    }
  }'
```

**Wait 10 seconds, then check:**
```bash
# Check BigQuery Loader logs
gcloud functions logs read bigquery-loader --region=us-central1 --limit=10

# Check if test record appears in BigQuery
bq query --use_legacy_sql=false \
  'SELECT * FROM `vendor-risk-digital-twin.vendor_risk.simulations` 
   WHERE simulation_id = "test-manual-123"'
```

**✅ Success if:** Logs show function was triggered AND record appears in BigQuery

### Test Graph Loader
```bash
# Publish a test message to vendor-discovery-events topic
gcloud pubsub topics publish vendor-discovery-events \
  --message='{
    "project_id": "vendor-risk-digital-twin",
    "storage_path": "gs://vendor-risk-digital-twin-discovery-results/discoveries/test.json",
    "discovery_timestamp": "2025-01-15T12:00:00Z",
    "summary": {
      "cloud_functions": 2,
      "cloud_run_services": 1,
      "vendors_found": 1
    }
  }'
```

**Wait 10 seconds, then check:**
```bash
# Check Graph Loader logs
gcloud functions logs read graph-loader --region=us-central1 --limit=10
```

**✅ Success if:** Logs show function was triggered (may fail if Cloud Storage file doesn't exist, but function should still be triggered)

---

## 📊 Monitoring Pub/Sub Activity

### Check message counts
```bash
# Check how many messages are in each subscription
gcloud pubsub subscriptions describe discovery-to-neo4j-subscription \
  --format="value(numUndeliveredMessages)"

gcloud pubsub subscriptions describe simulation-results-to-bigquery-subscription \
  --format="value(numUndeliveredMessages)"
```

**✅ Success if:** Numbers are low (0-5) - means messages are being processed

### Check Pub/Sub metrics in Console
1. Go to: https://console.cloud.google.com/cloudpubsub/topic/list?project=vendor-risk-digital-twin
2. Click on a topic (e.g., `simulation-results`)
3. Check "Messages published" and "Messages delivered" graphs

**✅ Success if:** You see activity when you run tests

---

## 🔍 Troubleshooting

### If BigQuery Loader isn't triggered:

1. **Check function is active:**
   ```bash
   gcloud functions describe bigquery-loader --region=us-central1
   ```
   Should show `state: ACTIVE`

2. **Check Pub/Sub subscription:**
   ```bash
   gcloud pubsub subscriptions describe simulation-results-to-bigquery-subscription
   ```
   Should show `state: ACTIVE`

3. **Check function logs for errors:**
   ```bash
   gcloud functions logs read bigquery-loader --region=us-central1 --limit=50
   ```

4. **Check if message was published:**
   ```bash
   # Pull messages from subscription to see if they're stuck
   gcloud pubsub subscriptions pull simulation-results-to-bigquery-subscription --limit=5
   ```

### If Graph Loader isn't triggered:

1. **Check function is active:**
   ```bash
   gcloud functions describe graph-loader --region=us-central1
   ```

2. **Check function logs:**
   ```bash
   gcloud functions logs read graph-loader --region=us-central1 --limit=50
   ```

3. **Check Neo4j credentials:**
   ```bash
   # Verify secrets exist
   gcloud secrets list | grep neo4j
   ```

---

## ✅ Success Checklist

- [ ] Simulation → BigQuery: New simulation appears in BigQuery automatically
- [ ] BigQuery Loader logs show function was triggered
- [ ] Discovery → Neo4j: Graph Loader logs show function was triggered
- [ ] Pub/Sub subscriptions show low/zero undelivered messages
- [ ] No errors in Cloud Function logs

---

## 🎯 Quick One-Liner Tests

**Test BigQuery automation:**
```bash
# Run simulation and check BigQuery 10 seconds later
curl -X POST "https://simulation-service-16418516910.us-central1.run.app/simulate" \
  -H "Content-Type: application/json" -d '{"vendor": "auth0", "duration": 4}' && \
sleep 10 && \
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`'
```

**Check if functions are being triggered:**
```bash
# Check last 5 log entries from both functions
gcloud functions logs read bigquery-loader --region=us-central1 --limit=5 && \
gcloud functions logs read graph-loader --region=us-central1 --limit=5
```

---

**If all tests pass, your Pub/Sub automation is working! 🎉**

