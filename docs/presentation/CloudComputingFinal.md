# Slide 1: Vendor Risk Digital Twin: A Cloud-Native Framework for Predicting Third-Party Failure Impact

**Cloud Computing Course | December 2025**  
**Authors:** Mahendra Shahi, Clifford Odhiambo, Jalil Rezek

---

## Slide 2: Problem Statement & Motivation

### The Problem: Organizations Cannot Predict Vendor Failure Impact

- Cloud-native organizations depend on **30-50 third-party SaaS vendors**
- Average cost: **$500K-$2M per major vendor failure**
- Current tools are **reactive** (static questionnaires, no simulation)
- **No cloud integration** - can't map vendor → cloud resource → business process

### Why It Matters

- Regulatory requirements (DORA, NIS2) mandate resilience testing
- Organizations need **predictive capabilities**, not reactive checklists

> "Especially on the contract, the legality side, the trade compliance, the contracts, procurements, that's a lot of manual work and sometimes they get tricked"  
> — *John Zehnpfennig II, 20+ years, Director of Cybersecurity, CGI Federal*

---

## Slide 3: Background / Prior Work

### Related Work and Gaps

#### Existing Solutions

- **GRC Platforms:** Manual data entry, no simulation
- **Security Ratings:** External scores, no infrastructure mapping
- **Risk Quantification:** Financial-only, no operational simulation

#### Gap Identified

No existing solution combines:
- ✅ Automated cloud-native discovery
- ✅ Graph-based dependency modeling
- ✅ Real-time failure simulation
- ✅ Multi-dimensional impact prediction

> "Most companies are still struggling to implement basic automation... so a dynamic, predictive approach is exactly where the market is heading, even if it still feels futuristic to some"  
> — *Anurag Baral, 5+ years, Cyber Security Sales Engineer, Carahsoft*

GRC 7.0 – GRC Orchestrate: Digital Twins and the Forward-Looking Power of Risk, Integrity, and Objectives
- Michael Rasmussen
Screenshot of article about GRC 7.0
---

## Slide 4: Design / Approach

### Cloud-Native, Event-Driven Architecture

#### Architecture

- **4-Layer Design:** Web Dashboard → Application → Data → External Systems
- **GCP Services:** Cloud Functions (Gen2), Cloud Run, Pub/Sub, Neo4j, BigQuery, Cloud Storage, Secret Manager, Cloud Scheduler, Cloud Build, Cloud Monitoring

#### Design Principles

- **Serverless backend** (Cloud Functions & Cloud Run)
- **Event-driven** (Pub/Sub for decoupled processing)
- **Graph-based modeling** (Neo4j for dependency traversal)
- **Automated discovery** (GCP API integration)

#### Graph Model

- **Nodes:** Vendor, Service, BusinessProcess, ComplianceControl
- **Relationships:** DEPENDS_ON, SUPPORTS, SATISFIES
- **Example:** `payment-api → DEPENDS_ON → Stripe → SUPPORTS → checkout`
- **Vendors:** 5 vendors (Stripe, Auth0, SendGrid, Twilio, MongoDB Atlas)

#### Architecture Diagrams

- **Figure 1:** 4-Layer Architecture
- **Figure 2:** Graph Data Model

---

## Slide 5: Architecture Diagrams

- **Figure 1:** 4-Layer Architecture
- **Figure 2:** Graph Data Model

---

## Slide 6: Implementation

### Web Dashboard (Presentation Layer)

#### Technology Stack

- **Backend:** Node.js/Express server, RESTful API architecture
- **Frontend:** HTML/CSS/JavaScript with responsive UI

#### Backend Integration

- Direct Neo4j connection for real-time graph queries
- REST API endpoints for vendor simulation (`/api/simulate`)
- Graph statistics and dependency visualization (`/api/graph/*`)

#### Features

- Vendor selection
- Failure duration configuration
- Multi-dimensional impact visualization
- Actionable recommendations
- **Deployment:** Standalone Express server, can be containerized or deployed to Cloud Run

### Data Sources

#### Operational/Financial

- Hardcoded business metrics (revenue/hour, customer count)
- Configurable via `config.yaml`

#### Compliance

- Framework mappings loaded from `compliance_frameworks.yaml`
- SOC 2, NIST, ISO 27001 controls with vendor-to-control mappings and weights

**Example Configuration:**
```yaml
# Example: Stripe maps to SOC 2 CC6.6 (Transmission Security)
soc2:
  CC6.6:
    vendors: [Stripe, SendGrid, Twilio]
    weight: 0.12
```

---

## Slide 7: Results

### Functional Evaluation

- **Vendor Detection:** Pattern-based detection for known vendors (Stripe, Auth0, SendGrid, etc.)
- **Simulation Accuracy:** Calculation logic verified through unit tests
- **Test Coverage:** Unit + integration tests (discovery, simulation, impact calculations)
- **Scaling:** Auto-scaling configured (Cloud Run: 0-10 container instances, Cloud Functions: auto-scale based on Pub/Sub message volume)

---

## Slide 8: Results Visualizations

- **Figure 3:** Neo4j graph showing relationships between vendors, compliances, and Cloud services
- **Figure 4:** Simulation results showing what happens if Auth0 goes down for 4 hours with full impact report

---

## Slide 10: Dashboard Performance Metrics

- **Figure 5:** Dashboard to track performance and metrics

---

## Slide 11: Remaining Issues & Future Directions

### Current Limitations

- Pattern-based vendor detection (~5% false negative rate)
- GCP-only (no AWS/Azure support yet)

### Future Directions

- **Multi-cloud support** (AWS, Azure)
- **ML-based vendor detection**
- **Machine Learning integration** (Vertex AI)
- Reach out to small government federal contractors

---

## Slide 12: Summary & Key Takeaways

### Problem Addressed

- Organizations cannot predict vendor failure impact
- Current tools are reactive, not predictive

### Our Solution

- Automated cloud-native discovery from GCP
- Graph-based dependency modeling
- Real-time failure simulation

> "Digital twins are not dashboards. They are strategic instruments of foresight. They empower GRC to shift from accountability to adaptability, from control to intelligence."  
> — *Michael Rasmussen, GRC Analyst & Pundit at GRC 20/20 Research*

### Integration Opportunity with Existing GRC Tools

**Proven Integration Approach:** Our cloud-native GCP integration demonstrates automated data ingestion at scale

- **Figure 6:** Integration Opportunity with Existing GRC Tools (simplified architecture)

The framework can serve as an **augmented intelligence layer** for existing GRC platforms (Archer, MetricStream, ServiceNow), combining automated discovery with enterprise GRC workflows.

---

## Contact & Resources

**Course:** Cloud Computing | December 2025  
**Institution:** Johns Hopkins University

---

## Slide 13: Thank You

*Thank You*
