# Simplified End-to-End Flow Diagram

**Complete flow from "Refresh Vendor Inventory" to Logging & Monitoring**

---

## Simplified Visual Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           USER ACTION                                        │
│                    Click "Refresh Vendor Inventory"                          │
│                         (Dashboard - localhost:3000)                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Dashboard API                                                       │
│  POST /api/discovery/load                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Trigger Discovery Function                                          │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Cloud Functions API                                        │            │
│  │  → vendor-discovery (Cloud Function Gen2)                  │            │
│  │  GCP: functions.googleapis.com                             │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: Discover GCP Resources                                              │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Query Cloud Functions (Cloud Functions API)              │            │
│  │  Query Cloud Run Services (Cloud Run API)                  │            │
│  │  Extract Environment Variables                             │            │
│  │  Detect Vendors (Stripe, Auth0, SendGrid, etc.)           │            │
│  │  GCP: functions.googleapis.com, run.googleapis.com         │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: Store Discovery Results                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Cloud Storage                                             │            │
│  │  Bucket: vendor-risk-digital-twin-discovery-results        │            │
│  │  Path: discoveries/YYYYMMDD_HHMMSS_discovery.json          │            │
│  │  GCP: storage.googleapis.com                               │            │
│  │  IAM: roles/storage.objectCreator                          │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: Publish Discovery Event                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Pub/Sub                                                    │            │
│  │  Topic: vendor-discovery-events                             │            │
│  │  Message: {project_id, storage_path, summary}              │            │
│  │  GCP: pubsub.googleapis.com                                │            │
│  │  IAM: roles/pubsub.publisher                                │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: Eventarc Triggers Graph Loader                                      │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Eventarc                                                   │            │
│  │  Trigger: graph-loader-369906                               │            │
│  │  Event: google.cloud.pubsub.topic.v1.messagePublished      │            │
│  │  GCP: eventarc.googleapis.com                              │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: Graph Loader Function Executes                                      │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  graph-loader (Cloud Function Gen2)                        │            │
│  │  GCP: functions.googleapis.com                             │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: Read Discovery Results                                               │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Cloud Storage (Read)                                       │            │
│  │  Download JSON file from storage_path                       │            │
│  │  GCP: storage.googleapis.com                               │            │
│  │  IAM: roles/storage.objectViewer                            │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: Get Neo4j Credentials                                                │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Secret Manager                                             │            │
│  │  Secrets: neo4j-uri, neo4j-user, neo4j-password            │            │
│  │  GCP: secretmanager.googleapis.com                          │            │
│  │  IAM: roles/secretmanager.secretAccessor                    │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 10: Load Data into Neo4j Aura                                          │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Neo4j Aura (External)                                      │            │
│  │  Connection: neo4j+s://d29c0138.databases.neo4j.io         │            │
│  │  Actions:                                                   │            │
│  │    • Create/Update Vendor nodes                             │            │
│  │    • Create/Update Service nodes                            │            │
│  │    • Create/Update BusinessProcess nodes                    │            │
│  │    • Create relationships (DEPENDS_ON, SUPPORTS, etc.)     │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 11: Logging & Monitoring (Throughout All Steps)                        │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Cloud Logging                                               │            │
│  │  • Discovery Function logs                                   │            │
│  │  • Graph Loader Function logs                                │            │
│  │  • Pub/Sub message logs                                      │            │
│  │  • Eventarc trigger logs                                     │            │
│  │  GCP: logging.googleapis.com                                │            │
│  └────────────────────────────────────────────────────────────┘            │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  Cloud Monitoring                                            │            │
│  │  • Discovery Function metrics (execution count, time)        │            │
│  │  • Graph Loader metrics (execution count, time)              │            │
│  │  • Pub/Sub metrics (message count, delivery)                 │            │
│  │  • Cloud Storage metrics (object count, size)                │            │
│  │  Dashboard: "Vendor Risk Digital Twin - Service Health"     │            │
│  │  GCP: monitoring.googleapis.com                             │            │
│  └────────────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 12: Success Response                                                   │
│  Dashboard displays: "Vendor inventory refreshed successfully"               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Simplified Component Flow

```
┌─────────────┐
│   USER      │
│  (Browser)  │
└──────┬──────┘
       │ Click "Refresh Vendor Inventory"
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD (localhost:3000)                    │
│                    POST /api/discovery/load                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              DISCOVERY FUNCTION (Cloud Functions)                │
│  • Query GCP Resources (Functions API, Run API)                 │
│  • Detect Vendors                                                │
│  • Store in Cloud Storage                                        │
│  • Publish to Pub/Sub                                            │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│Cloud Storage │  │   Pub/Sub    │
│  (JSON file) │  │(discovery    │
│              │  │   events)    │
└──────────────┘  └──────┬────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVENTARC (Trigger)                            │
│              Detects Pub/Sub message                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              GRAPH LOADER (Cloud Functions)                      │
│  • Read from Cloud Storage                                       │
│  • Get credentials from Secret Manager                          │
│  • Load into Neo4j Aura                                          │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│Secret Manager│  │  Neo4j Aura  │
│  (Credentials)│  │  (Graph DB)  │
└──────────────┘  └──────────────┘

       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│              LOGGING & MONITORING (All Steps)                    │
│  ┌────────────────────────┐  ┌────────────────────────┐        │
│  │   Cloud Logging        │  │  Cloud Monitoring      │        │
│  │  • Function logs       │  │  • Execution metrics   │        │
│  │  • Pub/Sub logs        │  │  • Performance metrics │        │
│  │  • Error logs          │  │  • Dashboard          │        │
│  └────────────────────────┘  └────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## GCP Components at Each Stage

### Stage 1: Discovery
```
┌─────────────────────────────────────────┐
│  Cloud Functions API                    │
│  Cloud Run API                          │
│  → Query GCP resources                  │
└─────────────────────────────────────────┘
```

### Stage 2: Storage
```
┌─────────────────────────────────────────┐
│  Cloud Storage                           │
│  → Store discovery results (JSON)        │
└─────────────────────────────────────────┘
```

### Stage 3: Event-Driven Processing
```
┌─────────────────────────────────────────┐
│  Pub/Sub                                 │
│  → Publish discovery event               │
│                                          │
│  Eventarc                                │
│  → Trigger Graph Loader                  │
└─────────────────────────────────────────┘
```

### Stage 4: Data Loading
```
┌─────────────────────────────────────────┐
│  Cloud Storage (Read)                   │
│  → Read discovery results               │
│                                          │
│  Secret Manager                        │
│  → Get Neo4j credentials                │
│                                          │
│  Neo4j Aura                              │
│  → Load graph data                       │
└─────────────────────────────────────────┘
```

### Stage 5: Observability
```
┌─────────────────────────────────────────┐
│  Cloud Logging                           │
│  → Capture all logs                     │
│                                          │
│  Cloud Monitoring                        │
│  → Track metrics & dashboards            │
└─────────────────────────────────────────┘
```

---

## Data Flow Summary

```
User Click
    ↓
Dashboard API
    ↓
┌───────────────────────────────────────┐
│  DISCOVERY PHASE                      │
│  • Cloud Functions API                │
│  • Cloud Run API                      │
│  • Cloud Storage (Write)              │
│  • Pub/Sub (Publish)                  │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│  PROCESSING PHASE                     │
│  • Eventarc (Trigger)                 │
│  • Graph Loader Function              │
│  • Cloud Storage (Read)               │
│  • Secret Manager                     │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│  STORAGE PHASE                        │
│  • Neo4j Aura (Graph Database)        │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│  OBSERVABILITY PHASE                  │
│  • Cloud Logging (All steps)          │
│  • Cloud Monitoring (All steps)       │
└───────────────────────────────────────┘
    ↓
Success Response
```

---

## IAM Roles Summary

### Discovery Function
- `roles/pubsub.publisher` - Publish to Pub/Sub
- `roles/storage.objectCreator` - Write to Cloud Storage
- `roles/cloudfunctions.viewer` - Query Cloud Functions
- `roles/run.viewer` - Query Cloud Run services

### Graph Loader Function
- `roles/storage.objectViewer` - Read from Cloud Storage
- `roles/secretmanager.secretAccessor` - Access Neo4j credentials

### Logging & Monitoring
- Automatic (no additional IAM needed)
- All services automatically log to Cloud Logging
- Metrics automatically collected by Cloud Monitoring

---

## Monitoring Dashboard View

After the flow completes, you can view:

**Cloud Monitoring Dashboard:**
- Discovery Function - Execution Count: 1
- Discovery Function - Execution Time: ~15-30 seconds
- Graph Loader - Execution Count: 1
- Graph Loader - Execution Time: ~5-10 seconds
- Pub/Sub - Messages Published: 1
- Cloud Storage - Objects Created: 1

**Cloud Logging:**
- Discovery Function logs (INFO, WARNING, ERROR)
- Graph Loader logs (INFO, WARNING, ERROR)
- Pub/Sub message logs
- Eventarc trigger logs

---

## Quick Reference

**Trigger:** User clicks "Refresh Vendor Inventory"  
**Duration:** ~25-50 seconds end-to-end  
**GCP Services Used:** 8 services  
**Data Stores:** Cloud Storage, Neo4j Aura  
**Observability:** Cloud Logging, Cloud Monitoring  

---

**Last Updated:** 2025-11-30  
**Status:** ✅ Operational

