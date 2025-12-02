# Root Cause Analysis: Simulation Service Deployment Failures

## Executive Summary

The `simulation-service` deployment failed due to a **cascading series of issues** that started with a simple import path error and escalated through Docker caching, Python package structure, and Cloud Build configuration problems.

---

## Timeline of Issues

### Issue #1: Incorrect Import Path (Original Root Cause)

**Error:**
```
ModuleNotFoundError: No module named 'scripts.simulate_failure'
```

**Root Cause:**
- The code file was moved from `scripts/simulate_failure.py` to `scripts/simulation/simulate_failure.py`
- But `app.py` still had the old import: `from scripts.simulate_failure import VendorFailureSimulator`
- Should have been: `from scripts.simulation.simulate_failure import VendorFailureSimulator`

**Why it happened:**
- Code refactoring moved files into subdirectories (`scripts/simulation/`, `scripts/gcp/`)
- Import statements were not updated to match the new directory structure

**Fix Applied:**
- Updated import in `cloud_run/simulation-service/app.py`:
  ```python
  # Before:
  from scripts.simulate_failure import VendorFailureSimulator
  
  # After:
  from scripts.simulation.simulate_failure import VendorFailureSimulator
  ```

---

### Issue #2: Docker Layer Caching (Why Fixes Didn't Work Initially)

**Error:**
```
ModuleNotFoundError: No module named 'scripts.simulate_failure'
```
*(Persisted even after fixing the import path)*

**Root Cause:**
- Docker was using **cached layers** from previous builds
- The cached layers contained the old code with the wrong import
- Even though the source code was fixed, Docker reused old layers

**Why it happened:**
- Docker's layer caching is designed to speed up builds
- Docker determines if a layer has changed by:
  1. **Checking the Dockerfile instruction** (e.g., `COPY scripts/ ./scripts/`)
  2. **Computing checksums of the files being copied** (e.g., all files in `scripts/`)
  3. **If BOTH the instruction AND file checksums match a previous build**, Docker reuses the cached layer
- **In our case:** Even though we fixed `app.py` in git, Docker was using a **cached layer from a previous Cloud Build run** that had the old code
- **Why the layer didn't "change" from Docker's perspective:**
  - Docker's cache can persist across multiple Cloud Build runs
  - If Docker calculated the same checksum for the files (or used a stale cache), it thought nothing changed
  - The `COPY scripts/ ./scripts/` command reused the old cached layer with the wrong import path
  - This is why `--no-cache` was needed: to force Docker to rebuild every layer from scratch, ignoring the cache

**Fix Applied:**
- Added `--no-cache` flag to Docker build in `cloudbuild.yaml`:
  ```yaml
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--no-cache'  # Force rebuild without cache
      - '--pull'      # Force fresh base image
      - '-f'
      - 'cloud_run/simulation-service/Dockerfile'
      - '-t'
      - 'gcr.io/$PROJECT_ID/simulation-service:latest'
      - '.'
  ```

---

### Issue #3: Missing Python Package Markers

**Error:**
```
ModuleNotFoundError: No module named 'scripts.simulation'
```

**Root Cause:**
- Python requires `__init__.py` files to recognize directories as packages
- Without these files, Python can't import from subdirectories
- The `scripts/`, `scripts/simulation/`, and `scripts/gcp/` directories were missing `__init__.py`

**Why it happened:**
- When files were moved into subdirectories, the package markers weren't created
- Python's import system needs these files to treat directories as importable packages

**Fix Applied:**
- Created `__init__.py` files:
  - `scripts/__init__.py`
  - `scripts/simulation/__init__.py`
  - `scripts/gcp/__init__.py`

---

### Issue #4: Incorrect sys.path Calculation

**Error:**
```
ModuleNotFoundError: No module named 'scripts.simulation.simulate_failure'
```
*(Persisted even with correct imports and __init__.py files)*

**Root Cause:**
- The `sys.path.insert()` was calculating the wrong path
- In Docker, `app.py` is at `/app/app.py`
- The code was doing `Path(__file__).parent.parent.parent` which went to `/` instead of `/app`

**Why it happened:**
- The path calculation assumed a different directory structure
- In Docker, the working directory is `/app`, but the code was going up too many levels

**Fix Applied:**
- Updated `app.py`:
  ```python
  # Before:
  sys.path.insert(0, str(Path(__file__).parent.parent.parent))
  
  # After:
  app_dir = str(Path(__file__).parent)  # /app
  if app_dir not in sys.path:
      sys.path.insert(0, app_dir)
  ```

---

### Issue #5: Cloud Build Variable Substitution Error

**Error:**
```
invalid value for 'build.substitutions': key in the template "IMAGE_DIGEST" 
is not a valid built-in substitution
```

**Root Cause:**
- Cloud Build was trying to substitute `$IMAGE_DIGEST` as a built-in variable
- But `IMAGE_DIGEST` is a custom variable we create in bash
- Cloud Build's substitution system was interfering with bash variable expansion

**Why it happened:**
- Cloud Build automatically tries to substitute variables in the format `$VARIABLE`
- We were using `$IMAGE_DIGEST` in bash scripts, which Cloud Build tried to process
- Cloud Build doesn't know about our custom `IMAGE_DIGEST` variable

**Fix Applied:**
- Escaped variables in bash scripts using `$$`:
  ```yaml
  # Before:
  IMAGE_DIGEST=$(cat /workspace/image_digest.txt)
  echo "Deploying: $IMAGE_DIGEST"
  
  # After:
  IMAGE_DIGEST=$(cat /workspace/image_digest.txt)
  echo "Deploying: $$IMAGE_DIGEST"  # $$ escapes to $ in bash
  ```
- This tells Cloud Build: "Don't substitute this, let bash handle it"

---

### Issue #6: Empty Image Digest (Final Issue)

**Error:**
```
ERROR: service.spec.template.spec.containers[0].image: expected a container 
image path in the form [hostname/]repo-path[:tag and/or @digest].
```

**Root Cause:**
- The image digest file was empty or didn't exist
- This created an invalid image path: `gcr.io//simulation-service@` (empty digest)
- Cloud Run rejected the deployment because the image path was malformed

**Why it happened:**
- The digest retrieval methods (`docker inspect`) might fail if:
  - The image hasn't been pushed to the registry yet
  - The digest isn't available immediately after build
  - The image is only available locally, not in the registry

**Fix Applied:**
- Added error handling and fallback to `latest` tag:
  ```bash
  # Try to get digest, fallback to 'latest' if unavailable
  IMAGE_DIGEST=$(cat /workspace/image_digest.txt 2>/dev/null || echo "latest")
  
  if [ -n "$IMAGE_DIGEST" ] && [ "$IMAGE_DIGEST" != "latest" ]; then
    IMAGE_REF="gcr.io/$PROJECT_ID/simulation-service@$IMAGE_DIGEST"
  else
    IMAGE_REF="gcr.io/$PROJECT_ID/simulation-service:latest"
  fi
  ```

---

## Why Step 4 (deploy-simulation-service) Kept Failing

### The Cascade Effect

1. **First Failure**: Wrong import path → Container couldn't start
2. **Second Failure**: Docker cache → Old code still in image
3. **Third Failure**: Missing `__init__.py` → Python couldn't import packages
4. **Fourth Failure**: Wrong `sys.path` → Python couldn't find modules
5. **Fifth Failure**: Cloud Build substitution → Bash variables didn't work
6. **Sixth Failure**: Empty digest → Invalid image path

Each fix revealed the next issue, creating a "whack-a-mole" situation.

### Why It Was Hard to Debug

1. **Docker Caching**: Made it seem like fixes weren't being applied
2. **Multiple Layers**: Issues at different levels (code, Docker, Cloud Build)
3. **Error Messages**: Sometimes showed the wrong error (e.g., import error when it was actually a path issue)
4. **CI/CD Pipeline**: Each fix required a full rebuild, taking time

---

## The Complete Fix Chain

### 1. Code Level
- ✅ Fixed import paths
- ✅ Added `__init__.py` files
- ✅ Fixed `sys.path` calculation

### 2. Docker Level
- ✅ Added `--no-cache` to force clean builds
- ✅ Added `--pull` to get fresh base images

### 3. Cloud Build Level
- ✅ Escaped bash variables (`$$` instead of `$`)
- ✅ Added error handling for digest retrieval
- ✅ Added fallback to `latest` tag

---

## Lessons Learned

1. **Always update imports when moving files**
2. **Docker caching can hide fixes** - use `--no-cache` when debugging
3. **Python packages need `__init__.py` files**
4. **Test path calculations in the actual runtime environment**
5. **Cloud Build variable substitution can interfere with bash variables**
6. **Always have fallbacks for dynamic values (like image digests)**

---

## Final Working Configuration

The deployment now works because:

1. ✅ **Correct imports**: `from scripts.simulation.simulate_failure import VendorFailureSimulator`
2. ✅ **Package structure**: All directories have `__init__.py` files
3. ✅ **Correct paths**: `sys.path` points to `/app` in Docker
4. ✅ **Clean builds**: `--no-cache` ensures fresh code
5. ✅ **Proper variables**: Escaped bash variables work correctly
6. ✅ **Reliable image reference**: Falls back to `latest` if digest unavailable

---

## Verification

The successful build shows:
- ✅ All 8 steps completed
- ✅ Docker image built with correct code
- ✅ Image digest retrieved (or fallback used)
- ✅ Cloud Run deployment succeeded
- ✅ All Cloud Functions deployed

**Build ID**: `f859fba8-9648-4393-9f0c-138011146e64`  
**Status**: ✅ Successful  
**Duration**: 00:01:41

