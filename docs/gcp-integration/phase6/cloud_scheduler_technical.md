# Cloud Scheduler Technical Documentation

**How Cloud Scheduler Works in Vendor Risk Digital Twin**

This document explains the technical implementation of Cloud Scheduler in our codebase, including code flow, configuration, and integration points.

---

## Table of Contents

1. [Overview](#overview)
2. [Benefits of Cloud Scheduler](#benefits-of-cloud-scheduler)
3. [Architecture & Flow](#architecture--flow)
4. [Code Components](#code-components)
5. [Configuration Details](#configuration-details)
6. [Execution Flow](#execution-flow)
7. [Integration Points](#integration-points)
8. [Verification & Monitoring](#verification--monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Cloud Scheduler automates the vendor dependency discovery process by triggering the Discovery Cloud Function on a daily schedule. This eliminates the need for manual intervention and ensures the Neo4j graph database stays up-to-date with the latest vendor dependencies.

### Key Components

- **Cloud Scheduler Job**: `daily-vendor-discovery`
- **Target**: Discovery Cloud Function (`vendor-discovery`)
- **Schedule**: Daily at 2:00 AM (America/Los_Angeles)
- **Method**: HTTP POST
- **Setup Script**: `scripts/setup_cloud_scheduler.sh`

---

## Benefits of Cloud Scheduler

Cloud Scheduler provides significant value to the Vendor Risk Digital Twin project by automating critical discovery processes. Here are the key benefits in the context of our system:

### 1. **Automated Continuous Monitoring**

**Problem Without Cloud Scheduler**:
- Manual discovery runs require human intervention
- Risk of forgetting to run discovery scans
- Inconsistent update frequency leads to stale data
- Neo4j graph becomes outdated, reducing simulation accuracy

**Solution With Cloud Scheduler**:
- ✅ **Zero-touch automation**: Discovery runs automatically every day at 2 AM
- ✅ **Consistent updates**: Neo4j graph always reflects current vendor dependencies
- ✅ **No human dependency**: System operates independently
- ✅ **Reliable cadence**: Daily scans ensure rapid detection of new vendor integrations

**Business Impact**: 
- Reduces operational overhead by eliminating manual tasks
- Ensures risk assessments are always based on current data
- Enables proactive risk management instead of reactive responses

---

### 2. **Real-Time Vendor Risk Visibility**

**Problem Without Cloud Scheduler**:
- New vendor dependencies go undetected for days or weeks
- Risk assessments based on outdated dependency maps
- Compliance gaps emerge when new services are deployed
- Business processes change but risk models don't reflect changes

**Solution With Cloud Scheduler**:
- ✅ **Daily discovery**: New vendor dependencies detected within 24 hours
- ✅ **Automatic graph updates**: Neo4j reflects changes immediately after discovery
- ✅ **Current risk posture**: Simulations always use latest dependency data
- ✅ **Rapid response**: Risk teams can react to new dependencies quickly

**Business Impact**:
- Faster identification of new vendor risks
- More accurate risk simulations and impact assessments
- Better compliance posture through continuous monitoring
- Reduced time-to-insight for risk management decisions

---

### 3. **Cost-Effective Automation**

**Problem Without Cloud Scheduler**:
- Manual discovery requires developer/operations time
- Inconsistent execution leads to missed scans
- Need for monitoring/alerting infrastructure to ensure scans run
- Potential for human error in scheduling or execution

**Solution With Cloud Scheduler**:
- ✅ **Low cost**: ~$3/month for daily executions (30 executions × $0.10)
- ✅ **No infrastructure**: Fully managed service, no servers to maintain
- ✅ **Built-in reliability**: GCP handles scheduling, retries, and error handling
- ✅ **No operational overhead**: No need to monitor cron jobs or scheduled tasks

**Cost Comparison**:
```
Manual Approach:
- Developer time: ~15 min/day × 30 days = 7.5 hours/month
- At $100/hour: $750/month in developer time
- Infrastructure monitoring: Additional costs

Cloud Scheduler:
- Service cost: ~$3/month
- Zero operational overhead
- Savings: ~$747/month
```

**Business Impact**:
- 99.6% cost reduction compared to manual execution
- Frees up developer time for higher-value work
- Predictable, low-cost operational model

---

### 4. **Integration with Event-Driven Architecture**

**Problem Without Cloud Scheduler**:
- Discovery runs in isolation
- Manual coordination required between discovery and graph loading
- Risk of discovery completing but graph not being updated
- Difficult to track end-to-end automation flow

**Solution With Cloud Scheduler**:
- ✅ **Seamless integration**: Triggers Discovery Function via HTTP POST
- ✅ **Event-driven flow**: Discovery → Pub/Sub → Graph Loader → Neo4j
- ✅ **Automatic chaining**: Each step triggers the next automatically
- ✅ **Full traceability**: Cloud Logging tracks entire automation chain

**Technical Benefits**:
- Leverages existing Pub/Sub infrastructure (Phase 5)
- No code changes needed to existing functions
- Decoupled architecture: Scheduler doesn't need to know about downstream steps
- Easy to extend: Add more downstream consumers without changing scheduler

---

### 5. **Reliability and Fault Tolerance**

**Problem Without Cloud Scheduler**:
- Manual execution can fail silently
- No automatic retries if discovery fails
- Difficult to track execution history
- No built-in error handling or alerting

**Solution With Cloud Scheduler**:
- ✅ **Built-in retries**: Automatic retry on transient failures
- ✅ **Execution history**: Complete audit trail of all job executions
- ✅ **Error handling**: Failed executions logged and visible in Cloud Logging
- ✅ **Monitoring**: Integration with Cloud Monitoring for alerts
- ✅ **High availability**: GCP-managed service with 99.9% SLA

**Operational Benefits**:
- Reduced risk of missed discovery scans
- Automatic recovery from transient failures
- Complete visibility into automation health
- Proactive alerting when issues occur

---

### 6. **Scalability and Flexibility**

**Problem Without Cloud Scheduler**:
- Fixed schedule requires code changes to modify
- Difficult to add multiple discovery schedules
- No easy way to trigger discovery on-demand
- Limited scheduling options

**Solution With Cloud Scheduler**:
- ✅ **Flexible scheduling**: Easy to modify schedule without code changes
- ✅ **Multiple jobs**: Can create additional jobs for different schedules
- ✅ **On-demand execution**: Manual trigger available for testing/debugging
- ✅ **Cron-based**: Standard cron syntax for complex schedules

**Use Cases Enabled**:
- **Daily discovery**: Current implementation (2 AM daily)
- **Weekly compliance reports**: Could add Monday 9 AM job
- **Monthly risk assessments**: Could add 1st of month job
- **Emergency scans**: Manual trigger for immediate discovery
- **Multi-region**: Different schedules for different regions

---

### 7. **Compliance and Audit Readiness**

**Problem Without Cloud Scheduler**:
- No audit trail of when discovery was run
- Difficult to prove continuous monitoring
- Manual processes don't meet compliance requirements
- No documentation of discovery frequency

**Solution With Cloud Scheduler**:
- ✅ **Audit trail**: Complete execution history in Cloud Logging
- ✅ **Compliance documentation**: Scheduled jobs demonstrate continuous monitoring
- ✅ **Automated evidence**: Logs prove discovery runs without manual intervention
- ✅ **Reproducible process**: Standardized, documented automation

**Compliance Benefits**:
- **SOC 2**: Demonstrates continuous monitoring controls
- **ISO 27001**: Shows automated risk assessment processes
- **NIST CSF**: Proves continuous monitoring capabilities
- **Internal audits**: Clear evidence of operational processes

---

### 8. **Developer Experience and Maintainability**

**Problem Without Cloud Scheduler**:
- Developers must remember to run discovery manually
- Inconsistent execution across team members
- Difficult to test automation flows
- No standardized way to trigger discovery

**Solution With Cloud Scheduler**:
- ✅ **Self-service**: Any team member can trigger discovery via scheduler
- ✅ **Consistent execution**: Same process for all team members
- ✅ **Easy testing**: Manual trigger allows testing without waiting for schedule
- ✅ **Simple setup**: One script to configure entire automation

**Developer Benefits**:
- Reduced cognitive load (no need to remember manual steps)
- Faster onboarding (automation is self-documenting)
- Easier debugging (can trigger on-demand for testing)
- Better collaboration (shared automation, not individual manual processes)

---

### 9. **Integration with GCP Ecosystem**

**Problem Without Cloud Scheduler**:
- Need external scheduling solution (cron, external services)
- Additional infrastructure to manage
- Potential security/compliance concerns with external services
- Integration complexity with GCP services

**Solution With Cloud Scheduler**:
- ✅ **Native GCP service**: No external dependencies
- ✅ **Integrated security**: Uses GCP IAM for authentication
- ✅ **Seamless integration**: Works directly with Cloud Functions, Pub/Sub, etc.
- ✅ **Unified monitoring**: All logs/metrics in Cloud Logging/Monitoring

**Architectural Benefits**:
- Simpler architecture (fewer moving parts)
- Better security (no external services)
- Unified observability (all in GCP)
- Easier compliance (all GCP services)

---

### 10. **Future-Proofing and Extensibility**

**Problem Without Cloud Scheduler**:
- Hard to add new automated workflows
- Each new automation requires separate infrastructure
- Difficult to coordinate multiple automated processes
- Limited extensibility

**Solution With Cloud Scheduler**:
- ✅ **Easy extension**: Add new jobs for new automation needs
- ✅ **Centralized scheduling**: All automation in one place
- ✅ **Standardized approach**: Same pattern for all scheduled tasks
- ✅ **Scalable**: Can handle hundreds of jobs if needed

**Future Possibilities**:
- Weekly compliance report generation
- Monthly risk assessment automation
- Quarterly framework reviews
- Custom schedules for different business units
- Integration with external systems via HTTP triggers

---

## Summary of Benefits

| Benefit Category | Impact | Value |
|-----------------|--------|-------|
| **Automation** | Eliminates manual tasks | 7.5 hours/month saved |
| **Cost** | Low operational cost | ~$3/month vs $750/month manual |
| **Reliability** | Built-in retries and monitoring | 99.9% SLA |
| **Compliance** | Audit trail and documentation | Meets SOC 2, ISO 27001, NIST requirements |
| **Timeliness** | Daily updates | 24-hour detection of new dependencies |
| **Scalability** | Easy to extend | Can add unlimited jobs |
| **Developer Experience** | Self-service and consistent | Reduced cognitive load |

---

## Architecture & Flow

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Scheduler (GCP Service)                 │
│  Job: daily-vendor-discovery                                    │
│  Schedule: 0 2 * * * (2 AM daily)                              │
│  Timezone: America/Los_Angeles                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST
                             │ Body: {"project_id": "vendor-risk-digital-twin"}
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Discovery Cloud Function                            │
│  Function: vendor-discovery                                    │
│  URL: https://vendor-discovery-wearla5naa-uc.a.run.app/        │
│  Entry Point: discover_vendors(request)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ 1. Scans GCP resources
                             │ 2. Extracts vendor dependencies
                             │ 3. Stores results in Cloud Storage
                             │ 4. Publishes to Pub/Sub
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Pub/Sub Topic                                │
│  Topic: vendor-discovery-events                                │
│  Message: Discovery results JSON                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Eventarc Trigger
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Graph Loader Cloud Function                        │
│  Function: graph-loader                                         │
│  Entry Point: load_discovery_to_neo4j(event, context)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Loads data into Neo4j
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Neo4j Graph Database                         │
│  Updated with latest vendor dependencies                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Components

### 1. Setup Script: `scripts/setup_cloud_scheduler.sh`

**Purpose**: Creates and configures the Cloud Scheduler job.

**Key Code Sections**:

```bash
# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"
DISCOVERY_FUNCTION_URL="https://vendor-discovery-wearla5naa-uc.a.run.app"
JOB_NAME="daily-vendor-discovery"

# Enable Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID

# Create/Update Scheduler Job
gcloud scheduler jobs create http $JOB_NAME \
    --location=$REGION \
    --schedule="0 2 * * *" \
    --uri="$DISCOVERY_FUNCTION_URL" \
    --http-method=POST \
    --message-body='{"project_id": "'$PROJECT_ID'"}' \
    --headers="Content-Type=application/json" \
    --time-zone="America/Los_Angeles" \
    --description="Daily automated vendor dependency discovery scan at 2 AM" \
    --project=$PROJECT_ID
```

**What This Does**:
- Enables the Cloud Scheduler API if not already enabled
- Creates an HTTP-triggered scheduler job
- Configures the job to POST to the Discovery Function URL
- Sets the schedule to run daily at 2:00 AM
- Includes the project ID in the request body

**Location**: `scripts/setup_cloud_scheduler.sh`

---

### 2. Discovery Function: `cloud_functions/discovery/main.py`

**Purpose**: Receives the HTTP POST from Cloud Scheduler and runs the discovery process.

**Key Code Sections**:

```python
def discover_vendors(request):
    """
    Cloud Function entry point for HTTP triggers
    
    Args:
        request: Flask request object (for HTTP triggers)
    
    Returns:
        HTTP response with discovery results
    """
    try:
        # Get project ID from environment or request
        project_id = os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        
        if not project_id:
            # Try to get from request body (Cloud Scheduler sends this)
            if hasattr(request, 'get_json'):
                request_data = request.get_json(silent=True)
                if request_data:
                    project_id = request_data.get('project_id')
            
            if not project_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'GCP_PROJECT_ID or project_id parameter required'})
                }
        
        logger.info(f"Starting vendor discovery for project: {project_id}")
        
        # Run discovery
        results = run_discovery(project_id)
        
        # Publish to Pub/Sub
        publish_discovery_event(project_id, results)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'vendors_found': len(results.get('vendors', [])),
                'message': 'Discovery complete'
            })
        }
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**How Cloud Scheduler Triggers It**:

1. Cloud Scheduler sends HTTP POST to the function URL
2. Request body contains: `{"project_id": "vendor-risk-digital-twin"}`
3. Function extracts `project_id` from request body
4. Function calls `run_discovery(project_id)` to scan GCP resources
5. Function publishes results to Pub/Sub via `publish_discovery_event()`
6. Function returns success response

**Location**: `cloud_functions/discovery/main.py`

---

### 3. Pub/Sub Integration: `cloud_functions/discovery/main.py`

**Purpose**: Publishes discovery events to trigger the Graph Loader.

**Key Code**:

```python
def publish_discovery_event(project_id: str, discovery_results: dict):
    """
    Publish discovery completion event to Pub/Sub
    
    Args:
        project_id: GCP project ID
        discovery_results: Discovery results dictionary
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
        
        message_data = json.dumps({
            'project_id': project_id,
            'timestamp': datetime.utcnow().isoformat(),
            'vendors_found': len(discovery_results.get('vendors', [])),
            'storage_path': discovery_results.get('storage_path'),
            'status': 'completed'
        }).encode('utf-8')
        
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        logger.info(f"Published discovery event to Pub/Sub: {message_id}")
    except Exception as e:
        logger.error(f"Failed to publish to Pub/Sub: {e}", exc_info=True)
```

**What Happens**:
- Discovery Function publishes a message to `vendor-discovery-events` topic
- Message contains discovery metadata (project_id, timestamp, vendor count, storage path)
- Graph Loader Function is automatically triggered via Eventarc subscription

**Location**: `cloud_functions/discovery/main.py`

---

### 4. Graph Loader Function: `cloud_functions/graph_loader/main.py`

**Purpose**: Automatically triggered by Pub/Sub to load discovery results into Neo4j.

**Key Code**:

```python
def load_discovery_to_neo4j(event, context):
    """
    Cloud Function triggered by Pub/Sub event
    
    Args:
        event: Pub/Sub event containing discovery results
        context: Cloud Functions context
    """
    try:
        # Decode Pub/Sub message
        message_data = base64.b64decode(event['data']).decode('utf-8')
        discovery_event = json.loads(message_data)
        
        project_id = discovery_event['project_id']
        storage_path = discovery_event['storage_path']
        
        logger.info(f"Loading discovery results from {storage_path} into Neo4j")
        
        # Download discovery results from Cloud Storage
        discovery_results = download_from_storage(storage_path)
        
        # Load into Neo4j
        load_to_neo4j(discovery_results)
        
        logger.info("Successfully loaded discovery results into Neo4j")
        
    except Exception as e:
        logger.error(f"Failed to load discovery to Neo4j: {e}", exc_info=True)
        raise
```

**How It's Triggered**:
- Eventarc automatically creates a subscription to `vendor-discovery-events` topic
- When Discovery Function publishes a message, Eventarc triggers Graph Loader
- Graph Loader downloads results from Cloud Storage and loads into Neo4j

**Location**: `cloud_functions/graph_loader/main.py`

---

## Configuration Details

### Cloud Scheduler Job Configuration

**Job Name**: `daily-vendor-discovery`

**Configuration**:
```yaml
Location: us-central1
Schedule: "0 2 * * *"  # Cron expression: Daily at 2:00 AM
Timezone: America/Los_Angeles
HTTP Method: POST
Target URL: https://vendor-discovery-wearla5naa-uc.a.run.app/
Request Body: {"project_id": "vendor-risk-digital-twin"}
Headers:
  Content-Type: application/json
  User-Agent: Google-Cloud-Scheduler
State: ENABLED
```

### Cron Schedule Format

The schedule `0 2 * * *` means:
- `0` - Minute (0th minute)
- `2` - Hour (2 AM)
- `*` - Day of month (every day)
- `*` - Month (every month)
- `*` - Day of week (every day of week)

**Other Schedule Examples**:
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1` - Every Monday at 9 AM
- `0 0 1 * *` - First day of every month at midnight

---

## Execution Flow

### Step-by-Step Execution

1. **Cloud Scheduler Triggers (2:00 AM)**
   ```
   Cloud Scheduler → HTTP POST → Discovery Function URL
   Body: {"project_id": "vendor-risk-digital-twin"}
   ```

2. **Discovery Function Receives Request**
   ```python
   # In cloud_functions/discovery/main.py
   def discover_vendors(request):
       project_id = request.get_json().get('project_id')
       # ... runs discovery ...
   ```

3. **Discovery Process Runs**
   ```python
   # Scans GCP resources
   - Cloud Functions
   - Cloud Run services
   - Extracts environment variables
   - Matches vendor patterns
   - Stores results in Cloud Storage
   ```

4. **Pub/Sub Event Published**
   ```python
   # In cloud_functions/discovery/main.py
   publish_discovery_event(project_id, results)
   # → Publishes to vendor-discovery-events topic
   ```

5. **Graph Loader Triggered**
   ```python
   # In cloud_functions/graph_loader/main.py
   def load_discovery_to_neo4j(event, context):
       # Eventarc automatically triggers this
       # Downloads from Cloud Storage
       # Loads into Neo4j
   ```

6. **Neo4j Updated**
   ```
   Graph Loader → Creates/Updates nodes and relationships
   → Neo4j graph reflects latest vendor dependencies
   ```

### Timeline Example

```
2:00:00 AM - Cloud Scheduler triggers
2:00:01 AM - Discovery Function starts
2:00:15 AM - Discovery completes, publishes to Pub/Sub
2:00:16 AM - Graph Loader triggered
2:00:30 AM - Neo4j graph updated
2:00:31 AM - Complete automation cycle finished
```

---

## Integration Points

### 1. Cloud Scheduler → Discovery Function

**Integration Type**: HTTP POST

**Request Format**:
```json
POST https://vendor-discovery-wearla5naa-uc.a.run.app/
Content-Type: application/json

{
  "project_id": "vendor-risk-digital-twin"
}
```

**Response Format**:
```json
{
  "statusCode": 200,
  "body": {
    "status": "success",
    "vendors_found": 4,
    "message": "Discovery complete"
  }
}
```

### 2. Discovery Function → Pub/Sub

**Topic**: `vendor-discovery-events`

**Message Format**:
```json
{
  "project_id": "vendor-risk-digital-twin",
  "timestamp": "2025-11-29T10:00:00.000Z",
  "vendors_found": 4,
  "storage_path": "gs://bucket/discoveries/20251129_100000_discovery.json",
  "status": "completed"
}
```

### 3. Pub/Sub → Graph Loader

**Integration Type**: Eventarc (automatic Pub/Sub trigger)

**Event Format**:
```json
{
  "data": "base64-encoded-message",
  "attributes": {
    "eventType": "google.cloud.pubsub.topic.v1.messagePublished"
  }
}
```

---

## Verification & Monitoring

### Check Scheduler Job Status

```bash
# List all scheduler jobs
gcloud scheduler jobs list --location=us-central1 --project=vendor-risk-digital-twin

# Describe specific job
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin \
  --format="yaml(name,schedule,timeZone,state,httpTarget)"
```

**Expected Output**:
```yaml
name: projects/vendor-risk-digital-twin/locations/us-central1/jobs/daily-vendor-discovery
schedule: 0 2 * * *
state: ENABLED
timeZone: America/Los_Angeles
httpTarget:
  uri: https://vendor-discovery-wearla5naa-uc.a.run.app/
  httpMethod: POST
```

### Check Execution History

```bash
# View last execution time
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin \
  --format="value(lastAttemptTime)"
```

### Monitor Discovery Function Logs

```bash
# View recent logs
gcloud functions logs read vendor-discovery \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=20
```

**Expected Log Entries**:
```
INFO - Starting vendor discovery for project: vendor-risk-digital-twin
INFO - Discovering Cloud Functions...
INFO - Discovering Cloud Run services...
INFO - Discovery complete. Found 4 vendors
INFO - Published discovery event to Pub/Sub: <message_id>
```

### Monitor Pub/Sub Delivery

```bash
# Check subscription status
gcloud pubsub subscriptions describe discovery-to-neo4j-subscription \
  --project=vendor-risk-digital-twin \
  --format="yaml(name,numUndeliveredMessages)"
```

**Expected**: `numUndeliveredMessages: 0` (messages are processed quickly)

### Test Manually

```bash
# Trigger job immediately (for testing)
gcloud scheduler jobs run daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin
```

---

## Troubleshooting

### Issue: Scheduler Job Not Running

**Symptoms**:
- Job shows `state: ENABLED` but never executes
- No logs in Discovery Function at scheduled time

**Diagnosis**:
```bash
# Check job configuration
gcloud scheduler jobs describe daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin

# Check for errors
gcloud logging read "resource.type=cloud_scheduler_job" \
  --limit=10 \
  --project=vendor-risk-digital-twin
```

**Common Causes**:
1. **Timezone mismatch**: Job scheduled in wrong timezone
2. **API not enabled**: Cloud Scheduler API not enabled
3. **Permissions**: Service account lacks permissions

**Solutions**:
```bash
# Verify API is enabled
gcloud services list --enabled --project=vendor-risk-digital-twin \
  --filter="name:cloudscheduler.googleapis.com"

# Update timezone if needed
gcloud scheduler jobs update http daily-vendor-discovery \
  --location=us-central1 \
  --time-zone="America/Los_Angeles" \
  --project=vendor-risk-digital-twin
```

---

### Issue: Discovery Function Returns Error

**Symptoms**:
- Scheduler triggers but Discovery Function fails
- Error logs in Discovery Function

**Diagnosis**:
```bash
# Check Discovery Function logs
gcloud functions logs read vendor-discovery \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=50
```

**Common Causes**:
1. **Missing project_id**: Request body not parsed correctly
2. **GCP permissions**: Function lacks permissions to scan resources
3. **Function timeout**: Discovery takes too long

**Solutions**:
```bash
# Test function directly
curl -X POST "https://vendor-discovery-wearla5naa-uc.a.run.app/" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "vendor-risk-digital-twin"}'

# Check function configuration
gcloud functions describe vendor-discovery \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin
```

---

### Issue: Pub/Sub Messages Not Delivered

**Symptoms**:
- Discovery completes but Graph Loader never triggered
- Messages stuck in Pub/Sub subscription

**Diagnosis**:
```bash
# Check undelivered messages
gcloud pubsub subscriptions describe discovery-to-neo4j-subscription \
  --project=vendor-risk-digital-twin \
  --format="value(numUndeliveredMessages)"

# Check Graph Loader logs
gcloud functions logs read graph-loader \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=20
```

**Common Causes**:
1. **Eventarc not configured**: Graph Loader not subscribed to topic
2. **Function deployment issue**: Graph Loader function not deployed
3. **Permissions**: Eventarc service account lacks permissions

**Solutions**:
```bash
# Verify Eventarc subscription exists
gcloud eventarc triggers list \
  --location=us-central1 \
  --project=vendor-risk-digital-twin

# Check Graph Loader function
gcloud functions describe graph-loader \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin
```

---

### Issue: Neo4j Not Updated

**Symptoms**:
- All previous steps succeed but Neo4j unchanged
- Graph Loader logs show errors

**Diagnosis**:
```bash
# Check Graph Loader logs
gcloud functions logs read graph-loader \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=50

# Verify Neo4j connection
# (Check Graph Loader environment variables)
gcloud functions describe graph-loader \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --format="value(serviceConfig.environmentVariables)"
```

**Common Causes**:
1. **Neo4j credentials**: Missing or incorrect Neo4j credentials
2. **Neo4j connection**: Network/firewall issues
3. **Data format**: Discovery results format incompatible

**Solutions**:
```bash
# Verify Neo4j credentials in Secret Manager
gcloud secrets versions access latest \
  --secret=neo4j-uri \
  --project=vendor-risk-digital-twin

# Test Neo4j connection manually
# (Use scripts/test_neo4j_connection.py)
```

---

## Code References

### Key Files

1. **Setup Script**: `scripts/setup_cloud_scheduler.sh`
   - Creates and configures Cloud Scheduler job

2. **Discovery Function**: `cloud_functions/discovery/main.py`
   - Entry point: `discover_vendors(request)`
   - Handles HTTP POST from Cloud Scheduler
   - Publishes to Pub/Sub

3. **Graph Loader Function**: `cloud_functions/graph_loader/main.py`
   - Entry point: `load_discovery_to_neo4j(event, context)`
   - Triggered by Pub/Sub via Eventarc
   - Loads data into Neo4j

4. **Pub/Sub Setup**: `scripts/setup_pubsub.py`
   - Creates `vendor-discovery-events` topic
   - Sets up subscriptions

### Related Documentation

- **Phase 6 Guide**: `docs/phase6_cloud_scheduler.md`
- **Pub/Sub Documentation**: `docs/pubsub_explained.md`
- **GCP Integration Roadmap**: `docs/gcp_integration_roadmap.md`

---

## Summary

Cloud Scheduler provides fully automated vendor dependency discovery:

1. **Scheduler triggers** Discovery Function daily at 2 AM
2. **Discovery Function** scans GCP and publishes to Pub/Sub
3. **Graph Loader** automatically triggered to update Neo4j
4. **Zero manual intervention** required

The entire flow is event-driven and serverless, ensuring scalability and reliability.

---

**Last Updated**: 2025-11-29  
**Status**: ✅ Operational

