# Vendor Risk Digital Twin

A cloud-native framework for predicting third-party vendor failure impact on business operations and compliance posture.

## 🎯 Project Overview

This production-ready cloud-native framework demonstrates how to:
- **Discover** vendor dependencies automatically from GCP infrastructure (Cloud Functions, Cloud Run)
- **Model** vendor-to-service relationships in a graph database (Neo4j)
- **Simulate** vendor failure scenarios and predict cascading impact in real-time
- **Calculate** compliance posture changes (SOC 2, NIST, ISO) with predictive analytics
- **Automate** daily discovery scans and event-driven data processing
- **Track** historical simulation results in BigQuery for analytics and compliance reporting

## 📖 Research Inspiration & GRC 7.0 Context

Modern organizations are increasingly reliant on cloud providers and dozens of third-party SaaS integrations, making vendor risk a dynamic and business-critical concern. Traditional third-party risk management (TPRM) relies on static questionnaires and point-in-time assessments, which cannot keep up with the pace and interconnectedness of cloud-native environments.

Our research is inspired by the evolution of the GRC discipline from reactive, manual practices (GRC 6.0) to the emerging **GRC 7.0 paradigm**:

> **GRC 7.0** emphasizes continuous, API-driven risk monitoring, dynamic modeling, and predictive analytics to provide real-time, actionable insights—moving beyond static compliance checklists to automated, foresight-driven decision-making.

This shift is described by GRC thought leaders as the introduction of **"digital twins"** and **"foresight engines"** in risk and compliance functions.

**The Vendor Risk Digital Twin project implements these ideas by:**

- Modeling complex vendor and service dependencies as a live graph
- Simulating vendor failure scenarios before they happen
- Quantifying business and compliance impact in real-time
- Laying the groundwork for seamless integration with enterprise GRC tools (such as Archer/MetricStream) as an augmented intelligence layer

**For more, see:** [GRC 7.0 – GRC Orchestrate: Digital Twins and the Forward-Looking Power of Risk, Integrity, and Objectives](https://grc2020.com/2025/07/01/grc-7-0-grc-orchestrate-digital-twins-and-the-forward-looking-power-of-risk-integrity-and-objectives/)

## 🏗️ Architecture

**Cloud-Native Architecture (Production-Ready):**
```
GCP APIs → Discovery (Cloud Function) → Pub/Sub → Graph Loader → Neo4j
                                                              ↓
Simulation Service (Cloud Run) ← Dashboard/CLI
         ↓
    Pub/Sub → BigQuery Loader → BigQuery Analytics
```

**Key Components:**
- **Cloud Functions (Gen2):** Discovery, Graph Loader, BigQuery Loader
- **Cloud Run:** Simulation Service (REST API)
- **Pub/Sub:** Event-driven messaging (3 topics, 5 subscriptions)
- **BigQuery:** Historical analytics and compliance reporting
- **Secret Manager:** Secure credential management
- **Cloud Scheduler:** Daily automated discovery (2 AM)
- **Cloud Build:** CI/CD pipeline for automated deployments
- **Cloud Monitoring:** Real-time dashboards and alerting

See [docs/reports/final_report.md](docs/reports/final_report.md) for complete architecture documentation.

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.9+
- **Neo4j Database** (choose one):
  - **Neo4j Desktop** - [Download here](https://neo4j.com/download/) - Local development option (recommended for local-only usage)
  - **Docker** - Containerized local setup
  - **Neo4j Aura** (for cloud-native) - [Free trial available](https://neo4j.com/cloud/aura/) - Managed cloud database, perfect for production deployments

**Optional (for cloud-native features only):**
- **Google Cloud Platform Account:**
  - GCP Project with billing enabled
  - `gcloud` CLI installed and authenticated
  - Required APIs enabled (Cloud Functions, Cloud Run, Pub/Sub, BigQuery, Secret Manager, Cloud Scheduler)

### Installation

**Step 1: Install and Configure Neo4j Database**

<details>
<summary><b>Option A: Neo4j Aura (Recommended for Cloud-Native)</b></summary>

**Best for:** Production deployments, cloud-native architecture, managed service

1. Sign up for [Neo4j Aura](https://neo4j.com/cloud/aura/) (free trial available)
2. Create a new Aura instance:
   - Choose instance size (free tier available)
   - Select region closest to your GCP resources
   - Note: Aura provides a connection URI (not localhost)
3. Copy your connection URI from the Aura dashboard:
   - Format: `neo4j+s://xxxxx.databases.neo4j.io`
   - Username: `neo4j` (or custom)
   - Password: Set during instance creation
4. **Important:** Store credentials in GCP Secret Manager for production deployments

**Note:** This project uses Neo4j Aura on a free trial. For production, consider upgrading to a paid plan based on your data volume and performance requirements.

</details>

<details>
<summary><b>Option B: Neo4j Desktop (Local Development)</b></summary>

1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and launch Neo4j Desktop
3. Create a new project (or use existing)
4. Create a new local DBMS instance:
   - Set password: `password` (or your preferred password)
   - Start the instance
   - Note the connection URI: `neo4j://localhost:7687`

</details>

<details>
<summary><b>Option C: Docker (Local Development)</b></summary>

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

</details>

**Step 2: Setup Python Environment**

```bash
cd vendor-risk-digital-twin
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 3: Configure Credentials**

```bash
cp env.example .env
# Edit .env with your Neo4j connection details:
# - For Aura: Use the connection URI from Aura dashboard (neo4j+s://...)
# - For Desktop/Docker: Use neo4j://localhost:7687
# - Set NEO4J_USER and NEO4J_PASSWORD accordingly
# - Add GCP project details
```

**For Neo4j Aura users:**
- Connection URI format: `neo4j+s://xxxxx.databases.neo4j.io`
- Use the exact URI provided by Aura (includes SSL/TLS)
- Store credentials securely in GCP Secret Manager for production

**For GCP Integration (Optional but Recommended):**
```bash
# Set GCP project
export GCP_PROJECT_ID=your-project-id
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com \
  run.googleapis.com \
  pubsub.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com
```

**Step 4: Verify Neo4j Connection**

**For Neo4j Aura:**
```bash
# Replace with your Aura connection URI and credentials
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('neo4j+s://YOUR_AURA_URI', auth=('neo4j', 'YOUR_PASSWORD')); driver.verify_connectivity(); print('✅ Connected to Neo4j Aura!'); driver.close()"
```

**For Neo4j Desktop/Docker:**
```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Connected to Neo4j!'); driver.close()"
```

If you see `✅ Connected to Neo4j!` (or `✅ Connected to Neo4j Aura!`), you're ready to proceed!

### Usage

#### 🔍 **Just Want to See Results? (No Setup Required)**

If you just want to view existing simulation results without running anything:

```bash
# View the latest simulation output (already generated)
cat data/outputs/simulation_result.json
```

This shows the complete Stripe failure simulation results (operational, financial, compliance impact).

---

#### ✅ **Run Your Own Simulations (Requires Neo4j Setup)**

**Step 1: Load Sample Data into Neo4j**
```bash
python scripts/load_graph.py
# Uses data/sample/sample_dependencies.json and compliance_controls.json by default
```

**Step 2: Run Failure Simulation**
```bash
python scripts/simulate_failure.py --vendor "Stripe" --duration 4
# Outputs impact report to console AND saves to data/outputs/simulation_result.json
```

**Step 3: Visualize in Neo4j Browser**

**For Neo4j Aura:**
- Open the Aura dashboard and click "Open" to launch Neo4j Browser
- Or use the browser URL provided in your Aura instance details
- Run: `MATCH (n) RETURN n LIMIT 40;`

**For Neo4j Desktop/Docker:**
- Open Neo4j Browser: http://localhost:7474
- Run: `MATCH (n) RETURN n LIMIT 40;`

> **Note:** Even for console-only output, Neo4j must be running/accessible because the simulation engine queries the graph database to calculate impact.

**Step 4: Use Web Dashboard (Optional)**

For an interactive web interface to run simulations and view results:

```bash
# Install Node.js dependencies (requires Node.js 18.0+)
cd dashboard
npm install

# Start the dashboard server
npm start
```

Access the dashboard at `http://localhost:5000` to:
- Run simulations through a web interface
- View multi-dimensional impact results
- See graph statistics and recommendations

See `dashboard/README.md` and `dashboard/GETTING_STARTED.md` for detailed setup instructions.

#### ☁️ **Cloud-Native Approach (GCP Integration - Optional)**

**Option A: Use Deployed Cloud Functions (Recommended)**

The system includes automated daily discovery via Cloud Scheduler. To trigger manually:

```bash
# Trigger discovery via HTTP (if deployed)
curl -X POST https://REGION-PROJECT.cloudfunctions.net/vendor-discovery

# Or use gcloud
gcloud functions call vendor-discovery --region=us-central1
```

Discovery results are automatically:
1. Stored in Cloud Storage
2. Published to Pub/Sub (`vendor-discovery-events`)
3. Loaded into Neo4j via Graph Loader Function
4. Available for simulation via Cloud Run service

**Option B: Run Discovery Locally**

```bash
# Discover GCP dependencies
python scripts/gcp_discovery.py --project-id YOUR_PROJECT_ID

# Load discovered data into Neo4j
python scripts/load_graph.py --data-file data/outputs/discovered_dependencies.json
```

**Option C: Use Cloud Run Simulation Service**

```bash
# Run simulation via REST API
curl -X POST https://simulation-service-XXXXX.run.app/simulate \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}'

# List available vendors
curl https://simulation-service-XXXXX.run.app/vendors

# Health check
curl https://simulation-service-XXXXX.run.app/health
```

Results are automatically published to Pub/Sub and loaded into BigQuery for analytics.

## 📁 Project Structure

```
vendor-risk-digital-twin/
├── config/              # Configuration files
├── data/                # Sample data and outputs
├── scripts/             # Python scripts
├── queries/             # Neo4j Cypher queries
├── tests/               # Unit tests
├── docs/                # Documentation
├── research/            # Research deliverables
└── notebooks/           # Jupyter notebooks
```

## 🎓 Research Context

This PoC is part of a research project validating the market gap for cloud-native vendor risk management. For full research proposal, see [docs/ClassProjectProposal.md](docs/ClassProjectProposal.md).

**Research Questions:**
1. Can we automatically discover vendor dependencies from cloud infrastructure?
2. Can we predict vendor failure impact before incidents occur?
3. Can we quantify compliance posture changes from vendor failures?

## 📊 Demo Scenarios

**Tested vendor failure scenarios:**

| Vendor | Duration | Financial Impact | Compliance Impact | Overall Score |
|--------|----------|------------------|-------------------|---------------|
| **Stripe** | 4 hours | $550K total loss | SOC2: -22%, NIST: -12%, ISO: -23% | 0.32 (HIGH) |
| **SendGrid** | 4 hours | $400K total loss | SOC2: -12%, NIST: -10%, ISO: -12% | 0.28 (HIGH) |

**Key Results:**
- **Stripe Failure:** Impacts 2 services, 50,000 customers, 3 business processes
- **SendGrid Failure:** Impacts 1 service, 50,000 customers, 3 business processes
- **Simulation Performance:** <2 seconds per simulation
- **Automation:** Daily discovery runs automatically at 2 AM via Cloud Scheduler

See `data/outputs/simulation_result.json` for detailed results, or query BigQuery `simulations` table for historical analytics.

## 🔧 Development

**Run tests**
```bash
pytest tests/
```

**Format code**
```bash
black scripts/
```

**Lint**
```bash
flake8 scripts/
```

## 📚 Documentation

- [Final Report](docs/reports/final_report.md) - Complete research paper with GCP integration details
- [Architecture Design](docs/design/architecture.md) - System architecture
- [Setup Guide](docs/setup-guides/setup_guide.md) - Detailed setup instructions
- [API Design](docs/design/api_design.md) - REST API documentation
- [Simulation Methodology](docs/setup-guides/simulation_methodology.md) - Impact calculation formulas
- [GCP Integration Phases](docs/reports/final_report.md#6-gcp-cloud-native-integration) - Complete implementation details

## 🔄 Automation & Monitoring

**Automated Workflows:**
- **Daily Discovery:** Cloud Scheduler triggers discovery at 2 AM daily
- **Event-Driven Processing:** Pub/Sub automatically routes events to Graph Loader and BigQuery Loader
- **CI/CD Pipeline:** Cloud Build automatically deploys on code changes

**Monitoring:**
- **Cloud Monitoring Dashboard:** "Vendor Risk Digital Twin - Service Health"
- **Metrics Tracked:** Success rates, error rates, latency (P50/P95/P99), execution counts
- **Alerting:** High error rate alerts, latency alerts, job failure notifications

**Analytics:**
- **BigQuery Tables:** `simulations` table with historical simulation results
- **Analytics Views:** `most_critical_vendors`, `impact_trends`, `vendor_dependency_summary`
- **Integration:** Compatible with Data Studio, Looker, and other BI tools

## 🚀 Deployment

**Deploy All Services via CI/CD:**
```bash
# Deploy via Cloud Build (recommended)
gcloud builds submit --config cloudbuild.yaml

# Or deploy individually
./scripts/deploy_all.sh
```

**Manual Deployment:**
- See [docs/reports/final_report.md](docs/reports/final_report.md#6-gcp-cloud-native-integration) for detailed deployment instructions for each phase

## 🤝 Contributing

This is a research project. For questions or suggestions, contact the research team.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Research inspiration: [GRC 7.0 Digital Twins](https://grc2020.com/2025/07/01/grc-7-0-grc-orchestrate-digital-twins-and-the-forward-looking-power-of-risk-integrity-and-objectives/)
- **Neo4j Aura** for managed cloud graph database (free trial used for this project)
- **Google Cloud Platform** for cloud-native infrastructure and services
- Industry professionals who provided validation through interviews

**Note on Neo4j Aura:** This project uses Neo4j Aura on a free trial. For production deployments, consider upgrading to a paid plan based on your data volume, performance requirements, and SLA needs. Aura provides managed backups, high availability, and automatic scaling.

## 📈 Status

**Current Status:** ✅ Production-Ready
- ✅ Phases 1-8 Complete (Secret Management, Cloud Functions, Cloud Run, BigQuery, Pub/Sub, Cloud Scheduler, Monitoring, CI/CD)
- ✅ Automated daily discovery
- ✅ Event-driven architecture
- ✅ Real-time simulation service
- ✅ Historical analytics in BigQuery
- ✅ Comprehensive monitoring and alerting
