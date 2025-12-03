# CI/CD Pipeline Flow Diagram
**For Presentation: Vendor Risk Digital Twin**

This document provides visual flow diagrams for the CI/CD pipeline that can be used to create presentation slides.

---

## Overview

The Vendor Risk Digital Twin uses Google Cloud Build for automated CI/CD, enabling:
- Automated testing before deployment
- Multi-service deployment (Cloud Run + Cloud Functions)
- Event-driven builds (manual or GitHub trigger)
- Production-ready DevOps practices

---

## Complete CI/CD Pipeline Flow

### High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE FLOW                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Code Changes │
│ (Git Push)   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Trigger: Manual or GitHub Push      │
│  • gcloud builds submit              │
│  • OR: GitHub webhook → Cloud Build  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 1: Upload Source Code          │
│  • Compress to .tgz                  │
│  • Upload to Cloud Storage            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 2: Run Tests                   │
│  • Install dependencies              │
│  • Run pytest (if tests exist)        │
│  • Continue even if tests fail       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 3: Verify Source Code         │
│  • Check imports                     │
│  • Verify __init__.py files          │
│  • Validate structure                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 4: Build Docker Image          │
│  • Use Dockerfile                    │
│  • Build simulation-service image    │
│  • Tag: latest + SHORT_SHA           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 5: Verify Docker Image         │
│  • Check image contents              │
│  • Get image digest                  │
│  • Validate structure                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 6: Deploy Services             │
│  ┌──────────────────────────────┐   │
│  │ 6a. Cloud Run                │   │
│  │    • simulation-service       │   │
│  │    • With secrets & env vars  │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ 6b. Cloud Functions           │   │
│  │    • vendor-discovery         │   │
│  │    • graph-loader             │   │
│  │    • bigquery-loader          │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  ✅ Deployment Complete              │
│  • All services running             │
│  • Monitoring active                │
│  • Ready for production              │
└─────────────────────────────────────┘
```

---

## Detailed Step-by-Step Flow

### Phase 1: Trigger & Source Upload

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: TRIGGER & SOURCE UPLOAD                            │
└─────────────────────────────────────────────────────────────┘

Developer
    │
    │ Makes code changes
    │ (app.py, scripts/, config/, etc.)
    │
    ▼
┌──────────────────────┐
│  Option A: Manual     │  Option B: GitHub Trigger
│  gcloud builds submit │  (Push to main branch)
└──────────┬───────────┘  └──────────┬───────────────┘
           │                         │
           └──────────┬─────────────┘
                      │
                      ▼
┌─────────────────────────────────────┐
│  Cloud Build Triggered               │
│  • Receives source code              │
│  • Creates build context             │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Upload to Cloud Storage            │
│  • Compress: project-code.tgz       │
│  • Upload to: gs://[PROJECT]_cloudbuild/ │
│  • Extract in build environment      │
└─────────────────────────────────────┘
```

### Phase 2: Testing & Verification

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: TESTING & VERIFICATION                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Step 1: Run Tests                  │
│  • pip install -r requirements.txt │
│  • pytest tests/ -v                 │
│  • Continue even if tests fail       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Step 2: Verify Source Code         │
│  • Check: from scripts imports      │
│  • Verify: __init__.py files exist  │
│  • Validate: directory structure    │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  ✅ Source Code Validated            │
└─────────────────────────────────────┘
```

### Phase 3: Build Docker Image

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: BUILD DOCKER IMAGE                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Docker Build Process               │
│  ┌──────────────────────────────┐   │
│  │ FROM python:3.11-slim        │   │
│  │ WORKDIR /app                 │   │
│  │ COPY requirements.txt         │   │
│  │ RUN pip install              │   │
│  │ COPY scripts/ ./scripts/     │   │
│  │ COPY config/ ./config/       │   │
│  │ COPY app.py .                │   │
│  └──────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Image Created                       │
│  • Tag: latest                       │
│  • Tag: $SHORT_SHA                   │
│  • Push to: gcr.io/$PROJECT_ID/      │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Verify Image Contents               │
│  • Check app.py in image             │
│  • Verify scripts/ directory         │
│  • Get image digest                  │
└─────────────────────────────────────┘
```

### Phase 4: Deploy Services

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: DEPLOY SERVICES                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Deploy Cloud Run Service            │
│  ┌──────────────────────────────┐   │
│  │ Service: simulation-service    │   │
│  │ Image: gcr.io/.../simulation- │   │
│  │        service:latest         │   │
│  │ Region: us-central1            │   │
│  │ Memory: 512Mi                 │   │
│  │ CPU: 1                        │   │
│  │ Secrets: Neo4j credentials    │   │
│  │ Env: GCP_PROJECT_ID           │   │
│  └──────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Deploy Cloud Functions (Parallel)   │
│  ┌──────────────────────────────┐   │
│  │ 1. vendor-discovery          │   │
│  │    • Trigger: HTTP          │   │
│  │    • Runtime: Python 3.11    │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ 2. graph-loader              │   │
│  │    • Trigger: Pub/Sub        │   │
│  │    • Runtime: Python 3.11    │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ 3. bigquery-loader            │   │
│  │    • Trigger: Pub/Sub        │   │
│  │    • Runtime: Python 3.11    │   │
│  └──────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  ✅ All Services Deployed             │
│  • Cloud Run: simulation-service      │
│  • Cloud Functions: 3 functions      │
│  • Monitoring: Active                 │
│  • Ready for production                │
└─────────────────────────────────────┘
```

---

## Parallel Deployment Flow

### Services Deployed in Parallel

```
┌─────────────────────────────────────────────────────────────┐
│ PARALLEL DEPLOYMENT FLOW                                    │
└─────────────────────────────────────────────────────────────┘

                    Build Complete
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Cloud Run    │  │ Discovery    │  │ Graph Loader │
│ Service      │  │ Function     │  │ Function     │
│              │  │              │  │              │
│ Deploy       │  │ Deploy       │  │ Deploy       │
│ (Sequential) │  │ (Parallel)    │  │ (Parallel)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └───────────────┬─────────────────┘
                       │
                       ▼
              ┌──────────────┐
              │ BigQuery     │
              │ Loader       │
              │ Function     │
              │              │
              │ Deploy       │
              │ (Parallel)   │
              └──────┬───────┘
                     │
                     ▼
            ┌──────────────┐
            │ All Services │
            │ Running      │
            └──────────────┘
```

---

## Event-Driven CI/CD Flow

### GitHub Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│ GITHUB TRIGGERED CI/CD FLOW                                 │
└─────────────────────────────────────────────────────────────┘

Developer
    │
    │ git push origin main
    │
    ▼
┌──────────────────────┐
│  GitHub Repository    │
│  • Code pushed        │
│  • Webhook triggered  │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Cloud Build Trigger                │
│  • Receives webhook                 │
│  • Validates branch (main)           │
│  • Starts build process              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Automated Build Pipeline            │
│  (Same as manual flow)               │
│  • Tests                             │
│  • Build                             │
│  • Deploy                            │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  ✅ Automatic Deployment Complete     │
│  • No manual intervention            │
│  • Production updated                │
└─────────────────────────────────────┘
```

---

## Build Steps Timeline

### Sequential Steps with Dependencies

```
Time →
│
│ Step 1: Run Tests
│ ├─ Install dependencies
│ └─ Run pytest
│
│ Step 2: Verify Source Code
│ ├─ Check imports
│ └─ Validate structure
│
│ Step 3: Build Docker Image
│ ├─ Build image
│ ├─ Tag image
│ └─ Push to registry
│
│ Step 4: Verify Image
│ ├─ Check contents
│ └─ Get digest
│
│ Step 5: Deploy Cloud Run
│ ├─ Deploy simulation-service
│ └─ Configure secrets
│
│ Step 6: Deploy Cloud Functions (Parallel)
│ ├─ vendor-discovery ──┐
│ ├─ graph-loader ───────┼─→ All deploy simultaneously
│ └─ bigquery-loader ────┘
│
│ ✅ Complete
│
```

---

## Key Components Diagram

### CI/CD Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│ CI/CD ARCHITECTURE COMPONENTS                               │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Source Control       │
│  • GitHub/GitLab      │
│  • Code repository     │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Cloud Build                         │
│  ┌──────────────────────────────┐   │
│  │ • cloudbuild.yaml            │   │
│  │ • Build orchestration        │   │
│  │ • Test execution             │   │
│  │ • Image building             │   │
│  │ • Service deployment         │   │
│  └──────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ├─────────────────┬─────────────────┐
           ▼                 ▼                 ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Container Registry│  │ Cloud Run    │  │ Cloud       │
│ (GCR)            │  │ Service      │  │ Functions   │
│                  │  │              │  │             │
│ • Docker images  │  │ • simulation │  │ • discovery │
│ • Tagged versions│  │   -service   │  │ • loaders   │
└──────────────────┘  └──────────────┘  └──────────────┘
```

---

## Success Metrics

### Pipeline Success Indicators

```
┌─────────────────────────────────────────────────────────────┐
│ PIPELINE SUCCESS METRICS                                    │
└─────────────────────────────────────────────────────────────┘

✅ Build Status
   • Tests: Passed (or skipped)
   • Build: Successful
   • Deploy: All services deployed

✅ Service Health
   • Cloud Run: Running
   • Cloud Functions: Active
   • Monitoring: Enabled

✅ Performance
   • Build time: ~5-10 minutes
   • Deployment: Automated
   • Zero downtime: Rolling updates
```

---

## Error Handling Flow

### Failure Recovery

```
┌─────────────────────────────────────────────────────────────┐
│ ERROR HANDLING & RECOVERY                                   │
└─────────────────────────────────────────────────────────────┘

Build Step Fails
    │
    ├─ Test Failure
    │  └─→ Continue build (non-blocking)
    │
    ├─ Build Failure
    │  └─→ Stop pipeline, notify developer
    │
    ├─ Deploy Failure (Cloud Run)
    │  └─→ Stop pipeline, rollback
    │
    └─ Deploy Failure (Cloud Function)
       └─→ Continue (non-blocking), log warning
```

---

## Visual Elements for Presentation

### Slide-Ready Diagrams

#### Option 1: Simple Linear Flow
```
Code → Test → Build → Deploy → ✅
```

#### Option 2: Detailed Flow
```
┌─────┐
│Code │
└──┬──┘
   │
   ▼
┌─────┐
│Test │
└──┬──┘
   │
   ▼
┌──────┐
│Build │
└──┬───┘
   │
   ▼
┌───────┐
│Deploy │
└───┬───┘
    │
    ▼
   ✅
```

#### Option 3: Service-Specific Flow
```
Code Changes
    │
    ├─→ Cloud Run Service
    │      (simulation-service)
    │
    ├─→ Cloud Functions
    │      (discovery, loaders)
    │
    └─→ All Services Updated
```

---

## Notes for Presentation

### Key Talking Points

1. **Automated Testing**
   - Tests run before deployment
   - Non-blocking (continues even if tests fail)
   - Ensures code quality

2. **Multi-Service Deployment**
   - Single pipeline deploys all services
   - Cloud Run + Cloud Functions
   - Parallel deployment for efficiency

3. **Production-Ready**
   - Automated rollback on failure
   - Image versioning (latest + SHA)
   - Monitoring and logging

4. **Event-Driven**
   - Manual trigger: `gcloud builds submit`
   - Automatic trigger: GitHub push
   - Zero manual intervention

5. **Security**
   - Secrets managed via Secret Manager
   - IAM-based permissions
   - Secure service-to-service communication

---

**Last Updated:** 2025-12-01  
**For:** Vendor Risk Digital Twin Presentation  
**Purpose:** Visual reference for creating CI/CD pipeline diagrams
