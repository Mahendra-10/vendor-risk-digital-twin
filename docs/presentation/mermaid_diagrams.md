# Mermaid Diagrams for Presentation
**For: Vendor Risk Digital Twin - Cloud Computing Presentation**

This file contains Mermaid diagram code that can be used in presentations, documentation, or converted to images.

---

## 1. 4-Layer Architecture Diagram

```mermaid
graph TB
    subgraph Presentation["📊 Presentation Layer"]
        Dashboard["Dashboard<br/>(Node.js)"]
        Neo4jBrowser["Neo4j Browser"]
        RESTAPI["REST API"]
    end
    
    subgraph Application["⚙️ Application Layer"]
        Discovery["Discovery Function<br/>(Cloud Functions Gen2)"]
        Simulation["Simulation Service<br/>(Cloud Run)"]
        GraphLoader["Graph Loader<br/>(Cloud Functions)"]
        CICD["CI/CD Pipeline<br/>(Cloud Build)"]
    end
    
    subgraph Data["💾 Data Layer"]
        Neo4j["Neo4j Graph Database"]
        CloudStorage["Cloud Storage<br/>(Discovery Results)"]
        BigQuery["BigQuery<br/>(Analytics)"]
    end
    
    subgraph External["🌐 External Systems"]
        GCPAPIs["GCP APIs<br/>(Functions, Run)"]
        Compliance["Compliance Frameworks<br/>(SOC 2, NIST, ISO)"]
    end
    
    Dashboard --> RESTAPI
    Neo4jBrowser --> Neo4j
    RESTAPI --> Simulation
    RESTAPI --> Discovery
    
    Discovery --> GCPAPIs
    Discovery --> CloudStorage
    Discovery --> GraphLoader
    
    GraphLoader --> Neo4j
    Simulation --> Neo4j
    Simulation --> BigQuery
    
    Neo4j --> Compliance
    
    style Presentation fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style Application fill:#fff4e1,stroke:#e65100,stroke-width:2px
    style Data fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style External fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

---

## 2. Graph Data Model

```mermaid
graph LR
    V[Vendor<br/>Stripe, Auth0, etc.]
    S[Service<br/>payment-api, etc.]
    BP[BusinessProcess<br/>checkout, etc.]
    CC[ComplianceControl<br/>SOC 2, NIST, ISO]
    
    S -->|DEPENDS_ON| V
    S -->|SUPPORTS| BP
    V -->|SATISFIES| CC
    
    style V fill:#ffebee,stroke:#c62828,stroke-width:2px
    style S fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style BP fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style CC fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

---

## 3. Event-Driven Discovery Flow

```mermaid
sequenceDiagram
    participant CS as Cloud Scheduler
    participant DF as Discovery Function
    participant GCP as GCP APIs
    participant CS2 as Cloud Storage
    participant PS as Pub/Sub
    participant GL as Graph Loader
    participant N4J as Neo4j
    
    CS->>DF: Daily Trigger (2 AM)
    DF->>GCP: Query Cloud Functions & Run
    GCP-->>DF: Resource Data
    DF->>DF: Pattern Match Vendors
    DF->>CS2: Store Results (JSON)
    DF->>PS: Publish Event
    PS->>GL: Trigger Graph Loader
    GL->>CS2: Read Discovery Results
    GL->>GL: Convert to Neo4j Format
    GL->>N4J: Load into Graph
    N4J-->>GL: Success
```

---

## 4. Simulation Flow

```mermaid
flowchart TD
    Start([User Request:<br/>Simulate Vendor Failure]) --> API[Simulation Service<br/>Cloud Run]
    API --> Query[Neo4j Query:<br/>Find Affected Services]
    Query --> Traverse[Graph Traversal:<br/>Vendor → Services → Processes]
    Traverse --> Calc[Impact Calculation]
    
    Calc --> Op[Operational Impact<br/>40% weight]
    Calc --> Fin[Financial Impact<br/>35% weight]
    Calc --> Comp[Compliance Impact<br/>25% weight]
    
    Op --> Combine[Combine Scores]
    Fin --> Combine
    Comp --> Combine
    
    Combine --> Results[Return Results<br/><2 seconds]
    Results --> PubSub[Publish to Pub/Sub]
    PubSub --> BQ[BigQuery<br/>Analytics]
    
    style Start fill:#e1f5ff
    style Results fill:#c8e6c9
    style Calc fill:#fff9c4
```

---

## 5. CI/CD Pipeline Flow

```mermaid
flowchart LR
    Code[Code Changes] --> Trigger{Trigger}
    Trigger -->|Manual| Manual[gcloud builds submit]
    Trigger -->|GitHub| GitHub[GitHub Push]
    
    Manual --> Build[Cloud Build]
    GitHub --> Build
    
    Build --> Test[Run Tests<br/>pytest]
    Test --> Docker[Build Docker Image]
    Docker --> Deploy[Deploy Services]
    
    Deploy --> CR[Cloud Run<br/>simulation-service]
    Deploy --> CF1[Cloud Function<br/>vendor-discovery]
    Deploy --> CF2[Cloud Function<br/>graph-loader]
    Deploy --> CF3[Cloud Function<br/>bigquery-loader]
    
    CR --> Done[✅ All Services<br/>Deployed]
    CF1 --> Done
    CF2 --> Done
    CF3 --> Done
    
    style Build fill:#fff4e1
    style Done fill:#c8e6c9
```

---

## 6. Complete System Flow (End-to-End)

```mermaid
graph TB
    subgraph Discovery["Discovery Phase"]
        Scheduler[Cloud Scheduler<br/>Daily 2 AM] --> DiscFunc[Discovery Function]
        DiscFunc --> GCPAPI[GCP APIs]
        GCPAPI --> Storage[Cloud Storage]
        DiscFunc --> PubSub1[Pub/Sub Event]
    end
    
    subgraph Graph["Graph Loading"]
        PubSub1 --> GraphLoader[Graph Loader Function]
        GraphLoader --> Neo4j[(Neo4j Graph)]
    end
    
    subgraph Simulation["Simulation Phase"]
        User[User Request] --> SimService[Simulation Service]
        SimService --> Neo4j
        Neo4j --> SimService
        SimService --> Results[Impact Results]
        Results --> PubSub2[Pub/Sub]
        PubSub2 --> BigQuery[(BigQuery)]
    end
    
    style Discovery fill:#e1f5ff
    style Graph fill:#fff4e1
    style Simulation fill:#e8f5e9
```

---

## 7. GCP Services Integration

```mermaid
graph TB
    subgraph Compute["Compute Services"]
        CF[Cloud Functions Gen2<br/>Discovery, Loaders]
        CR[Cloud Run<br/>Simulation Service]
    end
    
    subgraph Storage["Storage Services"]
        CS[Cloud Storage<br/>Discovery Results]
        BQ[BigQuery<br/>Analytics]
        SM[Secret Manager<br/>Credentials]
    end
    
    subgraph Messaging["Messaging"]
        PS[Pub/Sub<br/>Event Routing]
    end
    
    subgraph Automation["Automation"]
        CSched[Cloud Scheduler<br/>Daily Discovery]
        CB[Cloud Build<br/>CI/CD]
        CM[Cloud Monitoring<br/>Observability]
    end
    
    CSched --> CF
    CF --> CS
    CF --> PS
    PS --> CF
    CR --> BQ
    CR --> PS
    CF --> SM
    CB --> CR
    CB --> CF
    
    style Compute fill:#e3f2fd
    style Storage fill:#e8f5e9
    style Messaging fill:#fff4e1
    style Automation fill:#fce4ec
```

---

## Usage Instructions

### For Presentations:
1. Copy the Mermaid code
2. Use in tools that support Mermaid:
   - **Markdown viewers** (GitHub, GitLab, etc.)
   - **Mermaid Live Editor**: https://mermaid.live
   - **Presentation tools** (some support Mermaid)
   - **Documentation tools** (Confluence, Notion, etc.)

### To Convert to Images:
1. Go to https://mermaid.live
2. Paste the Mermaid code
3. Export as PNG/SVG
4. Use in PowerPoint, Google Slides, etc.

### For Documentation:
- These diagrams can be embedded directly in Markdown files
- GitHub/GitLab will render them automatically

---

**Last Updated:** 2025-12-01  
**Purpose:** Mermaid diagram code for Cloud Computing presentation
