"""
Cloud Function: Transform Sales Data
Processes raw data in BigQuery using SQL transformations

This replaces the Airflow transform task and leverages BigQuery's
free tier processing power (1TB queries/month).
"""

import json
import logging
from datetime import datetime, date
from google.cloud import bigquery

def transform_sales_data(request):
    """
    HTTP Cloud Function to transform sales data in BigQuery
    
    Why BigQuery for transformations:
    - 1TB of free queries per month
    - Serverless - no infrastructure to manage
    - SQL-based transformations are faster than Python for large datasets
    - Built-in data quality functions
    """
    
    try:
        # Get execution date from request
        request_json = request.get_json(silent=True)
        if request_json and 'execution_date' in request_json:
            execution_date = request_json['execution_date']
        else:
            execution_date = str(date.today())
            
        logging.info(f"Transforming sales data for {execution_date}")
        
        # Initialize BigQuery client
        client = bigquery.Client()
        
        # Run transformation query
        transformation_results = run_transformation_query(client, execution_date)
        
        # Run data quality checks
        quality_results = run_data_quality_checks(client, execution_date)
        
        result = {
            'status': 'success',
            'execution_date': execution_date,
            'transformed_records': transformation_results['row_count'],
            'total_revenue': transformation_results['total_revenue'],
            'quality_checks': quality_results,
            'message': 'Data transformation completed successfully'
        }
        
        logging.info(f"Transformation completed: {result}")
        return json.dumps(result, default=str), 200
        
    except Exception as e:
        error_result = {
            'status': 'error',
            'error': str(e),
            'execution_date': execution_date if 'execution_date' in locals() else None
        }
        logging.error(f"Transformation failed: {error_result}")
        return json.dumps(error_result), 500

def run_transformation_query(client, execution_date):
    """
    Execute BigQuery transformation SQL
    
    Benefits of SQL transformations in BigQuery:
    - Faster than Python for large datasets
    - Built-in aggregation functions
    - Automatic optimization
    - Easy to version control and test
    """
    
    # Transformation SQL - this is where the real work happens
    transformation_sql = f"""
    CREATE OR REPLACE TABLE `sales_pipeline.transformed_sales_data` 
    PARTITION BY DATE(order_date)
    CLUSTER BY region, product
    AS
    SELECT 
        order_id,
        customer_id,
        product,
        quantity,
        price,
        total_amount,
        DATE(order_date) as order_date,
        region,
        channel,
        
        -- Business calculations (common in real pipelines)
        CASE 
            WHEN total_amount >= 100 THEN 'High Value'
            WHEN total_amount >= 50 THEN 'Medium Value'
            ELSE 'Low Value'
        END as order_category,
        
        -- Product categorization
        CASE 
            WHEN product LIKE '%Widget%' THEN 'Widgets'
            WHEN product LIKE '%Gadget%' THEN 'Gadgets'
            ELSE 'Other'
        END as product_category,
        
        -- Time-based features for analysis
        EXTRACT(DAYOFWEEK FROM DATE(order_date)) as day_of_week,
        EXTRACT(MONTH FROM DATE(order_date)) as month,
        EXTRACT(QUARTER FROM DATE(order_date)) as quarter,
        
        -- Customer analytics
        RANK() OVER (
            PARTITION BY customer_id 
            ORDER BY DATE(order_date)
        ) as customer_order_sequence,
        
        -- Revenue calculations
        total_amount as revenue,
        total_amount * 0.3 as estimated_profit,  -- Assuming 30% margin
        
        -- Data quality indicators
        CASE 
            WHEN quantity <= 0 OR price <= 0 THEN TRUE 
            ELSE FALSE 
        END as has_data_quality_issues,
        
        CURRENT_TIMESTAMP() as processed_at
        
    FROM `sales_pipeline.raw_sales_data`
    WHERE DATE(order_date) = '{execution_date}'
    AND quantity > 0  -- Basic data quality filter
    AND price > 0
    """
    
    # Execute the transformation
    job = client.query(transformation_sql)
    job.result()  # Wait for completion
    
    # Get summary statistics
    stats_sql = f"""
    SELECT 
        COUNT(*) as row_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM `sales_pipeline.transformed_sales_data`
    WHERE order_date = '{execution_date}'
    """
    
    stats_job = client.query(stats_sql)
    stats_result = list(stats_job.result())[0]
    
    return {
        'row_count': stats_result.row_count,
        'total_revenue': float(stats_result.total_revenue or 0),
        'avg_order_value': float(stats_result.avg_order_value or 0),
        'unique_customers': stats_result.unique_customers
    }

def run_data_quality_checks(client, execution_date):
    """
    Data quality validation using BigQuery SQL
    
    Common checks in production pipelines:
    - Completeness (no nulls in required fields)
    - Validity (values within expected ranges)
    - Consistency (referential integrity)
    - Accuracy (business rule validation)
    """
    
    quality_sql = f"""
    WITH quality_checks AS (
        SELECT 
            -- Completeness checks
            COUNTIF(order_id IS NULL) as null_order_ids,
            COUNTIF(customer_id IS NULL) as null_customer_ids,
            COUNTIF(product IS NULL) as null_products,
            
            -- Validity checks  
            COUNTIF(quantity <= 0) as invalid_quantities,
            COUNTIF(price <= 0) as invalid_prices,
            COUNTIF(total_amount != quantity * price) as calculation_errors,
            
            -- Business rule checks
            COUNTIF(total_amount > 1000) as high_value_orders,  -- Flag for review
            COUNTIF(quantity > 10) as bulk_orders,  -- Unusual quantities
            
            -- Summary stats
            COUNT(*) as total_records,
            MIN(total_amount) as min_revenue,
            MAX(total_amount) as max_revenue
            
        FROM `sales_pipeline.transformed_sales_data`
        WHERE order_date = '{execution_date}'
    )
    SELECT * FROM quality_checks
    """
    
    job = client.query(quality_sql)
    result = list(job.result())[0]
    
    # Convert to dictionary for easier handling
    quality_results = {
        'total_records': result.total_records,
        'data_issues': {
            'null_order_ids': result.null_order_ids,
            'null_customer_ids': result.null_customer_ids,
            'null_products': result.null_products,
            'invalid_quantities': result.invalid_quantities,
            'invalid_prices': result.invalid_prices,
            'calculation_errors': result.calculation_errors
        },
        'business_flags': {
            'high_value_orders': result.high_value_orders,
            'bulk_orders': result.bulk_orders
        },
        'revenue_range': {
            'min': float(result.min_revenue or 0),
            'max': float(result.max_revenue or 0)
        }
    }
    
    # Validate results - fail if critical issues found
    total_issues = (result.null_order_ids + result.invalid_quantities + 
                   result.invalid_prices + result.calculation_errors)
    
    if total_issues > 0:
        raise ValueError(f"Data quality issues found: {total_issues} records with problems")
    
    if result.total_records == 0:
        raise ValueError("No records found for transformation")
    
    return quality_results

# For local testing
if __name__ == '__main__':
    class MockRequest:
        def get_json(self, silent=True):
            return {'execution_date': '2024-01-15'}
    
    result = transform_sales_data(MockRequest())
    print(result)