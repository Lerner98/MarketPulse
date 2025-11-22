-- MarketPulse Database Schema
-- PostgreSQL 15+
-- Created: 2025-11-20
-- Purpose: E-commerce analytics platform database schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id INTEGER UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'ILS',
    transaction_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'pending', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_name);
CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions(product);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);

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

-- Stored procedure for inserting transaction (SQL injection prevention)
CREATE OR REPLACE PROCEDURE insert_transaction(
    p_transaction_id INTEGER,
    p_customer_name VARCHAR(255),
    p_product VARCHAR(255),
    p_amount NUMERIC(10, 2),
    p_currency VARCHAR(3),
    p_transaction_date DATE,
    p_status VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO transactions (
        transaction_id,
        customer_name,
        product,
        amount,
        currency,
        transaction_date,
        status
    ) VALUES (
        p_transaction_id,
        p_customer_name,
        p_product,
        p_amount,
        p_currency,
        p_transaction_date,
        p_status
    )
    ON CONFLICT (transaction_id) DO NOTHING;
END;
$$;

-- Stored procedure for batch insert (better performance)
CREATE OR REPLACE FUNCTION upsert_transaction(
    p_transaction_id INTEGER,
    p_customer_name VARCHAR(255),
    p_product VARCHAR(255),
    p_amount NUMERIC(10, 2),
    p_currency VARCHAR(3),
    p_transaction_date DATE,
    p_status VARCHAR(20)
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO transactions (
        transaction_id,
        customer_name,
        product,
        amount,
        currency,
        transaction_date,
        status
    ) VALUES (
        p_transaction_id,
        p_customer_name,
        p_product,
        p_amount,
        p_currency,
        p_transaction_date,
        p_status
    )
    ON CONFLICT (transaction_id)
    DO UPDATE SET
        customer_name = EXCLUDED.customer_name,
        product = EXCLUDED.product,
        amount = EXCLUDED.amount,
        currency = EXCLUDED.currency,
        transaction_date = EXCLUDED.transaction_date,
        status = EXCLUDED.status,
        updated_at = NOW();
END;
$$;

-- Analytics views for dashboard
CREATE OR REPLACE VIEW v_daily_revenue AS
SELECT
    transaction_date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction_value,
    COUNT(DISTINCT customer_name) as unique_customers
FROM transactions
WHERE status = 'completed'
GROUP BY transaction_date
ORDER BY transaction_date DESC;

CREATE OR REPLACE VIEW v_product_performance AS
SELECT
    product,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_price,
    COUNT(DISTINCT customer_name) as unique_customers
FROM transactions
WHERE status = 'completed'
GROUP BY product
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW v_customer_analytics AS
SELECT
    customer_name,
    COUNT(*) as transaction_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_transaction,
    MIN(transaction_date) as first_purchase,
    MAX(transaction_date) as last_purchase
FROM transactions
WHERE status = 'completed'
GROUP BY customer_name
ORDER BY total_spent DESC;

-- Grant permissions (adjust as needed for production)
-- GRANT SELECT, INSERT, UPDATE ON transactions TO marketpulse_app;
-- GRANT EXECUTE ON PROCEDURE insert_transaction TO marketpulse_app;
-- GRANT EXECUTE ON FUNCTION upsert_transaction TO marketpulse_app;
