# Neo4j Aura Queries for Vendor Data

**Neo4j Aura Connection:** https://d29c0138.databases.neo4j.io/browser/

Since you're using Neo4j Aura (cloud-hosted Neo4j), all vendor dependency data is stored in the graph database, not in BigQuery's `dependencies` table.

---

## Accessing Neo4j Aura

1. Go to: https://d29c0138.databases.neo4j.io/browser/
2. Log in with your Neo4j Aura credentials
3. Use the Cypher query editor to run queries

---

## Queries for SendGrid

### 1. Find SendGrid Vendor Node

```cypher
MATCH (v:Vendor {name: "SendGrid"})
RETURN v
```

**Returns:** All properties of the SendGrid vendor node (name, category, criticality, etc.)

### 2. Find All Services That Depend on SendGrid

```cypher
MATCH (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)
RETURN v.name as vendor, 
       s.name as service_name,
       s.type as service_type,
       s.service_id as service_id
ORDER BY s.name
```

**Returns:** All services that depend on SendGrid

### 3. Find SendGrid and All Related Nodes (Complete View)

```cypher
MATCH (v:Vendor {name: "SendGrid"})-[r]-(n)
RETURN v, r, n
```

**Returns:** SendGrid vendor node, all relationships, and connected nodes (services, business processes, compliance controls)

### 4. Find Business Processes Affected by SendGrid

```cypher
MATCH (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN v.name as vendor,
       s.name as service,
       collect(DISTINCT bp.name) as business_processes
```

**Returns:** All business processes that would be affected if SendGrid fails

### 5. Complete SendGrid Dependency Graph

```cypher
MATCH path = (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN path
```

**Returns:** Visual graph showing SendGrid → Services → Business Processes

### 6. Count SendGrid Dependencies

```cypher
MATCH (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)
RETURN v.name as vendor,
       count(s) as service_count,
       collect(s.name) as services
```

**Returns:** Count and list of all services depending on SendGrid

### 7. Find Compliance Controls for SendGrid

```cypher
MATCH (v:Vendor {name: "SendGrid"})-[:SATISFIES]->(cc:ComplianceControl)
RETURN v.name as vendor,
       cc.control_id as control_id,
       cc.framework as framework
ORDER BY cc.framework, cc.control_id
```

**Returns:** All compliance controls that SendGrid satisfies

---

## Queries for Any Vendor

### Find All Vendors

```cypher
MATCH (v:Vendor)
RETURN v.name as vendor_name,
       v.category as category,
       v.criticality as criticality
ORDER BY v.name
```

### Find Vendor by Name (Case-Insensitive)

```cypher
MATCH (v:Vendor)
WHERE toLower(v.name) = toLower("SendGrid")
RETURN v
```

### Get Complete Vendor Information

```cypher
MATCH (v:Vendor {name: "SendGrid"})
OPTIONAL MATCH (v)<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
RETURN v.name as vendor,
       v.category as category,
       v.criticality as criticality,
       collect(DISTINCT s.name) as services,
       collect(DISTINCT bp.name) as business_processes,
       collect(DISTINCT cc.control_id) as compliance_controls
```

---

## Visual Graph Queries

### View SendGrid in Graph Visualization

```cypher
MATCH (v:Vendor {name: "SendGrid"})-[r]-(n)
RETURN v, r, n
LIMIT 50
```

**Tip:** In Neo4j Browser, this will show a visual graph. Click on nodes to expand and see more connections.

### View 2-Level Deep Graph

```cypher
MATCH path = (v:Vendor {name: "SendGrid"})-[*1..2]-(n)
RETURN path
LIMIT 100
```

**Returns:** SendGrid and all nodes within 2 relationship hops

---

## Statistics Queries

### Count All Nodes

```cypher
MATCH (v:Vendor)
RETURN count(v) as vendor_count
```

### Count All Relationships

```cypher
MATCH ()-[r]->()
RETURN count(r) as relationship_count
```

### Count Nodes by Type

```cypher
MATCH (n)
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC
```

---

## Troubleshooting

### If SendGrid Not Found

**Check if vendor exists with different case:**
```cypher
MATCH (v:Vendor)
WHERE toLower(v.name) CONTAINS "sendgrid"
RETURN v.name
```

**List all vendors:**
```cypher
MATCH (v:Vendor)
RETURN v.name
ORDER BY v.name
```

### Check Graph Loader Status

**Verify data was loaded:**
```cypher
MATCH (v:Vendor)
RETURN count(v) as total_vendors
```

**Check recent data:**
```cypher
MATCH (v:Vendor)
RETURN v.name, v.category, v.criticality
ORDER BY v.name
LIMIT 20
```

---

## Connection Details

**Neo4j Aura URL:** https://d29c0138.databases.neo4j.io/browser/

**Connection String Format:**
```
neo4j+s://<instance-id>.databases.neo4j.io
```

**Note:** The connection string for applications (not browser) would be:
```
neo4j+s://d29c0138.databases.neo4j.io
```

---

## Comparison: Neo4j vs BigQuery

| Data Type | Location | Query Language |
|-----------|----------|----------------|
| **Vendor Dependencies** | Neo4j Aura | Cypher |
| **Simulation Results** | BigQuery | SQL |
| **Discovery Results** | Cloud Storage + Neo4j | JSON + Cypher |

**Why:**
- **Neo4j** stores the **graph structure** (vendors, services, relationships)
- **BigQuery** stores **simulation results** (time-series data, analytics)
- **Cloud Storage** stores **raw discovery results** (JSON files)

---

## Quick Reference

**Most Common Query:**
```cypher
MATCH (v:Vendor {name: "SendGrid"})-[r]-(n)
RETURN v, r, n
```

**Get All SendGrid Services:**
```cypher
MATCH (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)
RETURN s.name, s.type, s.service_id
```

**Get SendGrid Business Impact:**
```cypher
MATCH (v:Vendor {name: "SendGrid"})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN v.name, s.name, bp.name
```

---

**Last Updated:** 2025-11-30  
**Neo4j Aura Instance:** d29c0138.databases.neo4j.io

