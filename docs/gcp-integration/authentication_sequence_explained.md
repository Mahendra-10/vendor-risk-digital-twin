# Authentication Sequence: Host to Cloud Service

## Educational Overview

This document explains the **authentication sequence** for a host (VM or container) to authenticate to another cloud service, including the relationships between hosts, metadata services, and identity standards like SPIFFE. We'll use the Vendor Risk Digital Twin application as a real-world example.

---

## 🎯 The Core Question

**How does a Cloud Function or Cloud Run container authenticate to GCP services like Pub/Sub or Secret Manager?**

**Answer:** Through a multi-step authentication sequence involving:
1. **Host Identity** (Service Account)
2. **Metadata Service** (GCP Metadata Server)
3. **Token Exchange** (OAuth 2.0 Access Tokens)
4. **Service Authentication** (Using tokens to access cloud services)

---

## 🔄 The Authentication Sequence (Step-by-Step)

### Scenario: Discovery Function → Pub/Sub

Let's trace what happens when your Discovery Function tries to publish to Pub/Sub:

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Discovery Function (Host) Needs to Publish            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Function Requests Access Token from Metadata Service  │
│         GET http://metadata.google.internal/computeMetadata/... │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Metadata Service Validates Host Identity               │
│         - Checks: Is this a valid Cloud Function?              │
│         - Checks: What service account is assigned?            │
│         - Checks: What IAM roles does it have?                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Metadata Service Issues OAuth 2.0 Access Token       │
│         - Token includes: service account identity             │
│         - Token includes: scopes (permissions)                 │
│         - Token expires: typically 1 hour                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Function Uses Token to Authenticate to Pub/Sub          │
│         POST https://pubsub.googleapis.com/v1/projects/...     │
│         Header: Authorization: Bearer <access_token>            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Pub/Sub Validates Token                                 │
│         - Checks: Is token valid? (not expired)                 │
│         - Checks: Does service account have pubsub.publisher?   │
│         - Checks: Is token signed by Google?                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Pub/Sub Grants Access                                  │
│         ✅ Message published successfully                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Component Relationships

### 1. **The Host (VM/Container)**

**In Your Application:**
- **Cloud Function**: `discovery` function (runs in a managed container)
- **Cloud Run**: `simulation-service` (runs in a container)

**Host Identity:**
- Each host has a **service account** assigned
- Example: `16418516910-compute@developer.gserviceaccount.com`
- This identity is **immutable** - it's part of the host's configuration

**Code Example:**
```python
# Discovery Function code (cloud_functions/discovery/main.py)
def publish_discovery_event(project_id, storage_path, results):
    """Publish event to Pub/Sub"""
    # The function doesn't explicitly authenticate
    # It relies on the service account assigned to the Cloud Function
    publisher = pubsub_v1.PublisherClient()  # ← Uses service account automatically
    topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
    publisher.publish(topic_path, data)
```

**Key Point:** The host doesn't manage credentials directly. It relies on the **metadata service** to provide tokens.

---

### 2. **The Metadata Service**

**What It Is:**
- A **local service** running at a special IP address
- In GCP: `metadata.google.internal` (169.254.169.254)
- Provides **instance metadata** and **authentication tokens**
- Only accessible from within the host (not from internet)

**In GCP:**
```
Metadata Server Endpoint:
http://metadata.google.internal/computeMetadata/v1/

Key Endpoints:
- /instance/service-accounts/default/token
- /instance/service-accounts/default/identity
- /project/project-id
```

**How It Works:**
1. Host makes HTTP request to metadata server
2. Metadata server validates the request is from a legitimate GCP resource
3. Metadata server checks the host's service account
4. Metadata server issues an OAuth 2.0 access token

**Real Example:**
```python
# What happens behind the scenes when you call:
publisher = pubsub_v1.PublisherClient()

# The Google Cloud client library:
# 1. Checks if running in GCP environment
# 2. Requests token from metadata server:
#    GET http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?scopes=https://www.googleapis.com/auth/pubsub
# 3. Receives token:
#    {
#      "access_token": "ya29.c.b0Aaek...",
#      "expires_in": 3600,
#      "token_type": "Bearer"
#    }
# 4. Uses token in API calls:
#    Authorization: Bearer ya29.c.b0Aaek...
```

**Security Features:**
- **Only accessible from host**: Cannot be accessed from internet
- **Automatic rotation**: Tokens expire and are refreshed automatically
- **No credential storage**: No keys stored on disk
- **Audit logging**: All token requests are logged

---

### 3. **Identity Standards: SPIFFE**

**What is SPIFFE?**
- **Secure Production Identity Framework for Everyone**
- Standard for **workload identity** (not just user identity)
- Provides secure identity for services across different platforms
- Works with Kubernetes, VMs, containers, serverless

**SPIFFE Identity Format:**
```
spiffe://trust-domain/workload-identifier

Example:
spiffe://vendor-risk-digital-twin.iam.gserviceaccount.com/discovery-function
```

**How SPIFFE Relates to Your Application:**

**Current State (GCP Native):**
```
Service Account Identity:
16418516910-compute@developer.gserviceaccount.com
```

**With SPIFFE (Future):**
```
SPIFFE Identity:
spiffe://vendor-risk-digital-twin.iam.gserviceaccount.com/discovery-function
```

**Benefits of SPIFFE:**
1. **Cross-Platform**: Same identity standard for GCP, AWS, Azure
2. **Workload-Focused**: Identity for services, not just users
3. **Standard Format**: Consistent identity format across environments
4. **Mutual TLS**: Can use SPIFFE for mTLS authentication

**SPIFFE Components:**
- **SPIFFE ID**: Unique identity for each workload
- **SVID (SPIFFE Verifiable Identity Document)**: Certificate or JWT proving identity
- **SPIRE**: SPIFFE Runtime Environment (implements SPIFFE)

**In Your Application Context:**
- **Current**: GCP service accounts (GCP-specific)
- **With SPIFFE**: Could have SPIFFE identities that work across clouds
- **Benefit**: If you migrate to AWS/Azure, same identity standard

---

### 4. **Token Exchange and OAuth 2.0**

**The Token Flow:**

```
Host → Metadata Service → OAuth 2.0 Token → Cloud Service
```

**Token Contents:**
```json
{
  "access_token": "ya29.c.b0Aaek...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "https://www.googleapis.com/auth/pubsub"
}
```

**Token Validation:**
1. **Signature**: Token is signed by Google (cannot be forged)
2. **Expiration**: Token expires after 1 hour (security)
3. **Scopes**: Token includes what permissions it grants
4. **Identity**: Token includes service account identity

**Automatic Refresh:**
- Tokens are automatically refreshed before expiration
- No manual intervention needed
- Seamless for applications

---

## 📊 Complete Authentication Flow in Your Application

### Example 1: Discovery Function → Pub/Sub

**Step-by-Step:**

```python
# 1. Discovery Function code (cloud_functions/discovery/main.py)
def publish_discovery_event(project_id, storage_path, results):
    publisher = pubsub_v1.PublisherClient()  # ← Step 1: Create client
    topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
    
    # Step 2: Publish (authentication happens automatically)
    future = publisher.publish(topic_path, data)
    message_id = future.result()
```

**Behind the Scenes:**

```
1. PublisherClient() initializes
   ↓
2. Detects running in GCP environment
   ↓
3. Requests token from metadata server:
   GET http://metadata.google.internal/computeMetadata/v1/
       instance/service-accounts/default/token
       ?scopes=https://www.googleapis.com/auth/pubsub
   ↓
4. Metadata server validates:
   - Is this a valid Cloud Function? ✅
   - What service account? 16418516910-compute@developer.gserviceaccount.com
   - Does it have pubsub.publisher role? ✅ (from IAM)
   ↓
5. Metadata server issues token:
   {
     "access_token": "ya29.c.b0Aaek...",
     "expires_in": 3600
   }
   ↓
6. PublisherClient uses token:
   POST https://pubsub.googleapis.com/v1/projects/vendor-risk-digital-twin/topics/vendor-discovery-events:publish
   Headers:
     Authorization: Bearer ya29.c.b0Aaek...
   ↓
7. Pub/Sub validates token:
   - Token signature valid? ✅
   - Token not expired? ✅
   - Service account has pubsub.publisher? ✅
   ↓
8. Pub/Sub grants access:
   ✅ Message published (message_id: 1234567890)
```

---

### Example 2: Simulation Service → Secret Manager

**Step-by-Step:**

```python
# Simulation Service code (cloud_run/simulation-service/app.py)
from scripts.gcp.gcp_secrets import get_secret

# Get Neo4j credentials
neo4j_uri = get_secret('neo4j-uri')
```

**Behind the Scenes:**

```
1. get_secret() called
   ↓
2. Google Cloud Secret Manager client initializes
   ↓
3. Requests token from metadata server:
   GET http://metadata.google.internal/computeMetadata/v1/
       instance/service-accounts/default/token
       ?scopes=https://www.googleapis.com/auth/cloud-platform
   ↓
4. Metadata server validates:
   - Is this a valid Cloud Run service? ✅
   - What service account? 16418516910-compute@developer.gserviceaccount.com
   - Does it have secretmanager.secretAccessor role? ✅ (from IAM)
   ↓
5. Metadata server issues token
   ↓
6. Secret Manager client uses token:
   GET https://secretmanager.googleapis.com/v1/projects/vendor-risk-digital-twin/secrets/neo4j-uri/versions/latest:access
   Headers:
     Authorization: Bearer ya29.c.b0Aaek...
   ↓
7. Secret Manager validates token and grants access
   ↓
8. Returns secret value: "neo4j+s://xxxxx.databases.neo4j.io"
```

---

## 🔐 Security Properties

### 1. **No Credentials on Disk**

**Traditional Approach (Insecure):**
```python
# ❌ BAD: Credentials stored in code or files
with open('service-account-key.json') as f:
    credentials = json.load(f)
```

**Metadata Service Approach (Secure):**
```python
# ✅ GOOD: No credentials stored
# Metadata service provides tokens automatically
publisher = pubsub_v1.PublisherClient()  # No key file needed!
```

**Why This Matters:**
- **No credential theft**: No keys to steal from disk
- **Automatic rotation**: Tokens expire and refresh
- **Audit trail**: All token requests logged

---

### 2. **Token Expiration**

**Security Feature:**
- Tokens expire after **1 hour** (typical)
- Automatically refreshed before expiration
- If token is stolen, it's only valid for 1 hour

**Example:**
```json
{
  "access_token": "ya29.c.b0Aaek...",
  "expires_in": 3600,  // 1 hour
  "token_type": "Bearer"
}
```

**After 1 hour:**
- Token becomes invalid
- New token automatically requested
- Old token cannot be reused

---

### 3. **Scope Limitation**

**Tokens Include Scopes:**
```json
{
  "access_token": "ya29.c.b0Aaek...",
  "scope": "https://www.googleapis.com/auth/pubsub"
}
```

**What This Means:**
- Token can only be used for Pub/Sub operations
- Cannot be used for other services (e.g., BigQuery)
- **Principle of least privilege** enforced

---

### 4. **Metadata Server Isolation**

**Security Feature:**
- Metadata server only accessible from **within the host**
- Cannot be accessed from internet
- Prevents external attacks

**Example:**
```bash
# From inside Cloud Function (works):
curl http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# From your laptop (fails):
curl http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
# ❌ Connection refused (not accessible from internet)
```

---

## 🌐 Cross-Cloud Comparison

### GCP (Your Application)

**Metadata Service:**
- Endpoint: `metadata.google.internal` (169.254.169.254)
- Provides: OAuth 2.0 access tokens
- Identity: Service accounts

**Example:**
```python
# GCP: Automatic authentication
publisher = pubsub_v1.PublisherClient()  # Uses metadata service
```

---

### AWS (Equivalent)

**Metadata Service:**
- Endpoint: `169.254.169.254` (Instance Metadata Service - IMDS)
- Provides: Temporary credentials (STS tokens)
- Identity: IAM roles

**Example:**
```python
# AWS: Automatic authentication
s3_client = boto3.client('s3')  # Uses IMDS
```

---

### Azure (Equivalent)

**Metadata Service:**
- Endpoint: `169.254.169.254` (Instance Metadata Service - IMDS)
- Provides: Access tokens
- Identity: Managed identities

**Example:**
```python
# Azure: Automatic authentication
blob_client = BlobServiceClient(...)  # Uses IMDS
```

---

### SPIFFE (Cross-Cloud Standard)

**SPIFFE Identity:**
- Works across **all clouds**
- Standard format: `spiffe://trust-domain/workload-id`
- Can be used for mutual TLS (mTLS)

**Example:**
```
GCP Service: spiffe://vendor-risk-digital-twin.iam.gserviceaccount.com/discovery-function
AWS Service: spiffe://vendor-risk-digital-twin.iam.gserviceaccount.com/discovery-function
Azure Service: spiffe://vendor-risk-digital-twin.iam.gserviceaccount.com/discovery-function
```

**Benefit:** Same identity standard across all clouds!

---

## 📋 Summary: The Complete Picture

### Authentication Sequence

```
1. Host (Cloud Function/Cloud Run) needs to access cloud service
   ↓
2. Host requests token from Metadata Service
   ↓
3. Metadata Service validates host identity (service account)
   ↓
4. Metadata Service checks IAM roles (what permissions host has)
   ↓
5. Metadata Service issues OAuth 2.0 access token
   ↓
6. Host uses token to authenticate to cloud service
   ↓
7. Cloud service validates token (signature, expiration, permissions)
   ↓
8. Cloud service grants access
```

### Component Relationships

```
┌─────────────┐
│    Host     │ (Cloud Function/Cloud Run)
│  (Service   │
│  Account)   │
└──────┬──────┘
       │
       │ Requests token
       ↓
┌──────────────────┐
│ Metadata Service │ (metadata.google.internal)
│  - Validates     │
│  - Issues tokens │
└──────┬───────────┘
       │
       │ Returns token
       ↓
┌─────────────┐
│    Host     │
│  (Uses      │
│   token)    │
└──────┬──────┘
       │
       │ Authenticates with token
       ↓
┌──────────────────┐
│  Cloud Service   │ (Pub/Sub, Secret Manager, BigQuery)
│  - Validates     │
│  - Grants access │
└──────────────────┘
```

### Identity Standards

**Current (GCP Native):**
- Service accounts: `16418516910-compute@developer.gserviceaccount.com`
- GCP-specific format

**Future (SPIFFE):**
- SPIFFE identities: `spiffe://trust-domain/workload-id`
- Cross-cloud standard
- Works with GCP, AWS, Azure

---

## 🎓 Key Takeaways for Cloud Security Practice

### 1. **Metadata Services are Critical**
- Provide secure credential management
- No credentials stored on disk
- Automatic token rotation

### 2. **Host Identity Matters**
- Service accounts identify hosts
- IAM roles define permissions
- Identity is immutable (part of host config)

### 3. **Token-Based Authentication**
- OAuth 2.0 access tokens
- Short-lived (1 hour typical)
- Scope-limited (principle of least privilege)

### 4. **SPIFFE Enables Cross-Cloud**
- Standard identity format
- Works across GCP, AWS, Azure
- Enables workload identity portability

### 5. **Security Properties**
- No credentials on disk
- Token expiration
- Scope limitation
- Metadata server isolation

---

## 🔍 Practice Question Answer

**Question:** Explain the authentication sequence for a host (VM or container) to another cloud service and related relationships between the host, metadata services for authentication that implement identity standards like SPIFFE, and other cloud services.

**Answer:**

**Authentication Sequence:**
1. Host (VM/container) needs to access cloud service (e.g., Pub/Sub)
2. Host requests access token from metadata service (e.g., `metadata.google.internal`)
3. Metadata service validates host identity (service account) and IAM roles
4. Metadata service issues OAuth 2.0 access token
5. Host uses token to authenticate to cloud service
6. Cloud service validates token (signature, expiration, permissions)
7. Cloud service grants access

**Component Relationships:**
- **Host**: Has immutable service account identity assigned
- **Metadata Service**: Provides tokens without storing credentials on disk
- **Cloud Service**: Validates tokens and enforces IAM permissions
- **SPIFFE**: Standard identity format enabling cross-cloud workload identity

**Security Properties:**
- No credentials on disk (metadata service provides tokens)
- Token expiration (typically 1 hour)
- Scope limitation (principle of least privilege)
- Metadata server isolation (only accessible from host)

**In Your Application:**
- Discovery Function uses metadata service to get token for Pub/Sub
- Simulation Service uses metadata service to get token for Secret Manager
- All authentication is automatic (no manual credential management)

---

**Related Documentation:**
- [Why IAM is Critical](./why_iam_is_critical.md) - IAM fundamentals
- [IAM Service Accounts Guide](./iam_service_accounts_guide.md) - Service account setup
- [GCP Metadata Server Documentation](https://cloud.google.com/compute/docs/metadata/overview)
