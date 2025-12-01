# Discovery Function Pub/Sub Publishing Fix

**Date:** 2025-11-30  
**Status:** ✅ Fixed

---

## Issue

The Discovery Function was not automatically publishing discovery events to Pub/Sub, preventing Graph Loader from being triggered automatically.

## Root Cause

The Discovery Function's service account (`16418516910-compute@developer.gserviceaccount.com`) lacked the `roles/pubsub.publisher` IAM role required to publish messages to Pub/Sub topics.

**Why it was silent:**
- The `publish_discovery_event()` function catches exceptions and only logs warnings
- Discovery Function continued to run successfully (storing results in Cloud Storage)
- No error was visible in the function response
- Only warning logs were generated (which weren't being monitored)

## Solution

Granted Pub/Sub Publisher role to the Discovery Function service account:

```bash
gcloud projects add-iam-policy-binding vendor-risk-digital-twin \
  --member="serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

## Verification

### Check Permissions

```bash
# Verify service account has Pub/Sub Publisher role
gcloud projects get-iam-policy vendor-risk-digital-twin \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:16418516910-compute@developer.gserviceaccount.com" \
  --format="table(bindings.role)" | grep pubsub
```

### Test Discovery Function

```bash
# Manually trigger Discovery Function
gcloud scheduler jobs run daily-vendor-discovery \
  --location=us-central1 \
  --project=vendor-risk-digital-twin
```

### Check Logs

```bash
# Look for successful Pub/Sub publishing
gcloud functions logs read vendor-discovery \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=20 | grep -i "Published discovery event"
```

**Expected output:**
```
✅ Published discovery event to Pub/Sub: <message_id>
```

### Verify Graph Loader Triggered

```bash
# Check Graph Loader logs (should trigger automatically)
gcloud functions logs read graph-loader \
  --gen2 \
  --region=us-central1 \
  --project=vendor-risk-digital-twin \
  --limit=10
```

## Prevention

### Best Practices

1. **Check IAM Permissions During Deployment**
   - Include permission checks in deployment scripts
   - Document required IAM roles for each function

2. **Improve Error Handling**
   - Consider failing the function if Pub/Sub publishing fails (for critical workflows)
   - Or use retry logic with exponential backoff
   - Log errors at ERROR level, not just WARNING

3. **Monitor Warnings**
   - Set up alerting for WARNING level logs
   - Monitor for "Failed to publish" messages

### Recommended Code Change

Consider updating `publish_discovery_event()` to be more explicit about failures:

```python
def publish_discovery_event(project_id: str, storage_path: str, results: Dict[str, Any]) -> None:
    """
    Publish discovery completion event to Pub/Sub
    
    Args:
        project_id: GCP project ID
        storage_path: Path to results in Cloud Storage
        results: Discovery results
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
        
        # Create event message
        event_data = {
            'project_id': project_id,
            'storage_path': storage_path,
            'discovery_timestamp': results.get('discovery_timestamp', datetime.utcnow().isoformat()),
            'summary': {
                'cloud_functions': len(results.get('cloud_functions', [])),
                'cloud_run_services': len(results.get('cloud_run_services', [])),
                'vendors_found': len(results.get('vendors', []))
            }
        }
        
        # Publish message
        message_data = json.dumps(event_data).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result(timeout=10)  # Add timeout
        
        logger.info(f"✅ Published discovery event to Pub/Sub: {message_id}")
        
    except Exception as e:
        # Log at ERROR level for better visibility
        logger.error(f"❌ Failed to publish discovery event to Pub/Sub: {e}", exc_info=True)
        # Consider raising exception for critical workflows
        # raise  # Uncomment if publishing is critical
```

## Related Files

- `cloud_functions/discovery/main.py` - Discovery Function code
- `scripts/setup_pubsub.py` - Pub/Sub setup script (should include IAM permissions)
- `cloud_functions/discovery/deploy.sh` - Deployment script (should grant permissions)

## Summary

✅ **Fixed:** Discovery Function now has Pub/Sub Publisher permissions  
✅ **Verified:** Function can publish to `vendor-discovery-events` topic  
✅ **Result:** Graph Loader will now trigger automatically after Discovery completes  

**Next Steps:**
- Monitor Discovery Function logs for successful publishing
- Verify Graph Loader triggers automatically
- Consider updating deployment scripts to include IAM permission setup

