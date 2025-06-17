-- Daily Sales Summary Query
-- This query aggregates daily sales data into summary metrics
-- Designed to run within BigQuery free tier limits (1TB queries/month)

-- Use this as a scheduled query in BigQuery (free tier includes scheduled queries)
-- Or call it from a Cloud Function

-- Insert daily summary data
INSERT INTO `sales_pipeline.daily_sales_summary` (
  summary_date,
  total_orders,
  total_revenue,
  average_order_value,
  unique_customers,
  north_region_revenue,
  south_region_revenue,
  east_region_revenue,
  west_region_revenue,
  online_revenue,
  retail_revenue,
  mobile_revenue,
  widgets_revenue,
  gadgets_revenue,
  other_revenue,
  data_quality_issues_count
)

-- Main aggregation query
WITH daily_metrics AS (
  SELECT 
    order_date as summary_date,
    
    -- Overall metrics
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as average_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    
    -- Regional breakdown
    SUM(CASE WHEN region = 'North' THEN total_amount ELSE 0 END) as north_region_revenue,
    SUM(CASE WHEN region = 'South' THEN total_amount ELSE 0 END) as south_region_revenue,
    SUM(CASE WHEN region = 'East' THEN total_amount ELSE 0 END) as east_region_revenue,
    SUM(CASE WHEN region = 'West' THEN total_amount ELSE 0 END) as west_region_revenue,
    
    -- Channel breakdown
    SUM(CASE WHEN channel = 'Online' THEN total_amount ELSE 0 END) as online_revenue,
    SUM(CASE WHEN channel = 'Retail' THEN total_amount ELSE 0 END) as retail_revenue,
    SUM(CASE WHEN channel = 'Mobile' THEN total_amount ELSE 0 END) as mobile_revenue,
    
    -- Product category breakdown
    SUM(CASE WHEN product_category = 'Widgets' THEN total_amount ELSE 0 END) as widgets_revenue,
    SUM(CASE WHEN product_category = 'Gadgets' THEN total_amount ELSE 0 END) as gadgets_revenue,
    SUM(CASE WHEN product_category NOT IN ('Widgets', 'Gadgets') THEN total_amount ELSE 0 END) as other_revenue,
    
    -- Data quality metrics
    SUM(CASE WHEN has_data_quality_issues THEN 1 ELSE 0 END) as data_quality_issues_count
    
  FROM `sales_pipeline.transformed_sales_data`
  WHERE order_date = CURRENT_DATE() - 1  -- Yesterday's data
  -- For backfill: WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
  GROUP BY order_date
)

SELECT * FROM daily_metrics;

-- Optional: Delete existing summary for the date to avoid duplicates
-- DELETE FROM `sales_pipeline.daily_sales_summary` 
-- WHERE summary_date = CURRENT_DATE() - 1;