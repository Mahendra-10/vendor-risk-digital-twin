# Vendor Risk Digital Twin

A cloud-native framework for predicting third-party vendor failure impact on business operations and compliance posture.

## 🎯 Project Overview

This proof-of-concept demonstrates how to:
- **Discover** vendor dependencies across GCP infrastructure
- **Model** vendor-to-service relationships in a graph database
- **Simulate** vendor failure scenarios and predict cascading impact
- **Calculate** compliance posture changes (SOC 2, NIST, ISO)

## 🏗️ Architecture

```
Vendor Dependencies → GCP Discovery → Neo4j Graph → Simulation Engine → Impact Report
```

See [docs/architecture.md](docs/architecture.md) for detailed design.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Neo4j Desktop or Docker
- GCP Account (free tier)
- GCP Service Account with Cloud Functions/Cloud Run read permissions

### Installation

1. **Clone and setup**
```bash
cd vendor-risk-digital-twin
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure credentials**
```bash
cp .env.example .env
# Edit .env with your Neo4j and GCP credentials
```

3. **Start Neo4j**
```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### Usage

**Step 1: Discover GCP Dependencies**
```bash
python scripts/gcp_discovery.py --project-id YOUR_PROJECT_ID
```

**Step 2: Load Data into Neo4j**
```bash
python scripts/load_graph.py --data-file data/outputs/discovered_dependencies.json
```

**Step 3: Run Failure Simulation**
```bash
python scripts/simulate_failure.py --vendor "Stripe" --duration 4
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

This PoC is part of a research project validating the market gap for cloud-native vendor risk management. For full research proposal, see [../ProjectProposal.md](../ProjectProposal.md).

**Research Questions:**
1. Can we automatically discover vendor dependencies from cloud infrastructure?
2. Can we predict vendor failure impact before incidents occur?
3. Can we quantify compliance posture changes from vendor failures?

## 📊 Demo Scenarios

Three vendor failure scenarios are demonstrated:

| Vendor | Affected Services | Business Impact | Compliance Impact |
|--------|------------------|-----------------|-------------------|
| Stripe | Payment API, Checkout | $150K/hour revenue | SOC 2: -16% |
| Auth0 | User Auth, SSO | 50K users locked out | NIST: -12% |
| SendGrid | Email Notifications | Customer comms down | ISO 27001: -8% |

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

- [Architecture Design](docs/architecture.md)
- [Setup Guide](docs/setup_guide.md)
- [API Design](docs/api_design.md)
- [Simulation Methodology](docs/simulation_methodology.md)

## 🤝 Contributing

This is a research PoC. For questions or suggestions, contact the research team.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Research inspiration: [GRC 7.0 Digital Twins](https://grc2020.com/2025/07/01/grc-7-0-grc-orchestrate-digital-twins-and-the-forward-looking-power-of-risk-integrity-and-objectives/)
- Neo4j for graph database technology
- GCP for cloud API access

