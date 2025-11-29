# Quick Start: Running Simulations with Neo4j

This guide provides step-by-step instructions for running vendor failure simulations using Neo4j.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Neo4j Desktop installed and running (or Docker with Neo4j)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with Neo4j credentials

---

## Step-by-Step Process

### Step 1: Verify Neo4j is Running

**Option A: Neo4j Desktop**
1. Open Neo4j Desktop application
2. Ensure your database instance is **Started** (green status)
3. Note the connection URI (usually `bolt://localhost:7687`)

**Option B: Docker**
```bash
docker ps | grep neo4j
# Should show a running container
```

**Test Connection:**
```bash
cd vendor-risk-digital-twin
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Neo4j connected!'); driver.close()"
```

**Expected Output:**
```
✅ Neo4j connected!
```

---

### Step 2: Load Data into Neo4j

Load the sample vendor dependency data into your Neo4j graph:

```bash
python scripts/load_graph.py
```

**What this does:**
- Connects to Neo4j database
- Loads vendor dependencies from `data/sample/sample_dependencies.json`
- Loads compliance controls from `data/sample/compliance_controls.json`
- Creates nodes (Vendors, Services, Business Processes, Compliance Controls)
- Creates relationships (DEPENDS_ON, SUPPORTS, SATISFIES)

**Expected Output:**
```
2025-11-19 13:25:34 - __main__ - INFO - Connected to Neo4j at neo4j://127.0.0.1:7687
2025-11-19 13:25:34 - __main__ - INFO - Loading vendor dependencies into Neo4j...
2025-11-19 13:25:36 - __main__ - INFO - ✅ Data loaded successfully
2025-11-19 13:25:36 - __main__ - INFO - ✅ Compliance controls loaded
2025-11-19 13:25:36 - scripts.utils - INFO - ✅ Graph loaded successfully!
2025-11-19 13:25:36 - scripts.utils - INFO -    - Vendors: 5
2025-11-19 13:25:36 - scripts.utils - INFO -    - Services: 6
2025-11-19 13:25:36 - scripts.utils - INFO -    - Business Processes: 14
2025-11-19 13:25:36 - scripts.utils - INFO -    - Compliance Controls: 15
2025-11-19 13:25:36 - scripts.utils - INFO -    - Relationships: 40
```

**Verify Data Loaded:**
```bash
# Quick check - count nodes
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('MATCH (n) RETURN count(n) as count')
    print(f'Total nodes: {result.single()[\"count\"]}')
driver.close()
"
```

---

### Step 3: Run a Simulation

Run a vendor failure simulation:

```bash
python scripts/simulate_failure.py --vendor "Stripe" --duration 4
```

**Parameters:**
- `--vendor`: Name of the vendor to simulate (must match a vendor in Neo4j)
- `--duration`: Failure duration in hours (1, 2, 4, 8, 24, 72)

**Available Vendors (from sample data):**
- Stripe
- Auth0
- SendGrid
- Datadog
- MongoDB Atlas

**Expected Output:**
```
2025-11-19 13:25:41 - __main__ - INFO - 🔴 Simulating Stripe failure for 4 hours...
2025-11-19 13:25:41 - __main__ - INFO - Calculating operational impact...
2025-11-19 13:25:41 - __main__ - INFO - Calculating financial impact...
2025-11-19 13:25:41 - __main__ - INFO - Calculating compliance impact...
2025-11-19 13:25:41 - __main__ - INFO - ✅ Simulation complete. Impact score: 0.32

============================================================
VENDOR FAILURE SIMULATION: Stripe
============================================================

📊 OPERATIONAL IMPACT:
   - Services Affected: 2
   - Customers Affected: 50,000
   - Business Processes: 3

💰 FINANCIAL IMPACT:
   - Total Cost: $550,000.00
   - Revenue Loss: $300,000.00
   - Failed Transactions: 10,000

🔒 COMPLIANCE IMPACT:
   - SOC2: 22.0% → 70.0%
   - NIST: 12.0% → 76.0%
   - ISO27001: 23.0% → 67.0%

⚠️  OVERALL IMPACT SCORE: 0.32/1.0

💡 RECOMMENDATIONS:
   1. Implement fallback mechanisms for 2 services depending on Stripe
   2. Consider vendor diversification for critical business processes
   3. High financial impact detected ($550,000.00). Implement circuit breakers...
   ...

✅ Results saved to: data/outputs/simulation_result.json
```

---

### Step 4: View Results

**Option A: View JSON Output**
```bash
cat data/outputs/simulation_result.json | python -m json.tool
```

**Option B: View in Neo4j Browser**
1. Open Neo4j Browser: http://localhost:7474
2. Login with credentials (default: `neo4j` / `password`)
3. Run queries to explore the graph:

```cypher
// View all vendors
MATCH (v:Vendor)
RETURN v.name as vendor

// View Stripe dependencies
MATCH (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)
RETURN v, s

// View full dependency path
MATCH path = (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN path
```

**Option C: Query Graph Statistics**
```bash
python -c "
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))

with driver.session() as session:
    # Get statistics
    result = session.run('MATCH (v:Vendor) RETURN count(v) as count')
    print(f'Vendors: {result.single()[\"count\"]}')
    
    result = session.run('MATCH (s:Service) RETURN count(s) as count')
    print(f'Services: {result.single()[\"count\"]}')
    
    result = session.run('MATCH ()-[r]->() RETURN count(r) as count')
    print(f'Relationships: {result.single()[\"count\"]}')

driver.close()
"
```

---

## Complete Example Workflow

Here's a complete example from start to finish:

```bash
# 1. Navigate to project directory
cd vendor-risk-digital-twin

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux

# 3. Verify Neo4j connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Connected'); driver.close()"

# 4. Load sample data
python scripts/load_graph.py

# 5. Run simulation for Stripe (4-hour failure)
python scripts/simulate_failure.py --vendor "Stripe" --duration 4

# 6. Run simulation for SendGrid (2-hour failure)
python scripts/simulate_failure.py --vendor "SendGrid" --duration 2

# 7. View latest results
cat data/outputs/simulation_result.json | python -m json.tool | head -50

# 8. Explore graph in Neo4j Browser
# Open: http://localhost:7474
# Run: MATCH (n) RETURN n LIMIT 40
```

---

## Troubleshooting

### Issue: "Unable to retrieve routing information"

**Cause:** Neo4j is not running or connection URI is incorrect.

**Solution:**
1. Check Neo4j Desktop status (should be "Active")
2. Verify connection URI in `.env` file:
   ```
   NEO4J_URI=bolt://localhost:7687
   ```
3. Try using `bolt://` instead of `neo4j://`:
   ```python
   driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
   ```

### Issue: "Vendor not found"

**Cause:** The vendor name doesn't exist in the graph.

**Solution:**
1. Check available vendors:
   ```bash
   python -c "
   from neo4j import GraphDatabase
   driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
   with driver.session() as session:
       result = session.run('MATCH (v:Vendor) RETURN v.name as vendor')
       for record in result:
           print(record['vendor'])
   driver.close()
   "
   ```
2. Reload data if needed:
   ```bash
   python scripts/load_graph.py
   ```

### Issue: "ModuleNotFoundError: No module named 'neo4j'"

**Cause:** Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Empty graph (0 nodes)

**Cause:** Data not loaded into Neo4j.

**Solution:**
```bash
python scripts/load_graph.py --data-file data/sample/sample_dependencies.json
```

---

## Advanced Usage

### Run Multiple Simulations

```bash
# Test different vendors
for vendor in Stripe Auth0 SendGrid; do
    echo "Simulating $vendor failure..."
    python scripts/simulate_failure.py --vendor "$vendor" --duration 4
    echo ""
done
```

### Custom Duration

```bash
# Simulate 24-hour outage
python scripts/simulate_failure.py --vendor "Stripe" --duration 24

# Simulate 1-hour outage
python scripts/simulate_failure.py --vendor "Stripe" --duration 1
```

### Query Specific Dependencies

```bash
python -c "
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))

with driver.session() as session:
    # Find all services depending on Stripe
    result = session.run('''
        MATCH (v:Vendor {name: \"Stripe\"})<-[:DEPENDS_ON]-(s:Service)
        RETURN s.name as service, s.type as type
    ''')
    print('Services depending on Stripe:')
    for record in result:
        print(f'  - {record[\"service\"]} ({record[\"type\"]})')

driver.close()
"
```

---

## What Happens Behind the Scenes

1. **Simulation Engine** (`simulate_failure.py`):
   - Queries Neo4j to find all services depending on the vendor
   - Traverses the graph to find affected business processes
   - Calculates operational impact (services, customers, RPM)
   - Calculates financial impact (revenue loss, transaction failures)
   - Calculates compliance impact (control failures, score changes)
   - Generates recommendations based on impact severity

2. **Neo4j Queries Used:**
   ```cypher
   // Find services depending on vendor
   MATCH (v:Vendor {name: $vendor})<-[:DEPENDS_ON]-(s:Service)
   RETURN s
   
   // Find business processes supported by those services
   MATCH (v:Vendor {name: $vendor})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
   RETURN DISTINCT bp
   
   // Find compliance controls affected
   MATCH (v:Vendor {name: $vendor})-[:SATISFIES]->(cc:ComplianceControl)
   RETURN cc
   ```

3. **Impact Calculation:**
   - Operational: Based on service count, customer count, RPM
   - Financial: Based on revenue per hour × duration × impact percentage
   - Compliance: Based on control weights and framework baselines

---

## Next Steps

After running simulations:

1. **Explore Neo4j Browser:** Visualize the dependency graph
2. **Modify Sample Data:** Edit `data/sample/sample_dependencies.json` to test your own scenarios
3. **Run Different Scenarios:** Test various vendors and durations
4. **Review Recommendations:** Use the generated recommendations to plan mitigation strategies
5. **Integrate with GCP:** Follow `docs/gcp_integration_roadmap.md` for cloud integration

---

## Quick Reference

```bash
# Activate environment
source venv/bin/activate

# Load data
python scripts/load_graph.py

# Run simulation
python scripts/simulate_failure.py --vendor "Stripe" --duration 4

# View results
cat data/outputs/simulation_result.json

# Open Neo4j Browser
open http://localhost:7474  # macOS
# or visit http://localhost:7474 in your browser
```

---

**✅ You're ready to run simulations!**

For more details, see:
- [Setup Guide](setup_guide.md) - Complete installation instructions
- [Architecture](architecture.md) - System design overview
- [Simulation Methodology](simulation_methodology.md) - How impact is calculated

