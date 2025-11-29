# Phase 1: Secret Management - Implementation Guide

## Overview

This phase migrates secrets from `.env` files to GCP Secret Manager, providing secure credential storage for cloud deployments while maintaining local development support.

## Prerequisites

✅ GCP project created (`vendor-risk-digital-twin`)  
✅ Secret Manager API enabled  
✅ Service account with `roles/secretmanager.secretAccessor` permission  
✅ `google-cloud-secret-manager` package installed

## Step 1: Install Required Package

```bash
pip install google-cloud-secret-manager
```

Or add to `requirements.txt`:
```
google-cloud-secret-manager==2.18.0
```

## Step 2: Authenticate with GCP

```bash
# Authenticate with your Google account
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project vendor-risk-digital-twin
```

## Step 3: Store Secrets in Secret Manager

### Option A: Using the Setup Script (Recommended)

```bash
# Make sure your .env file has Neo4j credentials
# Then run:
python scripts/setup_secrets.py vendor-risk-digital-twin
```

The script will:
- Read Neo4j credentials from `.env` or prompt for them
- Create secrets in GCP Secret Manager
- Handle existing secrets (updates with new version)

### Option B: Using gcloud CLI

```bash
# Store Neo4j URI
echo -n "bolt://localhost:7687" | gcloud secrets create neo4j-uri \
  --data-file=- \
  --replication-policy="automatic" \
  --project=vendor-risk-digital-twin

# Store Neo4j User
echo -n "neo4j" | gcloud secrets create neo4j-user \
  --data-file=- \
  --replication-policy="automatic" \
  --project=vendor-risk-digital-twin

# Store Neo4j Password (you'll be prompted)
echo -n "your-password" | gcloud secrets create neo4j-password \
  --data-file=- \
  --replication-policy="automatic" \
  --project=vendor-risk-digital-twin
```

### Option C: Using Python Script Directly

```bash
# Test secret creation
python scripts/gcp_secrets.py create neo4j-uri "bolt://localhost:7687"
python scripts/gcp_secrets.py create neo4j-user "neo4j"
python scripts/gcp_secrets.py create neo4j-password "your-password"
```

## Step 4: Verify Secrets

```bash
# List all secrets
gcloud secrets list --project=vendor-risk-digital-twin

# View a secret (be careful - this shows the value)
gcloud secrets versions access latest --secret="neo4j-uri" --project=vendor-risk-digital-twin

# Test fetching via Python
python scripts/gcp_secrets.py get neo4j-uri
```

## Step 5: Test the Integration

The code has been updated to automatically use Secret Manager when available, with fallback to environment variables.

### Test Locally (uses .env):
```bash
# Should work with .env file
python scripts/simulate_failure.py --vendor Stripe --duration 4
```

### Test with Secret Manager:
```bash
# Set GCP_PROJECT_ID
export GCP_PROJECT_ID=vendor-risk-digital-twin

# Authenticate
gcloud auth application-default login

# Should now use Secret Manager
python scripts/simulate_failure.py --vendor Stripe --duration 4
```

## How It Works

### Fallback Chain:

1. **GCP Secret Manager** (if `GCP_PROJECT_ID` is set and authenticated)
2. **Environment Variables** (from `.env` file or system env)
3. **Default Values** (hardcoded fallbacks)

### Code Flow:

```python
# In utils.py load_config():
1. Try to import gcp_secrets module
2. If available, call get_neo4j_credentials()
3. get_neo4j_credentials() tries Secret Manager first
4. Falls back to environment variables
5. Falls back to defaults
```

## Security Best Practices

1. **Never commit secrets to git**
   - `.env` is in `.gitignore` ✅
   - Secret Manager values are never in code ✅

2. **Use least privilege**
   - Service account only has `secretmanager.secretAccessor` role ✅

3. **Rotate secrets regularly**
   - Update secrets in Secret Manager
   - Old versions are automatically retained for audit

4. **Local development**
   - Use `.env` file (not committed)
   - Secret Manager not required for local dev

## Troubleshooting

### Error: "Permission denied"
**Solution:** Ensure service account has `roles/secretmanager.secretAccessor`:
```bash
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
  --member="serviceAccount:vendor-risk-sa@vendor-risk-digital-twin.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Error: "Secret not found"
**Solution:** Create the secret first:
```bash
python scripts/setup_secrets.py vendor-risk-digital-twin
```

### Error: "Authentication failed"
**Solution:** Authenticate with GCP:
```bash
gcloud auth application-default login
```

### Secrets not being used
**Check:**
1. Is `GCP_PROJECT_ID` set?
2. Are you authenticated? (`gcloud auth application-default login`)
3. Does the secret exist? (`gcloud secrets list`)

## Next Steps

After completing Phase 1:

✅ Secrets stored in Secret Manager  
✅ Code updated to use Secret Manager  
✅ Fallback to .env for local development  
✅ Tested and working  

**Ready for Phase 2:** Serverless Discovery - Cloud Functions

## Files Modified

- ✅ `scripts/gcp_secrets.py` - New Secret Manager integration
- ✅ `scripts/utils.py` - Updated to use Secret Manager
- ✅ `scripts/setup_secrets.py` - Helper script for setup

## Learning Outcomes

- ✅ Understand Secret Manager API
- ✅ Practice secure credential management
- ✅ Learn IAM permissions for secrets
- ✅ Implement fallback patterns for local/cloud development

