#!/usr/bin/env python3
"""
Test script for pipeline functions without Airflow
Run this to see what the data processing logic actually does
"""

import pandas as pd
import logging
from datetime import datetime, date
import json

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_sales_data(**context):
    """Extract sales data - copied from DAG"""
    execution_date = context.get('execution_date', datetime.now())
    logging.info(f"Extracting sales data for {execution_date}")
    
    sample_data = {
        'order_id': [1001, 1002, 1003, 1004, 1005],
        'customer_id': [501, 502, 503, 504, 505],
        'product': ['Widget A', 'Widget B', 'Widget A', 'Widget C', 'Widget B'],
        'quantity': [2, 1, 3, 1, 2],
        'price': [29.99, 49.99, 29.99, 19.99, 49.99],
        'order_date': [execution_date.date()] * 5
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('/tmp/raw_sales_data.csv', index=False)
    logging.info(f"Extracted {len(df)} sales records")
    return f"Extracted {len(df)} records"

def transform_sales_data(**context):
    """Transform sales data - copied from DAG"""
    logging.info("Starting data transformation")
    
    df = pd.read_csv('/tmp/raw_sales_data.csv')
    df['total_amount'] = df['quantity'] * df['price']
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['product_category'] = df['product'].apply(lambda x: 'Electronics' if 'Widget' in x else 'Other')
    
    if df['total_amount'].sum() == 0:
        raise ValueError("No sales data found")
    
    df.to_csv('/tmp/transformed_sales_data.csv', index=False)
    total_revenue = df['total_amount'].sum()
    logging.info(f"Transformation complete. Total revenue: ${total_revenue:.2f}")
    return f"Processed {len(df)} records, total revenue: ${total_revenue:.2f}"

def generate_sales_report(**context):
    """Generate sales report - copied from DAG"""
    logging.info("Generating sales report")
    
    df = pd.read_csv('/tmp/transformed_sales_data.csv')
    
    report = {
        'date': context.get('execution_date', datetime.now()).strftime('%Y-%m-%d'),
        'total_orders': len(df),
        'total_revenue': df['total_amount'].sum(),
        'average_order_value': df['total_amount'].mean(),
        'top_product': df.groupby('product')['quantity'].sum().idxmax(),
        'unique_customers': df['customer_id'].nunique()
    }
    
    with open('/tmp/sales_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logging.info(f"Report generated: {report}")
    return report

if __name__ == "__main__":
    print("🚀 Testing Sales Pipeline Functions")
    print("=" * 50)
    
    # Simulate context that Airflow would provide
    context = {'execution_date': datetime.now()}
    
    try:
        # Run pipeline steps
        print("1. Extracting data...")
        extract_result = extract_sales_data(**context)
        print(f"   ✅ {extract_result}")
        
        print("\n2. Transforming data...")
        transform_result = transform_sales_data(**context)
        print(f"   ✅ {transform_result}")
        
        print("\n3. Generating report...")
        report_result = generate_sales_report(**context)
        print(f"   ✅ Report: {report_result}")
        
        print("\n4. Checking generated files...")
        import os
        files = ['/tmp/raw_sales_data.csv', '/tmp/transformed_sales_data.csv', '/tmp/sales_report.json']
        for file in files:
            if os.path.exists(file):
                print(f"   ✅ {file} created")
            else:
                print(f"   ❌ {file} missing")
        
        print("\n🎉 Pipeline test completed successfully!")
        print("\nGenerated files:")
        print("- /tmp/raw_sales_data.csv")
        print("- /tmp/transformed_sales_data.csv") 
        print("- /tmp/sales_report.json")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")