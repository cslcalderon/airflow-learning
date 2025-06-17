-- BigQuery Setup for Sales Pipeline
-- Run these commands in BigQuery console or via bq CLI
-- Free tier: 10GB storage, 1TB queries per month

-- Create dataset for the pipeline
-- Run: bq mk --dataset --location=US sales_pipeline
CREATE SCHEMA IF NOT EXISTS `sales_pipeline`
OPTIONS (
  description = "Sales data pipeline dataset",
  location = "US"  -- US multi-region is free tier eligible
);

-- Raw sales data table (where Cloud Functions insert data)
CREATE OR REPLACE TABLE `sales_pipeline.raw_sales_data` (
  order_id INT64,
  customer_id INT64,
  product STRING,
  quantity INT64,
  price FLOAT64,
  total_amount FLOAT64,
  order_date DATE,
  region STRING,
  channel STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY order_date  -- Partition by date for better performance and cost control
CLUSTER BY region, product  -- Cluster frequently queried columns
OPTIONS (
  description = "Raw sales data from source systems",
  partition_expiration_days = 90  -- Auto-delete old partitions to save storage
);

-- Transformed sales data table (output of transformation function)
CREATE OR REPLACE TABLE `sales_pipeline.transformed_sales_data` (
  order_id INT64,
  customer_id INT64,
  product STRING,
  quantity INT64,
  price FLOAT64,
  total_amount FLOAT64,
  order_date DATE,
  region STRING,
  channel STRING,
  
  -- Business enrichment columns
  order_category STRING,  -- High/Medium/Low value
  product_category STRING,  -- Widgets/Gadgets/Other
  
  -- Time-based features
  day_of_week INT64,
  month INT64,
  quarter INT64,
  
  -- Customer analytics
  customer_order_sequence INT64,
  
  -- Financial calculations
  revenue FLOAT64,
  estimated_profit FLOAT64,
  
  -- Data quality flags
  has_data_quality_issues BOOL,
  processed_at TIMESTAMP
)
PARTITION BY order_date
CLUSTER BY region, product_category
OPTIONS (
  description = "Transformed and enriched sales data",
  partition_expiration_days = 365
);

-- Daily summary table for reporting
CREATE OR REPLACE TABLE `sales_pipeline.daily_sales_summary` (
  summary_date DATE,
  total_orders INT64,
  total_revenue FLOAT64,
  average_order_value FLOAT64,
  unique_customers INT64,
  
  -- Regional breakdown
  north_region_revenue FLOAT64,
  south_region_revenue FLOAT64,
  east_region_revenue FLOAT64,
  west_region_revenue FLOAT64,
  
  -- Channel breakdown  
  online_revenue FLOAT64,
  retail_revenue FLOAT64,
  mobile_revenue FLOAT64,
  
  -- Product breakdown
  widgets_revenue FLOAT64,
  gadgets_revenue FLOAT64,
  other_revenue FLOAT64,
  
  -- Quality metrics
  data_quality_issues_count INT64,
  processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY summary_date
OPTIONS (
  description = "Daily aggregated sales metrics for reporting",
  partition_expiration_days = 1095  -- Keep 3 years of daily summaries
);

-- Create views for common queries (views don't use storage)
CREATE OR REPLACE VIEW `sales_pipeline.current_month_sales` AS
SELECT 
  order_date,
  COUNT(*) as orders,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_order_value
FROM `sales_pipeline.transformed_sales_data`
WHERE order_date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY order_date
ORDER BY order_date;

CREATE OR REPLACE VIEW `sales_pipeline.top_customers` AS
SELECT 
  customer_id,
  COUNT(*) as order_count,
  SUM(total_amount) as total_spent,
  AVG(total_amount) as avg_order_value,
  MAX(order_date) as last_order_date
FROM `sales_pipeline.transformed_sales_data`
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY customer_id
HAVING COUNT(*) > 1  -- Repeat customers only
ORDER BY total_spent DESC
LIMIT 100;

CREATE OR REPLACE VIEW `sales_pipeline.product_performance` AS
SELECT 
  product,
  product_category,
  COUNT(*) as times_sold,
  SUM(quantity) as total_quantity,
  SUM(total_amount) as total_revenue,
  AVG(price) as avg_price
FROM `sales_pipeline.transformed_sales_data`
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY product, product_category
ORDER BY total_revenue DESC;