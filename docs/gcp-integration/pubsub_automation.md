# Pub/Sub Event-Driven Automation

**Purpose:** This document explains how Pub/Sub enables automatic, event-driven workflows in the Vendor Risk Digital Twin system, eliminating manual steps and enabling true automation.

**Last Updated:** 2025-11-27

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pub/Sub Concepts](#pubsub-concepts)
3. [Architecture](#architecture)
4. [Automation Flows](#automation-flows)
5. [Topics and Subscriptions](#topics-and-subscriptions)
6. [How It Works](#how-it-works)
7. [Benefits](#benefits)
8. [Usage Examples](#usage-examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Pub/Sub?

**Google Cloud Pub/Sub** is a messaging service that enables **decoupled, event-driven communication** between services. Instead of services calling each other directly, they communicate through **topics** (message channels) and **subscriptions** (receivers).

### Why Use Pub/Sub?

**Before Pub/Sub (Manual Steps):**
```
Discovery completes → ❌ Manual: Click "Load into Neo4j"
Simulation completes → ❌ Manual: Add --bigquery flag
```

**After Pub/Sub (Automatic):**
```
Discovery completes → ✅ Automatic: Data loads into Neo4j
Simulation completes → ✅ Automatic: Results save to BigQuery
```

### Key Benefits

- ✅ **Zero Manual Steps**: Everything happens automatically
- ✅ **Decoupled Services**: Services don't need to know about each other
- ✅ **Reliable**: Automatic retries if processing fails
- ✅ **Scalable**: Handles bursts of events
- ✅ **Asynchronous**: Non-blocking, services process at their own pace

---

## Pub/Sub Concepts

### Topics (Message Channels)

A **topic** is like a mailbox where messages are published. Multiple services can publish to the same topic, and multiple subscribers can listen to it.

**Example:**
```
Discovery Function publishes → "vendor-discovery-events" topic
```

### Subscriptions (Receivers)

A **subscription** is like an address that receives messages from a topic. When a message arrives, it automatically triggers a Cloud Function.

**Example:**
```
"discovery-to-neo4j-subscription" listens to "vendor-discovery-events"
→ Automatically triggers Graph Loader Cloud Function
```

### Publishers vs Subscribers

- **Publisher**: Service that sends messages (e.g., Discovery Function)
- **Subscriber**: Service that receives and processes messages (e.g., Graph Loader)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PUB/SUB INFRASTRUCTURE                    │
└─────────────────────────────────────────────────────────────┘

Topics:
  • vendor-discovery-events
  • simulation-requests
  • simulation-results

Subscriptions:
  • discovery-to-neo4j-subscription
  • simulation-request-subscription
  • simulation-results-to-bigquery-subscription
```

### Service Flow

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│  Discovery      │ publish │   Topic      │ trigger │  Graph      │
│  Function       │─────────▶│              │────────▶│  Loader     │
│                 │         │              │         │  Function   │
└─────────────────┘         └──────────────┘         └─────────────┘
                                    │
                                    │ subscription
                                    ▼
                            ┌──────────────┐
                            │ Subscription │
                            └──────────────┘
```

---

## Automation Flows

### Flow #1: Discovery → Neo4j (Automatic)

**What Happens:**

1. **Discovery Function runs** (triggered manually or by Cloud Scheduler)
2. **Discovers vendor dependencies** from GCP resources
3. **Saves results to Cloud Storage**
4. **Publishes event** to `vendor-discovery-events` topic
5. **Subscription receives event** (`discovery-to-neo4j-subscription`)
6. **Graph Loader Cloud Function automatically triggered**
7. **Fetches data from Cloud Storage**
8. **Loads data into Neo4j automatically** ✅

**Message Format:**
```json
{
  "project_id": "vendor-risk-digital-twin",
  "storage_path": "gs://bucket/discoveries/20251127_120000_discovery.json",
  "discovery_timestamp": "2025-11-27T12:00:00Z",
  "summary": {
    "cloud_functions": 5,
    "cloud_run_services": 3,
    "vendors_found": 4
  }
}
```

**Code Location:**
- Publisher: `cloud_functions/discovery/main.py` → `publish_discovery_event()`
- Subscriber: `cloud_functions/graph_loader/main.py` → `load_discovery_to_neo4j()`

---

### Flow #2: Simulation → BigQuery (Automatic)

**What Happens:**

1. **Simulation Service runs** (via HTTP POST or Pub/Sub)
2. **Calculates vendor failure impact**
3. **Generates simulation results**
4. **Publishes event** to `simulation-results` topic
5. **Subscription receives event** (`simulation-results-to-bigquery-subscription`)
6. **BigQuery Loader Cloud Function automatically triggered**
7. **Extracts data from event**
8. **Loads results into BigQuery automatically** ✅

**Message Format:**
```json
{
  "simulation_id": "stripe-20251127120000",
  "vendor": "Stripe",
  "duration_hours": 4,
  "overall_impact_score": 0.32,
  "operational_impact": 0.30,
  "financial_impact": 0.35,
  "compliance_impact": 0.25,
  "timestamp": "2025-11-27T12:00:00Z",
  "full_result": { /* complete simulation result */ }
}
```

**Code Location:**
- Publisher: `cloud_run/simulation-service/app.py` → `publish_simulation_result()`
- Subscriber: `cloud_functions/bigquery_loader/main.py` → `load_simulation_result()`

---

### Flow #3: Simulation Request (Future Use)

**What Happens:**

1. **Dashboard/API publishes request** to `simulation-requests` topic
2. **Subscription receives event** (`simulation-request-subscription`)
3. **Simulation Service automatically triggered**
4. **Runs simulation**
5. **Publishes results** to `simulation-results` topic
6. **BigQuery Loader automatically triggered** (Flow #2)

**Message Format:**
```json
{
  "vendor": "Stripe",
  "duration": 4,
  "requested_by": "user@example.com"
}
```

**Use Case:** Cloud Scheduler can publish simulation requests daily for automated risk assessments.

---

## Topics and Subscriptions

### Topic: `vendor-discovery-events`

**Purpose:** Notify when vendor discovery completes

**Publisher:** Discovery Function (`cloud_functions/discovery/main.py`)

**Subscribers:**
- `discovery-to-neo4j-subscription` → Graph Loader Cloud Function

**When Published:** After discovery completes and results are saved to Cloud Storage

**Message Contains:**
- `project_id`: GCP project ID
- `storage_path`: Path to discovery results in Cloud Storage
- `discovery_timestamp`: When discovery ran
- `summary`: Summary of discovered resources

---

### Topic: `simulation-results`

**Purpose:** Notify when simulation completes

**Publisher:** Simulation Service (`cloud_run/simulation-service/app.py`)

**Subscribers:**
- `simulation-results-to-bigquery-subscription` → BigQuery Loader Cloud Function

**When Published:** After simulation completes and results are generated

**Message Contains:**
- `simulation_id`: Unique simulation identifier
- `vendor`: Vendor name
- `duration_hours`: Failure duration
- `overall_impact_score`: Calculated impact score
- `full_result`: Complete simulation result data

---

### Topic: `simulation-requests`

**Purpose:** Request a simulation to run

**Publisher:** Dashboard, API, or Cloud Scheduler (future)

**Subscribers:**
- `simulation-request-subscription` → Simulation Service (future)

**When Published:** When a simulation is requested (manual or scheduled)

**Message Contains:**
- `vendor`: Vendor to simulate
- `duration`: Failure duration in hours
- `requested_by`: Who requested the simulation

---

## How It Works

### Step-by-Step: Discovery Automation

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Discovery Function Runs                            │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ Scans GCP resources (Cloud Functions, Cloud Run)
    ├─→ Detects vendor dependencies from environment variables
    └─→ Saves results to Cloud Storage
            │
            │ gs://bucket/discoveries/20251127_120000_discovery.json
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Publish Event to Pub/Sub                           │
└─────────────────────────────────────────────────────────────┘
    │
    └─→ publish_discovery_event()
            │
            │ Publishes to "vendor-discovery-events" topic
            │ Message: {project_id, storage_path, summary}
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Subscription Receives Event                        │
└─────────────────────────────────────────────────────────────┘
    │
    └─→ "discovery-to-neo4j-subscription" receives message
            │
            │ Automatically triggers Cloud Function
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Graph Loader Cloud Function Runs                   │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ Decodes Pub/Sub message
    ├─→ Extracts storage_path from message
    ├─→ Fetches discovery results from Cloud Storage
    ├─→ Converts to Neo4j format
    └─→ Loads into Neo4j graph database
            │
            ▼
    ✅ Data automatically in Neo4j!
    (No manual step needed!)
```

### Step-by-Step: Simulation Automation

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Simulation Service Runs                            │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ Queries Neo4j for vendor dependencies
    ├─→ Calculates operational impact
    ├─→ Calculates financial impact
    ├─→ Calculates compliance impact
    └─→ Generates simulation results
            │
            │ {simulation_id, vendor, impact_score, ...}
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Publish Event to Pub/Sub                           │
└─────────────────────────────────────────────────────────────┘
    │
    └─→ publish_simulation_result()
            │
            │ Publishes to "simulation-results" topic
            │ Message: {simulation_id, vendor, impact_score, full_result}
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Subscription Receives Event                        │
└─────────────────────────────────────────────────────────────┘
    │
    └─→ "simulation-results-to-bigquery-subscription" receives message
            │
            │ Automatically triggers Cloud Function
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: BigQuery Loader Cloud Function Runs                │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ Decodes Pub/Sub message
    ├─→ Extracts simulation data
    ├─→ Formats for BigQuery
    └─→ Inserts into BigQuery table
            │
            ▼
    ✅ Results automatically in BigQuery!
    (No manual step needed!)
```

---

## Benefits

### 1. Zero Manual Steps

**Before:**
- ❌ Click "Load into Neo4j" button after discovery
- ❌ Remember to add `--bigquery` flag to simulations
- ❌ Manually run `bigquery_loader.py` for existing data

**After:**
- ✅ Discovery → Neo4j: Automatic
- ✅ Simulation → BigQuery: Automatic
- ✅ No flags, no buttons, no manual scripts

### 2. Decoupled Architecture

Services don't need to know about each other:

- **Discovery Function** doesn't need to know about Neo4j
- **Simulation Service** doesn't need to know about BigQuery
- They just publish events and move on

### 3. Reliability

- **Automatic Retries**: If processing fails, Pub/Sub retries automatically
- **Message Persistence**: Messages persist until successfully processed
- **Dead-Letter Queue**: Failed messages go to dead-letter queue for investigation

### 4. Scalability

- **Parallel Processing**: Multiple subscribers can process messages in parallel
- **Burst Handling**: Handles sudden spikes in events
- **Auto-Scaling**: Cloud Functions scale automatically based on message volume

### 5. Asynchronous Processing

- **Non-Blocking**: Services don't wait for downstream processing
- **Independent Pacing**: Each service processes at its own speed
- **Better Performance**: No bottlenecks from synchronous calls

---

## Usage Examples

### Example 1: Manual Discovery Trigger

**Before Pub/Sub:**
```bash
# 1. Trigger discovery
curl https://[region]-[project].cloudfunctions.net/vendor-discovery

# 2. Wait for completion
# 3. Manually click "Load into Neo4j" in dashboard
# OR run:
python scripts/load_graph.py --from-gcp --project-id vendor-risk-digital-twin
```

**After Pub/Sub:**
```bash
# 1. Trigger discovery
curl https://[region]-[project].cloudfunctions.net/vendor-discovery

# 2. That's it! Data automatically loads into Neo4j
# No manual step needed!
```

### Example 2: Simulation with BigQuery

**Before Pub/Sub:**
```bash
# Must remember --bigquery flag
python scripts/simulate_failure.py --vendor Stripe --duration 4 --bigquery
```

**After Pub/Sub:**
```bash
# Just run simulation - BigQuery happens automatically
python scripts/simulate_failure.py --vendor Stripe --duration 4
# OR via API:
curl -X POST https://[service-url]/simulate \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}'
# Results automatically saved to BigQuery!
```

### Example 3: Scheduled Discovery (Future)

**With Cloud Scheduler + Pub/Sub:**
```bash
# Cloud Scheduler triggers discovery daily at 2 AM
# Discovery completes → Publishes event
# Graph Loader automatically triggered
# Neo4j automatically updated
# No human intervention needed!
```

---

## Troubleshooting

### Issue: Events Not Being Processed

**Symptoms:**
- Discovery completes but Neo4j not updated
- Simulation completes but BigQuery not updated

**Check:**
1. **Verify subscriptions exist:**
   ```bash
   gcloud pubsub subscriptions list
   ```

2. **Check Cloud Function logs:**
   ```bash
   gcloud functions logs read graph-loader --limit 50
   gcloud functions logs read bigquery-loader --limit 50
   ```

3. **Verify Cloud Functions are deployed:**
   ```bash
   gcloud functions list
   ```

### Issue: Messages Stuck in Queue

**Symptoms:**
- Messages in subscription but not being processed

**Check:**
1. **View subscription details:**
   ```bash
   gcloud pubsub subscriptions describe discovery-to-neo4j-subscription
   ```

2. **Check for errors in Cloud Function:**
   ```bash
   gcloud functions logs read graph-loader --limit 100
   ```

3. **Check dead-letter queue** (if configured)

### Issue: Events Published But Not Received

**Symptoms:**
- Discovery publishes event but Graph Loader not triggered

**Check:**
1. **Verify topic exists:**
   ```bash
   gcloud pubsub topics list
   ```

2. **Check subscription is attached to topic:**
   ```bash
   gcloud pubsub subscriptions describe discovery-to-neo4j-subscription
   ```

3. **Verify Cloud Function trigger:**
   ```bash
   gcloud functions describe graph-loader
   ```

### Common Solutions

1. **Redeploy Cloud Functions:**
   ```bash
   # Graph Loader
   cd cloud_functions/graph_loader
   gcloud functions deploy graph-loader \
     --runtime python311 \
     --trigger-topic vendor-discovery-events \
     --entry-point load_discovery_to_neo4j
   
   # BigQuery Loader
   cd cloud_functions/bigquery_loader
   gcloud functions deploy bigquery-loader \
     --runtime python311 \
     --trigger-topic simulation-results \
     --entry-point load_simulation_result
   ```

2. **Check IAM Permissions:**
   - Cloud Functions need `pubsub.subscriber` role
   - Publishers need `pubsub.publisher` role

3. **Verify Environment Variables:**
   - `GCP_PROJECT_ID` must be set
   - Neo4j credentials must be in Secret Manager

---

## Setup and Configuration

### Initial Setup

1. **Create Topics and Subscriptions:**
   ```bash
   python scripts/setup_pubsub.py --project-id vendor-risk-digital-twin
   ```

2. **Deploy Graph Loader Cloud Function:**
   ```bash
   cd cloud_functions/graph_loader
   gcloud functions deploy graph-loader \
     --runtime python311 \
     --trigger-topic vendor-discovery-events \
     --entry-point load_discovery_to_neo4j \
     --set-env-vars GCP_PROJECT_ID=vendor-risk-digital-twin
   ```

3. **Deploy BigQuery Loader Cloud Function:**
   ```bash
   cd cloud_functions/bigquery_loader
   gcloud functions deploy bigquery-loader \
     --runtime python311 \
     --trigger-topic simulation-results \
     --entry-point load_simulation_result \
     --set-env-vars GCP_PROJECT_ID=vendor-risk-digital-twin
   ```

### Verification

1. **Test Discovery Flow:**
   ```bash
   # Trigger discovery
   curl https://[region]-[project].cloudfunctions.net/vendor-discovery
   
   # Check Pub/Sub messages
   gcloud pubsub subscriptions pull discovery-to-neo4j-subscription --limit 1
   
   # Check Neo4j (should have new data)
   # Query Neo4j to verify
   ```

2. **Test Simulation Flow:**
   ```bash
   # Run simulation
   curl -X POST https://[service-url]/simulate \
     -H "Content-Type: application/json" \
     -d '{"vendor": "Stripe", "duration": 4}'
   
   # Check BigQuery
   python scripts/verify_bigquery.py
   ```

---

## Code Reference

### Publisher: Discovery Function

**File:** `cloud_functions/discovery/main.py`

**Function:** `publish_discovery_event()`

```python
def publish_discovery_event(project_id: str, storage_path: str, results: Dict[str, Any]) -> None:
    """Publish discovery completion event to Pub/Sub"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
    
    event_data = {
        'project_id': project_id,
        'storage_path': storage_path,
        'discovery_timestamp': results.get('discovery_timestamp'),
        'summary': {...}
    }
    
    message_data = json.dumps(event_data).encode('utf-8')
    future = publisher.publish(topic_path, message_data)
    message_id = future.result()
```

### Subscriber: Graph Loader

**File:** `cloud_functions/graph_loader/main.py`

**Function:** `load_discovery_to_neo4j()`

```python
def load_discovery_to_neo4j(event: Dict[str, Any], context) -> None:
    """Cloud Function entry point for Pub/Sub trigger"""
    # Decode Pub/Sub message
    message_data = base64.b64decode(event['data']).decode('utf-8')
    event_data = json.loads(message_data)
    
    # Fetch discovery results from Cloud Storage
    discovery_data = fetch_discovery_from_storage(storage_path, project_id)
    
    # Load into Neo4j
    load_into_neo4j(neo4j_data, credentials)
```

### Publisher: Simulation Service

**File:** `cloud_run/simulation-service/app.py`

**Function:** `publish_simulation_result()`

```python
def publish_simulation_result(result: Dict[str, Any]) -> None:
    """Publish simulation result event to Pub/Sub"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'simulation-results')
    
    event_data = {
        'simulation_id': result.get('simulation_id'),
        'vendor': result.get('vendor'),
        'overall_impact_score': result.get('overall_impact_score'),
        'full_result': result
    }
    
    message_data = json.dumps(event_data).encode('utf-8')
    future = publisher.publish(topic_path, message_data)
```

### Subscriber: BigQuery Loader

**File:** `cloud_functions/bigquery_loader/main.py`

**Function:** `load_simulation_result()`

```python
def load_simulation_result(event: Dict[str, Any], context) -> None:
    """Cloud Function entry point for Pub/Sub trigger"""
    # Decode Pub/Sub message
    message_data = base64.b64decode(event['data']).decode('utf-8')
    event_data = json.loads(message_data)
    
    # Get full result from event
    result = event_data.get('full_result', event_data)
    
    # Load into BigQuery
    load_simulation_to_bigquery(result, project_id, dataset_id)
```

---

## Summary

**Pub/Sub enables true automation by:**

1. **Decoupling services** - Services communicate through messages, not direct calls
2. **Automatic triggering** - Subscriptions automatically trigger Cloud Functions
3. **Reliable processing** - Automatic retries and message persistence
4. **Zero manual steps** - Everything happens automatically

**Key Takeaway:** Once set up, the system runs automatically. Discovery completes → Neo4j updates automatically. Simulation completes → BigQuery updates automatically. No manual intervention needed!

**Testing:** See [Testing Automation Guide](testing_automation.md) for step-by-step procedures to verify that automation is working correctly.

---

**Related Documentation:**
- [GCP Integration Roadmap](gcp_integration_roadmap.md)
- [Cloud Run Architecture](cloud_run_architecture.md)
- [Testing Automation](testing_automation.md) - **How to test and verify automation is working**
- [BigQuery Integration](../scripts/setup_bigquery.py)

