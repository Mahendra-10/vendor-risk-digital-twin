# Simulation Service API Documentation

**File:** `cloud_run/simulation-service/app.py`  
**Service:** Cloud Run REST API for Vendor Failure Simulations  
**Last Updated:** 2025-12-02

---

## 📋 Overview

`app.py` is the main entry point for the **Cloud Run Simulation Service**. It provides a REST API that allows clients to run vendor failure simulations and retrieve simulation results. The service is containerized and deployed on Google Cloud Run, providing auto-scaling and serverless capabilities.

### Primary Purpose

1. **REST API for Vendor Failure Simulations**
   - Accepts HTTP requests to simulate vendor failures
   - Returns comprehensive impact analysis (operational, financial, compliance)

2. **Cloud-Native Service**
   - Containerized Flask application
   - Auto-scales based on traffic
   - Runs on Google Cloud Run platform

---

## 🎯 Key Features

### 1. REST API Endpoints

The service exposes the following HTTP endpoints:

#### `POST /simulate`
Run a vendor failure simulation.

**Request Body:**
```json
{
    "vendor": "Stripe",
    "duration": 4
}
```

**Response:**
```json
{
    "simulation_id": "stripe-20251202120000",
    "vendor": "Stripe",
    "duration_hours": 4,
    "operational_impact": {
        "service_count": 3,
        "impact_score": 0.75,
        "affected_services": [...]
    },
    "financial_impact": {
        "revenue_loss": 50000,
        "impact_score": 0.60
    },
    "compliance_impact": {
        "affected_frameworks": {...},
        "impact_score": 0.45
    },
    "overall_impact_score": 0.60
}
```

#### `GET /vendors`
List all available vendors from the Neo4j graph database.

**Response:**
```json
{
    "vendors": ["Stripe", "Auth0", "SendGrid", ...],
    "count": 15
}
```

#### `GET /health`
Health check endpoint that verifies:
- Service is running
- Neo4j connection is active
- Simulator can be initialized

**Response:**
```json
{
    "status": "healthy",
    "service": "simulation-service",
    "neo4j": "connected",
    "timestamp": "2025-12-02T12:00:00"
}
```

#### `GET /`
Root endpoint providing API information and available endpoints.

---

### 2. Neo4j Graph Database Integration

The service connects to Neo4j to:
- Query vendor dependencies and relationships
- Calculate cascading impact of vendor failures
- Retrieve vendor and service information

**Connection Management:**
- Uses lazy initialization (simulator initialized on first request)
- Retrieves credentials from GCP Secret Manager
- Falls back to environment variables if Secret Manager is unavailable

**Code Reference:**
```python
def init_simulator():
    """Initialize the simulator (lazy initialization)"""
    global simulator
    
    if simulator is None:
        credentials = get_neo4j_credentials()
        simulator = VendorFailureSimulator(
            neo4j_uri=credentials['uri'],
            neo4j_user=credentials['user'],
            neo4j_password=credentials['password']
        )
    
    return simulator
```

---

### 3. GCP Secret Manager Integration

The service securely retrieves Neo4j credentials from Google Cloud Secret Manager:

**Secret Names:**
- `neo4j-uri` - Neo4j connection URI
- `neo4j-user` - Neo4j username (defaults to 'neo4j')
- `neo4j-password` - Neo4j password

**Fallback Strategy:**
1. First tries GCP Secret Manager (if `GCP_PROJECT_ID` is set)
2. Falls back to environment variables (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`)

**Code Reference:**
```python
def get_neo4j_credentials() -> Dict[str, str]:
    """Get Neo4j credentials from GCP Secret Manager or environment variables"""
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if project_id:
        uri = get_secret('neo4j-uri', project_id) or os.getenv('NEO4J_URI')
        user = get_secret('neo4j-user', project_id) or os.getenv('NEO4J_USER', 'neo4j')
        password = get_secret('neo4j-password', project_id) or os.getenv('NEO4J_PASSWORD')
    else:
        # Fallback to environment variables
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
    
    return {'uri': uri, 'user': user, 'password': password}
```

---

### 4. Pub/Sub Event Publishing

After each simulation completes, the service publishes results to Google Cloud Pub/Sub for downstream processing:

**Topic:** `simulation-results`

**Event Data:**
```json
{
    "simulation_id": "stripe-20251202120000",
    "vendor": "Stripe",
    "duration_hours": 4,
    "overall_impact_score": 0.60,
    "operational_impact": 0.75,
    "financial_impact": 0.60,
    "compliance_impact": 0.45,
    "timestamp": "2025-12-02T12:00:00",
    "full_result": {...}  // Complete simulation result
}
```

**Downstream Processing:**
- BigQuery Loader Function subscribes to this topic
- Stores simulation results in BigQuery for analytics
- Enables historical analysis and reporting

**Code Reference:**
```python
def publish_simulation_result(result: Dict[str, Any]) -> None:
    """Publish simulation result event to Pub/Sub"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'simulation-results')
    
    event_data = {
        'simulation_id': result.get('simulation_id'),
        'vendor': result.get('vendor'),
        'duration_hours': result.get('duration_hours'),
        'overall_impact_score': result.get('overall_impact_score'),
        # ... more fields
    }
    
    message_data = json.dumps(event_data).encode('utf-8')
    publisher.publish(topic_path, message_data)
```

---

## 🏗️ Architecture

### Service Architecture Diagram

```
┌─────────────┐
│   Client    │  (HTTP Request)
│  (Browser/  │
│   API/      │
│  Cloud      │
│  Scheduler)  │
└──────┬──────┘
       │ POST /simulate
       │ {vendor: "Stripe", duration: 4}
       ▼
┌─────────────────────────────────────────┐
│   Cloud Run Service (app.py)            │
│  ┌───────────────────────────────────┐ │
│  │  Flask REST API                    │ │
│  │  • POST /simulate                  │ │
│  │  • GET /vendors                     │ │
│  │  • GET /health                      │ │
│  │  • GET /                            │ │
│  └───────────┬─────────────────────────┘ │
│              │                            │
│  ┌───────────▼─────────────────────────┐ │
│  │ VendorFailureSimulator              │ │
│  │ (from scripts.simulation)           │ │
│  └───────────┬─────────────────────────┘ │
└──────────────┼───────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
   ┌────────┐      ┌──────────┐
   │ Neo4j  │      │ Pub/Sub   │
   │ Graph  │      │ Events    │
   │ DB     │      │           │
   └────────┘      └─────┬─────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ BigQuery      │
                  │ Loader        │
                  │ Function      │
                  └──────────────┘
```

### Component Interactions

1. **Client → Cloud Run Service**
   - HTTP requests to REST endpoints
   - JSON request/response format
   - CORS enabled for browser access

2. **Cloud Run Service → Neo4j**
   - Graph queries to find vendor dependencies
   - Calculates cascading impact
   - Retrieves vendor and service data

3. **Cloud Run Service → Pub/Sub**
   - Publishes simulation results as events
   - Enables asynchronous downstream processing

4. **Cloud Run Service → Secret Manager**
   - Retrieves Neo4j credentials securely
   - No secrets in code or environment variables

---

## 🔧 Technical Details

### Dependencies

**Core Framework:**
- `Flask` - Web framework
- `flask-cors` - CORS support

**GCP Services:**
- `google-cloud-pubsub` - Pub/Sub client
- `google-cloud-secret-manager` - Secret Manager client (via `scripts.gcp.gcp_secrets`)

**Simulation Engine:**
- `scripts.simulation.simulate_failure.VendorFailureSimulator` - Core simulation logic
- `scripts.utils` - Utility functions (logging, config, validation)
- `scripts.gcp.gcp_secrets` - Secret Manager wrapper

**Database:**
- `neo4j` - Neo4j Python driver

### Environment Variables

**Required:**
- `GCP_PROJECT_ID` - Google Cloud project ID
- `PORT` - HTTP port (set by Cloud Run, defaults to 8080)

**Optional (if not using Secret Manager):**
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password

**Cloud Run Secrets (via `--set-secrets`):**
- `NEO4J_URI` - Secret Manager reference: `neo4j-uri:latest`
- `NEO4J_USER` - Secret Manager reference: `neo4j-user:latest`
- `NEO4J_PASSWORD` - Secret Manager reference: `neo4j-password:latest`

### Lazy Initialization

The simulator is initialized **on first use** rather than at startup:

**Benefits:**
- Faster container startup (no Neo4j connection delay)
- Prevents startup failures if Neo4j is temporarily unavailable
- Better for Cloud Run's cold start optimization

**Initialization Points:**
- First call to `/simulate`
- First call to `/vendors`
- First call to `/health`

---

## 📊 Request/Response Examples

### Example 1: Run Simulation

**Request:**
```bash
curl -X POST https://simulation-service-xxx.run.app/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "vendor": "Stripe",
    "duration": 4
  }'
```

**Response:**
```json
{
    "simulation_id": "stripe-20251202120000",
    "vendor": "Stripe",
    "duration_hours": 4,
    "timestamp": "2025-12-02T12:00:00",
    "operational_impact": {
        "service_count": 3,
        "affected_services": [
            {"name": "payment-service", "status": "down"},
            {"name": "checkout-service", "status": "degraded"}
        ],
        "impact_score": 0.75
    },
    "financial_impact": {
        "revenue_loss": 50000,
        "transaction_failures": 1200,
        "impact_score": 0.60
    },
    "compliance_impact": {
        "affected_frameworks": {
            "SOC 2": {"score_change": -5, "controls_affected": 2},
            "PCI DSS": {"score_change": -8, "controls_affected": 3}
        },
        "impact_score": 0.45
    },
    "overall_impact_score": 0.60,
    "recommendations": [
        "Implement payment gateway redundancy",
        "Add fallback payment processor"
    ]
}
```

### Example 2: List Vendors

**Request:**
```bash
curl https://simulation-service-xxx.run.app/vendors
```

**Response:**
```json
{
    "vendors": [
        "Auth0",
        "Datadog",
        "MongoDB Atlas",
        "SendGrid",
        "Stripe",
        "Twilio"
    ],
    "count": 6
}
```

### Example 3: Health Check

**Request:**
```bash
curl https://simulation-service-xxx.run.app/health
```

**Response:**
```json
{
    "status": "healthy",
    "service": "simulation-service",
    "neo4j": "connected",
    "timestamp": "2025-12-02T12:00:00"
}
```

---

## 🚀 Deployment

### Cloud Build Configuration

The service is deployed via Cloud Build using `cloudbuild.yaml`:

```yaml
- name: 'gcr.io/cloud-builders/docker'
  args:
    - 'build'
    - '--no-cache'
    - '--pull'
    - '-f'
    - 'cloud_run/simulation-service/Dockerfile'
    - '-t'
    - 'gcr.io/$PROJECT_ID/simulation-service:latest'
    - '.'

- name: 'gcr.io/cloud-builders/gcloud'
  args:
    - 'run'
    - 'deploy'
    - 'simulation-service'
    - '--image'
    - 'gcr.io/$PROJECT_ID/simulation-service:latest'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
    - '--set-secrets'
    - 'NEO4J_URI=neo4j-uri:latest,NEO4J_USER=neo4j-user:latest,NEO4J_PASSWORD=neo4j-password:latest'
```

### Docker Configuration

The service runs in a Docker container with:
- **Base Image:** `python:3.11-slim`
- **Working Directory:** `/app`
- **Port:** `8080` (set by Cloud Run via `PORT` environment variable)
- **Python Path:** `/app` (set via `PYTHONPATH`)

---

## 🔍 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
**Symptom:** `ModuleNotFoundError: No module named 'scripts.simulation'`

**Solution:**
- Verify `__init__.py` files exist in `scripts/` and `scripts/simulation/`
- Check that `sys.path` is correctly set to `/app`
- Ensure Docker build includes all necessary files

#### 2. Neo4j Connection Failed
**Symptom:** Health check returns `"neo4j": "disconnected"`

**Solution:**
- Verify Secret Manager secrets are configured
- Check Neo4j Aura instance is running
- Verify network connectivity from Cloud Run to Neo4j

#### 3. Pub/Sub Publish Failed
**Symptom:** Warning in logs: `"Failed to publish simulation result"`

**Solution:**
- Verify `GCP_PROJECT_ID` environment variable is set
- Check that `simulation-results` topic exists
- Verify Cloud Run service account has Pub/Sub Publisher role

---

## 📚 Related Documentation

- [Cloud Run Architecture](./cloud_run_architecture.md) - Overall Cloud Run architecture
- [Deployment Root Cause Analysis](../../deployment_root_cause_analysis.md) - Troubleshooting deployment issues
- [VendorFailureSimulator](../../../scripts/simulation/simulate_failure.py) - Core simulation engine

---

## 🔄 Version History

- **2025-12-02-v3** - Fixed `sys.path` calculation, added debug prints
- **2025-12-02-v2** - Fixed import paths, added lazy initialization
- **2025-11-27** - Initial Cloud Run deployment

