image.png# Image Capture Guide for Slide 6: Results - Performance & Accuracy

## Image 1: Performance Metrics Dashboard

**URL:** https://console.cloud.google.com/monitoring/dashboards/custom/cae64d81-7c4f-45ed-b266-f224a6b8308a?project=vendor-risk-digital-twin

**Steps:**
1. Open the dashboard link above
2. Wait for metrics to load
3. Adjust time range to show recent activity (last 1 hour or 6 hours)
4. Take a screenshot showing:
   - Discovery Function - Execution Count chart
   - Simulation Service - Request Count chart
   - Graph Loader - Execution Count chart
   - Any latency charts visible
5. **Tip:** Use browser zoom (80-90%) to fit more charts in one screenshot

**What it demonstrates:** Real-time monitoring of all services, showing the system is actively running and processing requests.

---

## Image 2: Neo4j Graph Visualization

**URL:** Neo4j Browser (http://localhost:7474 or your Neo4j Aura URL)

**Query to Run:**
```cypher
MATCH (n) 
OPTIONAL MATCH (n)-[r]-(m) 
RETURN n, r, m 
LIMIT 500
```

**Steps:**
1. Open Neo4j Browser
2. Run the query above
3. In the graph view:
   - Click "Fit to Screen" to see all nodes
   - Use the node styling to differentiate:
     - Vendors (red/pink)
     - Services (blue)
     - Business Processes (purple)
     - Compliance Controls (green)
4. Adjust layout so labels are readable
5. Take a screenshot showing:
   - All 5 vendors clearly labeled
   - Services connected to vendors
   - Business processes
   - Relationships visible

**What it demonstrates:** The actual graph database showing discovered vendor dependencies from GCP infrastructure.

**Alternative Query (if too cluttered):**
```cypher
MATCH (v:Vendor)-[r1]-(s:Service)-[r2]-(bp:BusinessProcess)
RETURN v, s, bp, r1, r2
LIMIT 100
```

---

## Image 3: Simulation Results

**URL:** Your dashboard (http://localhost:3000 or deployed URL)

**Steps:**
1. Open your dashboard
2. Navigate to the simulation section
3. Select a vendor (e.g., Stripe)
4. Set failure duration: 4 hours
5. Click "Run Simulation"
6. Wait for results to load
7. Take a screenshot of the "Risk Assessment Report" showing:
   - **Operational Impact:**
     - Services Affected: 2
     - Customers Affected: 50,000
   - **Financial Impact:**
     - Revenue Loss: $550,000
   - **Compliance Impact:**
     - SOC 2: 90% → 70%
     - NIST: 88% → 68%
     - ISO: 85% → 62%
   - Any additional metrics visible

**What it demonstrates:** Real-time impact calculation showing operational, financial, and compliance consequences of vendor failure.

---

## Tips for Better Screenshots

1. **Use Full Screen:** Press F11 to hide browser UI
2. **High Resolution:** Use browser zoom at 100% for crisp images
3. **Clean UI:** Close unnecessary browser tabs/panels
4. **Timing:** Capture when data is fresh and metrics are visible
5. **Multiple Angles:** Consider taking 2-3 screenshots and picking the best one

---

## File Naming Convention

Save images as:
- `slide6_performance_dashboard.png`
- `slide6_neo4j_graph.png`
- `slide6_simulation_results.png`

---

## If Metrics Aren't Showing

**For Performance Dashboard:**
- Trigger a discovery or simulation to generate metrics
- Wait 1-2 minutes for metrics to appear
- Check that services are actually running

**For Neo4j Graph:**
- Ensure data has been loaded (run discovery + graph loader)
- Verify you have 5 vendors in the database
- Try the alternative query if the full graph is too cluttered

**For Simulation Results:**
- Make sure you've run at least one simulation
- Check that the dashboard is connected to Neo4j
- Verify the simulation service is running

