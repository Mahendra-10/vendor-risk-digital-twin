#!/bin/bash

# Monitor Cloud Build progress

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"

echo "🔍 Cloud Build Monitor"
echo "   Project: $PROJECT_ID"
echo ""

# Check for ongoing builds
echo "📊 Checking for running builds..."
ONGOING=$(gcloud builds list --ongoing --project=$PROJECT_ID --format="value(id)" 2>/dev/null)

if [ -z "$ONGOING" ]; then
    echo "   ℹ️  No builds currently running"
    echo ""
    echo "📋 Recent builds:"
    gcloud builds list --project=$PROJECT_ID --limit 5 --format="table(id,status,createTime,duration)"
else
    echo "   ✅ Found running build(s):"
    for build_id in $ONGOING; do
        echo "      Build ID: $build_id"
        echo ""
        echo "   📊 Build Status:"
        gcloud builds describe $build_id --project=$PROJECT_ID --format="value(status)" 2>/dev/null
        echo ""
        echo "   📝 View logs:"
        echo "      gcloud builds log $build_id --project=$PROJECT_ID"
        echo ""
        echo "   🌐 View in Console:"
        echo "      https://console.cloud.google.com/cloud-build/builds/$build_id?project=$PROJECT_ID"
    done
fi

echo ""
echo "🌐 Open Cloud Build Console:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""

