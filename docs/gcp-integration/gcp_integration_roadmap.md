# GCP Integration Roadmap - Vendor Risk Digital Twin

**Purpose:** Hands-on roadmap for integrating Google Cloud Platform services into the Vendor Risk Digital Twin project to gain practical cloud platform experience.

**Last Updated:** 2025-01-XX

---

## 🎯 Learning Objectives

By completing this roadmap, you will gain hands-on experience with:

- **Serverless Computing** (Cloud Functions, Cloud Run)
- **Data Analytics** (BigQuery)
- **Security & Secrets Management** (Secret Manager, IAM)
- **Event-Driven Architecture** (Pub/Sub)
- **Automation & Orchestration** (Cloud Scheduler, Cloud Build)
- **Monitoring & Logging** (Cloud Logging, Cloud Monitoring)
- **Storage Solutions** (Cloud Storage, Firestore)

---

## 📋 Prerequisites

### GCP Account Setup
1. **Create GCP Project**
   ```bash
   # Via Console: https://console.cloud.google.com/
   # Or via CLI:
   gcloud projects create vendor-risk-dt --name="Vendor Risk Digital Twin"
   gcloud config set project vendor-risk-dt
   ```

2. **Enable Required APIs**
   ```bash
   # Enable all required APIs
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable bigquery.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable pubsub.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable logging.googleapis.com
   gcloud services enable monitoring.googleapis.com
   ```

3. **Service Account Setup**
   ```bash
   # Create service account
   gcloud iam service-accounts create vendor-risk-sa \
     --display-name="Vendor Risk Service Account"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding vendor-risk-dt \
     --member="serviceAccount:vendor-risk-sa@vendor-risk-dt.iam.gserviceaccount.com" \
     --role="roles/cloudfunctions.developer"
   gcloud projects add-iam-policy-binding vendor-risk-dt \
     --member="serviceAccount:vendor-risk-sa@vendor-risk-dt.iam.gserviceaccount.com" \
     --role="roles/run.developer"
   gcloud projects add-iam-policy-binding vendor-risk-dt \
     --member="serviceAccount:vendor-risk-sa@vendor-risk-dt.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataEditor"
   gcloud projects add-iam-policy-binding vendor-risk-dt \
     --member="serviceAccount:vendor-risk-sa@vendor-risk-dt.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

4. **Install GCP CLI Tools**
   ```bash
   # Install gcloud CLI (if not already installed)
   # macOS:
   brew install google-cloud-sdk
   
   # Authenticate
   gcloud auth login
   gcloud auth application-default login
   ```

---

## 🗺️ Phase-by-Phase Roadmap

### **Phase 1: Foundation - Secret Management & Configuration** 
*Estimated Time: 2-3 hours*

**Goal:** Securely store credentials and configuration in GCP Secret Manager.

#### Tasks:
1. **Migrate Secrets to Secret Manager**
   - Move Neo4j credentials from `.env` to Secret Manager
   - Store GCP service account keys securely
   - Update `scripts/utils.py` to fetch secrets from Secret Manager

2. **Implementation Steps:**
   ```bash
   # Create secrets
   echo -n "your-neo4j-password" | gcloud secrets create neo4j-password \
     --data-file=- --replication-policy="automatic"
   
   echo -n "neo4j://localhost:7687" | gcloud secrets create neo4j-uri \
     --data-file=- --replication-policy="automatic"
   ```

3. **Code Changes:**
   - Create `scripts/gcp_secrets.py` to fetch secrets
   - Update `scripts/utils.py` to use Secret Manager instead of `.env`
   - Add error handling for secret access

4. **Learning Outcomes:**
   - Understand Secret Manager API
   - Practice secure credential management
   - Learn IAM permissions for secrets

**Deliverable:** All secrets migrated to Secret Manager, code updated to fetch from GCP.

---

### **Phase 2: Serverless Discovery - Cloud Functions**
*Estimated Time: 4-5 hours*

**Goal:** Convert the GCP discovery script into a serverless Cloud Function that can be triggered on-demand.

#### Tasks:
1. **Create Cloud Function for Discovery**
   - Convert `scripts/gcp_discovery.py` to a Cloud Function
   - Support HTTP triggers and Pub/Sub triggers
   - Store results in Cloud Storage

2. **Function Structure:**
   ```
   cloud_functions/
   ├── discovery/
   │   ├── main.py          # Cloud Function entry point
   │   ├── requirements.txt # Function dependencies
   │   └── gcp_discovery.py # Core discovery logic (refactored)
   ```

3. **Implementation:**
   ```bash
   # Deploy Cloud Function
   gcloud functions deploy vendor-discovery \
     --runtime python311 \
     --trigger-http \
     --allow-unauthenticated \
     --entry-point discover_vendors \
     --source cloud_functions/discovery \
     --set-env-vars PROJECT_ID=vendor-risk-dt
   ```

4. **Features to Add:**
   - HTTP endpoint for manual triggers
   - Pub/Sub trigger for scheduled scans
   - Error handling and retry logic
   - Structured logging to Cloud Logging

5. **Learning Outcomes:**
   - Cloud Functions development lifecycle
   - HTTP vs Pub/Sub triggers
   - Function deployment and versioning
   - Cloud Logging integration

**Deliverable:** Working Cloud Function that discovers vendor dependencies and stores results in Cloud Storage.

---

### **Phase 3: Containerized Services - Cloud Run**
*Estimated Time: 5-6 hours*

**Goal:** Deploy the simulation engine as a containerized Cloud Run service.

#### Tasks:
1. **Containerize Simulation Engine**
   - Create `Dockerfile` for simulation service
   - Convert `scripts/simulate_failure.py` to a web service
   - Add REST API endpoints using Flask/FastAPI

2. **Dockerfile Example:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY scripts/ ./scripts/
   COPY config/ ./config/
   CMD ["python", "-m", "scripts.simulate_api"]
   ```

3. **Cloud Run Service:**
   ```bash
   # Build and deploy
   gcloud builds submit --tag gcr.io/vendor-risk-dt/simulation-service
   gcloud run deploy simulation-service \
     --image gcr.io/vendor-risk-dt/simulation-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NEO4J_URI=$(gcloud secrets versions access latest --secret=neo4j-uri)
   ```

4. **API Endpoints to Implement:**
   - `POST /simulate` - Run failure simulation
   - `GET /simulate/{simulation_id}` - Get simulation results
   - `GET /health` - Health check endpoint

5. **Learning Outcomes:**
   - Docker containerization
   - Cloud Run deployment
   - Container registry (Artifact Registry/Container Registry)
   - Service-to-service authentication
   - Auto-scaling configuration

**Deliverable:** Containerized simulation service running on Cloud Run with REST API.

---

### **Phase 4: Data Analytics - BigQuery Integration**
*Estimated Time: 4-5 hours*

**Goal:** Store simulation results and vendor data in BigQuery for analytics and historical tracking.

#### Tasks:
1. **Create BigQuery Dataset and Tables**
   ```sql
   -- Create dataset
   CREATE SCHEMA IF NOT EXISTS `vendor-risk-dt.vendor_risk`
   OPTIONS(
     description="Vendor Risk Digital Twin Analytics Dataset"
   );
   
   -- Simulation results table
   CREATE TABLE `vendor-risk-dt.vendor_risk.simulations` (
     simulation_id STRING,
     vendor_name STRING,
     duration_hours INT64,
     operational_impact FLOAT64,
     financial_impact FLOAT64,
     compliance_impact FLOAT64,
     overall_score FLOAT64,
     timestamp TIMESTAMP,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
   );
   
   -- Vendor dependencies table
   CREATE TABLE `vendor-risk-dt.vendor_risk.dependencies` (
     vendor_name STRING,
     service_name STRING,
     resource_type STRING,
     discovered_at TIMESTAMP,
     project_id STRING
   );
   ```

2. **Stream Results to BigQuery**
   - Update simulation engine to write results to BigQuery
   - Use BigQuery streaming inserts or batch loads
   - Create `scripts/bigquery_loader.py`

3. **Analytics Queries**
   - Create views for common analytics:
     - Most critical vendors (by impact score)
     - Historical impact trends
     - Compliance framework vulnerabilities

4. **Learning Outcomes:**
   - BigQuery schema design
   - Streaming vs batch data loading
   - SQL queries on large datasets
   - Data visualization (Data Studio/Looker)

**Deliverable:** BigQuery dataset with simulation results, analytics queries, and dashboard.

---

### **Phase 5: Event-Driven Architecture - Pub/Sub**
*Estimated Time: 3-4 hours*

**Goal:** Implement event-driven workflows using Pub/Sub for decoupled service communication.

#### Tasks:
1. **Create Pub/Sub Topics and Subscriptions**
   ```bash
   # Topic for discovery events
   gcloud pubsub topics create vendor-discovery-events
   
   # Topic for simulation requests
   gcloud pubsub topics create simulation-requests
   
   # Topic for results
   gcloud pubsub topics create simulation-results
   ```

2. **Event Flow:**
   ```
   Discovery Function → Pub/Sub → Graph Loader → Neo4j
   Simulation Request → Pub/Sub → Simulation Service → BigQuery
   ```

3. **Implement Pub/Sub Publishers/Subscribers**
   - Update discovery function to publish events
   - Create Cloud Function subscriber for graph loading
   - Add retry logic and dead-letter topics

4. **Learning Outcomes:**
   - Pub/Sub messaging patterns
   - Event-driven architecture design
   - Message ordering and deduplication
   - Dead-letter queues

**Deliverable:** Event-driven workflow connecting discovery → graph loading → simulation.

**Documentation:** 
- [Pub/Sub Automation Guide](pubsub_automation.md) - How automation works
- [Testing Automation](testing_automation.md) - How to test and verify automation is working

---

### **Phase 6: Automation - Cloud Scheduler**
*Estimated Time: 2-3 hours*

**Goal:** Automate periodic discovery scans and compliance checks using Cloud Scheduler.

#### Tasks:
1. **Schedule Discovery Scans**
   ```bash
   # Daily discovery scan at 2 AM
   gcloud scheduler jobs create http daily-discovery \
     --schedule="0 2 * * *" \
     --uri="https://us-central1-vendor-risk-dt.cloudfunctions.net/vendor-discovery" \
     --http-method=POST \
     --time-zone="America/Los_Angeles"
   ```

2. **Schedule Compliance Reports**
   - Weekly compliance posture reports
   - Monthly vendor risk assessments
   - Quarterly compliance framework reviews

3. **Learning Outcomes:**
   - Cron job scheduling in GCP
   - HTTP-triggered automation
   - Timezone handling
   - Job monitoring and alerting

**Deliverable:** Automated daily discovery scans and scheduled compliance reports.

---

### **Phase 7: Monitoring & Observability**
*Estimated Time: 3-4 hours*

**Goal:** Implement comprehensive monitoring and alerting for the system.

#### Tasks:
1. **Cloud Logging Integration**
   - Structured logging from all services
   - Log-based metrics
   - Log retention policies

2. **Cloud Monitoring Dashboards**
   - Create custom dashboards for:
     - Discovery scan success rates
     - Simulation execution times
     - Error rates by service
     - Vendor dependency counts

3. **Alerting Policies**
   ```bash
   # Alert on high simulation failure rate
   gcloud alpha monitoring policies create \
     --notification-channels=CHANNEL_ID \
     --display-name="High Simulation Failure Rate" \
     --condition-threshold-value=0.1 \
     --condition-threshold-duration=300s
   ```

4. **Learning Outcomes:**
   - Cloud Monitoring metrics and dashboards
   - Alerting policy configuration
   - Log analysis and debugging
   - SLO/SLA tracking

**Deliverable:** Monitoring dashboards and alerting policies for all services.

---

### **Phase 8: CI/CD Pipeline - Cloud Build**
*Estimated Time: 4-5 hours*

**Goal:** Set up automated CI/CD pipeline for code deployment.

#### Tasks:
1. **Cloud Build Configuration**
   - Create `cloudbuild.yaml` for automated builds
   - Set up triggers for GitHub/GitLab
   - Automated testing before deployment

2. **Build Pipeline:**
   ```yaml
   steps:
     - name: 'python:3.11'
       entrypoint: 'bash'
       args:
         - '-c'
         - 'pip install -r requirements.txt && pytest tests/'
     - name: 'gcr.io/cloud-builders/docker'
       args: ['build', '-t', 'gcr.io/$PROJECT_ID/simulation-service', '.']
     - name: 'gcr.io/cloud-builders/gcloud'
       args: ['run', 'deploy', 'simulation-service', '--image', 'gcr.io/$PROJECT_ID/simulation-service']
   ```

3. **Learning Outcomes:**
   - Cloud Build configuration
   - CI/CD best practices
   - Automated testing in pipelines
   - Deployment strategies

**Deliverable:** Automated CI/CD pipeline with testing and deployment.

---

### **Phase 9: Advanced Features**
*Estimated Time: 6-8 hours*

**Goal:** Implement advanced GCP features for production readiness.

#### Tasks:
1. **Cloud Storage for Data Persistence**
   - Store discovery results as JSON files
   - Archive historical simulation results
   - Lifecycle policies for cost optimization

2. **Firestore for Real-time Data**
   - Store active simulations in Firestore
   - Real-time updates for dashboards
   - Query optimization

3. **Cloud IAM Best Practices**
   - Implement least-privilege access
   - Service account impersonation
   - Audit logging

4. **VPC Configuration** (Optional)
   - Private Cloud Run services
   - VPC connector for Neo4j access
   - Network security policies

5. **Learning Outcomes:**
   - Multi-service architecture
   - Security best practices
   - Cost optimization
   - Network configuration

**Deliverable:** Production-ready architecture with advanced GCP features.

---

## 📊 Progress Tracking

### Checklist Template

```
Phase 1: Secret Management
  [ ] GCP project created
  [ ] Secret Manager API enabled
  [ ] Secrets created and tested
  [ ] Code updated to use Secret Manager
  [ ] Documentation updated

Phase 2: Cloud Functions
  [ ] Discovery function created
  [ ] Function deployed and tested
  [ ] Cloud Logging integrated
  [ ] Error handling implemented

Phase 3: Cloud Run
  [ ] Dockerfile created
  [ ] Container built and tested locally
  [ ] Service deployed to Cloud Run
  [ ] API endpoints working
  [ ] Auto-scaling configured

Phase 4: BigQuery
  [ ] Dataset and tables created
  [ ] Data loading implemented
  [ ] Analytics queries written
  [ ] Dashboard created

Phase 5: Pub/Sub
  [ ] Topics and subscriptions created
  [ ] Event publishers implemented
  [ ] Event subscribers implemented
  [ ] End-to-end flow tested

Phase 6: Cloud Scheduler
  [ ] Scheduled jobs created
  [ ] Jobs tested and verified
  [ ] Monitoring configured

Phase 7: Monitoring
  [ ] Logging configured
  [ ] Dashboards created
  [ ] Alerts configured
  [ ] Documentation updated

Phase 8: CI/CD
  [ ] Cloud Build configured
  [ ] Triggers set up
  [ ] Pipeline tested
  [ ] Documentation updated

Phase 9: Advanced Features
  [ ] Cloud Storage integrated
  [ ] IAM policies reviewed
  [ ] Cost optimization implemented
  [ ] Final testing complete
```

---

## 💰 Cost Estimation

### Free Tier Usage (Monthly)
- **Cloud Functions:** 2 million invocations free
- **Cloud Run:** 2 million requests free
- **BigQuery:** 10 GB storage, 1 TB queries free
- **Secret Manager:** 6 secrets free
- **Cloud Scheduler:** 3 jobs free
- **Pub/Sub:** 10 GB free

### Estimated Monthly Cost (Beyond Free Tier)
- **Cloud Functions:** ~$5-10 (if exceeding free tier)
- **Cloud Run:** ~$10-20 (depending on traffic)
- **BigQuery:** ~$5-15 (storage and queries)
- **Cloud Storage:** ~$2-5 (data storage)
- **Total:** ~$25-50/month for moderate usage

---

## 🔧 Troubleshooting Guide

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify service account permissions
   gcloud projects get-iam-policy vendor-risk-dt
   
   # Test authentication
   gcloud auth application-default print-access-token
   ```

2. **Cloud Function Deployment Failures**
   ```bash
   # Check logs
   gcloud functions logs read vendor-discovery --limit 50
   
   # Verify requirements.txt
   pip install -r requirements.txt --dry-run
   ```

3. **Cloud Run Service Issues**
   ```bash
   # Check service logs
   gcloud run services logs read simulation-service --limit 50
   
   # Verify container locally
   docker run -p 8080:8080 gcr.io/vendor-risk-dt/simulation-service
   ```

4. **BigQuery Access Issues**
   ```bash
   # Verify dataset permissions
   bq show --format=prettyjson vendor-risk-dt:vendor_risk
   
   # Test query
   bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `vendor-risk-dt.vendor_risk.simulations`'
   ```

---

## 📚 Learning Resources

### Official Documentation
- [Cloud Functions Python Guide](https://cloud.google.com/functions/docs/writing)
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts)
- [BigQuery Python Client](https://cloud.google.com/bigquery/docs/reference/libraries)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)

### Hands-On Labs
- [Qwiklabs GCP Courses](https://www.qwiklabs.com/catalog?keywords=google+cloud)
- [Google Cloud Skills boost](https://www.cloudskillsboost.google/)

### Best Practices
- [GCP Architecture Framework](https://cloud.google.com/architecture/framework)
- [Cloud Functions Best Practices](https://cloud.google.com/functions/docs/bestpractices)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/tips)

---

## 🎓 Next Steps After Completion

1. **Multi-Cloud Expansion**
   - Add AWS Lambda equivalents
   - Azure Functions integration
   - Cross-cloud vendor discovery

2. **Machine Learning Integration**
   - Use Vertex AI for predictive analytics
   - ML models for failure probability prediction
   - Anomaly detection for vendor dependencies

3. **Enterprise Features**
   - Multi-tenant support
   - Advanced RBAC
   - Compliance reporting automation
   - GRC platform integrations (Archer, MetricStream)

4. **Performance Optimization**
   - Caching with Cloud Memorystore (Redis)
   - CDN integration with Cloud CDN
   - Database connection pooling
   - Query optimization

---

## 📝 Notes

- Start with Phase 1 and complete sequentially for best learning experience
- Each phase builds on previous knowledge
- Don't skip testing - it's crucial for understanding
- Document your learnings as you go
- Experiment with different configurations to understand trade-offs

---

## 🔗 Related Documentation

- [Architecture Design](architecture.md)
- [API Design](api_design.md)
- [Setup Guide](setup_guide.md)
- [Simulation Methodology](simulation_methodology.md)
- [Pub/Sub Automation Guide](pubsub_automation.md) - How event-driven automation works
- [Testing Automation](testing_automation.md) - Step-by-step testing procedures

---

**Happy Cloud Learning! 🚀**

