"""
Real-world Sales Data Pipeline DAG

This DAG demonstrates a typical business data pipeline that:
1. Extracts sales data from a database
2. Transforms and cleans the data
3. Generates business reports
4. Sends notifications

This is a common pattern in many organizations for daily/weekly reporting.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator  # type: ignore
from airflow.providers.standard.operators.bash import BashOperator  # type: ignore
from airflow.providers.smtp.operators.smtp import EmailOperator  # type: ignore
from airflow.providers.standard.sensors.filesystem import FileSensor  # type: ignore
import pandas as pd
import logging

# Default arguments that apply to all tasks in the DAG
# These are best practices for production DAGs
default_args = {
    'owner': 'data-team',  # Who owns this DAG - important for accountability
    'depends_on_past': False,  # Don't wait for previous runs to succeed
    'start_date': datetime(2024, 1, 1),  # When this DAG should start running
    'email_on_failure': True,  # Send email if tasks fail
    'email_on_retry': False,  # Don't spam on retries
    'retries': 2,  # Retry failed tasks twice (networks can be flaky)
    'retry_delay': timedelta(minutes=5),  # Wait 5 minutes between retries
    'catchup': False,  # Don't run historical data on first deployment
}

# Define the DAG
dag = DAG(
    'sales_data_pipeline',  # Unique identifier for this DAG
    default_args=default_args,
    description='Daily sales data processing and reporting pipeline',
    schedule='0 6 * * *',  # Run daily at 6 AM (cron format)
    # Alternative: schedule=timedelta(days=1) for every 24 hours
    max_active_runs=1,  # Only allow one instance running at a time
    tags=['sales', 'reporting', 'daily'],  # Tags help organize DAGs in UI
)

def extract_sales_data(**context):
    """
    Extract sales data from source system
    
    In a real scenario, this would connect to:
    - Database (PostgreSQL, MySQL, etc.)
    - API endpoints
    - Cloud storage (S3, GCS)
    - SaaS platforms (Salesforce, Shopify)
    
    **context contains runtime information like execution_date
    """
    # Simulate data extraction - in reality you'd use database connectors
    execution_date = context['execution_date']
    logging.info(f"Extracting sales data for {execution_date}")
    
    # This would be actual database query in production:
    # import psycopg2
    # conn = psycopg2.connect(database="sales", user="user", password="pass")
    # df = pd.read_sql("SELECT * FROM sales WHERE date = %s", conn, params=[execution_date])
    
    # For demo purposes, create sample data
    sample_data = {
        'order_id': [1001, 1002, 1003, 1004, 1005],
        'customer_id': [501, 502, 503, 504, 505],
        'product': ['Widget A', 'Widget B', 'Widget A', 'Widget C', 'Widget B'],
        'quantity': [2, 1, 3, 1, 2],
        'price': [29.99, 49.99, 29.99, 19.99, 49.99],
        'order_date': [execution_date.date()] * 5
    }
    
    df = pd.DataFrame(sample_data)
    
    # Save to temporary location for next task
    # In production, you might use XCom, database, or shared storage
    df.to_csv('/tmp/raw_sales_data.csv', index=False)
    logging.info(f"Extracted {len(df)} sales records")
    
    return f"Extracted {len(df)} records"

def transform_sales_data(**context):
    """
    Clean and transform the raw sales data
    
    Common transformations include:
    - Data cleaning (nulls, duplicates, formatting)
    - Calculations (totals, margins)
    - Categorization
    - Data validation
    """
    logging.info("Starting data transformation")
    
    # Read the raw data from previous task
    df = pd.read_csv('/tmp/raw_sales_data.csv')
    
    # Add calculated fields (common in business reporting)
    df['total_amount'] = df['quantity'] * df['price']
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Add business categorization
    df['product_category'] = df['product'].apply(lambda x: 'Electronics' if 'Widget' in x else 'Other')
    
    # Data quality checks (critical in production)
    if df['total_amount'].sum() == 0:
        raise ValueError("No sales data found - possible data quality issue")
    
    if df.isnull().any().any():
        logging.warning("Found null values in data")
        df = df.fillna(0)  # Handle nulls appropriately
    
    # Save transformed data
    df.to_csv('/tmp/transformed_sales_data.csv', index=False)
    
    total_revenue = df['total_amount'].sum()
    logging.info(f"Transformation complete. Total revenue: ${total_revenue:.2f}")
    
    return f"Processed {len(df)} records, total revenue: ${total_revenue:.2f}"

def generate_sales_report(**context):
    """
    Generate business reports and summaries
    
    This could create:
    - Executive dashboards
    - Detailed reports
    - Data exports for other systems
    """
    logging.info("Generating sales report")
    
    df = pd.read_csv('/tmp/transformed_sales_data.csv')
    
    # Generate summary statistics (what executives want to see)
    report = {
        'date': context['execution_date'].strftime('%Y-%m-%d'),
        'total_orders': len(df),
        'total_revenue': df['total_amount'].sum(),
        'average_order_value': df['total_amount'].mean(),
        'top_product': df.groupby('product')['quantity'].sum().idxmax(),
        'unique_customers': df['customer_id'].nunique()
    }
    
    # In production, you might:
    # - Save to database
    # - Upload to dashboard tool (Tableau, PowerBI)
    # - Send to data warehouse
    # - Create PDF reports
    
    # For demo, save as JSON
    import json
    with open('/tmp/sales_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logging.info(f"Report generated: {report}")
    return report

def validate_data_quality(**context):
    """
    Data quality validation - crucial for production pipelines
    
    Checks might include:
    - Row count validation
    - Revenue threshold checks
    - Data freshness validation
    - Schema validation
    """
    df = pd.read_csv('/tmp/transformed_sales_data.csv')
    
    # Business rule validations
    if len(df) == 0:
        raise ValueError("No data processed - pipeline failure")
    
    total_revenue = df['total_amount'].sum()
    if total_revenue < 0:
        raise ValueError("Negative revenue detected - data quality issue")
    
    # You might also check against previous day's data
    # if abs(total_revenue - previous_day_revenue) > threshold:
    #     raise ValueError("Revenue variance too high - investigate")
    
    logging.info("Data quality validation passed")
    return "Data quality OK"

# Define tasks using the functions above
# Each task runs independently and can be parallelized where possible

extract_task = PythonOperator(
    task_id='extract_sales_data',  # Unique task identifier
    python_callable=extract_sales_data,  # Function to execute
    dag=dag,
    # You can add task-specific overrides here:
    # retries=3,  # This task might need more retries
    # pool='database_pool',  # Limit concurrent database connections
)

transform_task = PythonOperator(
    task_id='transform_sales_data',
    python_callable=transform_sales_data,
    dag=dag,
)

report_task = PythonOperator(
    task_id='generate_sales_report',
    python_callable=generate_sales_report,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag,
)

# Example of using BashOperator for system commands
# This is useful for calling external scripts or system utilities
backup_task = BashOperator(
    task_id='backup_processed_data',
    bash_command='cp /tmp/transformed_sales_data.csv /tmp/backup_$(date +%Y%m%d).csv',
    dag=dag,
)

# Example of FileSensor - wait for external file to arrive
# Common in scenarios where you're waiting for data from external systems
file_sensor = FileSensor(
    task_id='wait_for_external_file',
    filepath='/tmp/external_trigger.txt',  # File to wait for
    timeout=300,  # Maximum wait time (5 minutes)
    poke_interval=30,  # Check every 30 seconds
    dag=dag,
    # In production, you might wait for files like:
    # - Daily exports from other systems
    # - Confirmation files from partners
    # - Batch processing completion markers
)

# Example of email notification
# Useful for alerting stakeholders about important pipeline events
notify_task = EmailOperator(
    task_id='send_completion_email',
    to=['data-team@company.com'],
    subject='Sales Pipeline Complete - {{ ds }}',  # {{ ds }} is execution date
    html_content="""
    <h3>Sales Data Pipeline Completed Successfully</h3>
    <p>Date: {{ ds }}</p>
    <p>The daily sales data pipeline has completed processing.</p>
    <p>Check the dashboard for updated reports.</p>
    """,
    dag=dag,
)

# Define task dependencies - this determines execution order
# This creates a Directed Acyclic Graph (DAG)

# Option 1: Using >> operator (most readable)
extract_task >> transform_task >> validate_task >> report_task
extract_task >> backup_task  # Backup can run in parallel with transform

# Option 2: You could also use set_downstream/set_upstream methods
# extract_task.set_downstream(transform_task)

# Option 3: For more complex dependencies, you can use lists
# [extract_task, file_sensor] >> transform_task >> [validate_task, backup_task] >> report_task >> notify_task

# The final dependency chain shows how tasks flow:
# extract_task (start)
#   ↓
# transform_task 
#   ↓
# validate_task
#   ↓  
# report_task
#   ↓
# notify_task (end)
#
# backup_task runs in parallel after extract_task

report_task >> notify_task

# Additional production considerations not shown in this example:
# 
# 1. Connection Management:
#    - Use Airflow Connections for database/API credentials
#    - Store in Airflow's encrypted connection store
#
# 2. Variable Management:
#    - Use Airflow Variables for configuration
#    - Environment-specific settings
#
# 3. XCom for task communication:
#    - Pass small amounts of data between tasks
#    - Better than using temporary files
#
# 4. Task Groups:
#    - Group related tasks for better organization
#    - Especially useful in complex DAGs
#
# 5. Error Handling:
#    - on_failure_callback for custom error handling
#    - Slack/Teams notifications on failures
#
# 6. Monitoring:
#    - SLA monitoring for critical pipelines
#    - Custom metrics and logging
#
# 7. Testing:
#    - Unit tests for task functions
#    - Integration tests for the full pipeline