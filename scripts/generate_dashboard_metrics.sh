#!/bin/bash
# Script to generate multiple data points for dashboard screenshot
# This triggers discovery and simulations to create more metrics

echo "🚀 Generating metrics for dashboard screenshot..."
echo ""

# Trigger Discovery Function 3 times
echo "📡 Triggering Discovery Function (3 times)..."
for i in {1..3}; do
  echo "  Request $i..."
  curl -X POST 'https://vendor-discovery-wearla5naa-uc.a.run.app' \
    -H 'Content-Type: application/json' \
    -d '{"project_id": "vendor-risk-digital-twin"}' \
    -s -o /dev/null
  sleep 5  # Wait 5 seconds between requests
done

echo ""
echo "✅ Discovery requests sent!"
echo ""
echo "📊 Next steps:"
echo "1. Go to your dashboard and run 2-3 simulations"
echo "2. Wait 2-3 minutes for metrics to appear"
echo "3. Refresh Cloud Monitoring dashboard"
echo ""
echo "Dashboard URL:"
echo "https://console.cloud.google.com/monitoring/dashboards/custom/cae64d81-7c4f-45ed-b266-f224a6b8308a?project=vendor-risk-digital-twin"

