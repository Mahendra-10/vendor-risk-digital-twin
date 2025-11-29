# Workflow Explanation: Discovery → Neo4j → Simulation → Browser

This document explains how the four main dashboard actions connect together in the Vendor Risk Digital Twin system.

## 🔄 Complete Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD WORKFLOW                           │
└─────────────────────────────────────────────────────────────────┘

1. Fetch Latest Discovery
   ↓
2. Load into Neo4j
   ↓
3. Run Simulation
   ↓
4. View in Neo4j Browser
```

---

## 📋 Step-by-Step Breakdown

### 1️⃣ **Fetch Latest Discovery** 🔍

**What it does:**
- Fetches the most recent vendor discovery results from **Google Cloud Storage**
- Discovery results contain information about:
  - Which vendors are used in your GCP project
  - Which services depend on each vendor
  - Service metadata (type, RPM, customers affected)

**How it works:**
```javascript
// Dashboard calls: GET /api/discovery/latest?project_id=vendor-risk-digital-twin
// Backend fetches from: gs://vendor-risk-digital-twin-discovery-results/discoveries/
```

**What you see:**
- Number of vendors discovered
- Number of services discovered
- Timestamp of discovery

**Data format:**
```json
{
  "vendors": [
    {
      "name": "Stripe",
      "category": "payment_processor",
      "services": [
        {
          "name": "checkout-service",
          "type": "cloud_run",
          "rpm": 1000,
          "customers_affected": 5000
        }
      ]
    }
  ]
}
```

**Important:** This step only **fetches** the data. It doesn't load it into Neo4j yet.

---

### 2️⃣ **Load into Neo4j** 📊

**What it does:**
- Takes the discovery results and loads them into your **Neo4j graph database**
- Creates nodes (Vendors, Services, Business Processes)
- Creates relationships (DEPENDS_ON, SUPPORTS, SATISFIES)

**How it works:**
```javascript
// Dashboard calls: POST /api/discovery/load
// Backend runs: python scripts/fetch_discovery_results.py --load-to-neo4j
// Which calls: python scripts/load_graph.py --from-gcp
```

**Graph structure created:**
```
(Vendor:Stripe) ←[:DEPENDS_ON]─ (Service:checkout-service) ─[:SUPPORTS]→ (BusinessProcess:Payment)
```

**What happens:**
1. Fetches latest discovery from Cloud Storage (again, to ensure latest)
2. Converts GCP discovery format → Neo4j format
3. Creates/updates nodes in Neo4j:
   - `Vendor` nodes with properties (name, category, criticality)
   - `Service` nodes with properties (name, type, rpm, customers_affected)
   - `BusinessProcess` nodes
4. Creates relationships:
   - `(Service)-[:DEPENDS_ON]->(Vendor)`
   - `(Service)-[:SUPPORTS]->(BusinessProcess)`
   - `(Vendor)-[:SATISFIES]->(ComplianceControl)`

**What you see:**
- Success message: "✅ Discovery results loaded into Neo4j!"
- Neo4j Browser URL appears (if using Aura)
- Vendor list refreshes
- Graph statistics update

**Important:** After this step, your graph database has the vendor dependency data. This is required before running simulations.

---

### 3️⃣ **Run Simulation** 🎯

**What it does:**
- Simulates a vendor failure scenario
- Calculates impact on:
  - **Operations** (affected services, business processes)
  - **Finance** (revenue loss, transaction failures)
  - **Compliance** (control failures, score changes)

**How it works:**
```javascript
// Dashboard calls: POST /api/simulate
// Backend calls: Cloud Run service (or local simulator)
// Cloud Run service:
//   1. Queries Neo4j for vendor dependencies
//   2. Calculates impact
//   3. Publishes result to Pub/Sub
//   4. BigQuery loader automatically saves to BigQuery
```

**Simulation process:**
1. **Query Neo4j** to find all services depending on the vendor:
   ```cypher
   MATCH (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)
   RETURN s.name, s.rpm, s.customers_affected
   ```

2. **Calculate Operational Impact:**
   - Count affected services
   - Sum RPM (requests per minute)
   - Identify business processes

3. **Calculate Financial Impact:**
   - Revenue loss = revenue_per_hour × duration × impact_percentage
   - Failed transactions = rpm × duration × 60
   - Customer impact cost

4. **Calculate Compliance Impact:**
   - Find compliance controls satisfied by vendor
   - Calculate score degradation

5. **Generate Overall Impact Score:**
   ```
   score = (operational × 0.4) + (financial × 0.35) + (compliance × 0.25)
   ```

**What you see:**
- Impact breakdown (operational, financial, compliance)
- Affected services list
- Revenue loss estimate
- Recommendations

**Important:** 
- Requires Neo4j to have data (from Step 2)
- Results are automatically saved to BigQuery (if using Cloud Run)
- Simulation reads from Neo4j but doesn't modify it

---

### 4️⃣ **Neo4j Browser** 🌐

**What it is:**
- Web-based interface to view and query your Neo4j graph database
- Allows you to:
  - Visualize the graph structure
  - Run Cypher queries
  - Explore vendor dependencies
  - See relationships between nodes

**How to access:**
- URL appears automatically after loading discovery into Neo4j
- Format: `https://{instance-id}.databases.neo4j.io/browser/`
- Example: `https://{your-instance-id}.databases.neo4j.io/browser/`

**What you can do:**
1. **View the graph visually:**
   ```cypher
   MATCH (v:Vendor)<-[:DEPENDS_ON]-(s:Service)
   RETURN v, s
   ```

2. **Find all services for a vendor:**
   ```cypher
   MATCH (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)
   RETURN s.name, s.type, s.rpm
   ```

3. **See business processes affected:**
   ```cypher
   MATCH (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
   RETURN DISTINCT bp.name
   ```

4. **Check compliance controls:**
   ```cypher
   MATCH (v:Vendor {name: "Stripe"})-[:SATISFIES]->(cc:ComplianceControl)
   RETURN cc.name, cc.framework
   ```

**Important:**
- Browser shows the **current state** of your graph
- Data is only visible after Step 2 (Load into Neo4j)
- Browser is read-only for viewing (you can't edit via browser in this setup)

---

## 🔗 How They Connect

### Dependency Chain:
```
Fetch Discovery → Load into Neo4j → Run Simulation → View in Browser
     (Step 1)         (Step 2)          (Step 3)         (Step 4)
```

### Data Flow:
```
┌─────────────────┐
│  Cloud Storage  │ ← Discovery results stored here
│  (GCS Bucket)   │
└────────┬────────┘
         │
         │ Fetch Latest Discovery (Step 1)
         ↓
┌─────────────────┐
│   Dashboard     │ ← Displays discovery summary
│   (Frontend)    │
└────────┬────────┘
         │
         │ Load into Neo4j (Step 2)
         ↓
┌─────────────────┐
│   Neo4j Graph   │ ← Vendor/Service nodes & relationships
│   Database      │
└────────┬────────┘
         │
         │ Run Simulation (Step 3)
         ↓
┌─────────────────┐
│  Simulation     │ ← Queries Neo4j, calculates impact
│  Engine         │
└────────┬────────┘
         │
         │ Results saved to BigQuery
         ↓
┌─────────────────┐
│    BigQuery     │ ← Historical simulation data
│   (Analytics)   │
└─────────────────┘

         │
         │ View in Browser (Step 4)
         ↓
┌─────────────────┐
│  Neo4j Browser   │ ← Visualize graph, run queries
│  (Web UI)        │
└─────────────────┘
```

---

## 🎯 Why This Order Matters

1. **Fetch Discovery First:**
   - You need to know what data is available
   - Shows you what will be loaded

2. **Load into Neo4j Second:**
   - Creates the graph structure
   - Required for simulations to work
   - Without this, Neo4j is empty

3. **Run Simulation Third:**
   - Needs Neo4j data to query
   - Can't calculate impact without vendor dependencies
   - Results are saved for analytics

4. **View in Browser Anytime:**
   - Can view graph after Step 2
   - Useful for exploring relationships
   - Helps understand the data structure

---

## 💡 Common Questions

**Q: Can I skip Step 1 and go straight to Step 2?**
- Yes! Step 2 will fetch the latest discovery automatically if you haven't done Step 1.

**Q: What if I run simulation before loading into Neo4j?**
- Simulation will fail or return empty results because there's no data in Neo4j to query.

**Q: Can I view Neo4j Browser before loading data?**
- Yes, but the graph will be empty. You need to load data first to see vendors and services.

**Q: Do I need to fetch discovery every time?**
- No, only when you want to see what's available. Loading into Neo4j will fetch automatically.

**Q: What happens if I load discovery multiple times?**
- Neo4j will update existing nodes or create new ones. It's safe to run multiple times.

---

## 📊 Example Workflow

1. **Click "Fetch Latest Discovery"**
   - Shows: "5 vendors, 12 services discovered"

2. **Click "Load into Neo4j"**
   - Creates 5 Vendor nodes, 12 Service nodes, relationships
   - Neo4j Browser URL appears

3. **Select "Stripe" and click "Run Simulation"**
   - Queries Neo4j: "Which services depend on Stripe?"
   - Finds: checkout-service, payment-service
   - Calculates: $50,000 revenue loss, 2 services affected
   - Saves to BigQuery automatically

4. **Click "Open Neo4j Browser"**
   - See visual graph: Stripe → checkout-service → Payment Process
   - Run queries to explore relationships
   - Verify simulation data

---

## 🔧 Technical Details

### Files Involved:
- **Dashboard Frontend:** `dashboard/templates/index.html`
- **Dashboard Backend:** `dashboard/server.js`
- **Discovery Fetcher:** `scripts/fetch_discovery_results.py`
- **Graph Loader:** `scripts/load_graph.py`
- **Simulation Engine:** `dashboard/simulator.js` (local) or `cloud_run/simulation-service/app.py` (Cloud Run)
- **Neo4j Browser:** Hosted by Neo4j Aura (cloud service)

### APIs Used:
- `GET /api/discovery/latest` - Fetch discovery from GCS
- `POST /api/discovery/load` - Load discovery into Neo4j
- `POST /api/simulate` - Run simulation
- `GET /api/neo4j/info` - Get Neo4j Browser URL

---

This workflow enables you to:
1. **Discover** vendor dependencies in your GCP infrastructure
2. **Model** them as a graph in Neo4j
3. **Simulate** failure scenarios and predict impact
4. **Visualize** and explore the relationships

Each step builds on the previous one, creating a complete vendor risk analysis system! 🎉

