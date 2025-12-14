# Neo4j Graph Visualization Queries

Use these Cypher queries in Neo4j Browser to generate the four graph visualizations for the report.

## Figure 3: Full Dependency Graph - Complete Vendor Ecosystem

**Query:**
```cypher
MATCH (v:Vendor)
OPTIONAL MATCH (v)<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
RETURN v, s, bp, cc
```

**What it shows:** All vendors, services, business processes, and compliance controls with their relationships.

**Instructions:**
1. Open Neo4j Browser
2. Paste the query above
3. Click "Run"
4. Adjust the visualization layout if needed (use the graph view)
5. Take a screenshot and save as `screenshot1_full_dependency_graph.png`

---

## Figure 4: Auth0 Dependency Cascade - Failure Impact Visualization

**Query:**
```cypher
MATCH path = (v:Vendor {name: 'Auth0'})<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
RETURN v, s, bp, cc, path
```

**Alternative (if Auth0 doesn't exist, use the first vendor):**
```cypher
MATCH (v:Vendor)
WITH v LIMIT 1
MATCH path = (v)<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
RETURN v, s, bp, cc, path
```

**What it shows:** A single vendor (Auth0) and all services, business processes, and compliance controls that depend on it.

**Instructions:**
1. Run the query in Neo4j Browser (Auth0 is the vendor being visualized)
2. The graph will show the cascade effect of Auth0's failure
3. Take a screenshot and save as `screenshot2_stripe_cascade.png` (keep filename for consistency with report)

---

## Figure 5: Business Process Dependencies - Service-to-Process Mapping

**Query:**
```cypher
MATCH (s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (s)-[:DEPENDS_ON]->(v:Vendor)
RETURN s, bp, v
```

**What it shows:** All services, the business processes they support, and the vendors they depend on.

**Instructions:**
1. Run the query in Neo4j Browser
2. The visualization will show service-to-process relationships
3. Take a screenshot and save as `screenshot3_business_processes.png`

---

## Figure 6: Compliance Control Attribution - Vendor-to-Control Relationships

**Query:**
```cypher
MATCH (v:Vendor)-[:SATISFIES]->(cc:ComplianceControl)
OPTIONAL MATCH (v)<-[:DEPENDS_ON]-(s:Service)
RETURN v, cc, s
```

**What it shows:** All vendors, the compliance controls they satisfy, and the services that depend on them.

**Instructions:**
1. Run the query in Neo4j Browser
2. The visualization will show vendor-to-compliance-control relationships
3. Take a screenshot and save as `screenshot4_compliance_controls.png`

---

## Tips for Better Visualizations

1. **Color coding:** In Neo4j Browser, you can customize node colors:
   - Vendors: Red or Orange
   - Services: Blue
   - Business Processes: Green
   - Compliance Controls: Purple

2. **Layout:** Use the graph view and try different layout options:
   - Force-directed layout (default)
   - Hierarchical layout
   - Circular layout

3. **Node sizing:** Adjust node sizes based on importance (e.g., larger nodes for critical vendors)

4. **Labels:** Make sure node labels are visible and readable

5. **Screenshot quality:** 
   - Use full-screen mode in Neo4j Browser
   - Zoom to fit all nodes
   - Use high-resolution screenshots (at least 1920x1080)

---

## Quick Check: Verify Your Data

Before generating screenshots, verify your current data:

```cypher
// Count nodes by type
MATCH (n)
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC;
```

This should show:
- 5 Vendors
- 4 Services
- Plus any Business Processes and Compliance Controls

