# Vendor Risk Digital Twin - Architecture Design

## Overview

The Vendor Risk Digital Twin is a cloud-native framework that models vendor dependencies as a graph database, enabling real-time failure simulation and compliance impact prediction.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Vendor Risk Digital Twin                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│   GCP Cloud     │      │   Neo4j Graph    │      │  Simulation  │
│   Discovery     │─────▶│    Database      │─────▶│    Engine    │
│                 │      │                  │      │              │
│ - Functions     │      │ - Vendors        │      │ - Impact     │
│ - Cloud Run     │      │ - Services       │      │ - Compliance │
│ - BigQuery      │      │ - Processes      │      │ - Financial  │
└─────────────────┘      └──────────────────┘      └──────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Environment    │      │  Relationships   │      │   Results    │
│  Variables      │      │  - DEPENDS_ON    │      │  - JSON      │
│  API Keys       │      │  - SUPPORTS      │      │  - Reports   │
│                 │      │  - SATISFIES     │      │  - Metrics   │
└─────────────────┘      └──────────────────┘      └──────────────┘
```

## Components

### 1. GCP Discovery (`gcp_discovery.py`)

**Purpose:** Automatically discover vendor dependencies from GCP infrastructure.

**How It Works:**
1. Queries GCP APIs (Cloud Functions, Cloud Run, etc.)
2. Extracts environment variables containing vendor API keys
3. Maps services to vendors based on pattern matching
4. Outputs discovered dependencies as JSON

**Key Features:**
- Pattern-based vendor detection (STRIPE_, AUTH0_, etc.)
- Supports multiple GCP resource types
- Handles authentication via service accounts
- Graceful degradation to sample data

**Output:** `data/outputs/discovered_dependencies.json`

### 2. Graph Database (Neo4j)

**Purpose:** Model vendor dependencies as a graph for relationship queries.

**Node Types:**
- **Vendor**: Third-party service providers (Stripe, Auth0, etc.)
  - Properties: `vendor_id`, `name`, `category`, `criticality`
- **Service**: Cloud services (Cloud Functions, Cloud Run)
  - Properties: `service_id`, `name`, `type`, `gcp_resource`, `rpm`, `customers_affected`
- **BusinessProcess**: Business operations (checkout, user_login)
  - Properties: `name`
- **ComplianceControl**: Compliance framework controls (SOC 2, NIST)
  - Properties: `control_id`, `framework`

**Relationship Types:**
- **DEPENDS_ON**: Service → Vendor (indicates dependency)
- **SUPPORTS**: Service → BusinessProcess (indicates support)
- **SATISFIES**: Vendor → ComplianceControl (indicates control satisfaction)

**Example Graph:**
```
(payment-api:Service)-[:DEPENDS_ON]→(Stripe:Vendor)
(payment-api:Service)-[:SUPPORTS]→(checkout:BusinessProcess)
(Stripe:Vendor)-[:SATISFIES]→(CC6.6:ComplianceControl)
```

### 3. Graph Loader (`load_graph.py`)

**Purpose:** Load vendor dependency data into Neo4j.

**Process:**
1. Parse vendor dependency JSON
2. Create nodes for vendors, services, processes, controls
3. Create relationships between nodes
4. Verify data integrity

**Key Features:**
- Idempotent loading (MERGE operations)
- Batch processing for efficiency
- Verification queries
- Clear/reset capability

### 4. Simulation Engine (`simulate_failure.py`)

**Purpose:** Simulate vendor failures and predict impact.

**Impact Categories:**

#### A. Operational Impact
- **Metrics:**
  - Number of affected services
  - Total RPM (requests per minute) impacted
  - Number of customers affected
  - Business processes disrupted
- **Calculation:** Graph traversal to find all services depending on vendor

#### B. Financial Impact
- **Metrics:**
  - Revenue loss (based on duration)
  - Failed transactions
  - Customer impact cost
  - Total cost
- **Calculation:** 
  ```
  revenue_loss = revenue_per_hour × duration × service_impact_percentage
  customer_cost = customers_affected × $5
  total_cost = revenue_loss + customer_cost
  ```

#### C. Compliance Impact
- **Metrics:**
  - Affected compliance frameworks (SOC 2, NIST, ISO 27001)
  - Control failures
  - Score changes
- **Calculation:**
  ```
  new_score = baseline_score - Σ(control_weight)
  score_change = (new_score - baseline_score) / baseline_score
  ```

**Overall Impact Score:**
```
impact_score = (operational × 0.4) + (financial × 0.35) + (compliance × 0.25)
```

### 5. Utility Functions (`utils.py`)

**Purpose:** Shared helper functions.

**Features:**
- Configuration loading (YAML + env vars)
- JSON file operations
- Logging setup
- Formatting (currency, percentages)
- Environment validation

## Data Flow

### Discovery Flow
```
1. User runs: python scripts/gcp_discovery.py --project-id PROJECT_ID
2. Script queries GCP APIs
3. Environment variables extracted
4. Vendor patterns matched
5. JSON output saved to data/outputs/
```

### Loading Flow
```
1. User runs: python scripts/load_graph.py --data-file FILE
2. JSON parsed
3. Neo4j nodes created (Vendor, Service, BusinessProcess)
4. Relationships created (DEPENDS_ON, SUPPORTS, SATISFIES)
5. Verification performed
```

### Simulation Flow
```
1. User runs: python scripts/simulate_failure.py --vendor "Stripe" --duration 4
2. Query Neo4j for vendor dependencies
3. Calculate operational impact (services, processes)
4. Calculate financial impact (revenue loss)
5. Calculate compliance impact (control failures)
6. Generate recommendations
7. Output JSON report
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Cloud Platform | Google Cloud Platform (GCP) | Infrastructure discovery |
| Graph Database | Neo4j | Dependency modeling |
| Language | Python 3.9+ | Scripting and logic |
| Config | YAML + .env | Configuration management |
| Data Format | JSON | Data interchange |
| API Client | google-cloud-* | GCP API access |
| Graph Driver | neo4j-python-driver | Neo4j connectivity |

## Security Considerations

### 1. Credential Management
- **GCP Service Account:** Stored in `config/secrets/` (gitignored)
- **Neo4j Password:** Stored in `.env` file (gitignored)
- **Environment Variables:** Used for sensitive configuration

### 2. Access Control
- GCP service account has read-only permissions
- Neo4j database isolated to local/private network
- No vendor API keys stored in graph (only detection patterns)

### 3. Data Privacy
- Sample data used for PoC (no real production data)
- Customer interview data anonymized
- Compliance control mappings are public framework information

## Scalability Considerations

### Current PoC Scope
- Single GCP project
- 5-10 vendors
- 10-20 services
- Neo4j free tier

### Production Scaling
- **Multi-cloud support:** Add AWS/Azure discovery scripts
- **Real-time monitoring:** Stream events from cloud APIs
- **Distributed graph:** Neo4j clustering
- **API layer:** Flask/FastAPI REST API
- **UI dashboard:** React/Vue.js frontend
- **Caching:** Redis for simulation results

## Query Performance

**Optimizations:**
- Indexed properties: `vendor_id`, `service_id`, `name`
- Relationship direction matters (uni-directional)
- Limit query depth (max 3 hops)
- Use `MATCH` with specific labels

**Example Optimized Query:**
```cypher
// Optimized: Uses index on vendor name
MATCH (v:Vendor {name: 'Stripe'})<-[:DEPENDS_ON]-(s:Service)
RETURN v, s

// Not optimized: Scans all nodes
MATCH (v)-[r]-(s) WHERE v.name = 'Stripe'
RETURN v, s
```

## Extension Points

### 1. Additional Vendors
Add patterns to `gcp_discovery.py`:
```python
self.vendor_patterns = {
    'NewVendor': ['NEWVENDOR_', 'newvendor'],
    ...
}
```

### 2. Additional Cloud Providers
Create new discovery scripts:
- `aws_discovery.py`
- `azure_discovery.py`

### 3. Additional Compliance Frameworks
Add to `config/compliance_frameworks.yaml`:
```yaml
new_framework:
  name: "Framework Name"
  controls:
    CONTROL_ID:
      name: "Control Name"
      vendors: [...]
```

### 4. Real-time Monitoring
Integrate with cloud logging:
```python
# Stream Cloud Logging events
from google.cloud import logging_v2
# Detect vendor API failures in real-time
```

## Next Steps

1. **Phase 1 (Current):** Basic PoC with sample data
2. **Phase 2:** Real GCP integration
3. **Phase 3:** Multi-vendor simulation
4. **Phase 4:** Compliance automation
5. **Phase 5:** Production-ready API

## References

- [Neo4j Cypher Documentation](https://neo4j.com/docs/cypher-manual/)
- [GCP Python Client Libraries](https://cloud.google.com/python/docs/reference)
- [GRC 7.0 Digital Twins](https://grc2020.com/2025/07/01/grc-7-0-grc-orchestrate-digital-twins-and-the-forward-looking-power-of-risk-integrity-and-objectives/)

