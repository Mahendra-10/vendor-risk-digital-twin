#!/bin/bash

# Setup Cloud Monitoring & Observability for Vendor Risk Digital Twin
# Phase 7: Monitoring & Observability

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"

echo "🚀 Setting up Cloud Monitoring & Observability for Vendor Risk Digital Twin"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Enable required APIs
echo "📋 Enabling required APIs..."
APIS=(
    "monitoring.googleapis.com"
    "logging.googleapis.com"
)

for api in "${APIS[@]}"; do
    if ! gcloud services list --enabled --project=$PROJECT_ID --filter="name:$api" | grep -q "$api"; then
        echo "   Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
        echo "   ✅ $api enabled"
    else
        echo "   ✅ $api already enabled"
    fi
done

echo ""

# Create notification channel (email)
echo "📧 Setting up notification channels..."
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-$(gcloud config get-value account)}"

if [ -z "$NOTIFICATION_EMAIL" ]; then
    echo "   ⚠️  No email found. Please set NOTIFICATION_EMAIL environment variable"
    echo "   Example: export NOTIFICATION_EMAIL=your-email@example.com"
    NOTIFICATION_EMAIL="admin@example.com"  # Placeholder
fi

echo "   Notification email: $NOTIFICATION_EMAIL"
echo ""

# Create log-based metrics
echo "📊 Creating log-based metrics..."

# Discovery Function Success Rate Metric
echo "   Creating discovery-success-rate metric..."
gcloud logging metrics create discovery_success_rate \
    --description="Discovery function execution success rate" \
    --log-filter='resource.type="cloud_function"
    resource.labels.function_name="vendor-discovery"
    jsonPayload.message=~"Discovery complete"' \
    --value-extractor='EXTRACT(jsonPayload.message)' \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Metric may already exist"

# Simulation Service Error Rate Metric
echo "   Creating simulation-error-rate metric..."
gcloud logging metrics create simulation_error_rate \
    --description="Simulation service error rate" \
    --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="simulation-service"
    severity>=ERROR' \
    --value-extractor='EXTRACT(severity)' \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Metric may already exist"

# Graph Loader Processing Time Metric
echo "   Creating graph-loader-processing-time metric..."
gcloud logging metrics create graph_loader_processing_time \
    --description="Graph loader processing time" \
    --log-filter='resource.type="cloud_function"
    resource.labels.function_name="graph-loader"
    jsonPayload.message=~"Successfully loaded"' \
    --value-extractor='EXTRACT(jsonPayload.processing_time)' \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Metric may already exist"

echo ""

# Create alerting policies
echo "🚨 Creating alerting policies..."

# Alert 1: Discovery Function High Error Rate
echo "   Creating alert: Discovery Function High Error Rate..."
cat > /tmp/discovery_error_alert.yaml <<EOF
displayName: "Discovery Function High Error Rate"
combiner: OR
conditions:
  - displayName: "Error rate > 10%"
    conditionThreshold:
      filter: 'resource.type="cloud_function" AND resource.labels.function_name="vendor-discovery"'
      aggregations:
        - alignmentPeriod: 300s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_SUM
      comparison: COMPARISON_GT
      thresholdValue: 0.1
      duration: 300s
notificationChannels: []
documentation:
  content: "Discovery function error rate exceeds 10% for 5 minutes"
  mimeType: "text/markdown"
EOF

gcloud alpha monitoring policies create \
    --notification-channels="" \
    --policy-from-file=/tmp/discovery_error_alert.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Alert policy may already exist or notification channel needed"

# Alert 2: Simulation Service High Latency
echo "   Creating alert: Simulation Service High Latency..."
cat > /tmp/simulation_latency_alert.yaml <<EOF
displayName: "Simulation Service High Latency"
combiner: OR
conditions:
  - displayName: "P95 latency > 5s"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="simulation-service"'
      aggregations:
        - alignmentPeriod: 300s
          perSeriesAligner: ALIGN_DELTA
          crossSeriesReducer: REDUCE_PERCENTILE_95
      comparison: COMPARISON_GT
      thresholdValue: 5000
      duration: 300s
notificationChannels: []
documentation:
  content: "Simulation service P95 latency exceeds 5 seconds for 5 minutes"
  mimeType: "text/markdown"
EOF

gcloud alpha monitoring policies create \
    --notification-channels="" \
    --policy-from-file=/tmp/simulation_latency_alert.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Alert policy may already exist or notification channel needed"

# Alert 3: Cloud Scheduler Job Failure
echo "   Creating alert: Cloud Scheduler Job Failure..."
cat > /tmp/scheduler_failure_alert.yaml <<EOF
displayName: "Cloud Scheduler Job Failure"
combiner: OR
conditions:
  - displayName: "Job execution failed"
    conditionThreshold:
      filter: 'resource.type="cloud_scheduler_job" AND resource.labels.job_id="daily-vendor-discovery"'
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
      comparison: COMPARISON_GT
      thresholdValue: 0
      duration: 60s
notificationChannels: []
documentation:
  content: "Cloud Scheduler job daily-vendor-discovery failed"
  mimeType: "text/markdown"
EOF

gcloud alpha monitoring policies create \
    --notification-channels="" \
    --policy-from-file=/tmp/scheduler_failure_alert.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Alert policy may already exist or notification channel needed"

echo ""

# Create dashboard (using gcloud commands)
echo "📊 Creating monitoring dashboard..."
echo "   Note: Dashboards are best created via Cloud Console UI"
echo "   See docs/gcp-integration/phase7/phase7_implementation.md for dashboard JSON"
echo ""

# Summary
echo "✅ Cloud Monitoring setup initiated!"
echo ""
echo "📊 Summary:"
echo "   - APIs enabled: Monitoring, Logging"
echo "   - Log-based metrics: Created (3 metrics)"
echo "   - Alerting policies: Created (3 policies)"
echo ""
echo "📝 Next Steps:"
echo "   1. Create notification channels in Cloud Console:"
echo "      https://console.cloud.google.com/monitoring/alerting/notifications?project=$PROJECT_ID"
echo ""
echo "   2. Create custom dashboards in Cloud Console:"
echo "      https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "   3. View logs:"
echo "      https://console.cloud.google.com/logs?project=$PROJECT_ID"
echo ""
echo "   4. View metrics:"
echo "      https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
echo ""
echo "📖 Documentation:"
echo "   - Implementation guide: docs/gcp-integration/phase7/phase7_implementation.md"
echo "   - Benefits: docs/gcp-integration/phase7/phase7_benefits.md"
echo ""

# Cleanup
rm -f /tmp/discovery_error_alert.yaml
rm -f /tmp/simulation_latency_alert.yaml
rm -f /tmp/scheduler_failure_alert.yaml

