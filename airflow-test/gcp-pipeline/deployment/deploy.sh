#!/bin/bash

# GCP Sales Pipeline Deployment Script
# This script deploys the entire pipeline to GCP using free tier services
# 
# Prerequisites:
# 1. GCP account with billing enabled (free tier still requires billing setup)
# 2. gcloud CLI installed and authenticated
# 3. APIs enabled: Cloud Functions, Cloud Workflows, BigQuery, Cloud Storage

set -e  # Exit on any error

# Configuration - UPDATE THESE VALUES
PROJECT_ID="your-project-id"
REGION="us-central1"  # Free tier eligible region
BUCKET_NAME="${PROJECT_ID}-sales-pipeline-bucket"
DATASET_NAME="sales_pipeline"

echo "🚀 Starting GCP Sales Pipeline Deployment"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set default project
echo "📋 Setting up GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable workflows.googleapis.com  
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Create Cloud Storage bucket for temporary data
echo "📦 Creating Cloud Storage bucket..."
if ! gsutil ls gs://$BUCKET_NAME > /dev/null 2>&1; then
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ Created bucket: gs://$BUCKET_NAME"
else
    echo "✅ Bucket already exists: gs://$BUCKET_NAME"
fi

# Create BigQuery dataset and tables
echo "🗄️  Setting up BigQuery dataset..."
if ! bq ls -d $PROJECT_ID:$DATASET_NAME > /dev/null 2>&1; then
    bq mk --dataset --location=US $PROJECT_ID:$DATASET_NAME
    echo "✅ Created BigQuery dataset: $DATASET_NAME"
else
    echo "✅ BigQuery dataset already exists: $DATASET_NAME"
fi

# Create tables using SQL file
echo "📊 Creating BigQuery tables..."
bq query --use_legacy_sql=false < ../bigquery/setup_tables.sql
echo "✅ BigQuery tables created"

# Deploy Cloud Functions
echo "☁️  Deploying Cloud Functions..."

# Extract function
echo "  📤 Deploying extract-sales-data function..."
cd ../functions/extract_sales_data
gcloud functions deploy extract-sales-data \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --region $REGION \
    --memory 256MB \
    --timeout 540s \
    --set-env-vars BUCKET_NAME=$BUCKET_NAME,DATASET_NAME=$DATASET_NAME

# Transform function  
echo "  🔄 Deploying transform-sales-data function..."
cd ../transform_sales_data
gcloud functions deploy transform-sales-data \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --region $REGION \
    --memory 256MB \
    --timeout 540s \
    --set-env-vars DATASET_NAME=$DATASET_NAME

echo "✅ Cloud Functions deployed"

# Deploy Cloud Workflow
echo "⚡ Deploying Cloud Workflow..."
cd ../../workflows

# Update workflow file with actual project and region
sed "s/REGION-PROJECT_ID/$REGION-$PROJECT_ID/g" sales_pipeline_workflow.yaml > sales_pipeline_workflow_updated.yaml

gcloud workflows deploy sales-pipeline \
    --source=sales_pipeline_workflow_updated.yaml \
    --location=$REGION

echo "✅ Cloud Workflow deployed"

# Create Cloud Scheduler job for daily execution
echo "⏰ Setting up Cloud Scheduler..."
gcloud scheduler jobs create http sales-pipeline-daily \
    --schedule="0 6 * * *" \
    --uri="https://workflowexecutions.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/workflows/sales-pipeline/executions" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{}' \
    --time-zone="America/New_York" \
    --location=$REGION || echo "⚠️  Scheduler job might already exist"

echo "✅ Cloud Scheduler configured"

# Test the pipeline
echo "🧪 Testing the pipeline..."
echo "  Triggering workflow execution..."

EXECUTION_ID=$(gcloud workflows run sales-pipeline --location=$REGION --format="value(name)")
echo "  ✅ Workflow started: $EXECUTION_ID"
echo "  📊 Check execution status:"
echo "     gcloud workflows executions describe $EXECUTION_ID --workflow=sales-pipeline --location=$REGION"

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Summary:"
echo "  • Project: $PROJECT_ID"
echo "  • Region: $REGION"
echo "  • Bucket: gs://$BUCKET_NAME"
echo "  • Dataset: $DATASET_NAME"
echo "  • Functions: extract-sales-data, transform-sales-data"
echo "  • Workflow: sales-pipeline"
echo "  • Schedule: Daily at 6 AM"
echo ""
echo "🔗 Useful Links:"
echo "  • Cloud Functions: https://console.cloud.google.com/functions/list?project=$PROJECT_ID"
echo "  • Cloud Workflows: https://console.cloud.google.com/workflows/workflow/details/$REGION/sales-pipeline?project=$PROJECT_ID"
echo "  • BigQuery: https://console.cloud.google.com/bigquery?project=$PROJECT_ID&ws=!1m4!1m3!3m2!1s$PROJECT_ID!2s$DATASET_NAME"
echo "  • Cloud Scheduler: https://console.cloud.google.com/cloudscheduler?project=$PROJECT_ID"
echo ""
echo "💰 Free Tier Usage:"
echo "  • Cloud Functions: ~100 invocations/day = 3000/month (well under 2M limit)"
echo "  • Cloud Workflows: ~30 steps/day = 900/month (well under 5K limit)"  
echo "  • BigQuery: ~1MB queries/day = 30MB/month (well under 1TB limit)"
echo "  • Cloud Storage: ~1MB/day = 30MB/month (well under 5GB limit)"
echo "  • Cloud Scheduler: 1 job (3 jobs free)"
echo ""
echo "🚨 Manual Steps Required:"
echo "  1. Update bucket name in Cloud Functions code:"
echo "     functions/extract_sales_data/main.py line 89"
echo "  2. Update dataset references in BigQuery if needed"
echo "  3. Set up monitoring/alerting if desired"

cd ../../deployment