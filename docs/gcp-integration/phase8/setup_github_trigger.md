# Setting Up Automatic CI/CD with GitHub Trigger

**Last Updated:** 2025-12-01  
**Phase:** 8 - CI/CD Pipeline (Automatic Deployment)

---

## Overview

This guide shows you how to set up automatic deployments so that every time you push code to GitHub, Cloud Build automatically builds and deploys your services.

**Before:** Manual build with `gcloud builds submit`  
**After:** Automatic build on every `git push`

---

## Prerequisites

✅ Cloud Build API enabled  
✅ `cloudbuild.yaml` created and tested  
✅ GitHub repository with your code  
✅ GitHub account connected to Google Cloud

---

## Step-by-Step Setup

### Step 1: Connect GitHub Repository

1. **Go to Cloud Build Triggers:**
   ```
   https://console.cloud.google.com/cloud-build/triggers?project=vendor-risk-digital-twin
   ```

2. **Click "Connect Repository"** (top of page)

3. **Select Source:**
   - Choose: **GitHub (Cloud Build GitHub App)**
   - Click **Continue**

4. **Authenticate:**
   - Click **Authenticate**
   - You'll be redirected to GitHub
   - Authorize Google Cloud Build to access your GitHub account
   - Select the repositories you want to connect (or all repositories)
   - Click **Install**

5. **Select Repository:**
   - Choose your `vendor-risk-digital-twin` repository
   - Click **Continue**

---

### Step 2: Create Trigger

**Important:** For 2nd-gen repositories, you must create triggers from the main Triggers page, not from the repository page.

1. **Go to Cloud Build Triggers page:**
   ```
   https://console.cloud.google.com/cloud-build/triggers?project=vendor-risk-digital-twin
   ```

2. **Click "Create Trigger"** (top of page, not from repository 3-dots menu)

2. **Configure Trigger:**

   **Name:**
   ```
   deploy-all-services
   ```

   **Region:**
   - **Important:** If using 2nd-gen repositories, change from `global` to `us-central1` (or your preferred region)
   - 2nd-gen repositories require a specific region, not global
   - If you see "2nd-gen repositories are not available in the global region", change to `us-central1`

   **Event:**
   - Select: **Push to a branch**
   - Branch: `^main$` (or your main branch name)
   - Optionally: Add file filters (e.g., only trigger on changes to `cloud_run/` or `cloud_functions/`)

   **Configuration:**
   - Select: **Cloud Build configuration file (yaml or json)**
   - Location: `cloudbuild.yaml`
   - This uses the `cloudbuild.yaml` in your repository root

   **Substitution variables:** (Optional - uses defaults)
   - Leave empty (uses `$PROJECT_ID` automatically)

3. **Click "Create"**

---

### Step 3: Verify Setup

1. **Check trigger is created:**
   - You should see your trigger in the list
   - Status should be "Enabled"

2. **Test it:**
   ```bash
   # Make a small change
   echo "# Test" >> README.md
   
   # Commit and push
   git add README.md
   git commit -m "Test CI/CD trigger"
   git push origin main
   ```

3. **Watch the build:**
   - Go to: https://console.cloud.google.com/cloud-build/builds?project=vendor-risk-digital-twin
   - You should see a new build automatically started
   - Watch it complete successfully

---

## What Happens Now

### Automatic Deployment Flow

```
You make code changes
    ↓
git add .
git commit -m "Update compliance controls"
git push origin main
    ↓
GitHub receives push
    ↓
GitHub webhook triggers Cloud Build
    ↓
Cloud Build runs cloudbuild.yaml
    ↓
Tests → Build → Deploy all services
    ↓
Services updated automatically ✅
```

### You Don't Need To:

❌ Run `gcloud builds submit` manually  
❌ Navigate to Cloud Console  
❌ Click any buttons  
❌ Wait for manual steps

### You Just:

✅ Push code to GitHub  
✅ CI/CD handles everything automatically

---

## Trigger Configuration Options

### Branch Pattern

**Only main branch:**
```
^main$
```

**Main and develop branches:**
```
^(main|develop)$
```

**All branches:**
```
.*
```

### File Filters (Optional)

**Only trigger on specific files:**
```
cloud_run/**,cloud_functions/**,cloudbuild.yaml
```

**Exclude certain files:**
```
!docs/**,!*.md
```

### Advanced: Multiple Triggers

You can create multiple triggers for different scenarios:

**Trigger 1: Production (main branch)**
- Branch: `^main$`
- Deploys to production

**Trigger 2: Staging (develop branch)**
- Branch: `^develop$`
- Deploys to staging environment

---

## Monitoring Automatic Builds

### View Build History

**Cloud Console:**
```
https://console.cloud.google.com/cloud-build/builds?project=vendor-risk-digital-twin
```

**Command Line:**
```bash
# List recent builds
gcloud builds list --project vendor-risk-digital-twin --limit 10

# View specific build
gcloud builds log BUILD_ID --project vendor-risk-digital-twin
```

### Build Notifications

**Email Notifications:**
1. Go to: https://console.cloud.google.com/cloud-build/settings?project=vendor-risk-digital-twin
2. Configure email notifications for build status

**Pub/Sub Notifications:**
- Set up Pub/Sub topic for build events
- Integrate with Slack, email, or other services

---

## Troubleshooting

### Trigger Not Firing

**Check:**
1. Is trigger enabled? (Status should be "Enabled")
2. Did you push to the correct branch? (matches trigger pattern)
3. Are file filters excluding your changes?
4. Check GitHub webhook status in repository settings

**Fix:**
- Verify branch name matches trigger pattern
- Check trigger configuration
- Test with a simple commit

### Build Fails

**Check build logs:**
```bash
gcloud builds list --project vendor-risk-digital-twin --limit 1
gcloud builds log BUILD_ID --project vendor-risk-digital-twin
```

**Common issues:**
- Missing permissions (run `./scripts/setup/setup_cicd.sh`)
- Syntax errors in code
- Missing dependencies

### GitHub Connection Issues

**Reconnect repository:**
1. Go to Cloud Build Triggers
2. Click "Manage connected repositories"
3. Disconnect and reconnect if needed

---

## Best Practices

### 1. Use Branch Protection

Protect your `main` branch:
- Require pull request reviews
- Require status checks (Cloud Build)
- Prevent force pushes

### 2. Test Before Merge

Use feature branches:
```bash
# Create feature branch
git checkout -b feature/update-compliance

# Make changes
# ... edit files ...

# Push to feature branch
git push origin feature/update-compliance

# Create pull request
# After review, merge to main
# → Triggers automatic deployment
```

### 3. Monitor Builds

- Set up email notifications
- Check build history regularly
- Review failed builds promptly

### 4. Use Meaningful Commit Messages

```bash
# Good
git commit -m "Add Twilio compliance controls"

# Bad
git commit -m "update"
```

---

## Disabling Automatic Builds

### Temporarily Disable

1. Go to Cloud Build Triggers
2. Click on your trigger
3. Click "Disable"
4. Re-enable when ready

### Permanently Delete

1. Go to Cloud Build Triggers
2. Click on your trigger
3. Click "Delete"
4. Confirm deletion

---

## Summary

### What You Get

✅ **Automatic deployments** on every push  
✅ **No manual commands** needed  
✅ **Consistent process** every time  
✅ **Professional workflow**  
✅ **Time saved** (13+ minutes per deployment)

### Setup Time

- **5-10 minutes** to set up
- **Lifetime of time saved** after that

### Next Steps

1. Connect GitHub repository
2. Create trigger
3. Test with a small change
4. Enjoy automatic deployments! 🚀

---

## Quick Reference

**Trigger URL:**
```
https://console.cloud.google.com/cloud-build/triggers?project=vendor-risk-digital-twin
```

**Build History:**
```
https://console.cloud.google.com/cloud-build/builds?project=vendor-risk-digital-twin
```

**Test Command:**
```bash
# Make a small change and push
echo "# Test" >> README.md
git add README.md
git commit -m "Test CI/CD"
git push origin main
```

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Ready to Use

