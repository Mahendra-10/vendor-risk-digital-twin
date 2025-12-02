# Vendor Risk Digital Twin

A cloud-native framework for predicting third-party vendor failure impact on business operations and compliance posture.

## 🎯 Project Overview

This proof-of-concept demonstrates how to:
- **Model** vendor-to-service relationships in a graph database (Neo4j)
- **Simulate** vendor failure scenarios and predict cascading impact
- **Calculate** compliance posture changes (SOC 2, NIST, ISO)
- **Discover** vendor dependencies across GCP infrastructure *(planned for Phase 4)*

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

**Current (Phase 3 PoC):**
```
Sample Data → Neo4j Graph → Simulation Engine → Impact Report
```

**Future (Phase 4):**
```
GCP APIs → Discovery Module → Neo4j Graph → Simulation Engine → Impact Report
```

See [docs/design/architecture.md](docs/design/architecture.md) for detailed design.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- **Neo4j Database** (choose one):
  - **Neo4j Desktop** (recommended) - [Download here](https://neo4j.com/download/)
  - Docker (if you prefer containerized setup)

### Installation

**Step 1: Install and Configure Neo4j Database**

<details>
<summary><b>Option A: Neo4j Desktop (Recommended)</b></summary>

1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and launch Neo4j Desktop
3. Create a new project (or use existing)
4. Create a new local DBMS instance:
   - Set password: `password` (or your preferred password)
   - Start the instance
   - Note the connection URI: `neo4j://localhost:7687`

</details>

<details>
<summary><b>Option B: Docker</b></summary>

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
cp .env.example .env
# Edit .env with your Neo4j password (if you changed it from 'password')
```

**Step 4: Verify Neo4j Connection**

```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Connected to Neo4j!'); driver.close()"
```

If you see `✅ Connected to Neo4j!`, you're ready to proceed!

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
```
Open Neo4j Browser: http://localhost:7474
Run: MATCH (n) RETURN n LIMIT 40;
```

> **Note:** Even for console-only output, Neo4j must be running because the simulation engine queries the graph database to calculate impact.

#### 🚧 **Future Approach (Phase 4 - GCP Integration)**

**Step 1: Discover GCP Dependencies** *(Not yet implemented)*
```bash
python scripts/gcp_discovery.py --project-id YOUR_PROJECT_ID
```

**Step 2: Load Discovered Data**
```bash
python scripts/load_graph.py --data-file data/outputs/discovered_dependencies.json
```

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
| **SendGrid** | 4 hours | $320K total loss | SOC2: -13%, NIST: -6%, ISO: -18% | 0.28 (HIGH) |
| Auth0 | *(not yet tested)* | TBD | TBD | TBD |

See `data/outputs/simulation_result.json` for detailed results.

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

- [Architecture Design](docs/design/architecture.md)
- [Setup Guide](docs/setup-guides/setup_guide.md)
- [API Design](docs/design/api_design.md)
- [Simulation Methodology](docs/setup-guides/simulation_methodology.md)

## 🤝 Contributing

This is a research PoC. For questions or suggestions, contact the research team.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Research inspiration: [GRC 7.0 Digital Twins](https://grc2020.com/2025/07/01/grc-7-0-grc-orchestrate-digital-twins-and-the-forward-looking-power-of-risk-integrity-and-objectives/)
- Neo4j for graph database technology
- GCP for cloud API access

# Test CI/CD
# Test CI/CD2
