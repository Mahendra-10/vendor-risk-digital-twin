# Setup Guide - Vendor Risk Digital Twin

This guide walks you through setting up the Vendor Risk Digital Twin PoC from scratch.

## Prerequisites

### Software Requirements
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Neo4j Desktop** or **Docker** ([Download Neo4j](https://neo4j.com/download/))
- **GCP Account** with a project ([Create free account](https://cloud.google.com/free))
- **Git** ([Download](https://git-scm.com/downloads))

### Knowledge Requirements
- Basic Python programming
- Basic understanding of graph databases (helpful but not required)
- Familiarity with GCP console (helpful but not required)

## Step 1: Clone Repository

```bash
cd ~/Documents
git clone <your-repo-url>
cd vendor-risk-digital-twin
```

## Step 2: Python Environment Setup

### Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import neo4j, google.cloud.functions_v1; print('✅ Dependencies installed')"
```

## Step 3: Neo4j Setup

### Option A: Neo4j Desktop (Recommended for PoC)

1. **Download and Install**
   - Download from: https://neo4j.com/download/
   - Install and launch Neo4j Desktop

2. **Create Database**
   - Click "New" → "Create Project"
   - Name: "Vendor Risk Digital Twin"
   - Click "Add" → "Local DBMS"
   - Name: `vendor-risk-db`
   - Password: `your_password_here` (remember this!)
   - Version: 5.x (latest)
   - Click "Create"

3. **Start Database**
   - Click "Start" button
   - Wait for status to show "Active"

4. **Verify Connection**
   - Click "Open" → "Neo4j Browser"
   - Run query: `:play start`
   - If browser opens, you're connected! ✅

### Option B: Docker (Alternative)

```bash
docker run -d \
  --name neo4j-vendor-risk \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password_here \
  -v $PWD/neo4j/data:/data \
  neo4j:latest
```

**Verify:**
```bash
docker ps | grep neo4j-vendor-risk
# Should show running container
```

Open browser: http://localhost:7474

## Step 4: GCP Setup

### 4.1 Create GCP Project (if needed)

1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name: `vendor-risk-poc`
4. Click "Create"

### 4.2 Enable Required APIs

```bash
# Enable Cloud Functions API
gcloud services enable cloudfunctions.googleapis.com

# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Secret Manager API (optional)
gcloud services enable secretmanager.googleapis.com
```

**Or via Console:**
1. Go to "APIs & Services" → "Library"
2. Search for and enable:
   - Cloud Functions API
   - Cloud Run API
   - Secret Manager API

### 4.3 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create vendor-risk-sa \
  --display-name="Vendor Risk Discovery"

# Grant permissions (read-only)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:vendor-risk-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.viewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:vendor-risk-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.viewer"

# Create and download key
gcloud iam service-accounts keys create \
  config/secrets/gcp-service-account.json \
  --iam-account=vendor-risk-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

**Verify:**
```bash
ls -l config/secrets/gcp-service-account.json
# Should show the JSON key file
```

### 4.4 Create Service Account via Console (Alternative)

1. Go to: IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `vendor-risk-sa`
4. Description: "Vendor Risk Discovery Service Account"
5. Click "Create and Continue"
6. Grant roles:
   - Cloud Functions Viewer
   - Cloud Run Viewer
7. Click "Continue" → "Done"
8. Click on the service account → "Keys" tab
9. Click "Add Key" → "Create New Key" → JSON
10. Save to: `config/secrets/gcp-service-account.json`

## Step 5: Configuration

### 5.1 Create .env File

```bash
cp .env.example .env
```

### 5.2 Edit .env

Open `.env` in a text editor and update:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here  # ← Update this!

# GCP Configuration
GCP_PROJECT_ID=vendor-risk-poc  # ← Update this!
GCP_SERVICE_ACCOUNT_KEY_PATH=./config/secrets/gcp-service-account.json
GCP_REGION=us-central1

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=False
```

### 5.3 Verify Configuration

```bash
python -c "from scripts.utils import load_config; config = load_config(); print('✅ Config loaded')"
```

## Step 6: Test the Setup

### Test 1: Verify Neo4j Connection

```bash
python scripts/load_graph.py --clear
```

**Expected output:**
```
Connected to Neo4j at bolt://localhost:7687
Database cleared
```

### Test 2: Load Sample Data

```bash
python scripts/load_graph.py \
  --data-file data/sample/sample_dependencies.json \
  --compliance-file data/sample/compliance_controls.json
```

**Expected output:**
```
✅ Graph loaded successfully!
   - Vendors: 5
   - Services: 6
   - Business Processes: 10
   - Compliance Controls: 12
   - Relationships: 23
```

### Test 3: Run Simulation

```bash
python scripts/simulate_failure.py --vendor "Stripe" --duration 4
```

**Expected output:**
```
🔴 Simulating Stripe failure for 4 hours...
✅ Simulation complete. Impact score: 0.67

📊 OPERATIONAL IMPACT:
   - Services Affected: 2
   - Customers Affected: 50,000
   - Business Processes: 3

💰 FINANCIAL IMPACT:
   - Total Cost: $550,000.00
   ...
```

### Test 4: Query Neo4j

Open Neo4j Browser (http://localhost:7474) and run:

```cypher
// View all vendors
MATCH (v:Vendor)
RETURN v

// View dependency graph
MATCH path = (v:Vendor)<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN path
LIMIT 10
```

## Step 7: Run Discovery (Optional)

If you have Cloud Functions or Cloud Run deployed:

```bash
python scripts/gcp_discovery.py \
  --project-id YOUR_PROJECT_ID \
  --output data/outputs/discovered_dependencies.json
```

If you don't have GCP resources yet, skip this step and use sample data.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'neo4j'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Neo4j connection failed"

**Solution:**
1. Verify Neo4j is running:
   - Desktop: Check status in Neo4j Desktop
   - Docker: `docker ps | grep neo4j`
2. Check credentials in `.env` file
3. Test connection:
   ```bash
   python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); print('✅ Connected')"
   ```

### Issue: "GCP authentication failed"

**Solution:**
1. Verify service account key exists:
   ```bash
   ls -l config/secrets/gcp-service-account.json
   ```
2. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="config/secrets/gcp-service-account.json"
   ```
3. Test authentication:
   ```bash
   gcloud auth activate-service-account --key-file=config/secrets/gcp-service-account.json
   ```

### Issue: "Permission denied" errors

**Solution:**
- Ensure service account has required roles:
  - Cloud Functions Viewer
  - Cloud Run Viewer
- Re-grant permissions:
  ```bash
  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vendor-risk-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.viewer"
  ```

### Issue: "No Cloud Functions found"

**Solution:**
- This is expected if you don't have Cloud Functions deployed
- Use sample data instead:
  ```bash
  python scripts/load_graph.py --data-file data/sample/sample_dependencies.json
  ```

## Next Steps

After successful setup:

1. **Explore Neo4j Queries:** See `queries/cypher/` for example queries
2. **Run Multiple Simulations:** Test different vendors and durations
3. **Customize Data:** Edit sample data files to match your scenario
4. **Deploy Test Services:** (Optional) Deploy simple Cloud Functions to test real discovery

## Directory Structure Reference

```
vendor-risk-digital-twin/
├── config/
│   ├── secrets/                      # ← Your GCP credentials go here
│   ├── config.yaml
│   └── compliance_frameworks.yaml
├── data/
│   ├── sample/                       # ← Sample data files
│   ├── schemas/
│   └── outputs/                      # ← Simulation results go here
├── scripts/                          # ← Main Python scripts
├── queries/                          # ← Neo4j query examples
├── tests/                            # ← Unit tests
├── docs/                             # ← Documentation
├── .env                              # ← Your configuration
└── requirements.txt
```

## Getting Help

- **Documentation:** See `docs/architecture.md`
- **Issues:** Check `README.md` for troubleshooting
- **Neo4j Help:** https://neo4j.com/docs/
- **GCP Help:** https://cloud.google.com/docs

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Load sample data
python scripts/load_graph.py --data-file data/sample/sample_dependencies.json

# Run simulation
python scripts/simulate_failure.py --vendor "Stripe" --duration 4

# Discover GCP resources (if available)
python scripts/gcp_discovery.py --project-id YOUR_PROJECT_ID

# Run tests
pytest tests/ -v

# Deactivate environment
deactivate
```

---

**✅ You're all set!** Proceed to run simulations and explore the system.

