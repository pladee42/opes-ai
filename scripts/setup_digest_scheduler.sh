#!/bin/bash
# Setup Cloud Scheduler for Technical Analysis Digest Push

PROJECT_ID="opes-ai-482213"
REGION="asia-southeast1"
SERVICE_NAME="opes-ai"

# Get Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)' --project $PROJECT_ID)

echo "Setting up Cloud Scheduler job for: $CLOUD_RUN_URL/api/digest-push"

# Create scheduler job if not exists, or update it
gcloud scheduler jobs create http digest-push \
  --schedule="0 * * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="$CLOUD_RUN_URL/api/digest-push" \
  --http-method=POST \
  --location=$REGION \
  --project=$PROJECT_ID \
  --description="Hourly trigger for technical analysis digest LINE push messages" \
  2>/dev/null || \
gcloud scheduler jobs update http digest-push \
  --schedule="0 * * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="$CLOUD_RUN_URL/api/digest-push" \
  --http-method=POST \
  --location=$REGION \
  --project=$PROJECT_ID \
  --description="Hourly trigger for technical analysis digest LINE push messages"

echo "✅ Cloud Scheduler job 'digest-push' setup complete!"
