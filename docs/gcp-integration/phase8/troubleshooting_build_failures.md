# Troubleshooting CI/CD Build Failures

**Last Updated:** 2025-12-01  
**Phase:** 8 - CI/CD Pipeline

---

## Common Build Failure Causes

### 1. Service Account Permissions (Most Common)

**Symptom:** Build fails with permission errors

**Solution:**
```bash
./scripts/setup/setup_compute_sa_for_build.sh
```

This grants the Compute Engine service account all required permissions.

---

### 2. Secret Manager Access

**Symptom:** Build fails when accessing secrets

**Check:**
- Secrets exist in Secret Manager
- Service account has `roles/secretmanager.secretAccessor`

**Fix:**
```bash
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

### 3. Missing Files or Dependencies

**Symptom:** Build fails with "file not found" errors

**Check:**
- All required files are in repository
- `cloudbuild.yaml` paths are correct
- Dockerfile exists and is correct

---

### 4. Build Configuration Errors

**Symptom:** Build fails with YAML syntax errors

**Check:**
- `cloudbuild.yaml` syntax is valid
- All required fields are present
- Indentation is correct

---

## How to Check Build Logs

### Option 1: Cloud Console (Easiest)

1. Go to: https://console.cloud.google.com/cloud-build/builds?project=vendor-risk-digital-twin
2. Click on the failed build
3. View detailed logs for each step
4. Look for ERROR messages

### Option 2: Command Line

```bash
# List recent builds
gcloud builds list --project vendor-risk-digital-twin --limit 5

# View specific build logs
gcloud builds log BUILD_ID --project vendor-risk-digital-twin
```

---

## Quick Fixes

### Fix 1: Grant Service Account Permissions

```bash
cd vendor-risk-digital-twin
./scripts/setup/setup_compute_sa_for_build.sh
```

### Fix 2: Verify Secrets Exist

```bash
gcloud secrets list --project vendor-risk-digital-twin
```

Should show:
- `neo4j-uri`
- `neo4j-user`
- `neo4j-password`

### Fix 3: Test Build Manually

```bash
gcloud builds submit --config cloudbuild.yaml --project vendor-risk-digital-twin
```

This helps identify the issue.

---

## Step-by-Step Debugging

### Step 1: Check Build Logs

1. Open Cloud Console
2. Navigate to Cloud Build
3. Click failed build
4. Review error messages

### Step 2: Identify Failed Step

Look for which step failed:
- Step 0: Tests
- Step 1: Build Docker image
- Step 2: Deploy Simulation Service
- Step 3-5: Deploy Cloud Functions

### Step 3: Check Error Message

Common errors:
- `PERMISSION_DENIED` → Service account permissions
- `SECRET_NOT_FOUND` → Secret Manager issue
- `FILE_NOT_FOUND` → Missing file
- `SYNTAX_ERROR` → Configuration error

### Step 4: Apply Fix

Based on error, apply appropriate fix above.

---

## Prevention

### Before Pushing

1. Test build manually:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

2. Verify service account permissions:
   ```bash
   ./scripts/setup/setup_compute_sa_for_build.sh
   ```

3. Check secrets exist:
   ```bash
   gcloud secrets list
   ```

---

## Summary

**Most Common Issue:** Service account permissions

**Quick Fix:**
```bash
./scripts/setup/setup_compute_sa_for_build.sh
```

**Check Logs:**
- Cloud Console: https://console.cloud.google.com/cloud-build/builds
- Look for ERROR messages
- Identify which step failed

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Complete

