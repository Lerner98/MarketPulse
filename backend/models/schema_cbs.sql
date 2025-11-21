-- MarketPulse CBS Database Schema
-- PostgreSQL 15+
-- Updated: 2025-11-20
-- Purpose: Israeli CBS Household Expenditure Analytics Platform
--
-- This schema supports the PROPER CBS data with 10 columns:
-- transaction_id, customer_name, product, category, amount, currency,
-- transaction_date, status, customer_city, income_quintile

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search on Hebrew

-- Drop existing tables if recreating schema
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS data_quality_metrics CASCADE;
DROP TABLE IF EXISTS business_insights CASCADE;

-- ============================================================================
-- MAIN TRANSACTIONS TABLE (CBS Schema)
-- ============================================================================

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id INTEGER UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    product VARCHAR(500) NOT NULL,  -- Hebrew product names can be longer
    category VARCHAR(255) NOT NULL,  -- CBS category (מזון ומשקאות, דיור, etc.)
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= -10000 AND amount <= 1000000),
    currency VARCHAR(3) NOT NULL DEFAULT 'ILS' CHECK (currency = 'ILS'),
    transaction_date DATE NOT NULL CHECK (transaction_date >= '2020-01-01'),
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'pending', 'cancelled')),
    customer_city VARCHAR(255) NOT NULL,  -- Hebrew city names
    income_quintile INTEGER NOT NULL CHECK (income_quintile BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_customer ON transactions(customer_name);
CREATE INDEX idx_transactions_product ON transactions USING gin(product gin_trgm_ops);  -- Hebrew text search
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_city ON transactions(customer_city);
CREATE INDEX idx_transactions_quintile ON transactions(income_quintile);
CREATE INDEX idx_transactions_amount ON transactions(amount) WHERE amount > 0;

-- Composite indexes for common queries
CREATE INDEX idx_transactions_date_status ON transactions(transaction_date DESC, status);
CREATE INDEX idx_transactions_category_date ON transactions(category, transaction_date DESC);
CREATE INDEX idx_transactions_city_quintile ON transactions(customer_city, income_quintile);

-- ============================================================================
-- DATA QUALITY METRICS TABLE
-- ============================================================================

CREATE TABLE data_quality_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    total_records INTEGER NOT NULL,
    missing_values INTEGER NOT NULL DEFAULT 0,
    duplicate_records INTEGER NOT NULL DEFAULT 0,
    outlier_records INTEGER NOT NULL DEFAULT 0,
    completeness_score NUMERIC(5, 2) NOT NULL CHECK (completeness_score BETWEEN 0 AND 100),
    uniqueness_score NUMERIC(5, 2) NOT NULL CHECK (uniqueness_score BETWEEN 0 AND 100),
    validity_score NUMERIC(5, 2) NOT NULL CHECK (validity_score BETWEEN 0 AND 100),
    overall_quality_score NUMERIC(5, 2) NOT NULL CHECK (overall_quality_score BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quality_metrics_date ON data_quality_metrics(metric_date DESC);

-- ============================================================================
-- BUSINESS INSIGHTS TABLE (From EDA)
-- ============================================================================

CREATE TABLE business_insights (
    id BIGSERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,  -- 'quintile', 'category', 'city', 'product', 'seasonal'
    insight_key VARCHAR(255) NOT NULL,  -- e.g., 'Q5', 'מזון ומשקאות', 'תל אביב'
    metric_name VARCHAR(100) NOT NULL,  -- e.g., 'total_revenue', 'avg_transaction', 'market_share_pct'
    metric_value NUMERIC(15, 2) NOT NULL,
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_insights_type_key ON business_insights(insight_type, insight_key);
CREATE INDEX idx_insights_period ON business_insights(period_start, period_end);

-- ============================================================================
-- AUTO-UPDATE TRIGGERS
-- ============================================================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to transactions
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply to business_insights
CREATE TRIGGER update_insights_updated_at
    BEFORE UPDATE ON business_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Insert transaction (SQL injection prevention)
CREATE OR REPLACE PROCEDURE insert_transaction(
    p_transaction_id INTEGER,
    p_customer_name VARCHAR(255),
    p_product VARCHAR(500),
    p_category VARCHAR(255),
    p_amount NUMERIC(12, 2),
    p_currency VARCHAR(3),
    p_transaction_date DATE,
    p_status VARCHAR(20),
    p_customer_city VARCHAR(255),
    p_income_quintile INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO transactions (
        transaction_id,
        customer_name,
        product,
        category,
        amount,
        currency,
        transaction_date,
        status,
        customer_city,
        income_quintile
    ) VALUES (
        p_transaction_id,
        p_customer_name,
        p_product,
        p_category,
        p_amount,
        p_currency,
        p_transaction_date,
        p_status,
        p_customer_city,
        p_income_quintile
    )
    ON CONFLICT (transaction_id) DO UPDATE SET
        customer_name = EXCLUDED.customer_name,
        product = EXCLUDED.product,
        category = EXCLUDED.category,
        amount = EXCLUDED.amount,
        currency = EXCLUDED.currency,
        transaction_date = EXCLUDED.transaction_date,
        status = EXCLUDED.status,
        customer_city = EXCLUDED.customer_city,
        income_quintile = EXCLUDED.income_quintile,
        updated_at = NOW();
END;
$$;

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Daily aggregates (refresh once per day)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_revenue AS
SELECT
    transaction_date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    COUNT(DISTINCT customer_name) as unique_customers,
    COUNT(DISTINCT product) as unique_products
FROM transactions
WHERE status = 'completed'
GROUP BY transaction_date
ORDER BY transaction_date DESC;

CREATE UNIQUE INDEX ON mv_daily_revenue(transaction_date);

-- Category performance (refresh as needed)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_performance AS
SELECT
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    COUNT(DISTINCT customer_name) as unique_customers,
    COUNT(DISTINCT product) as unique_products,
    (SUM(amount) / (SELECT SUM(amount) FROM transactions WHERE status = 'completed')) * 100 as market_share_pct
FROM transactions
WHERE status = 'completed'
GROUP BY category
ORDER BY total_revenue DESC;

CREATE UNIQUE INDEX ON mv_category_performance(category);

-- City performance
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_city_performance AS
SELECT
    customer_city,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    COUNT(DISTINCT customer_name) as unique_customers,
    (SUM(amount) / (SELECT SUM(amount) FROM transactions WHERE status = 'completed')) * 100 as market_share_pct
FROM transactions
WHERE status = 'completed'
GROUP BY customer_city
ORDER BY total_revenue DESC;

CREATE UNIQUE INDEX ON mv_city_performance(customer_city);

-- Income quintile analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_quintile_analysis AS
SELECT
    income_quintile,
    COUNT(*) as transaction_count,
    SUM(amount) as total_spending,
    AVG(amount) as avg_transaction,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_transaction,
    COUNT(DISTINCT customer_name) as unique_customers,
    (SUM(amount) / (SELECT SUM(amount) FROM transactions WHERE status = 'completed')) * 100 as spending_share_pct
FROM transactions
WHERE status = 'completed'
GROUP BY income_quintile
ORDER BY income_quintile;

CREATE UNIQUE INDEX ON mv_quintile_analysis(income_quintile);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_city_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_quintile_analysis;
END;
$$ LANGUAGE plpgsql;

-- Calculate data quality score
CREATE OR REPLACE FUNCTION calculate_data_quality()
RETURNS TABLE(
    completeness NUMERIC,
    uniqueness NUMERIC,
    validity NUMERIC,
    overall NUMERIC
) AS $$
DECLARE
    total_records INTEGER;
    complete_records INTEGER;
    unique_records INTEGER;
    valid_records INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_records FROM transactions;

    -- Completeness (no nulls in required fields)
    SELECT COUNT(*) INTO complete_records
    FROM transactions
    WHERE customer_name IS NOT NULL
      AND product IS NOT NULL
      AND category IS NOT NULL
      AND amount IS NOT NULL
      AND customer_city IS NOT NULL;

    -- Uniqueness (no duplicate transaction_ids)
    SELECT COUNT(DISTINCT transaction_id) INTO unique_records FROM transactions;

    -- Validity (data within expected ranges)
    SELECT COUNT(*) INTO valid_records
    FROM transactions
    WHERE amount > -10000 AND amount < 1000000
      AND income_quintile BETWEEN 1 AND 5
      AND transaction_date >= '2020-01-01';

    RETURN QUERY
    SELECT
        ROUND((complete_records::NUMERIC / total_records::NUMERIC) * 100, 2) as completeness,
        ROUND((unique_records::NUMERIC / total_records::NUMERIC) * 100, 2) as uniqueness,
        ROUND((valid_records::NUMERIC / total_records::NUMERIC) * 100, 2) as validity,
        ROUND((
            ((complete_records::NUMERIC / total_records::NUMERIC) * 0.4 +
             (unique_records::NUMERIC / total_records::NUMERIC) * 0.3 +
             (valid_records::NUMERIC / total_records::NUMERIC) * 0.3)
        ) * 100, 2) as overall;
END;
$$ LANGUAGE plpgsql;

-- Get top products
CREATE OR REPLACE FUNCTION get_top_products(limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    product VARCHAR,
    transaction_count BIGINT,
    total_revenue NUMERIC,
    avg_price NUMERIC,
    unique_customers BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.product,
        COUNT(*)::BIGINT as transaction_count,
        SUM(t.amount) as total_revenue,
        AVG(t.amount) as avg_price,
        COUNT(DISTINCT t.customer_name)::BIGINT as unique_customers
    FROM transactions t
    WHERE t.status = 'completed'
    GROUP BY t.product
    ORDER BY total_revenue DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Get revenue by date range
CREATE OR REPLACE FUNCTION get_revenue_by_date_range(
    start_date DATE,
    end_date DATE
)
RETURNS TABLE(
    transaction_date DATE,
    total_revenue NUMERIC,
    transaction_count BIGINT,
    avg_transaction NUMERIC,
    unique_customers BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.transaction_date,
        SUM(t.amount) as total_revenue,
        COUNT(*)::BIGINT as transaction_count,
        AVG(t.amount) as avg_transaction,
        COUNT(DISTINCT t.customer_name)::BIGINT as unique_customers
    FROM transactions t
    WHERE t.status = 'completed'
      AND t.transaction_date BETWEEN start_date AND end_date
    GROUP BY t.transaction_date
    ORDER BY t.transaction_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA VALIDATION
-- ============================================================================

-- Validate CBS schema compliance
CREATE OR REPLACE FUNCTION validate_cbs_schema()
RETURNS TABLE(
    check_name VARCHAR,
    status VARCHAR,
    details TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'Column Count'::VARCHAR,
        CASE WHEN COUNT(*) = 12 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Expected 12 columns (10 CBS + 2 timestamps), found: ' || COUNT(*)::TEXT)::TEXT
    FROM information_schema.columns
    WHERE table_name = 'transactions';

    RETURN QUERY
    SELECT
        'Currency Check'::VARCHAR,
        CASE WHEN COUNT(*) = COUNT(*) FILTER (WHERE currency = 'ILS') THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        'All transactions should be in ILS'::TEXT
    FROM transactions;

    RETURN QUERY
    SELECT
        'Quintile Range'::VARCHAR,
        CASE WHEN MIN(income_quintile) >= 1 AND MAX(income_quintile) <= 5 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Quintile range: ' || MIN(income_quintile)::TEXT || ' to ' || MAX(income_quintile)::TEXT)::TEXT
    FROM transactions;

    RETURN QUERY
    SELECT
        'Hebrew Text'::VARCHAR,
        CASE WHEN COUNT(*) > 0 THEN 'PASS'::VARCHAR ELSE 'FAIL'::VARCHAR END,
        ('Products with Hebrew characters: ' || COUNT(*)::TEXT)::TEXT
    FROM transactions
    WHERE product ~ '[\u0590-\u05FF]';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS (adjust for your users)
-- ============================================================================

-- Grant read access to application user (adjust username)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO marketpulse_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO marketpulse_app;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'CBS schema created successfully!';
    RAISE NOTICE 'Run validation: SELECT * FROM validate_cbs_schema();';
    RAISE NOTICE 'Check quality: SELECT * FROM calculate_data_quality();';
END $$;
