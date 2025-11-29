# Testing Pub/Sub Automation

**Purpose:** This document provides step-by-step instructions for testing and verifying that the Pub/Sub event-driven automation is working correctly.

**Last Updated:** 2025-11-28

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Testing BigQuery Automation](#testing-bigquery-automation)
4. [Testing Graph Loader Automation](#testing-graph-loader-automation)
5. [End-to-End Testing](#end-to-end-testing)
6. [Verification Checklist](#verification-checklist)
7. [Troubleshooting](#troubleshooting)
8. [Interpreting Results](#interpreting-results)

---

## Overview

### What We're Testing

The automation system has two main flows:

1. **Discovery → Neo4j Flow:**
   - Discovery Function completes → Publishes to `vendor-discovery-events`
   - Graph Loader Function automatically triggered → Loads data into Neo4j

2. **Simulation → BigQuery Flow:**
   - Simulation Service completes → Publishes to `simulation-results`
   - BigQuery Loader Function automatically triggered → Loads data into BigQuery

### Success Criteria

✅ **Automation is working if:**
- Events are published to Pub/Sub topics
- Cloud Functions are automatically triggered
- Data appears in destination systems (Neo4j/BigQuery)
- No manual steps required

---

## Prerequisites

### 1. Verify Infrastructure

```bash
# Check Pub/Sub topics exist
gcloud pubsub topics list

# Expected output:
# projects/vendor-risk-digital-twin/topics/vendor-discovery-events
# projects/vendor-risk-digital-twin/topics/simulation-requests
# projects/vendor-risk-digital-twin/topics/simulation-results
```

```bash
# Check Cloud Functions are deployed
gcloud functions list --regions us-central1

# Expected output:
# graph-loader      ACTIVE
# bigquery-loader   ACTIVE
```

```bash
# Check subscriptions exist
gcloud pubsub subscriptions list

# Expected output should include:
# discovery-to-neo4j-subscription
# simulation-results-to-bigquery-subscription
```

### 2. Required Tools

- `gcloud` CLI configured and authenticated
- Python 3.11+ with virtual environment
- Access to GCP project: `vendor-risk-digital-twin`
- Neo4j Aura credentials in Secret Manager
- BigQuery dataset `vendor_risk` created

---

## Testing BigQuery Automation

### Test Flow: Simulation → BigQuery

**What we're testing:** When a simulation completes, it should automatically save results to BigQuery.

### Step 1: Get Initial BigQuery Count

```bash
cd vendor-risk-digital-twin
source venv/bin/activate

# Count existing simulations
python -c "
from google.cloud import bigquery
client = bigquery.Client(project='vendor-risk-digital-twin')
query = 'SELECT COUNT(*) as count FROM \`vendor-risk-digital-twin.vendor_risk.simulations\`'
result = client.query(query).result()
count = list(result)[0].count
print(f'Current simulations in BigQuery: {count}')
"
```

**Record this number** - we'll verify it increases after testing.

### Step 2: Trigger Simulation via Cloud Run Service

```bash
# Get simulation service URL
SIMULATION_URL=$(gcloud run services describe simulation-service \
  --region us-central1 \
  --format="value(status.url)")

# Trigger simulation
curl -X POST "$SIMULATION_URL/simulate" \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}'
```

**Expected Response:**
```json
{
  "simulation_id": "stripe-20251128020000",
  "vendor": "Stripe",
  "duration_hours": 4,
  "overall_impact_score": 0.32,
  ...
}
```

### Step 3: Wait for Processing

```bash
# Wait 10-15 seconds for Pub/Sub event to be processed
echo "⏳ Waiting 15 seconds for BigQuery loader to process..."
sleep 15
```

### Step 4: Check BigQuery Loader Logs

```bash
# Check if function was triggered
gcloud functions logs read bigquery-loader \
  --region us-central1 \
  --limit 30 \
  | grep -E "(Received|simulation|BigQuery|Loaded|✅|ERROR)"
```

**Expected Log Output:**
```
📥 Received simulation result event
   Simulation ID: stripe-20251128020000
   Vendor: Stripe
✅ Loaded simulation result into BigQuery: stripe-20251128020000
✅ Simulation result successfully loaded into BigQuery
```

### Step 5: Verify Data in BigQuery

```bash
# Verify new simulation appears in BigQuery
python scripts/verify_bigquery.py
```

**Expected Output:**
```
✅ BigQuery Data Verification:
============================================================
  Simulation ID: stripe-20251128020000  ← NEW!
  Vendor: Stripe
  Duration: 4 hours
  Impact Score: 0.32
  ...
```

### Step 6: Count Simulations Again

```bash
# Count simulations again
python -c "
from google.cloud import bigquery
client = bigquery.Client(project='vendor-risk-digital-twin')
query = 'SELECT COUNT(*) as count FROM \`vendor-risk-digital-twin.vendor_risk.simulations\`'
result = client.query(query).result()
count = list(result)[0].count
print(f'New count: {count}')
"
```

**Success Criteria:**
- ✅ Count increased by 1
- ✅ New simulation ID appears in BigQuery
- ✅ BigQuery loader logs show successful processing

---

## Testing Graph Loader Automation

### Test Flow: Discovery → Neo4j

**What we're testing:** When discovery completes, it should automatically load data into Neo4j.

### Step 1: Get Initial Neo4j Count

```bash
cd vendor-risk-digital-twin
source venv/bin/activate

# Count vendors in Neo4j
python -c "
from neo4j import GraphDatabase
from scripts.gcp_secrets import get_secret
import os

project_id = 'vendor-risk-digital-twin'
uri = get_secret('neo4j-uri', project_id)
user = get_secret('neo4j-user', project_id) or 'neo4j'
password = get_secret('neo4j-password', project_id)

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as session:
    result = session.run('MATCH (v:Vendor) RETURN count(v) as count')
    count = result.single()['count']
    print(f'Current vendors in Neo4j: {count}')
driver.close()
"
```

**Record this number** - we'll verify it increases after testing.

### Step 2: Trigger Discovery Function

```bash
# Get discovery function URL
DISCOVERY_URL=$(gcloud functions describe vendor-discovery \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)")

# Trigger discovery
curl -X POST "$DISCOVERY_URL" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}'
```

**Expected Response:**
```json
{
  "body": "{\"success\": true, \"project_id\": \"vendor-risk-digital-twin\", ...}",
  "statusCode": 200
}
```

### Step 3: Verify Event Was Published

```bash
# Check discovery function logs for Pub/Sub publish
gcloud functions logs read vendor-discovery \
  --region us-central1 \
  --limit 20 \
  | grep -E "(Published|Pub/Sub|discovery event)"
```

**Expected Log Output:**
```
✅ Published discovery event to Pub/Sub: [message_id]
```

### Step 4: Wait for Processing

```bash
# Wait 15-20 seconds for Graph Loader to process
echo "⏳ Waiting 20 seconds for Graph Loader to process..."
sleep 20
```

### Step 5: Check Graph Loader Logs

```bash
# Check if function was triggered
gcloud functions logs read graph-loader \
  --region us-central1 \
  --limit 50 \
  | grep -E "(📥|Received|discovery event|Neo4j|Loaded|✅|Fetched|ERROR|Failed)"
```

**Expected Log Output:**
```
📥 Received discovery event for project: vendor-risk-digital-twin
   Storage path: gs://bucket/discoveries/...
✅ Fetched discovery results from gs://...
✅ Neo4j credentials loaded (URI: neo4j+s://...)
✅ Successfully loaded discovery data into Neo4j
✅ Discovery data successfully loaded into Neo4j
```

### Step 6: Verify Data in Neo4j

```bash
# Count vendors again
python -c "
from neo4j import GraphDatabase
from scripts.gcp_secrets import get_secret

project_id = 'vendor-risk-digital-twin'
uri = get_secret('neo4j-uri', project_id)
user = get_secret('neo4j-user', project_id) or 'neo4j'
password = get_secret('neo4j-password', project_id)

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as session:
    result = session.run('MATCH (v:Vendor) RETURN count(v) as count')
    count = result.single()['count']
    print(f'New vendor count: {count}')
    
    # List vendors
    result = session.run('MATCH (v:Vendor) RETURN v.name as name ORDER BY name')
    vendors = [record['name'] for record in result]
    print(f'Vendors: {vendors}')
driver.close()
"
```

**Success Criteria:**
- ✅ Vendor count increased
- ✅ New vendors appear in Neo4j
- ✅ Graph Loader logs show successful processing

---

## End-to-End Testing

### Complete Workflow Test

This test verifies the entire automation pipeline from start to finish.

### Test Scenario: Full Discovery and Simulation Flow

```bash
# Step 1: Trigger Discovery
echo "🔍 Step 1: Triggering Discovery..."
DISCOVERY_URL=$(gcloud functions describe vendor-discovery \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)")

curl -X POST "$DISCOVERY_URL" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}' \
  > /tmp/discovery_result.json

echo "✅ Discovery triggered"
cat /tmp/discovery_result.json | python3 -m json.tool | head -10

# Step 2: Wait for Graph Loader
echo ""
echo "⏳ Step 2: Waiting 20 seconds for Graph Loader..."
sleep 20

# Step 3: Verify Neo4j
echo ""
echo "📊 Step 3: Verifying Neo4j..."
python scripts/test_neo4j_connection.py

# Step 4: Run Simulation
echo ""
echo "🧪 Step 4: Running Simulation..."
SIMULATION_URL=$(gcloud run services describe simulation-service \
  --region us-central1 \
  --format="value(status.url)")

curl -X POST "$SIMULATION_URL/simulate" \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}' \
  > /tmp/simulation_result.json

echo "✅ Simulation triggered"
cat /tmp/simulation_result.json | python3 -m json.tool | head -15

# Step 5: Wait for BigQuery Loader
echo ""
echo "⏳ Step 5: Waiting 15 seconds for BigQuery Loader..."
sleep 15

# Step 6: Verify BigQuery
echo ""
echo "📊 Step 6: Verifying BigQuery..."
python scripts/verify_bigquery.py | tail -20
```

### Expected Results

**Discovery Flow:**
- ✅ Discovery completes
- ✅ Event published to Pub/Sub
- ✅ Graph Loader triggered automatically
- ✅ Data appears in Neo4j

**Simulation Flow:**
- ✅ Simulation completes
- ✅ Event published to Pub/Sub
- ✅ BigQuery Loader triggered automatically
- ✅ Data appears in BigQuery

---

## Verification Checklist

### ✅ BigQuery Automation Checklist

- [ ] **Step 1:** Count initial simulations in BigQuery
- [ ] **Step 2:** Trigger simulation via Cloud Run service
- [ ] **Step 3:** Wait 15 seconds for processing
- [ ] **Step 4:** Check BigQuery Loader logs show execution
- [ ] **Step 5:** Verify new simulation in BigQuery
- [ ] **Step 6:** Confirm count increased

**Success Indicators:**
- ✅ BigQuery Loader logs show "Received simulation result event"
- ✅ BigQuery Loader logs show "✅ Loaded simulation result into BigQuery"
- ✅ New simulation ID appears in BigQuery
- ✅ Simulation count increased

### ✅ Graph Loader Automation Checklist

- [ ] **Step 1:** Count initial vendors in Neo4j
- [ ] **Step 2:** Trigger discovery function
- [ ] **Step 3:** Verify event published (check discovery logs)
- [ ] **Step 4:** Wait 20 seconds for processing
- [ ] **Step 5:** Check Graph Loader logs show execution
- [ ] **Step 6:** Verify new vendors in Neo4j
- [ ] **Step 7:** Confirm count increased

**Success Indicators:**
- ✅ Discovery logs show "✅ Published discovery event to Pub/Sub"
- ✅ Graph Loader logs show "📥 Received discovery event"
- ✅ Graph Loader logs show "✅ Successfully loaded discovery data into Neo4j"
- ✅ New vendors appear in Neo4j
- ✅ Vendor count increased

---

## Troubleshooting

### Issue: BigQuery Loader Not Triggered

**Symptoms:**
- Simulation completes but no data in BigQuery
- No logs from bigquery-loader function

**Diagnosis:**
```bash
# Check if event was published
gcloud pubsub subscriptions pull simulation-results-to-bigquery-subscription \
  --limit 1

# Check BigQuery Loader function status
gcloud functions describe bigquery-loader \
  --region us-central1 \
  --format="value(state)"

# Check recent logs
gcloud functions logs read bigquery-loader \
  --region us-central1 \
  --limit 50
```

**Solutions:**
1. **Verify function is ACTIVE:**
   ```bash
   gcloud functions list --regions us-central1 | grep bigquery-loader
   ```

2. **Check Pub/Sub subscription:**
   ```bash
   gcloud pubsub subscriptions describe simulation-results-to-bigquery-subscription
   ```

3. **Verify topic exists:**
   ```bash
   gcloud pubsub topics list | grep simulation-results
   ```

4. **Manually publish test event:**
   ```bash
   python3 -c "
   import json
   from google.cloud import pubsub_v1
   from datetime import datetime
   
   publisher = pubsub_v1.PublisherClient()
   topic_path = publisher.topic_path('vendor-risk-digital-twin', 'simulation-results')
   
   event_data = {
       'simulation_id': 'test-manual-' + datetime.utcnow().strftime('%Y%m%d%H%M%S'),
       'vendor': 'Stripe',
       'duration_hours': 4,
       'overall_impact_score': 0.32,
       'full_result': {
           'simulation_id': 'test-manual-' + datetime.utcnow().strftime('%Y%m%d%H%M%S'),
           'vendor': 'Stripe',
           'duration_hours': 4,
           'overall_impact_score': 0.32,
           'operational_impact': {'impact_score': 0.30, 'service_count': 2},
           'financial_impact': {'impact_score': 0.35, 'revenue_loss': 300000},
           'compliance_impact': {'impact_score': 0.25},
           'timestamp': datetime.utcnow().isoformat()
       }
   }
   
   message_data = json.dumps(event_data).encode('utf-8')
   future = publisher.publish(topic_path, message_data)
   message_id = future.result()
   print(f'✅ Published test event: {message_id}')
   "
   ```

### Issue: Graph Loader Not Triggered

**Symptoms:**
- Discovery completes but no data in Neo4j
- No logs from graph-loader function

**Diagnosis:**
```bash
# Check if event was published
gcloud pubsub subscriptions pull discovery-to-neo4j-subscription \
  --limit 1

# Check Graph Loader function status
gcloud functions describe graph-loader \
  --region us-central1 \
  --format="value(state)"

# Check recent logs
gcloud functions logs read graph-loader \
  --region us-central1 \
  --limit 50
```

**Solutions:**
1. **Verify function is ACTIVE:**
   ```bash
   gcloud functions list --regions us-central1 | grep graph-loader
   ```

2. **Check Neo4j credentials:**
   ```bash
   # Verify secrets exist
   gcloud secrets list | grep neo4j
   
   # Verify function has access
   gcloud functions describe graph-loader \
     --region us-central1 \
     --format="get(serviceConfig.secretEnvironmentVariables)"
   ```

3. **Manually publish test event:**
   ```bash
   python3 -c "
   import json
   from google.cloud import pubsub_v1
   
   publisher = pubsub_v1.PublisherClient()
   topic_path = publisher.topic_path('vendor-risk-digital-twin', 'vendor-discovery-events')
   
   event_data = {
       'project_id': 'vendor-risk-digital-twin',
       'storage_path': 'gs://vendor-risk-digital-twin-discovery-results/discoveries/20251128_015102_discovery.json',
       'discovery_timestamp': '2025-11-28T02:00:00Z',
       'summary': {
           'cloud_functions': 0,
           'cloud_run_services': 8,
           'vendors_found': 4
       }
   }
   
   message_data = json.dumps(event_data).encode('utf-8')
   future = publisher.publish(topic_path, message_data)
   message_id = future.result()
   print(f'✅ Published test event: {message_id}')
   "
   ```

### Issue: Events Published But Not Processed

**Symptoms:**
- Events appear in Pub/Sub topics
- But Cloud Functions not triggered

**Diagnosis:**
```bash
# Check subscription has messages
gcloud pubsub subscriptions pull discovery-to-neo4j-subscription --limit 5

# Check function trigger configuration
gcloud functions describe graph-loader \
  --region us-central1 \
  --format="get(eventTrigger)"
```

**Solutions:**
1. **Verify trigger is configured:**
   ```bash
   gcloud functions describe graph-loader \
     --region us-central1 \
     --format="get(eventTrigger.pubsubTopic)"
   ```
   Should show: `projects/vendor-risk-digital-twin/topics/vendor-discovery-events`

2. **Check IAM permissions:**
   ```bash
   # Function service account needs pubsub.subscriber role
   gcloud projects get-iam-policy vendor-risk-digital-twin \
     --flatten="bindings[].members" \
     --filter="bindings.members:*compute@developer.gserviceaccount.com"
   ```

3. **Redeploy function:**
   ```bash
   cd cloud_functions/graph_loader
   bash deploy.sh
   ```

### Issue: Credentials Not Found

**Symptoms:**
- Graph Loader logs show "Neo4j credentials not configured"
- Function fails to connect to Neo4j

**Solutions:**
1. **Verify secrets exist:**
   ```bash
   gcloud secrets list | grep neo4j
   ```

2. **Verify function has secret access:**
   ```bash
   gcloud functions describe graph-loader \
     --region us-central1 \
     --format="get(serviceConfig.secretEnvironmentVariables)"
   ```

3. **Grant Secret Manager access:**
   ```bash
   gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
     --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

4. **Redeploy with secrets:**
   ```bash
   cd cloud_functions/graph_loader
   bash deploy.sh
   ```

---

## Interpreting Results

### Success Indicators

#### BigQuery Automation Working ✅

**Logs show:**
```
📥 Received simulation result event
   Simulation ID: stripe-20251128020000
   Vendor: Stripe
✅ Loaded simulation result into BigQuery: stripe-20251128020000
✅ Simulation result successfully loaded into BigQuery
```

**BigQuery shows:**
- New simulation ID appears
- Count of simulations increased
- Data matches simulation results

#### Graph Loader Automation Working ✅

**Logs show:**
```
📥 Received discovery event for project: vendor-risk-digital-twin
   Storage path: gs://bucket/discoveries/...
✅ Fetched discovery results from gs://...
✅ Neo4j credentials loaded (URI: neo4j+s://...)
✅ Successfully loaded discovery data into Neo4j
✅ Discovery data successfully loaded into Neo4j
```

**Neo4j shows:**
- New vendors appear
- Count of vendors increased
- Services and relationships created

### Failure Indicators

#### BigQuery Automation Not Working ❌

**Symptoms:**
- No logs from bigquery-loader
- Simulation completes but no data in BigQuery
- Logs show errors

**Check:**
1. Function is ACTIVE?
2. Event published to Pub/Sub?
3. Subscription exists?
4. Function has proper permissions?

#### Graph Loader Automation Not Working ❌

**Symptoms:**
- No logs from graph-loader
- Discovery completes but no data in Neo4j
- Logs show credential errors

**Check:**
1. Function is ACTIVE?
2. Event published to Pub/Sub?
3. Neo4j credentials configured?
4. Secret Manager permissions granted?

---

## Quick Test Script

Save this as `test_automation.sh`:

```bash
#!/bin/bash
# Quick automation test script

set -e

PROJECT_ID="vendor-risk-digital-twin"
REGION="us-central1"

echo "🧪 Testing Pub/Sub Automation"
echo "============================="
echo ""

# Test 1: BigQuery Automation
echo "📊 Test 1: BigQuery Automation"
echo "-------------------------------"

# Get initial count
INITIAL_COUNT=$(python3 -c "
from google.cloud import bigquery
client = bigquery.Client(project='$PROJECT_ID')
result = client.query('SELECT COUNT(*) as count FROM \`$PROJECT_ID.vendor_risk.simulations\`').result()
print(list(result)[0].count)
")

echo "Initial BigQuery count: $INITIAL_COUNT"

# Trigger simulation
echo "Triggering simulation..."
SIMULATION_URL=$(gcloud run services describe simulation-service \
  --region $REGION \
  --format="value(status.url)")

curl -X POST "$SIMULATION_URL/simulate" \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}' > /dev/null 2>&1

echo "⏳ Waiting 15 seconds..."
sleep 15

# Check logs
echo "Checking BigQuery Loader logs..."
gcloud functions logs read bigquery-loader \
  --region $REGION \
  --limit 10 \
  | grep -E "(Received|Loaded|✅)" | tail -3

# Get new count
NEW_COUNT=$(python3 -c "
from google.cloud import bigquery
client = bigquery.Client(project='$PROJECT_ID')
result = client.query('SELECT COUNT(*) as count FROM \`$PROJECT_ID.vendor_risk.simulations\`').result()
print(list(result)[0].count)
")

echo "New BigQuery count: $NEW_COUNT"

if [ "$NEW_COUNT" -gt "$INITIAL_COUNT" ]; then
    echo "✅ BigQuery automation: WORKING"
else
    echo "❌ BigQuery automation: NOT WORKING"
fi

echo ""
echo "📊 Test 2: Graph Loader Automation"
echo "-----------------------------------"

# Trigger discovery
echo "Triggering discovery..."
DISCOVERY_URL=$(gcloud functions describe vendor-discovery \
  --gen2 \
  --region $REGION \
  --format="value(serviceConfig.uri)")

curl -X POST "$DISCOVERY_URL" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\"}" > /dev/null 2>&1

echo "⏳ Waiting 20 seconds..."
sleep 20

# Check logs
echo "Checking Graph Loader logs..."
gcloud functions logs read graph-loader \
  --region $REGION \
  --limit 10 \
  | grep -E "(Received|Loaded|✅|Neo4j)" | tail -3

echo ""
echo "✅ Test complete! Check logs above for results."
```

**Usage:**
```bash
chmod +x test_automation.sh
./test_automation.sh
```

---

## Manual Testing Steps

### Quick Verification (5 minutes)

1. **Check Functions Status:**
   ```bash
   gcloud functions list --regions us-central1 | grep -E "(graph-loader|bigquery-loader)"
   ```
   Both should show `ACTIVE`

2. **Check Topics Exist:**
   ```bash
   gcloud pubsub topics list | grep -E "(vendor-discovery|simulation-results)"
   ```

3. **Trigger Test Simulation:**
   ```bash
   curl -X POST "https://simulation-service-wearla5naa-uc.a.run.app/simulate" \
     -H "Content-Type: application/json" \
     -d '{"vendor": "Stripe", "duration": 4}'
   ```

4. **Wait and Check BigQuery:**
   ```bash
   sleep 15
   python scripts/verify_bigquery.py | head -20
   ```

### Comprehensive Test (15 minutes)

Follow the complete testing procedures in:
- [Testing BigQuery Automation](#testing-bigquery-automation)
- [Testing Graph Loader Automation](#testing-graph-loader-automation)

---

## Expected Test Results

### Successful Test Output

**BigQuery Test:**
```
✅ BigQuery Loader logs:
   📥 Received simulation result event
   ✅ Loaded simulation result into BigQuery: stripe-20251128020000

✅ BigQuery Verification:
   Simulation ID: stripe-20251128020000  ← NEW!
   Vendor: Stripe
   Impact Score: 0.32
```

**Graph Loader Test:**
```
✅ Discovery Function logs:
   ✅ Published discovery event to Pub/Sub: 123456789

✅ Graph Loader logs:
   📥 Received discovery event for project: vendor-risk-digital-twin
   ✅ Fetched discovery results from gs://...
   ✅ Successfully loaded discovery data into Neo4j

✅ Neo4j Verification:
   Vendors: ['Auth0', 'SendGrid', 'Stripe', 'Twilio']  ← Updated!
```

---

## Summary

### How to Know Automation is Working

1. **BigQuery Automation:**
   - ✅ Simulation completes
   - ✅ BigQuery Loader logs show execution
   - ✅ New simulation appears in BigQuery
   - ✅ Count increases

2. **Graph Loader Automation:**
   - ✅ Discovery completes
   - ✅ Discovery logs show "Published event"
   - ✅ Graph Loader logs show execution
   - ✅ New vendors appear in Neo4j
   - ✅ Count increases

### Key Verification Points

- **Events Published:** Check publisher logs for "Published" messages
- **Functions Triggered:** Check subscriber logs for "Received" messages
- **Data Appears:** Verify data in destination systems (BigQuery/Neo4j)
- **Counts Increase:** Compare before/after counts

---

**Related Documentation:**
- [Pub/Sub Automation Guide](pubsub_automation.md)
- [GCP Integration Roadmap](gcp_integration_roadmap.md)

