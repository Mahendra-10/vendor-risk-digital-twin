# How CI/CD Works: Understanding the Build and Deployment Process

**Last Updated:** 2025-12-01  
**Phase:** 8 - CI/CD Pipeline

---

## Overview

This document explains how the CI/CD pipeline works, including:
- How `cloudbuild.yaml` and `Dockerfile` work together
- Where your code is uploaded
- How changes are detected and deployed
- The complete build and deployment flow

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [How cloudbuild.yaml and Dockerfile Work Together](#how-cloudbuildyaml-and-dockerfile-work-together)
3. [Where Your Code Goes](#where-your-code-goes)
4. [How Changes Are Detected](#how-changes-are-detected)
5. [Complete Build Flow](#complete-build-flow)
6. [Key Components](#key-components)

---

## The Big Picture

### What Happens When You Deploy

```
You make code changes
    ↓
Run: gcloud builds submit
    ↓
Code uploaded to Cloud Storage
    ↓
Cloud Build downloads code
    ↓
Dockerfile builds image
    ↓
Image deployed to Cloud Run
    ↓
Service running with your changes ✅
``` 

---

## How cloudbuild.yaml and Dockerfile Work Together

### The Relationship

**`cloudbuild.yaml`** = **Orchestrator** (tells Cloud Build what to do)  
**`Dockerfile`** = **Instructions** (tells Docker how to build the image)

They work together to automate the entire deployment process.

### cloudbuild.yaml's Role

The `cloudbuild.yaml` file orchestrates the build process:

```yaml
# Step 2: Build and Push Cloud Run Simulation Service
- name: 'gcr.io/cloud-builders/docker'
  id: 'build-simulation-service'
  args:
    - 'build'
    - '-f'
    - 'cloud_run/simulation-service/Dockerfile'  # ← Points to Dockerfile
    - '-t'
    - 'gcr.io/$PROJECT_ID/simulation-service:latest'
    - '.'
```

**What it does:**
- Tells Cloud Build to use Docker
- Specifies which Dockerfile to use
- Sets the image name and tag
- Defines the build context (project root)

### Dockerfile's Role

The `Dockerfile` contains the build instructions:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY cloud_run/simulation-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY data/sample/compliance_controls.json ./data/sample/  # ← Your changes here
COPY cloud_run/simulation-service/app.py .

# Run the application
CMD ["python", "app.py"]
```

**What it does:**
- Defines the base image (Python 3.11)
- Installs dependencies
- Copies your code files into the image
- Sets up the runtime environment
- Defines how to run the application

### How They Work Together

1. **cloudbuild.yaml** says: "Build using this Dockerfile"
2. **Dockerfile** says: "Here's how to build the image"
3. **Docker** follows Dockerfile instructions
4. **Image** is created with your code
5. **cloudbuild.yaml** deploys the image to Cloud Run

---

## Where Your Code Goes

### Upload Process

When you run:
```bash
gcloud builds submit --config cloudbuild.yaml
```

### Step 1: Create Tarball

Your local code is compressed into a `.tgz` file:
```
Your Computer
    ↓
Local files (compliance_controls.json, app.py, etc.)
    ↓
gcloud compresses everything
    ↓
Creates: project-code.tgz
```

### Step 2: Upload to Cloud Storage

The tarball is uploaded to a Google Cloud Storage bucket:

```
gs://vendor-risk-digital-twin_cloudbuild/source/
```

**Example filename:**
```
source/1764597012.504515-e7a1f9f5c45047a4809fab4dc6e09375.tgz
```

**What you see in output:**
```
Uploading tarball of [.] to 
[gs://vendor-risk-digital-twin_cloudbuild/source/1764597012.504515-...tgz]
```

### Step 3: Cloud Build Downloads

Cloud Build automatically:
1. Downloads the tarball from Cloud Storage
2. Extracts the files
3. Uses them to build the Docker image

### Step 4: Dockerfile Copies Files

The Dockerfile copies files from the extracted code into the Docker image:

```dockerfile
COPY data/sample/compliance_controls.json ./data/sample/
```

This copies your **current** version of the file (with your changes) into the image.

### Step 5: Image Deployed

The Docker image (with your changes) is deployed to Cloud Run.

---

## How Changes Are Detected

### Important: CI/CD Doesn't "Detect" Changes

**CI/CD doesn't know what changed.** Instead, it:

1. **Uploads your entire codebase** every time
2. **Rebuilds everything** from scratch
3. **Includes whatever files are in your directory**

### Example: Updating compliance_controls.json

**What you do:**
1. Edit `data/sample/compliance_controls.json` (add Twilio)
2. Save the file

**What CI/CD does:**
1. You run: `gcloud builds submit`
2. Uploads **all** your code (including updated file)
3. Dockerfile copies: `COPY data/sample/compliance_controls.json`
4. Copies the **current version** (with Twilio) into the image
5. Deploys the new image
6. Service uses the updated file ✅

### Why This Works

- Your local file has the changes
- Dockerfile copies the current version
- The service uses the copied file

**It's not smart about detecting changes** — it just rebuilds everything with your current files.

---

## Complete Build Flow

### Detailed Step-by-Step Process

#### 1. You Make Changes
```bash
# Edit compliance_controls.json
vim data/sample/compliance_controls.json
```

#### 2. You Trigger Build
```bash
gcloud builds submit --config cloudbuild.yaml --project vendor-risk-digital-twin
```

#### 3. Code Upload (Cloud Build)
```
Your Computer
    ↓
gcloud creates tarball
    ↓
Uploads to: gs://vendor-risk-digital-twin_cloudbuild/source/XXXXX.tgz
    ↓
Cloud Storage stores it
```

#### 4. Cloud Build Downloads
```
Cloud Build
    ↓
Downloads tarball from Cloud Storage
    ↓
Extracts files to workspace
    ↓
Files ready for Docker build
```

#### 5. Docker Build (cloudbuild.yaml Step 2)
```
cloudbuild.yaml says: "Build using Dockerfile"
    ↓
Docker reads Dockerfile
    ↓
Dockerfile says: "Copy compliance_controls.json"
    ↓
Docker copies current file (with your changes)
    ↓
Docker image created
```

#### 6. Image Push (Automatic)
```
Docker image
    ↓
Pushed to: gcr.io/vendor-risk-digital-twin/simulation-service:latest
    ↓
Stored in Google Container Registry
```

#### 7. Deploy to Cloud Run (cloudbuild.yaml Step 3)
```
cloudbuild.yaml says: "Deploy image to Cloud Run"
    ↓
Cloud Run pulls image from Container Registry
    ↓
Service starts with new image
    ↓
Service uses updated compliance_controls.json ✅
```

---

## Key Components

### 1. cloudbuild.yaml

**Location:** `cloudbuild.yaml` (project root)

**Purpose:**
- Orchestrates the entire build and deployment process
- Defines build steps
- Specifies which Dockerfile to use
- Configures deployment settings

**Key Sections:**
- **Steps:** What to do (test, build, deploy)
- **Images:** Which images to push
- **Options:** Build machine type, logging
- **Timeout:** Maximum build time

### 2. Dockerfile

**Location:** `cloud_run/simulation-service/Dockerfile`

**Purpose:**
- Defines how to build the Docker image
- Specifies which files to copy
- Sets up the runtime environment
- Defines how to run the application

**Key Instructions:**
- `FROM`: Base image
- `COPY`: Copy files into image
- `RUN`: Execute commands
- `CMD`: How to run the app

### 3. Cloud Storage

**Location:** `gs://vendor-risk-digital-twin_cloudbuild/source/`

**Purpose:**
- Temporary storage for your code
- Cloud Build downloads from here
- Created automatically by Cloud Build

**Lifecycle:**
- Created when you run `gcloud builds submit`
- Used during the build
- Can be cleaned up after build (optional)

### 4. Container Registry

**Location:** `gcr.io/vendor-risk-digital-twin/`

**Purpose:**
- Stores built Docker images
- Cloud Run pulls images from here
- Images tagged with `:latest` or build ID

**Example:**
```
gcr.io/vendor-risk-digital-twin/simulation-service:latest
```

### 5. Cloud Run

**Location:** `us-central1` region

**Purpose:**
- Runs your containerized application
- Serves your service at a URL
- Scales automatically based on traffic

**Service URL:**
```
https://simulation-service-wearla5naa-uc.a.run.app
```

---

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Computer                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Local Files                                         │   │
│  │  - compliance_controls.json (with changes)          │   │
│  │  - app.py                                            │   │
│  │  - Dockerfile                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    gcloud builds submit
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Storage                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  gs://vendor-risk-digital-twin_cloudbuild/source/    │   │
│  │  └── XXXXX.tgz (compressed code)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Cloud Build Downloads
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Build                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Step 1: Run Tests                                    │   │
│  │  Step 2: Build Image (uses Dockerfile)               │   │
│  │  Step 3: Deploy to Cloud Run                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Dockerfile Instructions
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Google Container Registry                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  gcr.io/vendor-risk-digital-twin/                      │   │
│  │  └── simulation-service:latest                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Cloud Run Deploys
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Run Service                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  https://simulation-service-...run.app                │   │
│  │  └── Running with your updated code ✅                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Questions

### Q: Does CI/CD know what files changed?

**A:** No. CI/CD doesn't detect changes. It:
- Uploads your entire codebase
- Rebuilds everything
- Includes whatever files are in your directory

### Q: Why does it rebuild everything?

**A:** For consistency and reliability:
- Ensures everything is up-to-date
- Avoids missing dependencies
- Guarantees reproducible builds

### Q: Can I see where my code is stored?

**A:** Yes! View in Cloud Console:
```
https://console.cloud.google.com/storage/browser?project=vendor-risk-digital-twin
```

Or via command line:
```bash
gsutil ls gs://vendor-risk-digital-twin_cloudbuild/source/
```

### Q: How long is code stored in Cloud Storage?

**A:** Indefinitely (unless you delete it). Cloud Build keeps build artifacts for:
- Build history
- Debugging
- Rollback capability

You can clean up old builds if needed.

### Q: What if I only change one file?

**A:** The entire codebase is still uploaded and rebuilt. This ensures:
- All dependencies are included
- No missing files
- Consistent builds

---

## Summary

### Key Takeaways

1. **cloudbuild.yaml** orchestrates the build process
2. **Dockerfile** defines how to build the image
3. **Code is uploaded** to Cloud Storage temporarily
4. **Dockerfile copies** your current files into the image
5. **Image is deployed** to Cloud Run
6. **Service uses** your updated code

### The Flow

```
Code Change → Upload → Build → Deploy → Running Service
```

### Why It Works

- Your local files have the changes
- Dockerfile copies the current version
- The service uses the copied file

**It's not smart about detecting changes** — it just rebuilds everything with your current files, which is why it works reliably every time.

---

## Related Documentation

- [Phase 8 Implementation Guide](./phase8_implementation.md)
- [Quick Start Guide](./QUICK_START.md)
- [Dockerfile Reference](../../../cloud_run/simulation-service/Dockerfile)
- [Cloud Build Configuration](../../../cloudbuild.yaml)

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Complete

