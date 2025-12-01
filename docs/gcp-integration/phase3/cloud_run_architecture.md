# Cloud Run, Docker, and Neo4j Aura Architecture

**Documentation:** How Cloud Run, Docker, and Neo4j Aura connect in the Vendor Risk Digital Twin system.

**Last Updated:** 2025-11-27

---

## 🏗️ Architecture Overview

The Vendor Risk Digital Twin simulation service uses a containerized architecture deployed on Google Cloud Run, connecting to a cloud-hosted Neo4j Aura database. This document explains how these components interact.

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Environment                   │
│                                                               │
│  ┌──────────────┐                                            │
│  │   Docker     │  ← Builds container image                  │
│  │  (Dockerfile)│     from source code                        │
│  └──────┬───────┘                                            │
│         │                                                     │
│         │ docker build / gcloud builds submit                │
│         ▼                                                     │
│  ┌──────────────────┐                                        │
│  │ Container Image   │  ← Contains:                          │
│  │ (simulation-      │     • Flask web application           │
│  │  service)         │     • Python dependencies             │
│  │                    │     • Application code               │
│  └──────────────────┘     • Neo4j driver                    │
└─────────────────────────────────────────────────────────────┘
         │
         │ Push to GCP Container Registry
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Cloud Run Service                        │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  Docker Container (running Flask app)        │  │    │
│  │  │                                              │  │    │
│  │  │  ┌────────────────────────────────────────┐ │  │    │
│  │  │  │  Flask API (app.py)                   │ │  │    │
│  │  │  │  • POST /simulate                     │ │  │    │
│  │  │  │  • GET /vendors                       │ │  │    │
│  │  │  │  • GET /health                        │ │  │    │
│  │  │  └───────────┬───────────────────────────┘ │  │    │
│  │  │              │                             │  │    │
│  │  │              │ Gets credentials             │  │    │
│  │  │              ▼                             │  │    │
│  │  │  ┌─────────────────────────────────────┐ │  │    │
│  │  │  │  GCP Secret Manager                 │ │  │    │
│  │  │  │  • neo4j-uri                        │ │  │    │
│  │  │  │  • neo4j-user                       │ │  │    │
│  │  │  │  • neo4j-password                   │ │  │    │
│  │  │  └───────────┬─────────────────────────┘ │  │    │
│  │  │              │                             │  │    │
│  │  │              │ Uses credentials            │  │    │
│  │  │              ▼                             │  │    │
│  │  │  ┌─────────────────────────────────────┐ │  │    │
│  │  │  │  Neo4j Python Driver                │ │  │    │
│  │  │  │  (neo4j package)                    │ │  │    │
│  │  │  └───────────┬─────────────────────────┘ │  │    │
│  │  └──────────────┼─────────────────────────────┘  │    │
│  │                 │                                 │    │
│  └─────────────────┼─────────────────────────────────┘    │
│                    │                                        │
│                    │ HTTPS/TLS Connection                   │
│                    │ (neo4j+s:// protocol)                   │
│                    ▼                                        │
└─────────────────────────────────────────────────────────────┘
                    │
                    │ Internet
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Neo4j Aura (Cloud-Hosted)                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Neo4j Database Instance                      │    │
│  │         (your-instance-id.databases.neo4j.io)        │    │
│  │                                                       │    │
│  │  Graph Data:                                         │    │
│  │  • Vendor nodes (Stripe, Auth0, etc.)                │    │
│  │  • Service nodes (payment-api, etc.)                │    │
│  │  • Business Process nodes                            │    │
│  │  • Compliance Control nodes                          │    │
│  │  • Relationships (DEPENDS_ON, SUPPORTS, SATISFIES)  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Component Relationships

### 1. Docker → Cloud Run

**Relationship:** Docker packages the application; Cloud Run executes it.

**Process:**
1. **Docker Build:** `Dockerfile` defines how to package the application
   
   The Dockerfile does more than just list dependencies - it defines the **entire runtime environment**:
   
   ```dockerfile
   # 1. Base image (Python runtime environment)
   FROM python:3.11-slim
   
   # 2. System dependencies (if needed)
   RUN apt-get update && apt-get install -y gcc
   
   # 3. Working directory (where files go)
   WORKDIR /app
   
   # 4. Python dependencies (libraries)
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # 5. Application code (your files)
   COPY scripts/ ./scripts/
   COPY config/ ./config/
   COPY app.py .
   
   # 6. Environment variables
   ENV PYTHONPATH=/app
   
   # 7. How to run the application
   CMD ["python", "app.py"]
   ```
   
   **What the Dockerfile specifies:**
   - ✅ **Base environment:** Python 3.11 runtime
   - ✅ **System tools:** gcc compiler (if needed)
   - ✅ **Python libraries:** From requirements.txt (Flask, Neo4j driver, etc.)
   - ✅ **File structure:** Where to put code files
   - ✅ **Environment setup:** PYTHONPATH, working directory
   - ✅ **Startup command:** How to run the app when container starts
   
   **How Docker Uses the Dockerfile:**
   
   When someone runs `docker build`, Docker **automatically**:
   1. Reads the Dockerfile line by line
   2. Executes each instruction in order
   3. Creates a container image with everything specified
   4. Produces the same result on any machine
   
   **Example:**
   ```bash
   # Someone clones your repo
   git clone https://github.com/your-repo/vendor-risk-digital-twin.git
   cd vendor-risk-digital-twin
   
   # They run this command
   docker build -f cloud_run/simulation-service/Dockerfile -t simulation-service .
   
   # Docker automatically:
   # ✅ Reads Dockerfile
   # ✅ Downloads Python 3.11 base image
   # ✅ Installs gcc
   # ✅ Copies requirements.txt
   # ✅ Runs pip install (installs Flask, Neo4j, etc.)
   # ✅ Copies your code files
   # ✅ Sets environment variables
   # ✅ Creates the image
   
   # Result: They get the EXACT same environment as you!
   ```
   
   **Why This Matters:**
   - ✅ **Reproducibility:** Same environment on any machine (Mac, Linux, Windows, Cloud)
   - ✅ **No "works on my machine":** Everyone gets identical setup
   - ✅ **Automatic:** Docker handles everything - no manual installation needed
   - ✅ **Version Control:** Dockerfile is in git, so everyone uses the same version

2. **Image Creation:** Docker builds a container image containing:
   - Python runtime
   - Application code (Flask API)
   - Dependencies (Flask, Neo4j driver, etc.)
   - Configuration files

3. **Image Push:** Image is pushed to GCP Container Registry
   ```bash
   gcloud builds submit --tag gcr.io/vendor-risk-digital-twin/simulation-service
   ```

4. **Cloud Run Deployment:** Cloud Run pulls the image and runs it
   ```bash
   gcloud run deploy simulation-service \
     --image gcr.io/vendor-risk-digital-twin/simulation-service
   ```

**Key Points:**
- Docker creates a portable, self-contained package
- Cloud Run provides the runtime environment
- No need to manage servers or infrastructure

---

### 2. Cloud Run → Neo4j Aura

**Relationship:** Cloud Run service queries Neo4j Aura for graph data.

**Connection Flow:**

1. **Credential Retrieval:**
   ```python
   # app.py gets credentials from Secret Manager
   uri = get_secret('neo4j-uri', project_id)  # neo4j+s://your-instance-id.databases.neo4j.io
   user = get_secret('neo4j-user', project_id)  # neo4j
   password = get_secret('neo4j-password', project_id)
   ```

2. **Driver Initialization:**
   ```python
   from neo4j import GraphDatabase
   driver = GraphDatabase.driver(uri, auth=(user, password))
   ```

3. **Connection Establishment:**
   - Cloud Run container → Internet → Neo4j Aura
   - Uses HTTPS/TLS (secure connection via `neo4j+s://`)
   - Authenticates with username/password

4. **Query Execution:**
   ```python
   session = driver.session()
   result = session.run("MATCH (v:Vendor {name: $name}) RETURN v", name="Stripe")
   ```

**Key Points:**
- Connection is over the public internet (HTTPS/TLS secured)
- No VPC required (Aura is publicly accessible)
- Credentials stored securely in GCP Secret Manager
- Connection is stateless (new connection per request, or connection pooling)

---

### 3. Docker → Neo4j Aura (Indirect)

**Relationship:** Docker packages the Neo4j driver; Cloud Run uses it to connect.

**Process:**
1. **Dockerfile includes Neo4j driver:**
   ```dockerfile
   # requirements.txt includes:
   neo4j==5.16.0
   ```

2. **Container has driver installed:**
   - When Cloud Run starts the container, the Neo4j driver is available
   - Application code can import and use it

3. **Runtime connection:**
   - Container runs → Flask app starts → Gets credentials → Connects to Aura

**Key Points:**
- Docker packages the connection capability
- Cloud Run provides the runtime to execute it
- Neo4j Aura provides the data storage

---

## 📊 Data Flow: Running a Simulation

Here's what happens when a user runs a simulation:

```
Step 1: User Request
   ↓
   POST https://simulation-service-xxx.run.app/simulate
   {"vendor": "Stripe", "duration": 4}

Step 2: Cloud Run Receives Request
   ↓
   • Cloud Run routes to available container instance
   • If no instance running, Cloud Run starts one (cold start)
   • Request forwarded to Flask app inside container

Step 3: Flask App Processes Request
   ↓
   • app.py receives POST /simulate
   • Extracts vendor name and duration
   • Calls get_neo4j_credentials()

Step 4: Credential Retrieval
   ↓
   • Queries GCP Secret Manager
   • Gets: neo4j-uri, neo4j-user, neo4j-password
   • Returns credentials to application

Step 5: Neo4j Connection
   ↓
   • Creates Neo4j driver: GraphDatabase.driver(uri, auth=(user, password))
   • Connects to: neo4j+s://your-instance-id.databases.neo4j.io
   • Establishes HTTPS/TLS connection

Step 6: Query Execution
   ↓
   • Runs Cypher query to find vendor dependencies:
     MATCH (v:Vendor {name: "Stripe"})<-[:DEPENDS_ON]-(s:Service)
     RETURN v, s
   • Neo4j Aura executes query and returns results

Step 7: Impact Calculation
   ↓
   • Flask app receives graph data from Neo4j
   • Calculates operational impact (services affected)
   • Calculates financial impact (revenue loss)
   • Calculates compliance impact (control failures)

Step 8: Response
   ↓
   • Flask app returns JSON with simulation results
   • Cloud Run sends HTTP response to user
   • Container may be kept warm for next request (or shut down)
```

---

## 🔐 Security Architecture

### Credential Management

```
┌─────────────────┐
│  GCP Secret     │  ← Stores credentials securely
│  Manager        │     • Encrypted at rest
│                 │     • Access controlled via IAM
└────────┬────────┘
         │
         │ Cloud Run service account has access
         ▼
┌─────────────────┐
│  Cloud Run      │  ← Reads credentials at runtime
│  Container      │     • Never stored in code
│                 │     • Retrieved per request/startup
└────────┬────────┘
         │
         │ Uses credentials to authenticate
         ▼
┌─────────────────┐
│  Neo4j Aura     │  ← Validates credentials
│                 │     • Username/password auth
│                 │     • TLS encryption
└─────────────────┘
```

### Network Security

- **Cloud Run → Neo4j Aura:** HTTPS/TLS encrypted connection
- **Protocol:** `neo4j+s://` (secure Neo4j protocol)
- **Authentication:** Username/password (stored in Secret Manager)
- **No VPC Required:** Aura is publicly accessible (but secured)

---

## 🚀 Deployment Flow

### Complete Deployment Process

```
1. Developer writes code
   ↓
   app.py, Dockerfile, requirements.txt

2. Docker builds image
   ↓
   docker build -t simulation-service .
   OR
   gcloud builds submit --tag gcr.io/.../simulation-service

3. Image stored in Container Registry
   ↓
   gcr.io/vendor-risk-digital-twin/simulation-service:latest

4. Cloud Run deploys service
   ↓
   gcloud run deploy simulation-service --image gcr.io/...

5. Cloud Run pulls image and starts container
   ↓
   Container runs Flask app

6. Flask app initializes
   ↓
   • Reads GCP_PROJECT_ID from environment
   • Fetches Neo4j credentials from Secret Manager
   • Ready to accept requests

7. Service is live
   ↓
   https://simulation-service-xxx.run.app
```

---

## 📝 Key Configuration Files

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```
**Purpose:** Defines how to package the application into a container.

### requirements.txt
```
Flask==3.0.0
neo4j==5.16.0
google-cloud-secret-manager==2.18.0
```
**Purpose:** Lists Python dependencies, including Neo4j driver.

### app.py
```python
# Gets credentials from Secret Manager
uri = get_secret('neo4j-uri', project_id)
driver = GraphDatabase.driver(uri, auth=(user, password))
```
**Purpose:** Application code that connects to Neo4j Aura.

### deploy.sh
```bash
# Builds and deploys
gcloud builds submit --tag ${IMAGE_NAME}
gcloud run deploy ${SERVICE_NAME} --image ${IMAGE_NAME}
```
**Purpose:** Automates the build and deployment process.

---

## 🔄 Lifecycle Management

### Container Lifecycle

1. **Cold Start:**
   - Cloud Run starts new container instance
   - Container initializes (loads Python, imports modules)
   - Flask app starts, connects to Neo4j
   - Ready to serve requests (~5-10 seconds)

2. **Warm Instance:**
   - Container stays alive between requests
   - Neo4j connection may be reused (connection pooling)
   - Fast response time (~100-500ms)

3. **Scaling:**
   - Cloud Run automatically scales based on traffic
   - Multiple container instances can run simultaneously
   - Each instance has its own Neo4j connection

4. **Shutdown:**
   - After idle period, Cloud Run shuts down container
   - Neo4j connections are closed
   - Next request triggers cold start

---

## 🎯 Benefits of This Architecture

### Docker Benefits
- **Portability:** Same container works locally and in cloud
- **Consistency:** Same environment everywhere
- **Isolation:** Dependencies don't conflict
- **Reproducibility:** Same build = same result

### Cloud Run Benefits
- **Serverless:** No server management
- **Auto-scaling:** Handles traffic spikes automatically
- **Pay-per-use:** Only pay for actual usage
- **HTTPS:** Automatic SSL certificates
- **Global:** Deploy to multiple regions

### Neo4j Aura Benefits
- **Managed:** No database administration
- **Scalable:** Handles growth automatically
- **Secure:** Enterprise-grade security
- **Accessible:** Available from anywhere (internet)
- **Free Tier:** Perfect for development/testing

---

## 🔍 Troubleshooting Connections

### Issue: Container can't connect to Neo4j Aura

**Check:**
1. Credentials in Secret Manager are correct
2. Neo4j Aura instance is running
3. Connection URI is correct (`neo4j+s://...`)
4. Firewall/network allows outbound HTTPS (port 443)

**Debug:**
```bash
# Check Cloud Run logs
gcloud run services logs read simulation-service --region us-central1

# Test connection from local machine
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j+s://your-instance-id.databases.neo4j.io', 
                               auth=('neo4j', 'password'))
driver.verify_connectivity()
print('✅ Connected')
"
```

### Issue: Cold start is slow

**Solution:**
- Use connection pooling
- Keep minimum instances warm
- Optimize container startup time

---

## 📚 Related Documentation

- [GCP Integration Roadmap](gcp_integration_roadmap.md) - Complete GCP integration guide
- [Phase 3: Cloud Run Deployment](gcp_integration_roadmap.md#phase-3-containerized-services---cloud-run) - Deployment details
- [Architecture Overview](architecture.md) - Overall system architecture
- [Setup Guide](setup_guide.md) - Initial setup instructions

---

## 🎓 Learning Outcomes

By understanding this architecture, you've learned:

1. **Containerization:** How Docker packages applications
2. **Serverless Computing:** How Cloud Run executes containers
3. **Cloud Databases:** How to connect to managed databases
4. **Secret Management:** Secure credential storage and retrieval
5. **Microservices:** Service-to-service communication patterns
6. **HTTPS/TLS:** Secure network connections
7. **Auto-scaling:** Automatic resource management

---

**This architecture demonstrates a production-ready, cloud-native application pattern used by modern applications.**

