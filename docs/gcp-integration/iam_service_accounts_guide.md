# IAM for Service Accounts: A Critical Cloud-Native Concept

**Date:** 2025-11-30  
**Context:** Understanding why IAM permissions are essential for automated services

---

## The Common Misconception

> **"IAM is just for people"** ❌

Many developers think IAM (Identity and Access Management) is only about controlling what **users** can do. However, in cloud-native architectures, **service accounts** (non-human identities) are just as important—if not more important—than user accounts.

---

## What Are Service Accounts?

**Service Accounts** are special accounts used by applications and services, not humans. They're like "robot users" that:

- Run automated processes
- Access GCP resources on behalf of applications
- Don't have passwords (use keys or default credentials)
- Are identified by email addresses ending in `.iam.gserviceaccount.com`

### Example Service Accounts in This Project

```
16418516910-compute@developer.gserviceaccount.com  # Default Compute Engine service account
vendor-risk-sa@vendor-risk-digital-twin.iam.gserviceaccount.com  # Custom service account
```

---

## Why Service Account IAM Matters

### 1. **Security Principle: Least Privilege**

Every service should only have the **minimum permissions** it needs to function. This prevents:

- **Accidental damage**: A service can't delete resources it shouldn't
- **Security breaches**: If compromised, limited damage
- **Cost overruns**: Services can't create expensive resources

### 2. **Automated Services Need Permissions Too**

When your Discovery Function tries to publish to Pub/Sub, it's not "you" doing it—it's the **service account** running the function. Without proper IAM roles, the service account is denied access.

---

## Real-World Example: The Discovery Function Issue

### What Happened

```
Discovery Function → Tries to publish to Pub/Sub → ❌ Permission Denied
```

**The Function:**
- ✅ Successfully discovered vendors
- ✅ Stored results in Cloud Storage
- ❌ **Silently failed** to publish to Pub/Sub (no error visible!)

**Why it was silent:**
- The code caught the exception and only logged a warning
- The function returned "success" (HTTP 200)
- No one noticed until Graph Loader wasn't triggering

### The Fix

```bash
# Grant Pub/Sub Publisher role to service account
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
  --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

**Result:**
- ✅ Discovery Function can now publish to Pub/Sub
- ✅ Graph Loader triggers automatically
- ✅ Full automation chain works

---

## Service Accounts in This Project

### 1. Discovery Function Service Account

**Account:** `16418516910-compute@developer.gserviceaccount.com`  
**Used By:** Discovery Cloud Function

**Required Roles:**
- ✅ `roles/pubsub.publisher` - Publish discovery events
- ✅ `roles/storage.objectCreator` - Store discovery results
- ✅ `roles/cloudfunctions.functionInvoker` - Invoke other functions (if needed)
- ✅ `roles/run.viewer` - View Cloud Run services (for discovery)
- ✅ `roles/cloudfunctions.viewer` - View Cloud Functions (for discovery)

### 2. Graph Loader Service Account

**Account:** `16418516910-compute@developer.gserviceaccount.com` (or custom)  
**Used By:** Graph Loader Cloud Function

**Required Roles:**
- ✅ `roles/pubsub.subscriber` - Receive Pub/Sub messages
- ✅ `roles/storage.objectViewer` - Read discovery results from Cloud Storage
- ✅ `roles/secretmanager.secretAccessor` - Access Neo4j credentials

### 3. Simulation Service Account

**Account:** `16418516910-compute@developer.gserviceaccount.com` (or custom)  
**Used By:** Cloud Run Simulation Service

**Required Roles:**
- ✅ `roles/pubsub.publisher` - Publish simulation results
- ✅ `roles/secretmanager.secretAccessor` - Access Neo4j credentials
- ✅ `roles/run.invoker` - Invoke Cloud Run services (if needed)

### 4. BigQuery Loader Service Account

**Account:** `16418516910-compute@developer.gserviceaccount.com` (or custom)  
**Used By:** BigQuery Loader Cloud Function

**Required Roles:**
- ✅ `roles/pubsub.subscriber` - Receive Pub/Sub messages
- ✅ `roles/bigquery.dataEditor` - Write simulation data to BigQuery
- ✅ `roles/bigquery.jobUser` - Run BigQuery jobs

---

## IAM Roles Explained

### Common GCP IAM Roles

| Role | Purpose | Example Use Case |
|------|---------|------------------|
| `roles/pubsub.publisher` | Publish messages to Pub/Sub topics | Discovery Function publishing events |
| `roles/pubsub.subscriber` | Receive messages from Pub/Sub | Graph Loader receiving discovery events |
| `roles/storage.objectCreator` | Create objects in Cloud Storage | Storing discovery results |
| `roles/storage.objectViewer` | Read objects from Cloud Storage | Reading discovery results |
| `roles/secretmanager.secretAccessor` | Access secrets in Secret Manager | Reading Neo4j credentials |
| `roles/bigquery.dataEditor` | Write data to BigQuery | Loading simulation results |
| `roles/cloudfunctions.invoker` | Invoke Cloud Functions | Triggering functions |
| `roles/run.invoker` | Invoke Cloud Run services | Calling simulation service |

### Custom Roles vs. Predefined Roles

**Predefined Roles** (recommended):
- ✅ Well-tested and maintained by Google
- ✅ Follow security best practices
- ✅ Easy to use: `roles/pubsub.publisher`

**Custom Roles** (advanced):
- More granular control
- Can combine specific permissions
- Requires more maintenance

---

## Best Practices

### 1. **Use Service Accounts, Not User Accounts**

❌ **Don't:**
```python
# Using your personal credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/my-key.json'
```

✅ **Do:**
```python
# Service account credentials are automatically used
# Cloud Functions/Cloud Run use the assigned service account
publisher = pubsub_v1.PublisherClient()  # Uses service account
```

### 2. **Follow Least Privilege Principle**

Grant only the **minimum permissions** needed:

❌ **Don't:**
```bash
# Too broad - gives editor access to everything
gcloud projects add-iam-policy-binding PROJECT \
  --member="serviceAccount:SA@project.iam.gserviceaccount.com" \
  --role="roles/editor"
```

✅ **Do:**
```bash
# Specific - only what's needed
gcloud projects add-iam-policy-binding PROJECT \
  --member="serviceAccount:SA@project.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

### 3. **Use Separate Service Accounts for Different Services**

**Benefits:**
- Better security isolation
- Easier to audit
- Can revoke permissions per service

**Example:**
```
discovery-sa@project.iam.gserviceaccount.com      # Discovery Function
graph-loader-sa@project.iam.gserviceaccount.com   # Graph Loader
simulation-sa@project.iam.gserviceaccount.com     # Simulation Service
```

### 4. **Document Required Permissions**

For each service, document:
- Which service account it uses
- What IAM roles it needs
- Why each role is needed

### 5. **Check Permissions During Deployment**

Include permission checks in deployment scripts:

```bash
#!/bin/bash
# Check if service account has required role
if ! gcloud projects get-iam-policy PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SA@project.iam.gserviceaccount.com AND bindings.role:roles/pubsub.publisher" \
  --format="value(bindings.role)" | grep -q "pubsub.publisher"; then
  echo "⚠️  Missing required role: roles/pubsub.publisher"
  echo "Granting role..."
  gcloud projects add-iam-policy-binding PROJECT \
    --member="serviceAccount:SA@project.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"
fi
```

---

## Common IAM Issues and Solutions

### Issue 1: "Permission Denied" Errors

**Symptoms:**
- Service runs but fails on specific operations
- Errors like: `403 Permission denied`
- Silent failures (exceptions caught)

**Solution:**
1. Identify which service account is being used
2. Check what operation is failing
3. Grant the appropriate IAM role
4. Verify with a test operation

### Issue 2: Service Works Locally But Fails in Cloud

**Why:**
- Local development uses your user credentials
- Cloud services use service account credentials
- Different permissions!

**Solution:**
- Always test with service account credentials
- Use `gcloud auth application-default login` for local testing
- Or use service account key files

### Issue 3: Too Many Permissions

**Risk:**
- Security vulnerability
- Accidental resource deletion
- Unnecessary costs

**Solution:**
- Audit service account permissions regularly
- Remove unused roles
- Use custom roles for specific needs

---

## How to Check Service Account Permissions

### Method 1: Cloud Console

1. Go to [IAM & Admin → IAM](https://console.cloud.google.com/iam-admin/iam)
2. Find the service account
3. View assigned roles

### Method 2: gcloud CLI

```bash
# List all IAM bindings for a service account
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --format="table(bindings.role)"
```

### Method 3: Check Specific Role

```bash
# Check if service account has a specific role
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SERVICE_ACCOUNT_EMAIL AND bindings.role:roles/pubsub.publisher" \
  --format="value(bindings.role)"
```

---

## IAM in the Vendor Risk Digital Twin Project

### Current Service Account Setup

| Service | Service Account | Required Roles | Status |
|---------|----------------|----------------|--------|
| Discovery Function | `16418516910-compute@developer.gserviceaccount.com` | `pubsub.publisher`, `storage.objectCreator` | ✅ Fixed |
| Graph Loader | `16418516910-compute@developer.gserviceaccount.com` | `pubsub.subscriber`, `storage.objectViewer`, `secretmanager.secretAccessor` | ✅ Working |
| Simulation Service | `16418516910-compute@developer.gserviceaccount.com` | `pubsub.publisher`, `secretmanager.secretAccessor` | ✅ Working |
| BigQuery Loader | `16418516910-compute@developer.gserviceaccount.com` | `pubsub.subscriber`, `bigquery.dataEditor` | ✅ Working |

### Recommended Improvements

1. **Create Dedicated Service Accounts:**
   ```bash
   # Create service accounts for each service
   gcloud iam service-accounts create discovery-sa \
     --display-name="Discovery Function Service Account"
   
   gcloud iam service-accounts create graph-loader-sa \
     --display-name="Graph Loader Service Account"
   ```

2. **Grant Specific Roles:**
   ```bash
   # Discovery Function
   gcloud projects add-iam-policy-binding PROJECT \
     --member="serviceAccount:discovery-sa@PROJECT.iam.gserviceaccount.com" \
     --role="roles/pubsub.publisher"
   
   gcloud projects add-iam-policy-binding PROJECT \
     --member="serviceAccount:discovery-sa@PROJECT.iam.gserviceaccount.com" \
     --role="roles/storage.objectCreator"
   ```

3. **Update Function Configurations:**
   ```bash
   # Deploy with specific service account
   gcloud functions deploy discovery \
     --service-account=discovery-sa@PROJECT.iam.gserviceaccount.com \
     --gen2 \
     --region=us-central1
   ```

---

## Key Takeaways

1. **Service Accounts Need IAM Too**
   - Every automated service uses a service account
   - Service accounts need permissions just like users
   - Missing permissions cause silent failures

2. **Least Privilege is Critical**
   - Grant only what's needed
   - Review permissions regularly
   - Use specific roles, not broad ones

3. **Document Permissions**
   - Know which service account each service uses
   - Document required roles
   - Include in deployment scripts

4. **Test with Service Accounts**
   - Don't assume it works because it works locally
   - Test with actual service account credentials
   - Verify permissions before deployment

---

## Related Documentation

- [Discovery Pub/Sub Fix](./discovery_pubsub_fix.md) - Real example of IAM issue
- [GCP IAM Documentation](https://cloud.google.com/iam/docs)
- [Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)

---

**Remember:** In cloud-native architectures, **service accounts are first-class citizens** with their own identities and permissions. Understanding and managing their IAM is as important as managing user permissions—if not more so, since they run automatically without human oversight.

