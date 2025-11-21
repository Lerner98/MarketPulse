-- MarketPulse Advanced Database Schema
-- PostgreSQL 15+
-- Created: 2025-11-20
-- Purpose: E-commerce analytics platform for Israeli market

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables and views (careful in production!)
DROP VIEW IF EXISTS v_customer_journey CASCADE;
DROP VIEW IF EXISTS v_customer_analytics CASCADE;
DROP VIEW IF EXISTS v_product_performance CASCADE;
DROP VIEW IF EXISTS v_daily_revenue CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;

-- Transactions table with comprehensive fields
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Customer information
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    customer_city VARCHAR(255),

    -- Product information
    product_name VARCHAR(255) NOT NULL,
    product_category VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),

    -- Transaction details
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'pending', 'cancelled')),
    payment_method VARCHAR(50) NOT NULL,
    traffic_source VARCHAR(255),
    device_type VARCHAR(20) CHECK (device_type IN ('mobile', 'desktop', 'tablet')),

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_customer_name ON transactions(customer_name);
CREATE INDEX idx_transactions_customer_city ON transactions(customer_city);
CREATE INDEX idx_transactions_product_name ON transactions(product_name);
CREATE INDEX idx_transactions_product_category ON transactions(product_category);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_device ON transactions(device_type);
CREATE INDEX idx_transactions_traffic ON transactions(traffic_source);

-- Auto-update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Analytics Views

-- Daily revenue aggregation
CREATE OR REPLACE VIEW v_daily_revenue AS
SELECT
    DATE(timestamp) as date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction_value,
    COUNT(DISTINCT customer_name) as unique_customers,
    SUM(CASE WHEN device_type = 'mobile' THEN 1 ELSE 0 END) as mobile_transactions,
    SUM(CASE WHEN device_type = 'desktop' THEN 1 ELSE 0 END) as desktop_transactions,
    SUM(CASE WHEN device_type = 'tablet' THEN 1 ELSE 0 END) as tablet_transactions
FROM transactions
WHERE status = 'completed'
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Product performance metrics
CREATE OR REPLACE VIEW v_product_performance AS
SELECT
    product_category,
    product_name,
    COUNT(*) as total_transactions,
    SUM(quantity) as total_units_sold,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_price,
    COUNT(DISTINCT customer_name) as unique_customers,
    MAX(timestamp) as last_sold
FROM transactions
WHERE status = 'completed'
GROUP BY product_category, product_name
ORDER BY total_revenue DESC;

-- Customer analytics
CREATE OR REPLACE VIEW v_customer_analytics AS
SELECT
    customer_name,
    customer_city,
    COUNT(*) as transaction_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_transaction,
    SUM(quantity) as total_items_purchased,
    MIN(timestamp) as first_purchase,
    MAX(timestamp) as last_purchase,
    EXTRACT(DAYS FROM (MAX(timestamp) - MIN(timestamp))) as customer_lifetime_days
FROM transactions
WHERE status = 'completed'
GROUP BY customer_name, customer_city
ORDER BY total_spent DESC;

-- Traffic source analysis
CREATE OR REPLACE VIEW v_traffic_performance AS
SELECT
    traffic_source,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_name) as unique_customers,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_transactions,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_transactions,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as conversion_rate
FROM transactions
GROUP BY traffic_source
ORDER BY total_revenue DESC;

-- Category performance
CREATE OR REPLACE VIEW v_category_performance AS
SELECT
    product_category,
    COUNT(*) as total_transactions,
    SUM(quantity) as total_units_sold,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction_value,
    COUNT(DISTINCT customer_name) as unique_customers,
    COUNT(DISTINCT product_name) as unique_products
FROM transactions
WHERE status = 'completed'
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Monthly trends
CREATE OR REPLACE VIEW v_monthly_trends AS
SELECT
    DATE_TRUNC('month', timestamp) as month,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_name) as unique_customers,
    SUM(quantity) as total_units_sold
FROM transactions
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', timestamp)
ORDER BY month DESC;

-- Customer journey for Sankey diagram
CREATE OR REPLACE VIEW v_customer_journey AS
SELECT
    traffic_source,
    product_category,
    status,
    COUNT(*) as customer_count,
    SUM(amount) as total_value
FROM transactions
GROUP BY traffic_source, product_category, status
ORDER BY customer_count DESC;

-- Grant permissions (adjust based on your database user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO marketpulse_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO marketpulse_user;
