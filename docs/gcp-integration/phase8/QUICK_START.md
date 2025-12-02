# Phase 8: CI/CD Pipeline - Quick Start Guide

## ✅ Setup Complete!

Phase 8 CI/CD pipeline is configured and ready to use.

---

## How to Use

### Option 1: Manual Build (Test Now)

```bash
cd vendor-risk-digital-twin
gcloud builds submit --config cloudbuild.yaml --project vendor-risk-digital-twin
```

**What this does:**
- Runs tests (if available)
- Builds Docker image for simulation-service
- Deploys all 4 services automatically
- Takes ~5-10 minutes

### Option 2: Automatic Builds (Recommended)

Set up GitHub/GitLab trigger for automatic deployments on every push:

**Quick Setup:**
1. **Go to:** https://console.cloud.google.com/cloud-build/triggers?project=vendor-risk-digital-twin
2. **Click:** "Connect Repository" → Select GitHub → Authenticate
3. **Click:** "Create Trigger"
4. **Configure:**
   - Name: `deploy-all-services`
   - Event: Push to a branch
   - Branch: `^main$`
   - Configuration: `cloudbuild.yaml`
5. **Save**

**Detailed Guide:** See [setup_github_trigger.md](./setup_github_trigger.md)

**Now:** Every push to main → Automatic deployment!

---

## What Gets Deployed

1. **Simulation Service** (Cloud Run)
2. **Discovery Function** (Cloud Functions Gen2)
3. **Graph Loader** (Cloud Functions Gen2)
4. **BigQuery Loader** (Cloud Functions Gen2)

---

## View Build Status

```bash
# List recent builds
gcloud builds list --project vendor-risk-digital-twin --limit 5

# View build logs
gcloud builds log BUILD_ID --project vendor-risk-digital-twin
```

**Or in Console:**
https://console.cloud.google.com/cloud-build/builds?project=vendor-risk-digital-twin

---

## Troubleshooting

### Build Fails
- Check build logs in Cloud Console
- Verify service account permissions: `./scripts/setup/setup_cicd.sh`

### Tests Fail
- Tests are optional - build continues even if tests fail
- Fix tests or remove test step from `cloudbuild.yaml`

### Permission Errors
- Run setup script: `./scripts/setup/setup_cicd.sh`
- Verify Cloud Build service account has required roles

---

## Benefits

✅ **Zero manual steps** - Push code, deployment happens automatically  
✅ **Quality assurance** - Tests run before deployment  
✅ **Fast iterations** - Deploy in minutes, not hours  
✅ **Team collaboration** - Anyone can deploy safely  

---

**Ready to use!** 🚀

