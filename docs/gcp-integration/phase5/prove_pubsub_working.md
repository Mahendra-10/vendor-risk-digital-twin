# How to Prove Pub/Sub is Actually Working

**The Problem:** Just seeing data appear in BigQuery doesn't prove Pub/Sub was used. The simulation service could write directly to BigQuery, or the BigQuery loader could be called directly.

**The Solution:** We need to verify the actual Pub/Sub message flow.

---

## 🔍 Evidence That Proves Pub/Sub is Working

### Evidence 1: Check Simulation Service Code
**What to verify:** The simulation service publishes to Pub/Sub, not directly to BigQuery.

```bash
# Check the code - simulation service should call publish_simulation_result()
grep -A 5 "publish_simulation_result" cloud_run/simulation-service/app.py
```

**Expected:** Code shows `publish_simulation_result(result)` which publishes to Pub/Sub topic `simulation-results`.

**✅ Proof:** If the code doesn't have direct BigQuery writes, it must use Pub/Sub.

---

### Evidence 2: Check BigQuery Loader Function Configuration
**What to verify:** The BigQuery loader function is triggered by Pub/Sub, not HTTP.

```bash
# Check function trigger type
gcloud functions describe bigquery-loader --region=us-central1 \
  --format="value(eventTrigger.eventType,eventTrigger.pubsubTopic)"
```

**Expected Output:**
```
google.cloud.pubsub.topic.v1.messagePublished
projects/vendor-risk-digital-twin/topics/simulation-results
```

**✅ Proof:** Function is configured to trigger ONLY from Pub/Sub messages.

---

### Evidence 3: Temporarily Disable BigQuery Loader Function
**What to verify:** If we disable the function, data should NOT appear in BigQuery (proving it's the only path).

```bash
# Disable the function
gcloud functions update bigquery-loader --region=us-central1 --no-allow-unauthenticated

# Or delete the function temporarily
# gcloud functions delete bigquery-loader --region=us-central1
```

**Then:**
1. Run a simulation
2. Wait 30 seconds
3. Check BigQuery count - should NOT increase

**✅ Proof:** If disabling the function stops BigQuery writes, it proves the function (triggered by Pub/Sub) is the only path.

**⚠️ Remember to re-enable:**
```bash
gcloud functions update bigquery-loader --region=us-central1 --allow-unauthenticated
```

---

### Evidence 4: Check Pub/Sub Message Delivery Metrics
**What to verify:** Messages are actually being published and delivered.

```bash
# Check Pub/Sub topic message count (via Console or API)
# Go to: https://console.cloud.google.com/cloudpubsub/topic/detail/simulation-results?project=vendor-risk-digital-twin

# Or check subscription metrics
gcloud pubsub subscriptions describe simulation-results-to-bigquery-subscription \
  --format="yaml(pushConfig,ackDeadlineSeconds,messageRetentionDuration)"
```

**✅ Proof:** If messages are being delivered to the subscription, Pub/Sub is working.

---

### Evidence 5: Manually Publish a Test Message
**What to verify:** Publishing directly to Pub/Sub triggers the BigQuery loader.

```bash
# 1. Get current count
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`'

# 2. Publish a test message directly to Pub/Sub
gcloud pubsub topics publish simulation-results \
  --message='{
    "project_id": "vendor-risk-digital-twin",
    "simulation_id": "test-pubsub-direct-123",
    "vendor": "TestVendor",
    "duration_hours": 1,
    "overall_impact_score": 0.5,
    "operational_impact": {"impact_score": 0.4, "service_count": 1, "customers_affected": 100},
    "financial_impact": {"impact_score": 0.3, "revenue_loss": 1000, "total_cost": 1500},
    "compliance_impact": {"impact_score": 0.2},
    "timestamp": "2025-01-15T12:00:00Z",
    "full_result": {
      "simulation_id": "test-pubsub-direct-123",
      "vendor": "TestVendor",
      "duration_hours": 1,
      "overall_impact_score": 0.5,
      "operational_impact": {"impact_score": 0.4, "service_count": 1, "customers_affected": 100},
      "financial_impact": {"impact_score": 0.3, "revenue_loss": 1000, "total_cost": 1500},
      "compliance_impact": {"impact_score": 0.2},
      "timestamp": "2025-01-15T12:00:00Z"
    }
  }'

# 3. Wait 10 seconds
sleep 10

# 4. Check count again - should increase
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`'

# 5. Verify the test record exists
bq query --use_legacy_sql=false \
  'SELECT simulation_id, vendor_name FROM `vendor-risk-digital-twin.vendor_risk.simulations` 
   WHERE simulation_id = "test-pubsub-direct-123"'
```

**✅ Proof:** If publishing directly to Pub/Sub creates a BigQuery record, it proves:
- Pub/Sub → BigQuery Loader → BigQuery flow works
- The function is triggered by Pub/Sub messages

---

### Evidence 6: Check Function Execution Logs
**What to verify:** The BigQuery loader function logs show it received a Pub/Sub event.

```bash
# Check recent executions
gcloud functions logs read bigquery-loader --region=us-central1 --limit=20

# Look for:
# - "📥 Received simulation result event"
# - Function execution triggered by Pub/Sub
# - No HTTP request logs (which would indicate direct calls)
```

**✅ Proof:** If logs show Pub/Sub event triggers (not HTTP), it proves Pub/Sub is the trigger.

---

### Evidence 7: Check for Direct BigQuery Writes
**What to verify:** The simulation service does NOT write directly to BigQuery.

```bash
# Search simulation service code for BigQuery
grep -r "bigquery\|BigQuery\|insert_rows" cloud_run/simulation-service/

# Should return: No matches (or only in comments)
```

**✅ Proof:** If simulation service has no BigQuery code, it must use Pub/Sub.

---

## 🎯 The Definitive Test

**Run this complete test to prove Pub/Sub is working:**

```bash
#!/bin/bash

echo "=== Step 1: Verify simulation service doesn't write to BigQuery directly ==="
grep -r "bigquery\|BigQuery" cloud_run/simulation-service/app.py
echo "✅ If no matches, service uses Pub/Sub"

echo ""
echo "=== Step 2: Verify BigQuery loader is triggered by Pub/Sub ==="
gcloud functions describe bigquery-loader --region=us-central1 \
  --format="value(eventTrigger.eventType)"
echo "✅ Should show: google.cloud.pubsub.topic.v1.messagePublished"

echo ""
echo "=== Step 3: Get baseline BigQuery count ==="
BEFORE=$(bq query --use_legacy_sql=false --format=csv \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`' | tail -1)
echo "Current count: $BEFORE"

echo ""
echo "=== Step 4: Publish test message directly to Pub/Sub ==="
gcloud pubsub topics publish simulation-results \
  --message='{"project_id":"vendor-risk-digital-twin","simulation_id":"test-pubsub-proof-'$(date +%s)'","vendor":"PubSubTest","duration_hours":1,"overall_impact_score":0.5,"operational_impact":{"impact_score":0.4,"service_count":1,"customers_affected":100},"financial_impact":{"impact_score":0.3,"revenue_loss":1000,"total_cost":1500},"compliance_impact":{"impact_score":0.2},"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","full_result":{"simulation_id":"test-pubsub-proof-'$(date +%s)'","vendor":"PubSubTest","duration_hours":1,"overall_impact_score":0.5,"operational_impact":{"impact_score":0.4,"service_count":1,"customers_affected":100},"financial_impact":{"impact_score":0.3,"revenue_loss":1000,"total_cost":1500},"compliance_impact":{"impact_score":0.2},"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}}'

echo "Waiting 15 seconds for Pub/Sub delivery..."
sleep 15

echo ""
echo "=== Step 5: Check if count increased ==="
AFTER=$(bq query --use_legacy_sql=false --format=csv \
  'SELECT COUNT(*) as count FROM `vendor-risk-digital-twin.vendor_risk.simulations`' | tail -1)
echo "New count: $AFTER"

if [ "$AFTER" -gt "$BEFORE" ]; then
    echo "✅ SUCCESS: Pub/Sub → BigQuery Loader → BigQuery flow is working!"
    echo "   Count increased from $BEFORE to $AFTER"
else
    echo "❌ FAILED: Count did not increase. Pub/Sub may not be working."
fi
```

---

## ✅ Conclusion

**Pub/Sub is proven to be working if:**
1. ✅ Simulation service code shows `publish_simulation_result()` (no direct BigQuery writes)
2. ✅ BigQuery loader function has Pub/Sub trigger (not HTTP trigger)
3. ✅ Publishing directly to Pub/Sub topic creates BigQuery records
4. ✅ Function logs show Pub/Sub event triggers
5. ✅ Disabling the function stops BigQuery writes

**If all 5 conditions are true, Pub/Sub is definitely working!**

