# API Design - Vendor Risk Digital Twin

This document describes the API design for the Vendor Risk Digital Twin system.

## Current State (PoC)

The current proof-of-concept implementation uses command-line scripts. This document outlines the future API design for production.

## Proposed REST API

### Base URL
```
https://api.vendorrisk.io/v1
```

### Authentication
```http
Authorization: Bearer <JWT_TOKEN>
```

## Endpoints

### 1. Discovery

#### Discover Vendor Dependencies
```http
POST /discovery/scan
Content-Type: application/json

{
  "cloud_provider": "gcp",
  "project_id": "my-project-123",
  "resources": ["cloud_functions", "cloud_run"],
  "credentials": {
    "service_account_key": "..."
  }
}
```

**Response:**
```json
{
  "scan_id": "scan_abc123",
  "status": "completed",
  "discovered_at": "2025-11-05T10:30:00Z",
  "summary": {
    "vendors_found": 5,
    "services_scanned": 12,
    "dependencies_mapped": 23
  },
  "vendors": [
    {
      "name": "Stripe",
      "category": "payment_processor",
      "criticality": "critical",
      "services": [...]
    }
  ]
}
```

#### Get Discovery History
```http
GET /discovery/scans?limit=10
```

### 2. Graph Operations

#### Load Data into Graph
```http
POST /graph/load
Content-Type: application/json

{
  "source": "scan_abc123",
  "clear_existing": false
}
```

#### Query Graph
```http
POST /graph/query
Content-Type: application/json

{
  "cypher": "MATCH (v:Vendor) RETURN v LIMIT 10"
}
```

**Response:**
```json
{
  "results": [
    {
      "vendor_id": "vendor_001",
      "name": "Stripe",
      "criticality": "critical"
    }
  ],
  "count": 10,
  "execution_time_ms": 45
}
```

#### Get Vendor Details
```http
GET /graph/vendors/{vendor_id}
```

**Response:**
```json
{
  "vendor_id": "vendor_001",
  "name": "Stripe",
  "category": "payment_processor",
  "criticality": "critical",
  "dependencies": {
    "services": 2,
    "business_processes": 3,
    "compliance_controls": 4
  },
  "services": [
    {
      "service_id": "svc_001",
      "name": "payment-api",
      "type": "cloud_function",
      "rpm": 500
    }
  ]
}
```

### 3. Simulation

#### Run Failure Simulation
```http
POST /simulation/run
Content-Type: application/json

{
  "vendor": "Stripe",
  "duration_hours": 4,
  "scenario": "complete_outage"
}
```

**Response:**
```json
{
  "simulation_id": "sim_xyz789",
  "vendor": "Stripe",
  "duration_hours": 4,
  "timestamp": "2025-11-05T10:45:00Z",
  "operational_impact": {
    "affected_services": 2,
    "customers_affected": 50000,
    "business_processes": ["checkout", "refunds"],
    "impact_score": 0.65
  },
  "financial_impact": {
    "revenue_loss": 300000.00,
    "failed_transactions": 20000,
    "total_cost": 550000.00,
    "impact_score": 0.55
  },
  "compliance_impact": {
    "affected_frameworks": {
      "soc2": {
        "baseline_score": 0.92,
        "new_score": 0.76,
        "score_change": -0.16
      }
    },
    "impact_score": 0.16
  },
  "overall_impact_score": 0.67,
  "recommendations": [
    "Implement fallback mechanisms for 2 services",
    "Consider vendor diversification"
  ]
}
```

#### Get Simulation History
```http
GET /simulation/history?vendor=Stripe&limit=5
```

#### Compare Simulations
```http
POST /simulation/compare
Content-Type: application/json

{
  "simulations": ["sim_001", "sim_002"],
  "metrics": ["financial_impact", "compliance_impact"]
}
```

### 4. Compliance

#### Get Compliance Posture
```http
GET /compliance/posture
```

**Response:**
```json
{
  "frameworks": {
    "soc2": {
      "current_score": 0.92,
      "total_controls": 25,
      "satisfied_controls": 23,
      "at_risk_controls": 2
    },
    "nist": {
      "current_score": 0.88,
      "total_controls": 30,
      "satisfied_controls": 26,
      "at_risk_controls": 4
    }
  },
  "vendor_dependencies": {
    "Stripe": ["CC6.6", "PR.DS-2"],
    "Auth0": ["CC6.1", "PR.AC-1"]
  }
}
```

#### Predict Compliance Impact
```http
POST /compliance/predict
Content-Type: application/json

{
  "vendor": "Auth0",
  "duration_hours": 8,
  "frameworks": ["soc2", "nist"]
}
```

### 5. Analytics

#### Get Risk Dashboard
```http
GET /analytics/dashboard
```

**Response:**
```json
{
  "summary": {
    "total_vendors": 10,
    "critical_vendors": 3,
    "total_services": 25,
    "avg_vendor_dependency": 2.5
  },
  "top_risks": [
    {
      "vendor": "Stripe",
      "risk_score": 0.85,
      "affected_services": 5
    }
  ],
  "single_points_of_failure": [
    {
      "business_process": "checkout",
      "vendor": "Stripe"
    }
  ]
}
```

#### Get Vendor Risk Score
```http
GET /analytics/vendors/{vendor_id}/risk-score
```

### 6. Recommendations

#### Get Mitigation Recommendations
```http
GET /recommendations?vendor=Stripe
```

**Response:**
```json
{
  "vendor": "Stripe",
  "recommendations": [
    {
      "type": "redundancy",
      "priority": "high",
      "description": "Implement fallback payment processor",
      "estimated_effort": "2 weeks",
      "impact_reduction": 0.45
    },
    {
      "type": "circuit_breaker",
      "priority": "medium",
      "description": "Add circuit breaker to payment-api",
      "estimated_effort": "3 days",
      "impact_reduction": 0.20
    }
  ]
}
```

## Webhooks

### Vendor Status Change
```json
{
  "event": "vendor.status.changed",
  "timestamp": "2025-11-05T11:00:00Z",
  "vendor": "Stripe",
  "old_status": "operational",
  "new_status": "degraded",
  "affected_services": 2
}
```

### Simulation Complete
```json
{
  "event": "simulation.completed",
  "simulation_id": "sim_xyz789",
  "vendor": "Auth0",
  "impact_score": 0.72,
  "url": "https://api.vendorrisk.io/v1/simulation/results/sim_xyz789"
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VENDOR_NOT_FOUND",
    "message": "Vendor 'XYZ' not found in graph database",
    "details": {
      "vendor_name": "XYZ",
      "suggestion": "Run discovery scan first"
    }
  }
}
```

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699180800
```

## Pagination

```http
GET /discovery/scans?page=2&per_page=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "next_page": "/discovery/scans?page=3&per_page=20",
    "prev_page": "/discovery/scans?page=1&per_page=20"
  }
}
```

## Implementation Notes

### Technology Stack (Proposed)
- **API Framework:** Flask-RESTful or FastAPI
- **Authentication:** JWT tokens
- **Database:** Neo4j (graph) + PostgreSQL (metadata)
- **Queue:** Celery + Redis (async tasks)
- **Caching:** Redis
- **Documentation:** OpenAPI/Swagger

### Security
- HTTPS only
- API key rotation
- Request signing
- Input validation
- SQL injection prevention (parameterized queries)
- Rate limiting per tenant

### Performance
- Caching for frequent queries
- Async processing for simulations
- Connection pooling for Neo4j
- CDN for static assets

## Future Endpoints (Roadmap)

### Real-time Monitoring
```http
GET /monitoring/vendors/{vendor_id}/status
WebSocket: ws://api.vendorrisk.io/v1/monitoring/stream
```

### ML-based Predictions
```http
POST /ml/predict-failure-probability
```

### Multi-vendor Scenarios
```http
POST /simulation/multi-vendor
Content-Type: application/json
{
  "vendors": ["Stripe", "Auth0", "MongoDB"],
  "scenario": "cascading_failure"
}
```

## Testing the API (PoC)

For now, use the CLI scripts as a proxy:

```bash
# Equivalent to POST /discovery/scan
python scripts/gcp_discovery.py --project-id PROJECT_ID

# Equivalent to POST /graph/load
python scripts/load_graph.py --data-file FILE

# Equivalent to POST /simulation/run
python scripts/simulate_failure.py --vendor "Stripe" --duration 4
```

## References

- [REST API Best Practices](https://restfulapi.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j HTTP API](https://neo4j.com/docs/http-api/)

