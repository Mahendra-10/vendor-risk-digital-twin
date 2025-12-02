# How to Grant Service Account Permissions in GCP

**Last Updated:** 2025-12-01

---

## Standard Command Format

### Basic Syntax

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="ROLE_NAME" \
    --condition=None
```

---

## Command Breakdown

### 1. `gcloud projects add-iam-policy-binding`
- The command to add IAM permissions
- Works at the project level

### 2. `PROJECT_ID`
- Your GCP project ID
- Example: `vendor-risk-digital-twin`

### 3. `--member="serviceAccount:EMAIL"`
- The service account to grant permissions to
- Format: `serviceAccount:EMAIL_ADDRESS`
- Example: `serviceAccount:16418516910-compute@developer.gserviceaccount.com`

### 4. `--role="ROLE_NAME"`
- The IAM role to grant
- Format: `roles/SERVICE.ACTION`
- Examples:
  - `roles/cloudfunctions.developer`
  - `roles/run.admin`
  - `roles/secretmanager.secretAccessor`

### 5. `--condition=None` (if needed)
- Required if project has IAM conditions
- Means: "Always allow" (no restrictions)
- Optional if project has no conditions

---

## Common IAM Roles

### Cloud Functions
```bash
--role="roles/cloudfunctions.developer"
```
- Deploy and manage Cloud Functions

### Cloud Run
```bash
--role="roles/run.admin"
```
- Deploy and manage Cloud Run services

### Secret Manager
```bash
--role="roles/secretmanager.secretAccessor"
```
- Read secrets from Secret Manager

### Storage
```bash
--role="roles/storage.admin"
```
- Full control over Cloud Storage (for Container Registry)

### Service Account User
```bash
--role="roles/iam.serviceAccountUser"
```
- Act as other service accounts

### Cloud Build
```bash
--role="roles/cloudbuild.builds.editor"
```
- Create and manage Cloud Build builds

---

## Real Examples

### Example 1: Grant Cloud Functions Permission

```bash
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/cloudfunctions.developer" \
    --condition=None
```

### Example 2: Grant Multiple Roles

```bash
# Cloud Run Admin
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/run.admin" \
    --condition=None

# Secret Manager Accessor
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

# Storage Admin
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin" \
    --condition=None
```

---

## Finding Service Account Email

### Compute Engine Default
```bash
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
echo "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
```

### Cloud Build Service Account
```bash
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
echo "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

### List All Service Accounts
```bash
gcloud iam service-accounts list --project=PROJECT_ID
```

---

## Finding Available Roles

### List All Roles
```bash
gcloud iam roles list
```

### Search for Specific Service
```bash
gcloud iam roles list --filter="name:cloudfunctions"
```

### View Role Permissions
```bash
gcloud iam roles describe roles/cloudfunctions.developer
```

---

## Checking Current Permissions

### See What Permissions a Service Account Has
```bash
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:SERVICE_ACCOUNT_EMAIL" \
    --format="table(bindings.role)"
```

### Example
```bash
gcloud projects get-iam-policy vendor-risk-digital-twin \
    --flatten="bindings[].members" \
    --filter="bindings.members:16418516910-compute@developer.gserviceaccount.com" \
    --format="table(bindings.role)"
```

---

## Removing Permissions

### Remove a Role
```bash
gcloud projects remove-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="ROLE_NAME" \
    --condition=None
```

### Example
```bash
gcloud projects remove-iam-policy-binding vendor-risk-digital-twin \
    --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
    --role="roles/cloudfunctions.developer" \
    --condition=None
```

---

## Common Patterns

### Pattern 1: Grant All Required Roles for CI/CD

```bash
PROJECT_ID="vendor-risk-digital-twin"
SA="16418516910-compute@developer.gserviceaccount.com"

ROLES=(
    "roles/cloudfunctions.developer"
    "roles/run.admin"
    "roles/secretmanager.secretAccessor"
    "roles/storage.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudbuild.builds.editor"
)

for ROLE in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA}" \
        --role="${ROLE}" \
        --condition=None \
        --quiet
done
```

### Pattern 2: Grant to Multiple Service Accounts

```bash
PROJECT_ID="vendor-risk-digital-twin"
ROLE="roles/secretmanager.secretAccessor"

SERVICE_ACCOUNTS=(
    "16418516910-compute@developer.gserviceaccount.com"
    "16418516910@cloudbuild.gserviceaccount.com"
)

for SA in "${SERVICE_ACCOUNTS[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA}" \
        --role="${ROLE}" \
        --condition=None \
        --quiet
done
```

---

## When to Use `--condition=None`

### Use `--condition=None` When:
- ✅ Project has IAM conditions on some bindings
- ✅ Running in non-interactive mode (scripts)
- ✅ You want permissions to always apply (no restrictions)

### Don't Need It When:
- ❌ Project has no IAM conditions
- ❌ Running interactively (gcloud will prompt)

### How to Check
```bash
# If you get this error, you need --condition=None:
# "Adding a binding without specifying a condition..."
```

---

## Best Practices

### 1. Use Least Privilege
- Grant only the permissions needed
- Don't use overly broad roles like `roles/owner`

### 2. Use Specific Roles
- `roles/cloudfunctions.developer` (specific)
- Not `roles/editor` (too broad)

### 3. Document Why
- Comment in scripts why each role is needed
- Keep track of what permissions each service account has

### 4. Test Permissions
- Test after granting permissions
- Verify the service account can perform required actions

---

## Summary

**Standard Command:**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="ROLE_NAME" \
    --condition=None
```

**Key Parts:**
- `PROJECT_ID`: Your GCP project
- `SERVICE_ACCOUNT_EMAIL`: The service account
- `ROLE_NAME`: The permission role
- `--condition=None`: No restrictions (if needed)

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Complete

