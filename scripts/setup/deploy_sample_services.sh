#!/bin/bash
# Deploy Sample Cloud Functions and Cloud Run Services with Vendor Environment Variables
# This script creates sample services to demonstrate vendor discovery

set -e

PROJECT_ID="${GCP_PROJECT_ID:-vendor-risk-digital-twin}"
REGION="${GCP_REGION:-us-central1}"

echo "🚀 Deploying sample services with vendor environment variables..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Create temporary directory for sample functions
TEMP_DIR=$(mktemp -d)
echo "📁 Created temp directory: $TEMP_DIR"

# Sample Cloud Function 1: Payment Service (Stripe)
echo "📦 Creating sample payment function (Stripe)..."
mkdir -p "$TEMP_DIR/payment-service"
cat > "$TEMP_DIR/payment-service/main.py" << 'EOF'
def payment_handler(request):
    """Sample payment processing function"""
    import os
    stripe_key = os.getenv('STRIPE_API_KEY', 'not_set')
    stripe_secret = os.getenv('STRIPE_WEBHOOK_SECRET', 'not_set')
    
    return {
        'status': 'ok',
        'message': 'Payment service',
        'stripe_configured': stripe_key != 'not_set'
    }
EOF

cat > "$TEMP_DIR/payment-service/requirements.txt" << 'EOF'
# No external dependencies for this sample
EOF

gcloud functions deploy payment-service \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source="$TEMP_DIR/payment-service" \
    --entry-point=payment_handler \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars="STRIPE_API_KEY=sk_test_sample123,STRIPE_WEBHOOK_SECRET=whsec_sample456" \
    --project=$PROJECT_ID \
    --quiet

echo "✅ Deployed payment-service"

# Sample Cloud Function 2: Auth Service (Auth0)
echo "📦 Creating sample auth function (Auth0)..."
mkdir -p "$TEMP_DIR/auth-service"
cat > "$TEMP_DIR/auth-service/main.py" << 'EOF'
def auth_handler(request):
    """Sample authentication function"""
    import os
    auth0_domain = os.getenv('AUTH0_DOMAIN', 'not_set')
    auth0_client_id = os.getenv('AUTH0_CLIENT_ID', 'not_set')
    
    return {
        'status': 'ok',
        'message': 'Auth service',
        'auth0_configured': auth0_domain != 'not_set'
    }
EOF

cat > "$TEMP_DIR/auth-service/requirements.txt" << 'EOF'
# No external dependencies for this sample
EOF

gcloud functions deploy auth-service \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source="$TEMP_DIR/auth-service" \
    --entry-point=auth_handler \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars="AUTH0_DOMAIN=dev-sample.auth0.com,AUTH0_CLIENT_ID=abc123xyz" \
    --project=$PROJECT_ID \
    --quiet

echo "✅ Deployed auth-service"

# Sample Cloud Function 3: Email Service (SendGrid)
echo "📦 Creating sample email function (SendGrid)..."
mkdir -p "$TEMP_DIR/email-service"
cat > "$TEMP_DIR/email-service/main.py" << 'EOF'
def email_handler(request):
    """Sample email sending function"""
    import os
    sendgrid_key = os.getenv('SENDGRID_API_KEY', 'not_set')
    
    return {
        'status': 'ok',
        'message': 'Email service',
        'sendgrid_configured': sendgrid_key != 'not_set'
    }
EOF

cat > "$TEMP_DIR/email-service/requirements.txt" << 'EOF'
# No external dependencies for this sample
EOF

gcloud functions deploy email-service \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source="$TEMP_DIR/email-service" \
    --entry-point=email_handler \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars="SENDGRID_API_KEY=SG.sample_key_123456" \
    --project=$PROJECT_ID \
    --quiet

echo "✅ Deployed email-service"

# Sample Cloud Run Service: Checkout Service (Stripe + Twilio)
echo "📦 Creating sample checkout Cloud Run service (Stripe + Twilio)..."
mkdir -p "$TEMP_DIR/checkout-service"
cat > "$TEMP_DIR/checkout-service/main.py" << 'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'checkout-service',
        'stripe_configured': bool(os.getenv('STRIPE_PUBLISHABLE_KEY')),
        'twilio_configured': bool(os.getenv('TWILIO_ACCOUNT_SID'))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

cat > "$TEMP_DIR/checkout-service/requirements.txt" << 'EOF'
Flask==3.0.0
EOF

cat > "$TEMP_DIR/checkout-service/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
EOF

# Build and deploy Cloud Run service
gcloud run deploy checkout-service \
    --source="$TEMP_DIR/checkout-service" \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="STRIPE_PUBLISHABLE_KEY=pk_test_sample789,TWILIO_ACCOUNT_SID=ACsample123,TWILIO_AUTH_TOKEN=token_sample456" \
    --project=$PROJECT_ID \
    --quiet

echo "✅ Deployed checkout-service"

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo ""
echo "✅ All sample services deployed successfully!"
echo ""
echo "📋 Summary:"
echo "   - payment-service (Cloud Function) - Stripe"
echo "   - auth-service (Cloud Function) - Auth0"
echo "   - email-service (Cloud Function) - SendGrid"
echo "   - checkout-service (Cloud Run) - Stripe + Twilio"
echo ""
echo "🔍 Now run discovery to find these vendors:"
echo "   gcloud functions call discover-vendors --region=$REGION --project=$PROJECT_ID"

