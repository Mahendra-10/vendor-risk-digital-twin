# Why Service Account Selection Matters for Cloud Build

**Last Updated:** 2025-12-01  
**Phase:** 8 - CI/CD Pipeline

---

## Overview

When setting up Cloud Build triggers, you're asked to select a service account. This choice is critical because it determines **what permissions** Cloud Build has when it runs your builds.

---

## What is a Service Account?

A **service account** is like a "robot user" that applications use to access GCP resources. Instead of using your personal account, Cloud Build uses a service account to:

- Deploy services
- Access Cloud Storage
- Push images to Container Registry
- Access Secret Manager
- Deploy to Cloud Run and Cloud Functions

---

## Why It Matters

### 1. Permissions Determine What Cloud Build Can Do

**Wrong Service Account = Build Fails**

If you choose a service account without the right permissions:
```
❌ Cannot deploy to Cloud Run
❌ Cannot push images to Container Registry
❌ Cannot access Secret Manager
❌ Build fails with permission errors
```

**Right Service Account = Build Succeeds**

If you choose a service account with the right permissions:
```
✅ Can deploy to Cloud Run
✅ Can push images to Container Registry
✅ Can access Secret Manager
✅ Build succeeds
```

---

## Real-World Example

### Scenario: Deploying Simulation Service

**With Wrong Service Account:**
```yaml
# cloudbuild.yaml tries to deploy
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'simulation-service', ...]

# Result:
ERROR: Permission denied
ERROR: Service account does not have roles/run.developer
Build fails ❌
```

**With Right Service Account:**
```yaml
# Same cloudbuild.yaml
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'simulation-service', ...]

# Result:
Deploying... ✅
Service deployed successfully ✅
Build succeeds ✅
```

---

## What Permissions Are Needed?

### For Your Project, Cloud Build Needs:

1. **Deploy Cloud Run Services**
   - Role: `roles/run.developer`
   - Allows: Deploy, update, delete Cloud Run services

2. **Deploy Cloud Functions**
   - Role: `roles/cloudfunctions.developer`
   - Allows: Deploy, update Cloud Functions

3. **Push Docker Images**
   - Role: `roles/storage.admin` or `roles/storage.objectAdmin`
   - Allows: Push images to Container Registry

4. **Access Secret Manager**
   - Role: `roles/secretmanager.secretAccessor`
   - Allows: Read secrets (Neo4j credentials)

5. **Use Service Accounts**
   - Role: `roles/iam.serviceAccountUser`
   - Allows: Act as other service accounts

---

## Service Account Comparison

### ✅ Cloud Build Service Account (Best Choice)

**Name:** `16418516910@cloudbuild.gserviceaccount.com`

**Why it's best:**
- ✅ Created automatically by Cloud Build
- ✅ Has Cloud Build-specific permissions
- ✅ Designed for CI/CD workflows
- ✅ We configured permissions in `setup_cicd.sh`

**Permissions we granted:**
- `roles/cloudfunctions.developer`
- `roles/run.admin`
- `roles/iam.serviceAccountUser`
- `roles/secretmanager.secretAccessor`
- `roles/storage.admin`

**Result:** Build succeeds ✅

---

### ⚠️ Compute Engine Default (Works, but not ideal)

**Name:** `16418516910-compute@developer.gserviceaccount.com`

**Why it works:**
- ✅ Has basic Compute Engine permissions
- ✅ Used by Cloud Functions Gen2
- ✅ Can be granted additional permissions

**Potential issues:**
- ⚠️ Not specifically designed for Cloud Build
- ⚠️ May need additional permissions
- ⚠️ Less secure (broader default permissions)

**Result:** May work, but not recommended

---

### ❌ App Engine Service Account (Wrong Choice)

**Name:** `vendor-risk-digital-twin@appspot.gserviceaccount.com`

**Why it's wrong:**
- ❌ Only has App Engine permissions
- ❌ Cannot deploy to Cloud Run
- ❌ Cannot deploy Cloud Functions
- ❌ Missing required roles

**Result:** Build fails ❌

---

### ❌ Custom Service Account (May not work)

**Name:** `vendor-risk-sa@vendor-risk-digital-twin.iam.gserviceaccount.com`

**Why it may not work:**
- ⚠️ May not have required permissions
- ⚠️ Need to manually grant all roles
- ⚠️ More complex setup

**Result:** May fail unless properly configured

---

## Security Implications

### Principle of Least Privilege

**Good:** Service account with only needed permissions
- Cloud Build service account: Only CI/CD permissions
- Secure and focused

**Bad:** Service account with too many permissions
- Compute Engine default: Broad permissions
- Less secure, more risk

### Why This Matters

If a service account is compromised:
- **Limited permissions** = Limited damage
- **Broad permissions** = Significant damage

---

## What Happens If You Choose Wrong?

### Build Fails with Permission Errors

**Example error:**
```
ERROR: (gcloud.run.deploy) PERMISSION_DENIED: 
The caller does not have permission to deploy to Cloud Run.

Service account: vendor-risk-digital-twin@appspot.gserviceaccount.com
Required role: roles/run.developer
```

**Solution:**
1. Choose the correct service account
2. Or grant required permissions to chosen account

---

## How We Set It Up

### We Configured Permissions in `setup_cicd.sh`

```bash
# Grant Cloud Functions Developer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/cloudfunctions.developer"

# Grant Cloud Run Developer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.developer"

# ... and more permissions
```

**This is why the Cloud Build service account works!**

---

## Best Practices

### 1. Use Cloud Build Service Account

✅ **Best:** `16418516910@cloudbuild.gserviceaccount.com`
- Purpose-built for Cloud Build
- Properly configured permissions
- Secure and focused

### 2. Don't Use Personal Accounts

❌ **Bad:** Your personal GCP account
- Security risk
- Not designed for automation
- Hard to manage

### 3. Don't Use App Engine Account

❌ **Bad:** `@appspot.gserviceaccount.com`
- Wrong permissions
- Build will fail

### 4. Verify Permissions

✅ **Good:** Check what permissions service account has
```bash
gcloud projects get-iam-policy vendor-risk-digital-twin \
    --flatten="bindings[].members" \
    --filter="bindings.members:16418516910@cloudbuild.gserviceaccount.com"
```

---

## Summary

### Why Service Account Selection Matters

1. **Permissions** - Determines what Cloud Build can do
2. **Security** - Limits access to only what's needed
3. **Success** - Right account = build succeeds
4. **Failure** - Wrong account = build fails

### The Right Choice

**✅ Use:** `16418516910@cloudbuild.gserviceaccount.com`

**Why:**
- Purpose-built for Cloud Build
- We configured all required permissions
- Secure and focused
- Guaranteed to work

---

## Related Documentation

- [Setup GitHub Trigger](./setup_github_trigger.md)
- [How CI/CD Works](./how_cicd_works.md)
- [Phase 8 Implementation](./phase8_implementation.md)
- [IAM Service Accounts Guide](../iam_service_accounts_guide.md)

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Complete

