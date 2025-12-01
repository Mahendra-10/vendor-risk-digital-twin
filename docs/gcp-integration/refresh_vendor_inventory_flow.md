# End-to-End Flow: Refresh Vendor Inventory

**Trigger:** User clicks "Refresh Vendor Inventory" / "Update Risk Database" button in the dashboard

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER ACTION                                        │
│  User clicks "Refresh Vendor Inventory" button in Dashboard (localhost)    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Dashboard API Call                                               │
│  Component: Node.js Dashboard (localhost:3000)                             │
│  Endpoint: POST /api/discovery/load                                        │
│  Action: Triggers discovery and loading process                            │
│  GCP Components: None (local)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Trigger Discovery Function                                        │
│  Component: Cloud Functions API                                           │
│  Action: HTTP POST to Discovery Function                                   │
│  URL: https://us-central1-{project-id}.cloudfunctions.net/vendor-discovery │
│  GCP Components:                                                           │
│    • Cloud Functions API (functions.googleapis.com)                        │
│    • Cloud Functions Gen2 Runtime                                          │
│    • Cloud Functions Invoker IAM role                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: Discovery Function Execution                                     │
│  Component: vendor-discovery Cloud Function (Gen2)                        │
│  Location: us-central1                                                     │
│  Runtime: Python 3.11                                                      │
│  Memory: 512 MB                                                            │
│  GCP Components:                                                           │
│    • Cloud Functions Gen2                                                  │
│    • Cloud Functions API (to query other functions)                       │
│    • Cloud Run API (to query Cloud Run services)                           │
│    • Secret Manager (to access credentials if needed)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: GCP Resource Discovery                                            │
│  Component: Discovery Function Logic                                       │
│  Actions:                                                                   │
│    1. Query Cloud Functions (via Cloud Functions API)                     │
│    2. Query Cloud Run Services (via Cloud Run API)                         │
│    3. Extract environment variables                                        │
│    4. Detect vendor dependencies (Stripe, Auth0, SendGrid, etc.)           │
│  GCP Components:                                                           │
│    • Cloud Functions API (functions.googleapis.com)                        │
│    • Cloud Run API (run.googleapis.com)                                   │
│    • Service Account IAM (for API access)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: Store Discovery Results                                           │
│  Component: Cloud Storage                                                  │
│  Action: Write JSON file with discovery results                            │
│  Path: gs://vendor-risk-digital-twin-discovery-results/                    │
│       discoveries/YYYYMMDD_HHMMSS_discovery.json                            │
│  GCP Components:                                                           │
│    • Cloud Storage (storage.googleapis.com)                                │
│    • Cloud Storage API                                                     │
│    • Service Account IAM: roles/storage.objectCreator                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: Publish Discovery Event                                           │
│  Component: Pub/Sub                                                        │
│  Topic: vendor-discovery-events                                            │
│  Message: {                                                                 │
│    project_id: "vendor-risk-digital-twin",                                  │
│    storage_path: "gs://.../discoveries/...json",                          │
│    discovery_timestamp: "2025-11-30T...",                                  │
│    summary: { cloud_functions: 2, cloud_run_services: 2, vendors_found: 4 }│
│  }                                                                          │
│  GCP Components:                                                           │
│    • Pub/Sub (pubsub.googleapis.com)                                       │
│    • Pub/Sub Publisher API                                                 │
│    • Service Account IAM: roles/pubsub.publisher                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: Eventarc Trigger                                                  │
│  Component: Eventarc                                                       │
│  Action: Detect Pub/Sub message published                                  │
│  Trigger: graph-loader-369906                                              │
│  Event Filter: google.cloud.pubsub.topic.v1.messagePublished              │
│  Topic: vendor-discovery-events                                            │
│  GCP Components:                                                           │
│    • Eventarc (eventarc.googleapis.com)                                   │
│    • Pub/Sub Topic: vendor-discovery-events                                │
│    • Eventarc Service Account                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: Graph Loader Function Triggered                                   │
│  Component: graph-loader Cloud Function (Gen2)                            │
│  Location: us-central1                                                     │
│  Runtime: Python 3.11                                                      │
│  Memory: 512 MB                                                            │
│  Trigger: Eventarc (Pub/Sub event)                                        │
│  GCP Components:                                                           │
│    • Cloud Functions Gen2                                                  │
│    • Eventarc (triggers the function)                                     │
│    • Pub/Sub Subscription (receives message)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: Read Discovery Results from Cloud Storage                         │
│  Component: Cloud Storage                                                  │
│  Action: Download JSON file from storage_path                              │
│  GCP Components:                                                           │
│    • Cloud Storage (storage.googleapis.com)                                │
│    • Cloud Storage API                                                     │
│    • Service Account IAM: roles/storage.objectViewer                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 10: Get Neo4j Credentials                                            │
│  Component: Secret Manager                                                 │
│  Secrets:                                                                   │
│    • neo4j-uri                                                             │
│    • neo4j-user                                                            │
│    • neo4j-password                                                        │
│  GCP Components:                                                           │
│    • Secret Manager (secretmanager.googleapis.com)                         │
│    • Secret Manager API                                                   │
│    • Service Account IAM: roles/secretmanager.secretAccessor                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 11: Load Data into Neo4j Aura                                        │
│  Component: Neo4j Aura (External)                                         │
│  Connection: neo4j+s://d29c0138.databases.neo4j.io                         │
│  Actions:                                                                   │
│    1. Create/Update Vendor nodes                                           │
│    2. Create/Update Service nodes                                         │
│    3. Create/Update BusinessProcess nodes                                  │
│    4. Create/Update ComplianceControl nodes                                │
│    5. Create relationships (DEPENDS_ON, SUPPORTS, SATISFIES)              │
│  GCP Components:                                                           │
│    • None (external Neo4j Aura service)                                    │
│    • Network: Outbound HTTPS connection                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 12: Return Success Response                                          │
│  Component: Graph Loader Function                                          │
│  Action: Return HTTP 200 (if triggered via HTTP)                          │
│  Logs: Published to Cloud Logging                                           │
│  GCP Components:                                                           │
│    • Cloud Logging (logging.googleapis.com)                               │
│    • Cloud Monitoring (monitoring.googleapis.com) - metrics collection     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 13: Dashboard Updates                                                │
│  Component: Node.js Dashboard (localhost:3000)                             │
│  Action: Display success message to user                                   │
│  GCP Components: None (local)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## GCP Components Summary

### Cloud Services Used

#### Discovery & Loading Flow (Refresh Vendor Inventory)

1. **Cloud Functions (Gen2)**
   - `vendor-discovery` - Discovery Function
   - `graph-loader` - Graph Loader Function
   - APIs: `functions.googleapis.com`, `run.googleapis.com`

2. **Cloud Storage**
   - Bucket: `vendor-risk-digital-twin-discovery-results`
   - Stores discovery results as JSON files

3. **Pub/Sub**
   - Topic: `vendor-discovery-events`
   - Enables event-driven architecture

4. **Eventarc**
   - Trigger: `graph-loader-369906`
   - Connects Pub/Sub to Cloud Functions

5. **Secret Manager**
   - Secrets: `neo4j-uri`, `neo4j-user`, `neo4j-password`
   - Secure credential storage

#### Simulation Flow (Run Simulation)

6. **Cloud Run**
   - Service: `simulation-service`
   - Runs Python simulation engine
   - Connects to Neo4j Aura

7. **Pub/Sub**
   - Topic: `simulation-results`
   - Receives simulation results from Cloud Run

8. **Eventarc**
   - Trigger: `bigquery-loader-652451`
   - Connects Pub/Sub to BigQuery Loader

9. **Cloud Functions (Gen2)**
   - `bigquery-loader` - BigQuery Loader Function
   - Processes simulation results

10. **BigQuery**
    - Dataset: `vendor_risk`
    - Table: `simulations`
    - Stores all simulation results

#### Shared Services

11. **Cloud Logging**
    - Logs from all Cloud Functions and Cloud Run
    - Centralized logging

12. **Cloud Monitoring**
    - Metrics collection
    - Dashboard: "Vendor Risk Digital Twin - Service Health"

13. **IAM (Identity and Access Management)**
    - Service Account: `16418516910-compute@developer.gserviceaccount.com`
    - **Discovery Flow Roles:**
      - `roles/pubsub.publisher` (Discovery Function)
      - `roles/storage.objectCreator` (Discovery Function)
      - `roles/storage.objectViewer` (Graph Loader)
      - `roles/secretmanager.secretAccessor` (Graph Loader)
    - **Simulation Flow Roles:**
      - `roles/pubsub.publisher` (Cloud Run)
      - `roles/secretmanager.secretAccessor` (Cloud Run)
      - `roles/bigquery.dataEditor` (BigQuery Loader)
      - `roles/bigquery.jobUser` (BigQuery Loader)

---

## Detailed Component Interactions

### Step-by-Step with GCP APIs

#### Step 1-2: Dashboard → Discovery Function
```
Dashboard (localhost)
  ↓ HTTP POST
Cloud Functions API
  ↓ Invoke
vendor-discovery Cloud Function (Gen2)
```

**GCP Components:**
- Cloud Functions API (`functions.googleapis.com`)
- Cloud Functions Gen2 Runtime

#### Step 3-4: Discovery Function Queries GCP
```
vendor-discovery Function
  ↓ Cloud Functions API
List all Cloud Functions
  ↓ Cloud Run API
List all Cloud Run Services
  ↓ Extract env vars
Detect vendor dependencies
```

**GCP Components:**
- Cloud Functions API
- Cloud Run API (`run.googleapis.com`)
- Service Account with appropriate IAM roles

#### Step 5: Store in Cloud Storage
```
Discovery Results (JSON)
  ↓ Cloud Storage API
gs://vendor-risk-digital-twin-discovery-results/
  discoveries/20251130_123456_discovery.json
```

**GCP Components:**
- Cloud Storage (`storage.googleapis.com`)
- Cloud Storage API
- IAM: `roles/storage.objectCreator`

#### Step 6: Publish to Pub/Sub
```
Discovery Results
  ↓ Pub/Sub Publisher API
Topic: vendor-discovery-events
  ↓ Message Published
Message ID: <message_id>
```

**GCP Components:**
- Pub/Sub (`pubsub.googleapis.com`)
- Pub/Sub Publisher API
- IAM: `roles/pubsub.publisher`

#### Step 7: Eventarc Detects Event
```
Pub/Sub Message Published
  ↓ Eventarc
Trigger: graph-loader-369906
  ↓ Event Filter Match
Event Type: google.cloud.pubsub.topic.v1.messagePublished
```

**GCP Components:**
- Eventarc (`eventarc.googleapis.com`)
- Pub/Sub Topic
- Eventarc Service Account

#### Step 8-9: Graph Loader Triggered
```
Eventarc Trigger
  ↓ Invoke
graph-loader Cloud Function (Gen2)
  ↓ Cloud Storage API
Read: gs://.../discoveries/...json
```

**GCP Components:**
- Cloud Functions Gen2
- Eventarc
- Cloud Storage API
- IAM: `roles/storage.objectViewer`

#### Step 10: Get Secrets
```
Graph Loader Function
  ↓ Secret Manager API
Secrets: neo4j-uri, neo4j-user, neo4j-password
  ↓ Decrypt
Neo4j Connection String
```

**GCP Components:**
- Secret Manager (`secretmanager.googleapis.com`)
- Secret Manager API
- IAM: `roles/secretmanager.secretAccessor`

#### Step 11: Load to Neo4j Aura
```
Graph Loader Function
  ↓ HTTPS (outbound)
Neo4j Aura: d29c0138.databases.neo4j.io
  ↓ Cypher Queries
Create/Update nodes and relationships
```

**GCP Components:**
- None (external service)
- Network: Outbound HTTPS

#### Step 12-13: Logging and Response
```
Graph Loader Function
  ↓ Cloud Logging API
Logs: Published to Cloud Logging
  ↓ Cloud Monitoring
Metrics: Execution count, execution time
  ↓ HTTP Response
Dashboard receives success
```

**GCP Components:**
- Cloud Logging (`logging.googleapis.com`)
- Cloud Monitoring (`monitoring.googleapis.com`)

---

## IAM Roles Required

### Discovery Function Service Account
```
Service Account: 16418516910-compute@developer.gserviceaccount.com

Required Roles:
  • roles/pubsub.publisher          (Publish to Pub/Sub)
  • roles/storage.objectCreator      (Write to Cloud Storage)
  • roles/cloudfunctions.viewer      (Query Cloud Functions)
  • roles/run.viewer                 (Query Cloud Run services)
```

### Graph Loader Service Account
```
Service Account: 16418516910-compute@developer.gserviceaccount.com

Required Roles:
  • roles/pubsub.subscriber          (Receive Pub/Sub messages via Eventarc)
  • roles/storage.objectViewer        (Read from Cloud Storage)
  • roles/secretmanager.secretAccessor (Access Neo4j credentials)
```

---

## Data Flow Summary

### Refresh Vendor Inventory Flow

```
User Click "Refresh Vendor Inventory"
  ↓
Dashboard API (POST /api/discovery/load)
  ↓
Discovery Function (Cloud Functions)
  ↓
Cloud Functions API + Cloud Run API (Query GCP resources)
  ↓
Discovery Results
  ↓
Cloud Storage (JSON file)
  ↓
Pub/Sub (vendor-discovery-events topic)
  ↓
Eventarc (Trigger)
  ↓
Graph Loader Function
  ↓
Cloud Storage (Read JSON)
  ↓
Secret Manager (Get Neo4j credentials)
  ↓
Neo4j Aura (Load graph data)
  ↓
Success Response
  ↓
Dashboard (Display to user)
```

### Run Simulation Flow

```
User Click "Run Simulation"
  ↓
Dashboard API (POST /api/simulate)
  ↓
Cloud Run (simulation-service)
  ↓
Secret Manager (Get Neo4j credentials)
  ↓
Neo4j Aura (Query vendor dependencies)
  ↓
Calculate Impact (operational, financial, compliance)
  ↓
Pub/Sub (simulation-results topic)
  ↓
Return Results to Dashboard
  ↓
Eventarc (Trigger BigQuery Loader)
  ↓
BigQuery Loader Function
  ↓
BigQuery (simulations table)
  ↓
Results Available for Querying
```

---

## Monitoring Points

### Cloud Monitoring Metrics

1. **Discovery Function**
   - Execution count
   - Execution time
   - Success/error rate

2. **Graph Loader Function**
   - Execution count
   - Execution time
   - Processing success rate

3. **Pub/Sub**
   - Message publish count
   - Message delivery count
   - Undelivered messages

4. **Cloud Storage**
   - Object creation count
   - Storage size

### Cloud Logging

- Discovery Function logs
- Graph Loader Function logs
- Pub/Sub message logs
- Eventarc trigger logs

---

## Error Handling

### Potential Failure Points

1. **Discovery Function fails**
   - Check Cloud Functions logs
   - Verify IAM permissions
   - Check API quotas

2. **Cloud Storage write fails**
   - Verify bucket exists
   - Check IAM: `roles/storage.objectCreator`
   - Check bucket permissions

3. **Pub/Sub publish fails**
   - Check IAM: `roles/pubsub.publisher`
   - Verify topic exists
   - Check Pub/Sub quotas

4. **Eventarc doesn't trigger**
   - Verify trigger exists
   - Check trigger configuration
   - Verify Pub/Sub message was published

5. **Graph Loader fails**
   - Check Cloud Functions logs
   - Verify Cloud Storage read permissions
   - Check Secret Manager access
   - Verify Neo4j connection

---

## Performance Considerations

### Typical Execution Times

- **Discovery Function**: 15-30 seconds
- **Cloud Storage Write**: < 1 second
- **Pub/Sub Publish**: < 1 second
- **Eventarc Trigger**: 1-2 seconds
- **Graph Loader Execution**: 5-10 seconds
- **Neo4j Load**: 2-5 seconds

**Total End-to-End Time**: ~25-50 seconds

### Optimization Opportunities

1. **Parallel Processing**: Run discovery and storage in parallel
2. **Caching**: Cache GCP resource lists
3. **Batch Operations**: Batch Neo4j writes
4. **Async Processing**: Make Pub/Sub publish async

---

## Security Considerations

1. **Service Account IAM**: Least privilege principle
2. **Secret Manager**: Encrypted credentials
3. **HTTPS**: All external connections use HTTPS
4. **VPC**: Functions can be deployed in VPC for additional security
5. **Audit Logs**: All API calls are logged

---

## Cost Considerations

### GCP Services Used (per execution)

#### Refresh Vendor Inventory Flow

- **Cloud Functions**: ~$0.0001 per execution (Discovery + Graph Loader)
- **Cloud Storage**: ~$0.00001 per GB stored
- **Pub/Sub**: ~$0.00004 per million messages
- **Eventarc**: Free (included with Cloud Functions)
- **Secret Manager**: ~$0.06 per secret version per month
- **Cloud Logging**: First 50 GB free per month
- **Cloud Monitoring**: First 150 MB free per month

**Estimated Cost per Refresh**: < $0.001

#### Run Simulation Flow

- **Cloud Run**: ~$0.000024 per vCPU-second + ~$0.0000025 per GiB-second
- **Pub/Sub**: ~$0.00004 per million messages
- **Cloud Functions**: ~$0.0001 per execution (BigQuery Loader)
- **BigQuery**: ~$5 per TB queried (storage is ~$0.02 per GB/month)
- **Eventarc**: Free (included with Cloud Functions)
- **Secret Manager**: ~$0.06 per secret version per month

**Estimated Cost per Simulation**: < $0.001 (assuming small queries)

---

## Simulation Flow: Run Vendor Failure Simulation

**Trigger:** User clicks "Run Simulation" button in the dashboard

This is a **separate flow** from Refresh Vendor Inventory. When a user runs a simulation, it follows this path:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER ACTION                                        │
│  User clicks "Run Simulation" button in Dashboard (localhost)              │
│  Selects: Vendor (e.g., "Auth0"), Duration (e.g., 4 hours)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Dashboard API Call                                               │
│  Component: Node.js Dashboard (localhost:3000)                             │
│  Endpoint: POST /api/simulate                                               │
│  Payload: { vendor: "Auth0", duration: 4 }                                 │
│  GCP Components: None (local)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Call Cloud Run Simulation Service                                 │
│  Component: Cloud Run                                                       │
│  Service: simulation-service                                               │
│  URL: https://simulation-service-{project-id}.us-central1.run.app/simulate  │
│  GCP Components:                                                           │
│    • Cloud Run (run.googleapis.com)                                        │
│    • Cloud Run API                                                         │
│    • Cloud Run Invoker IAM role                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: Simulation Service Execution                                      │
│  Component: simulation-service (Cloud Run)                                 │
│  Location: us-central1                                                     │
│  Runtime: Python 3.11 (Container)                                          │
│  Actions:                                                                   │
│    1. Connect to Neo4j Aura (via Secret Manager)                           │
│    2. Query vendor dependencies from Neo4j                                 │
│    3. Calculate operational, financial, compliance impact                  │
│    4. Generate recommendations                                             │
│  GCP Components:                                                           │
│    • Cloud Run                                                              │
│    • Secret Manager (neo4j credentials)                                    │
│    • Service Account IAM: roles/secretmanager.secretAccessor                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: Publish Simulation Results to Pub/Sub                            │
│  Component: Pub/Sub                                                        │
│  Topic: simulation-results                                                 │
│  Message: {                                                                 │
│    simulation_id: "auth0-20251130123456",                                  │
│    vendor: "Auth0",                                                         │
│    duration_hours: 4,                                                       │
│    operational_impact: {...},                                              │
│    financial_impact: {...},                                                  │
│    compliance_impact: {...},                                                │
│    overall_impact_score: 0.397,                                            │
│    timestamp: "2025-11-30T12:34:56Z"                                        │
│  }                                                                          │
│  GCP Components:                                                           │
│    • Pub/Sub (pubsub.googleapis.com)                                       │
│    • Pub/Sub Publisher API                                                 │
│    • Service Account IAM: roles/pubsub.publisher                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: Return Results to Dashboard                                      │
│  Component: Cloud Run → Dashboard                                          │
│  Action: HTTP 200 response with simulation results                          │
│  GCP Components:                                                           │
│    • Cloud Run (returns response)                                          │
│    • Cloud Logging (logs request/response)                                  │
│    • Cloud Monitoring (records metrics)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: Eventarc Triggers BigQuery Loader                                  │
│  Component: Eventarc                                                       │
│  Action: Detect Pub/Sub message published                                   │
│  Trigger: bigquery-loader-652451                                            │
│  Event Filter: google.cloud.pubsub.topic.v1.messagePublished               │
│  Topic: simulation-results                                                  │
│  GCP Components:                                                           │
│    • Eventarc (eventarc.googleapis.com)                                   │
│    • Pub/Sub Topic: simulation-results                                     │
│    • Eventarc Service Account                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: BigQuery Loader Function Execution                                │
│  Component: bigquery-loader Cloud Function (Gen2)                         │
│  Location: us-central1                                                     │
│  Runtime: Python 3.11                                                      │
│  Memory: 512 MB                                                            │
│  Trigger: Eventarc (Pub/Sub event)                                        │
│  GCP Components:                                                           │
│    • Cloud Functions Gen2                                                  │
│    • Eventarc (triggers the function)                                      │
│    • Pub/Sub Subscription (receives message)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: Load Data into BigQuery                                           │
│  Component: BigQuery                                                       │
│  Dataset: vendor_risk                                                      │
│  Table: simulations                                                        │
│  Actions:                                                                   │
│    1. Parse simulation results from Pub/Sub message                        │
│    2. Transform data to BigQuery schema                                    │
│    3. Insert row into simulations table                                    │
│  GCP Components:                                                           │
│    • BigQuery (bigquery.googleapis.com)                                    │
│    • BigQuery API                                                          │
│    • Service Account IAM: roles/bigquery.dataEditor                        │
│    • Service Account IAM: roles/bigquery.jobUser                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: Logging and Monitoring                                            │
│  Component: Cloud Logging & Monitoring                                     │
│  Actions:                                                                   │
│    • Log simulation execution                                               │
│    • Record metrics (execution count, latency)                              │
│    • Track BigQuery insert success                                         │
│  GCP Components:                                                           │
│    • Cloud Logging (logging.googleapis.com)                               │
│    • Cloud Monitoring (monitoring.googleapis.com)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Simulation Flow GCP Components

1. **Cloud Run**
   - Service: `simulation-service`
   - Runs Python simulation engine
   - Connects to Neo4j Aura

2. **Pub/Sub**
   - Topic: `simulation-results`
   - Receives simulation results from Cloud Run

3. **Eventarc**
   - Trigger: `bigquery-loader-652451`
   - Connects Pub/Sub to BigQuery Loader

4. **Cloud Functions (Gen2)**
   - Function: `bigquery-loader`
   - Processes simulation results
   - Loads into BigQuery

5. **BigQuery**
   - Dataset: `vendor_risk`
   - Table: `simulations`
   - Stores all simulation results

6. **Secret Manager**
   - Stores Neo4j credentials for Cloud Run

7. **Cloud Logging & Monitoring**
   - Logs all operations
   - Tracks metrics

### Simulation Flow IAM Roles

**Cloud Run Service Account:**
- `roles/pubsub.publisher` - Publish simulation results
- `roles/secretmanager.secretAccessor` - Access Neo4j credentials

**BigQuery Loader Service Account:**
- `roles/pubsub.subscriber` - Receive Pub/Sub messages (via Eventarc)
- `roles/bigquery.dataEditor` - Write to BigQuery
- `roles/bigquery.jobUser` - Run BigQuery jobs

### Querying Simulation Results in BigQuery

After simulation completes, you can query results:

```sql
-- Get all simulations for a vendor
SELECT *
FROM `vendor-risk-digital-twin.vendor_risk.simulations`
WHERE vendor_name = "Auth0"
ORDER BY timestamp DESC;

-- Get latest simulation for each vendor
SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY vendor_name ORDER BY timestamp DESC) as rn
  FROM `vendor-risk-digital-twin.vendor_risk.simulations`
)
WHERE rn = 1;

-- Calculate average impact scores
SELECT 
  vendor_name,
  AVG(overall_score) as avg_impact_score,
  AVG(operational_impact) as avg_operational_impact,
  AVG(financial_impact) as avg_financial_impact,
  COUNT(*) as simulation_count
FROM `vendor-risk-digital-twin.vendor_risk.simulations`
GROUP BY vendor_name
ORDER BY avg_impact_score DESC;
```

---

## Related Documentation

- [Discovery Function Implementation](../phase2/phase2_cloud_functions.md)
- [Graph Loader Function](../phase2/phase2_cloud_functions.md)
- [Pub/Sub Integration](../phase5/prove_pubsub_working.md)
- [Eventarc Configuration](../phase5/phase5_readiness_assessment.md)
- [IAM Service Accounts Guide](./iam_service_accounts_guide.md)
- [Neo4j Aura Queries](./neo4j_aura_queries.md)

---

**Last Updated:** 2025-11-30  
**Status:** ✅ Operational

