#!/bin/bash
# Deploy Family Wealth AI to GCP

set -e

# Configuration - UPDATE THESE
PROJECT_ID="opes-ai-482213"
REGION="asia-southeast1"
SERVICE_NAME="opes-ai"
BUCKET_NAME="opes-ai-liff"

echo "🚀 Deploying Family Wealth AI to GCP..."

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    echo "Please login first: gcloud auth login"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Deploy to Cloud Run
echo "📦 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 120

# Get Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
echo "✅ Cloud Run URL: $CLOUD_RUN_URL"

# Create bucket if not exists
if ! gsutil ls gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "📁 Creating Cloud Storage bucket..."
    gsutil mb -l $REGION gs://$BUCKET_NAME
    gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
fi

# Update LIFF with correct API URL and upload
echo "📤 Updating and uploading LIFF..."
TEMP_LIFF=$(mktemp)
sed "s|window.location.origin + '/api/allocation'|'$CLOUD_RUN_URL/api/allocation'|" liff/allocation.html > $TEMP_LIFF
gsutil -h "Content-Type:text/html" cp $TEMP_LIFF gs://$BUCKET_NAME/allocation.html
rm $TEMP_LIFF

LIFF_URL="https://storage.googleapis.com/$BUCKET_NAME/allocation.html"

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "📌 Update these in LINE Developers Console:"
echo ""
echo "Webhook URL:"
echo "  $CLOUD_RUN_URL/webhook"
echo ""
echo "LIFF Endpoint URL:"
echo "  $LIFF_URL"
echo ""
echo "📌 Update your .env file:"
echo "  LIFF_URL=https://liff.line.me/YOUR_LIFF_ID"
echo ""
