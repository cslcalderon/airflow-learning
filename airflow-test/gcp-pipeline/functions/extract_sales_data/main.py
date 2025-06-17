"""
Cloud Function: Extract Sales Data
Triggered by Cloud Scheduler or Cloud Workflows

This replaces the Airflow extract task and runs within free tier limits.
Cloud Functions free tier: 2M invocations/month, 400,000 GB-seconds/month
"""

import json
import logging
from datetime import datetime, date
from google.cloud import storage
from google.cloud import bigquery
import pandas as pd

def extract_sales_data(request):
    """
    HTTP Cloud Function to extract and upload sales data
    
    In production, this would:
    - Connect to source databases (Cloud SQL, external APIs)
    - Handle authentication securely using Secret Manager
    - Process larger datasets in chunks
    
    Free tier considerations:
    - Keep function execution under 9 minutes
    - Memory usage under 512MB for best free tier coverage
    - Use Cloud Storage for temporary files (5GB free)
    """
    
    try:
        # Get execution date from request or use current date
        request_json = request.get_json(silent=True)
        if request_json and 'execution_date' in request_json:
            execution_date = datetime.fromisoformat(request_json['execution_date']).date()
        else:
            execution_date = date.today()
        
        logging.info(f"Extracting sales data for {execution_date}")
        
        # Simulate data extraction - in reality you'd query external systems
        # For free tier demo, we'll generate sample data
        sample_data = generate_sample_sales_data(execution_date)
        
        # Upload raw data to Cloud Storage (free tier: 5GB storage)
        upload_to_gcs(sample_data, f"raw-sales-data/{execution_date}.json")
        
        # Insert into BigQuery for further processing
        # BigQuery free tier: 1TB queries/month, 10GB storage
        insert_to_bigquery(sample_data, execution_date)
        
        result = {
            'status': 'success',
            'execution_date': str(execution_date),
            'records_processed': len(sample_data),
            'message': f'Successfully extracted {len(sample_data)} sales records'
        }
        
        logging.info(f"Extraction completed: {result}")
        return json.dumps(result), 200
        
    except Exception as e:
        error_result = {
            'status': 'error',
            'error': str(e),
            'execution_date': str(execution_date) if 'execution_date' in locals() else None
        }
        logging.error(f"Extraction failed: {error_result}")
        return json.dumps(error_result), 500

def generate_sample_sales_data(execution_date):
    """
    Generate sample sales data for demonstration
    
    In production, this would be replaced with:
    - Database queries (Cloud SQL, Cloud Spanner)
    - API calls to external systems (Salesforce, Shopify)
    - File processing from Cloud Storage
    """
    
    # Generate realistic sample data
    import random
    
    products = ['Widget A', 'Widget B', 'Widget C', 'Gadget X', 'Gadget Y']
    
    sample_data = []
    for i in range(random.randint(10, 50)):  # Random number of orders per day
        record = {
            'order_id': 1000 + i,
            'customer_id': random.randint(100, 999),
            'product': random.choice(products),
            'quantity': random.randint(1, 5),
            'price': round(random.uniform(19.99, 99.99), 2),
            'order_date': str(execution_date),
            'region': random.choice(['North', 'South', 'East', 'West']),
            'channel': random.choice(['Online', 'Retail', 'Mobile'])
        }
        record['total_amount'] = round(record['quantity'] * record['price'], 2)
        sample_data.append(record)
    
    return sample_data

def upload_to_gcs(data, blob_name):
    """
    Upload data to Google Cloud Storage
    
    Free tier: 5GB storage, 1GB network egress per month
    Best practices:
    - Use regional buckets for better performance
    - Enable lifecycle management to auto-delete old files
    - Compress data to save space
    """
    
    try:
        # Initialize storage client
        storage_client = storage.Client()
        
        # Get bucket (you'll need to create this bucket)
        bucket_name = 'your-sales-pipeline-bucket'  # Replace with your bucket name
        bucket = storage_client.bucket(bucket_name)
        
        # Create blob and upload
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        
        logging.info(f"Data uploaded to gs://{bucket_name}/{blob_name}")
        
    except Exception as e:
        logging.error(f"Failed to upload to GCS: {e}")
        raise

def insert_to_bigquery(data, execution_date):
    """
    Insert data into BigQuery for analysis
    
    Free tier: 10GB storage, 1TB queries per month
    Best practices:
    - Use partitioned tables by date for better performance
    - Use clustering for frequently queried columns
    - Stream inserts are free but have quotas
    """
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client()
        
        # Define table reference
        dataset_id = 'sales_pipeline'  # You'll need to create this dataset
        table_id = 'raw_sales_data'
        table_ref = client.dataset(dataset_id).table(table_id)
        
        # Configure job to append data
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True  # Auto-detect schema for demo purposes
        )
        
        # Convert to NDJSON format for BigQuery
        ndjson_data = '\n'.join([json.dumps(record) for record in data])
        
        # Load data
        job = client.load_table_from_file(
            file_obj=ndjson_data,
            destination=table_ref,
            job_config=job_config
        )
        
        job.result()  # Wait for job to complete
        
        logging.info(f"Inserted {len(data)} rows into {dataset_id}.{table_id}")
        
    except Exception as e:
        logging.error(f"Failed to insert into BigQuery: {e}")
        raise

# For local testing
if __name__ == '__main__':
    # Simulate a request
    class MockRequest:
        def get_json(self, silent=True):
            return {'execution_date': '2024-01-15'}
    
    result = extract_sales_data(MockRequest())
    print(result)