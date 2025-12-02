# Cloud Build vs GitHub Actions: What's the Difference?

**Last Updated:** 2025-12-01  
**Phase:** 8 - CI/CD Pipeline

---

## Quick Answer

**Cloud Build** = Google Cloud's CI/CD service (what we set up)  
**GitHub Actions** = GitHub's built-in CI/CD service

Both do similar things, but they're different tools from different companies.

---

## Key Differences

### 1. Who Makes It

| Feature | Cloud Build | GitHub Actions |
|---------|-------------|---------------|
| **Provider** | Google Cloud | GitHub |
| **Where it runs** | Google Cloud infrastructure | GitHub's infrastructure (or self-hosted) |
| **Integration** | Native GCP integration | Native GitHub integration |

### 2. Configuration

| Feature | Cloud Build | GitHub Actions |
|---------|-------------|---------------|
| **Config file** | `cloudbuild.yaml` | `.github/workflows/*.yml` |
| **Location** | Project root | `.github/workflows/` folder |
| **Format** | YAML | YAML |

### 3. Where It Runs

| Feature | Cloud Build | GitHub Actions |
|---------|-------------|---------------|
| **Runners** | Google Cloud machines | GitHub-hosted or self-hosted |
| **OS options** | Linux, Windows, macOS | Linux, Windows, macOS |
| **Cost** | Pay per build minute | Free for public repos, paid for private |

### 4. GCP Integration

| Feature | Cloud Build | GitHub Actions |
|---------|-------------|---------------|
| **GCP services** | Native, seamless | Requires authentication setup |
| **Deploy to GCP** | Built-in commands | Need to install gcloud CLI |
| **GCP permissions** | Automatic | Manual setup needed |

---

## Side-by-Side Comparison

### Cloud Build (What We Set Up)

**Configuration:**
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/service', '.']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'service', '--image', 'gcr.io/$PROJECT_ID/service']
```

**Pros:**
- ✅ Native GCP integration
- ✅ No authentication setup needed
- ✅ Built-in GCP commands
- ✅ Automatic permissions
- ✅ Runs on Google Cloud infrastructure

**Cons:**
- ❌ Only works with GCP
- ❌ Less flexible for non-GCP deployments
- ❌ Requires GCP project

---

### GitHub Actions

**Configuration:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      - run: gcloud builds submit --config cloudbuild.yaml
```

**Pros:**
- ✅ Works with any cloud provider
- ✅ Free for public repositories
- ✅ Large marketplace of actions
- ✅ Can deploy to AWS, Azure, GCP, etc.
- ✅ Integrated with GitHub

**Cons:**
- ❌ Requires authentication setup for GCP
- ❌ Need to manage service account keys
- ❌ More configuration needed
- ❌ Runs on GitHub's infrastructure (unless self-hosted)

---

## Which One Should You Use?

### Use Cloud Build If:

✅ You're deploying to Google Cloud only  
✅ You want native GCP integration  
✅ You want simpler setup  
✅ You're already using GCP  
✅ You want automatic GCP permissions

**This is what we set up!** Perfect for your GCP-based project.

---

### Use GitHub Actions If:

✅ You're deploying to multiple cloud providers  
✅ You want to use GitHub's free tier  
✅ You need more flexibility  
✅ You want to use marketplace actions  
✅ You're deploying to AWS/Azure as well

---

## Can You Use Both?

**Yes!** You can use both together:

**Option 1: GitHub Actions → Cloud Build**
```yaml
# .github/workflows/deploy.yml
- name: Trigger Cloud Build
  run: gcloud builds submit --config cloudbuild.yaml
```

**Option 2: GitHub Actions → Direct Deploy**
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy service \
      --image gcr.io/$PROJECT_ID/service \
      --region us-central1
```

**Option 3: Cloud Build Only (What We Have)**
- Simpler
- Native GCP integration
- No GitHub Actions needed

---

## Real-World Example

### Scenario: Deploy to Cloud Run

**With Cloud Build (What We Set Up):**
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'service', '--image', '...']
```
- ✅ Works automatically
- ✅ No auth setup
- ✅ Simple

**With GitHub Actions:**
```yaml
# .github/workflows/deploy.yml
- uses: google-github-actions/setup-gcloud@v1
  with:
    service_account_key: ${{ secrets.GCP_SA_KEY }}
- run: gcloud run deploy service --image ...
```
- ⚠️ Need to set up service account
- ⚠️ Need to store key in GitHub secrets
- ⚠️ More steps

---

## Cost Comparison

### Cloud Build

- **Free tier:** 120 build-minutes per day
- **After free tier:** $0.003 per build-minute
- **Your builds:** ~2 minutes each
- **Cost:** Essentially free for your usage

### GitHub Actions

- **Public repos:** Free (unlimited)
- **Private repos:** 
  - Free: 2,000 minutes/month
  - Paid: $0.008 per minute after
- **Your builds:** ~2 minutes each
- **Cost:** Free for most usage

---

## For Your Project

### What We Set Up: Cloud Build

**Why it's perfect for you:**
1. ✅ You're deploying to GCP only
2. ✅ Native integration (no auth setup)
3. ✅ Simple configuration
4. ✅ Automatic permissions
5. ✅ Works seamlessly with GCP services

**What you get:**
- Automatic builds on GitHub push
- Native GCP deployment
- No authentication headaches
- Simple `cloudbuild.yaml` config

---

## Summary

| Aspect | Cloud Build | GitHub Actions |
|--------|------------|---------------|
| **Provider** | Google Cloud | GitHub |
| **Best for** | GCP-only projects | Multi-cloud projects |
| **Setup complexity** | Simple | Moderate |
| **GCP integration** | Native | Requires setup |
| **Cost** | Free tier available | Free for public repos |
| **Flexibility** | GCP-focused | Very flexible |

---

## Bottom Line

**Cloud Build** = Perfect for GCP projects (what you have)  
**GitHub Actions** = More flexible, works with any cloud

For your Vendor Risk Digital Twin project:
- ✅ **Cloud Build is the right choice**
- ✅ Already set up and working
- ✅ Native GCP integration
- ✅ Simple and effective

You don't need GitHub Actions unless you want to deploy to other clouds too.

---

## Related Documentation

- [How CI/CD Works](./how_cicd_works.md)
- [Setup GitHub Trigger](./setup_github_trigger.md)
- [Phase 8 Implementation](./phase8_implementation.md)

---

**Last Updated:** 2025-12-01  
**Status:** ✅ Complete

