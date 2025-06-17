# GCP Sales Data Pipeline (Free Tier)

A production-ready data pipeline built entirely on GCP's free tier services. This demonstrates how to build real-world data pipelines without paying for expensive managed services like Cloud Composer.

## 🏗️ Architecture

**Services Used (All Free Tier Eligible):**
- **Cloud Functions**: Data processing (2M invocations/month free)
- **Cloud Workflows**: Orchestration (5K steps/month free)  
- **BigQuery**: Data warehouse (1TB queries + 10GB storage/month free)
- **Cloud Storage**: Temporary file storage (5GB/month free)
- **Cloud Scheduler**: Pipeline scheduling (3 jobs/month free)

**Pipeline Flow:**
```
Cloud Scheduler → Cloud Workflows → Cloud Functions → BigQuery
     ↓                   ↓              ↓             ↓
  (Daily 6AM)        (Orchestration)  (Processing)  (Analytics)
```

## 💰 Cost Breakdown

**Monthly Usage (Typical Small Business):**
- Cloud Functions: ~3,000 executions = **FREE** (under 2M limit)
- Cloud Workflows: ~900 steps = **FREE** (under 5K limit)
- BigQuery: ~30MB queries = **FREE** (under 1TB limit)
- Cloud Storage: ~30MB data = **FREE** (under 5GB limit)
- Cloud Scheduler: 1 job = **FREE** (under 3 job limit)

**Total Monthly Cost: $0** ✨

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login
gcloud auth application-default login

# Create project (or use existing)
gcloud projects create your-project-id
gcloud config set project your-project-id

# Enable billing (required even for free tier)
# Go to: https://console.cloud.google.com/billing
```

### 2. Deploy Pipeline
```bash
cd deployment
./deploy.sh
```

### 3. Customize Configuration
Edit these files before deployment:
- `deployment/deploy.sh` - Update PROJECT_ID and REGION
- `functions/extract_sales_data/main.py` - Update bucket name (line 89)

### 4. Test Pipeline
```bash
# Manual trigger
gcloud workflows run sales-pipeline --location=us-central1

# Check execution
gcloud workflows executions list --workflow=sales-pipeline --location=us-central1
```

## 📁 Project Structure

```
gcp-pipeline/
├── functions/
│   ├── extract_sales_data/          # Data extraction function
│   │   ├── main.py
│   │   └── requirements.txt
│   └── transform_sales_data/        # Data transformation function
│       ├── main.py
│       └── requirements.txt
├── workflows/
│   └── sales_pipeline_workflow.yaml # Orchestration workflow
├── bigquery/
│   ├── setup_tables.sql            # Table definitions
│   └── daily_summary_query.sql     # Reporting queries
├── deployment/
│   └── deploy.sh                   # Automated deployment
└── README.md
```

## 🔍 Key Features

### Data Processing
- **Extract**: Simulates pulling from external APIs/databases
- **Transform**: SQL-based transformations in BigQuery
- **Load**: Automated data quality checks and reporting
- **Monitor**: Built-in logging and error handling

### Production Ready
- **Error Handling**: Retry logic and failure notifications
- **Data Quality**: Automated validation and alerting
- **Scalability**: Serverless components auto-scale
- **Monitoring**: Cloud Logging integration

### Cost Optimization
- **Partitioned Tables**: Reduce query costs
- **Clustered Storage**: Improve query performance
- **Lifecycle Policies**: Auto-delete old data
- **Efficient Queries**: Minimize BigQuery slot usage

## 📊 BigQuery Tables

### Raw Data (`raw_sales_data`)
- Source data from extraction
- Partitioned by date
- 90-day retention policy

### Transformed Data (`transformed_sales_data`)  
- Cleaned and enriched data
- Business calculations added
- 365-day retention policy

### Daily Summary (`daily_sales_summary`)
- Aggregated metrics
- Executive reporting
- 3-year retention policy

## 🔄 Scheduling

**Default Schedule**: Daily at 6 AM EST
```bash
# Modify schedule
gcloud scheduler jobs update http sales-pipeline-daily \
    --schedule="0 8 * * *"  # 8 AM instead
```

**Manual Triggers**:
```bash
# Run immediately
gcloud workflows run sales-pipeline --location=us-central1

# Run with specific date
gcloud workflows run sales-pipeline \
    --data='{"execution_date":"2024-01-15"}' \
    --location=us-central1
```

## 📈 Monitoring

### Cloud Console
- **Functions**: [Cloud Functions Console](https://console.cloud.google.com/functions)
- **Workflows**: [Workflows Console](https://console.cloud.google.com/workflows)
- **BigQuery**: [BigQuery Console](https://console.cloud.google.com/bigquery)

### Key Metrics to Watch
- Function execution count (stay under 2M/month)
- BigQuery query usage (stay under 1TB/month)
- Workflow execution count (stay under 5K steps/month)

### Alerts (Optional)
```bash
# Set up budget alerts
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Pipeline Budget" \
    --budget-amount=10USD
```

## 🔧 Customization

### Adding New Data Sources
1. Modify `functions/extract_sales_data/main.py`
2. Add connection logic for your data source
3. Update BigQuery schema in `bigquery/setup_tables.sql`

### Custom Transformations
1. Edit SQL in `functions/transform_sales_data/main.py`
2. Add business logic specific to your use case
3. Update data quality checks

### Additional Functions
1. Create new function directory
2. Add to `workflows/sales_pipeline_workflow.yaml`
3. Update `deployment/deploy.sh`

## 🚨 Common Issues

### "Functions not found"
- Ensure all functions deployed successfully
- Check function names match workflow YAML
- Verify region consistency

### "BigQuery permission denied"  
- Enable BigQuery API
- Check service account permissions
- Ensure dataset exists

### "Workflow execution failed"
- Check Cloud Functions logs
- Verify BigQuery table schemas
- Review workflow execution details

## 🔄 vs Airflow Comparison

| Feature | Airflow | GCP Native |
|---------|---------|------------|
| **Cost** | $300-500/month (Composer) | $0/month (free tier) |
| **Setup** | Complex infrastructure | Serverless deployment |
| **Maintenance** | High (updates, scaling) | None (managed services) |
| **Learning Curve** | Steep | Moderate |
| **Flexibility** | Very high | High |
| **Monitoring** | Custom setup needed | Built-in Cloud Console |

## 🎯 Next Steps

### For Learning
1. Run the pipeline with sample data
2. Explore BigQuery console and queries
3. Modify transformations to understand SQL processing
4. Add custom business logic

### For Production
1. Connect real data sources
2. Set up proper authentication (Service Accounts)
3. Implement comprehensive monitoring
4. Add data backup strategies
5. Set up CI/CD for function deployments

### Scaling Beyond Free Tier
When you outgrow free tier limits:
1. **Cloud Run**: More flexible than Functions
2. **Dataflow**: For complex transformations  
3. **Composer**: For complex orchestration
4. **BigQuery BI Engine**: For real-time dashboards

## 📚 Learning Resources

- [BigQuery Free Tier](https://cloud.google.com/bigquery/pricing#free-tier)
- [Cloud Functions Pricing](https://cloud.google.com/functions/pricing)
- [Cloud Workflows Pricing](https://cloud.google.com/workflows/pricing)
- [GCP Free Tier Overview](https://cloud.google.com/free)

---

**Built for learning data engineering on GCP without breaking the bank! 💸**