# How Pub/Sub Works in This System (And What It Would Look Like Without It)

**Purpose:** Understand the difference between event-driven architecture (with Pub/Sub) vs. direct calls (without Pub/Sub).

---

## 🎯 Current Architecture: WITH Pub/Sub

### Flow 1: Simulation → BigQuery (Event-Driven)

```
┌─────────────────────┐
│  User/Dashboard     │
│  Runs Simulation    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Simulation Service  │
│  (Cloud Run)         │
│                      │
│  1. Runs simulation  │
│  2. Gets results     │
│  3. Publishes to     │
│     Pub/Sub topic    │
└──────────┬──────────┘
           │
           │ publish_simulation_result()
           │ Publishes message to topic
           ▼
┌─────────────────────┐
│  Pub/Sub Topic:     │
│  simulation-results │
│                      │
│  [Message Queue]    │
│  - Stores message   │
│  - Delivers to      │
│    subscribers      │
└──────────┬──────────┘
           │
           │ Automatically delivers message
           │ (decoupled - simulation service doesn't wait)
           ▼
┌─────────────────────┐
│  BigQuery Loader    │
│  (Cloud Function)  │
│                      │
│  Triggered by       │
│  Pub/Sub message    │
│                      │
│  1. Receives message │
│  2. Extracts data    │
│  3. Writes to        │
│     BigQuery         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BigQuery Database  │
│  (Data stored)      │
└─────────────────────┘
```

### What Happens in Code:

**Step 1: Simulation Service Publishes to Pub/Sub**
```python
# cloud_run/simulation-service/app.py

@app.route('/simulate', methods=['POST'])
def run_simulation():
    # ... run simulation ...
    result = sim.simulate_vendor_failure(vendor, duration_hours)
    
    # ✅ WITH Pub/Sub: Just publish and return immediately
    publish_simulation_result(result)  # Non-blocking, async
    
    return jsonify(result), 200  # Returns immediately, doesn't wait for BigQuery

def publish_simulation_result(result):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'simulation-results')
    
    # Create message
    message_data = json.dumps(event_data).encode('utf-8')
    
    # Publish (non-blocking)
    future = publisher.publish(topic_path, message_data)
    message_id = future.result()  # Just gets message ID, doesn't wait for delivery
    
    logger.info(f"✅ Published to Pub/Sub: {message_id}")
    # Function returns - doesn't wait for BigQuery
```

**Step 2: BigQuery Loader Automatically Triggered**
```python
# cloud_functions/bigquery_loader/main.py

def load_simulation_result(event, context):
    """
    This function is AUTOMATICALLY called by Pub/Sub
    when a message arrives on the 'simulation-results' topic
    """
    # Decode Pub/Sub message
    message_data = base64.b64decode(event['data']).decode('utf-8')
    event_data = json.loads(message_data)
    
    # Get simulation result from message
    result = event_data.get('full_result')
    
    # Write to BigQuery
    load_simulation_to_bigquery(result, project_id, dataset_id)
    
    logger.info("✅ Loaded to BigQuery")
    # Function completes - Pub/Sub marks message as delivered
```

**Key Points:**
- ✅ **Decoupled**: Simulation service doesn't know or care about BigQuery
- ✅ **Async**: Simulation returns immediately, BigQuery happens later
- ✅ **Reliable**: Pub/Sub guarantees message delivery (retries if function fails)
- ✅ **Scalable**: Multiple subscribers can process same message
- ✅ **Resilient**: If BigQuery is down, message stays in queue

---

## ❌ Alternative Architecture: WITHOUT Pub/Sub

### Flow 1: Simulation → BigQuery (Direct Call)

```
┌─────────────────────┐
│  User/Dashboard     │
│  Runs Simulation    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Simulation Service  │
│  (Cloud Run)         │
│                      │
│  1. Runs simulation  │
│  2. Gets results     │
│  3. Calls BigQuery   │
│     API directly     │
│  4. Waits for        │
│     response         │
└──────────┬──────────┘
           │
           │ Direct HTTP call
           │ (blocking, synchronous)
           ▼
┌─────────────────────┐
│  BigQuery API        │
│  (Direct write)      │
│                      │
│  - Must be available │
│  - Blocks response   │
│  - No retry logic    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BigQuery Database  │
│  (Data stored)      │
└─────────────────────┘
```

### What the Code Would Look Like:

**Without Pub/Sub: Direct BigQuery Write**
```python
# cloud_run/simulation-service/app.py (ALTERNATIVE VERSION)

@app.route('/simulate', methods=['POST'])
def run_simulation():
    # ... run simulation ...
    result = sim.simulate_vendor_failure(vendor, duration_hours)
    
    # ❌ WITHOUT Pub/Sub: Direct BigQuery write (blocking)
    write_to_bigquery_directly(result)  # Blocks until complete
    
    return jsonify(result), 200  # Only returns after BigQuery write completes

def write_to_bigquery_directly(result):
    from google.cloud import bigquery
    
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.vendor_risk.simulations"
    
    # Prepare row
    row = {
        'simulation_id': result['simulation_id'],
        'vendor_name': result['vendor'],
        # ... more fields ...
    }
    
    # ❌ Direct write - blocks until complete
    errors = client.insert_rows_json(table_id, [row])
    
    if errors:
        raise Exception(f"BigQuery write failed: {errors}")
    
    logger.info("✅ Written to BigQuery")
    # Function waits here until BigQuery responds
```

**Problems with This Approach:**
- ❌ **Tightly Coupled**: Simulation service must know about BigQuery
- ❌ **Blocking**: User waits for BigQuery write to complete
- ❌ **No Retry**: If BigQuery fails, entire simulation fails
- ❌ **Not Scalable**: Can't easily add more destinations (e.g., send email, update dashboard)
- ❌ **Single Point of Failure**: If BigQuery is down, simulations fail

---

## 📊 Side-by-Side Comparison

### Scenario: User Runs Simulation

| Aspect | WITH Pub/Sub | WITHOUT Pub/Sub |
|--------|--------------|------------------|
| **Response Time** | ~2 seconds (simulation only) | ~5-10 seconds (simulation + BigQuery) |
| **Coupling** | Decoupled (services don't know each other) | Tightly coupled (simulation knows BigQuery) |
| **Reliability** | High (Pub/Sub retries if function fails) | Low (if BigQuery fails, simulation fails) |
| **Scalability** | Easy to add more subscribers | Hard to add more destinations |
| **Error Handling** | Pub/Sub handles retries automatically | Must implement retry logic manually |
| **User Experience** | Fast response, data appears later | Slower response, but data is immediately available |

### Code Flow Comparison

**WITH Pub/Sub:**
```python
# Simulation Service
result = run_simulation()
publish_to_pubsub(result)  # Non-blocking, ~50ms
return result              # Returns immediately

# BigQuery Loader (separate function, triggered automatically)
def load_simulation_result(event):
    write_to_bigquery(event.data)  # Runs independently
```

**WITHOUT Pub/Sub:**
```python
# Simulation Service
result = run_simulation()
write_to_bigquery(result)  # Blocking, ~2-5 seconds
return result              # Returns after BigQuery completes
```

---

## 🔄 Flow 2: Discovery → Neo4j (Event-Driven)

### WITH Pub/Sub:

```
Discovery Function
    ↓
Publishes to: vendor-discovery-events
    ↓
Pub/Sub Topic (message queue)
    ↓
Graph Loader Function (automatically triggered)
    ↓
Neo4j Database
```

**Benefits:**
- Discovery doesn't need Neo4j credentials
- If Neo4j is down, message stays in queue
- Can add more subscribers (e.g., update dashboard, send notification)

### WITHOUT Pub/Sub:

```
Discovery Function
    ↓
Direct Neo4j API call
    ↓
Neo4j Database
```

**Problems:**
- Discovery needs Neo4j credentials
- If Neo4j is down, discovery fails
- Hard to add more destinations

---

## 🎯 Real-World Example

### Scenario: 100 simulations run simultaneously

**WITH Pub/Sub:**
1. All 100 simulations complete quickly (~2 seconds each)
2. All 100 messages published to Pub/Sub (~50ms each)
3. BigQuery Loader processes messages asynchronously
4. User gets fast response
5. BigQuery writes happen in background (even if BigQuery is slow)

**Result:** Users happy (fast), system resilient (can handle BigQuery slowness)

**WITHOUT Pub/Sub:**
1. First simulation runs, waits for BigQuery (~5 seconds)
2. Second simulation runs, waits for BigQuery (~5 seconds)
3. ... continues sequentially or with limited concurrency
4. If BigQuery is slow, all simulations are slow
5. If BigQuery fails, all simulations fail

**Result:** Users wait longer, system fragile (BigQuery issues affect everything)

---

## 🔍 How to See Pub/Sub in Action

### 1. Check Message Flow

```bash
# Publish a message
gcloud pubsub topics publish simulation-results --message='{"test": "data"}'

# Check if message was delivered
gcloud pubsub subscriptions pull simulation-results-to-bigquery-subscription --limit=1
```

### 2. Monitor Pub/Sub Activity

```bash
# See undelivered messages (should be low/zero if working)
gcloud pubsub subscriptions describe simulation-results-to-bigquery-subscription \
  --format="value(numUndeliveredMessages)"
```

### 3. Check Function Triggers

```bash
# See when BigQuery loader was last triggered
gcloud functions logs read bigquery-loader --region=us-central1 --limit=5
```

---

## 💡 Key Takeaways

### Pub/Sub Provides:

1. **Decoupling**: Services don't need to know about each other
2. **Asynchrony**: Fast responses, background processing
3. **Reliability**: Automatic retries, message persistence
4. **Scalability**: Easy to add more subscribers
5. **Resilience**: One service failure doesn't break others

### Without Pub/Sub You Get:

1. **Tight Coupling**: Services must know about each other
2. **Synchrony**: Slow responses, blocking operations
3. **Manual Retries**: You must implement retry logic
4. **Hard to Scale**: Adding destinations requires code changes
5. **Fragility**: One service failure can break the chain

---

## 🎬 Visual Timeline

### WITH Pub/Sub:
```
Time: 0s    User clicks "Run Simulation"
Time: 2s    Simulation completes, publishes to Pub/Sub
Time: 2s    ✅ Response returned to user (fast!)
Time: 2.5s  Pub/Sub delivers message to BigQuery Loader
Time: 3s    BigQuery Loader writes to BigQuery
Time: 3s    ✅ Data appears in BigQuery
```

### WITHOUT Pub/Sub:
```
Time: 0s    User clicks "Run Simulation"
Time: 2s    Simulation completes
Time: 2s    Starts writing to BigQuery (blocking)
Time: 5s    BigQuery write completes
Time: 5s    ✅ Response returned to user (slow!)
Time: 5s    ✅ Data appears in BigQuery
```

**User waits 3 seconds longer without Pub/Sub!**

---

## 🛠️ When to Use Pub/Sub vs. Direct Calls

### Use Pub/Sub When:
- ✅ You want fast user responses
- ✅ You need reliability (automatic retries)
- ✅ You want to add more destinations later
- ✅ Services should be independent
- ✅ You need to handle high load

### Use Direct Calls When:
- ✅ You need immediate consistency (data must be there now)
- ✅ Simple system with few services
- ✅ Low traffic (performance not critical)
- ✅ You want simpler architecture (fewer moving parts)

---

## 📝 Summary

**Pub/Sub = Message Queue + Event-Driven Architecture**

- **Publisher** (Simulation Service) → Publishes message → Doesn't wait
- **Topic** (Pub/Sub) → Stores message → Delivers to subscribers
- **Subscriber** (BigQuery Loader) → Receives message → Processes independently

**Without Pub/Sub = Direct API Calls**

- **Service A** → Calls Service B directly → Waits for response
- If Service B is slow/down → Service A is slow/down

**In your system, Pub/Sub makes it:**
- Faster (users get responses quickly)
- More reliable (automatic retries)
- More flexible (easy to add more destinations)
- More resilient (one service failure doesn't break others)

