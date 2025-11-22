-- Strategic CBS Analysis Tables
-- For the 3 hero datasets: Tables 1.1, 40, 38
-- PostgreSQL 15+

-- Drop existing tables if recreating
DROP TABLE IF EXISTS quintile_expenditure CASCADE;
DROP TABLE IF EXISTS purchase_methods CASCADE;
DROP TABLE IF EXISTS store_competition CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_quintile_gap CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_digital_matrix CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_retail_battle CASCADE;

-- ============================================================================
-- TABLE 1.1: Quintile Expenditure
-- ============================================================================

CREATE TABLE quintile_expenditure (
    id SERIAL PRIMARY KEY,
    category VARCHAR(500) NOT NULL,  -- Hebrew product category
    quintile_1 NUMERIC(12, 2) NOT NULL DEFAULT 0,  -- Lowest income
    quintile_2 NUMERIC(12, 2) NOT NULL DEFAULT 0,
    quintile_3 NUMERIC(12, 2) NOT NULL DEFAULT 0,
    quintile_4 NUMERIC(12, 2) NOT NULL DEFAULT 0,
    quintile_5 NUMERIC(12, 2) NOT NULL DEFAULT 0,  -- Highest income
    total_spending NUMERIC(12, 2) NOT NULL,
    avg_spending NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quintile_category ON quintile_expenditure(category);
CREATE INDEX idx_quintile_total ON quintile_expenditure(total_spending DESC);

-- ============================================================================
-- TABLE 40: Purchase Methods (Digital vs Physical)
-- ============================================================================

CREATE TABLE purchase_methods (
    id SERIAL PRIMARY KEY,
    category VARCHAR(500) NOT NULL,  -- Hebrew product category
    physical_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,     -- Physical store %
    online_israel_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,  -- Online Israel %
    online_abroad_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,  -- Online Abroad %
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_purchase_category ON purchase_methods(category);
CREATE INDEX idx_purchase_online_israel ON purchase_methods(online_israel_pct DESC);
CREATE INDEX idx_purchase_online_abroad ON purchase_methods(online_abroad_pct DESC);

-- ============================================================================
-- TABLE 38: Store Competition (Retail Battle)
-- ============================================================================

CREATE TABLE store_competition (
    id SERIAL PRIMARY KEY,
    category VARCHAR(500) NOT NULL,  -- Food category (English)
    supermarket NUMERIC(5, 2) NOT NULL DEFAULT 0,  -- Supermarket %
    local_market NUMERIC(5, 2) NOT NULL DEFAULT 0,  -- Local market/Shuk %
    butcher NUMERIC(5, 2) NOT NULL DEFAULT 0,       -- Butcher %
    bakery NUMERIC(5, 2) NOT NULL DEFAULT 0,        -- Bakery %
    other NUMERIC(5, 2) NOT NULL DEFAULT 0,         -- Other stores %
    total NUMERIC(5, 2) NOT NULL,                   -- Total (should = 100)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_store_category ON store_competition(category);
CREATE INDEX idx_store_supermarket ON store_competition(supermarket DESC);
CREATE INDEX idx_store_local ON store_competition(local_market DESC);

-- ============================================================================
-- MATERIALIZED VIEWS (For Fast Queries)
-- ============================================================================

-- View 1: The 2.62x Rule (Quintile Gap)
CREATE MATERIALIZED VIEW vw_quintile_gap AS
SELECT
    (SELECT SUM(quintile_5) FROM quintile_expenditure) as q5_total,
    (SELECT SUM(quintile_1) FROM quintile_expenditure) as q1_total,
    ROUND(
        (SELECT SUM(quintile_5) FROM quintile_expenditure) /
        NULLIF((SELECT SUM(quintile_1) FROM quintile_expenditure), 0),
        2
    ) as spending_ratio
;

-- View 2: Digital Opportunity Matrix
CREATE MATERIALIZED VIEW vw_digital_matrix AS
SELECT
    category,
    physical_pct,
    online_israel_pct,
    online_abroad_pct,
    (online_israel_pct + online_abroad_pct) as total_online_pct
FROM purchase_methods
ORDER BY online_israel_pct DESC;

CREATE INDEX ON vw_digital_matrix(online_israel_pct DESC);
CREATE INDEX ON vw_digital_matrix(online_abroad_pct DESC);

-- View 3: Retail Battle (Market Shares)
CREATE MATERIALIZED VIEW vw_retail_battle AS
SELECT
    category,
    supermarket,
    local_market,
    butcher,
    bakery,
    other,
    total,
    CASE
        WHEN local_market > supermarket THEN 'Local Market Wins'
        WHEN supermarket > local_market THEN 'Supermarket Wins'
        ELSE 'Tie'
    END as winner
FROM store_competition
ORDER BY local_market DESC;

CREATE INDEX ON vw_retail_battle(supermarket DESC);
CREATE INDEX ON vw_retail_battle(local_market DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Refresh all strategic materialized views
CREATE OR REPLACE FUNCTION refresh_strategic_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY vw_quintile_gap;
    REFRESH MATERIALIZED VIEW CONCURRENTLY vw_digital_matrix;
    REFRESH MATERIALIZED VIEW CONCURRENTLY vw_retail_battle;
END;
$$ LANGUAGE plpgsql;

-- Get quintile gap summary
CREATE OR REPLACE FUNCTION get_quintile_gap_summary()
RETURNS TABLE(
    q5_total NUMERIC,
    q1_total NUMERIC,
    spending_ratio NUMERIC,
    insight TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vw.q5_total,
        vw.q1_total,
        vw.spending_ratio,
        ('High-income households (Q5) spend ' || vw.spending_ratio::TEXT ||
         'x more than low-income (Q1). Allocate 40% of marketing budget to Q4-Q5 for highest ROI.')::TEXT as insight
    FROM vw_quintile_gap vw;
END;
$$ LANGUAGE plpgsql;

-- Get digital penetration leaders
CREATE OR REPLACE FUNCTION get_digital_leaders(limit_count INTEGER DEFAULT 5)
RETURNS TABLE(
    category VARCHAR,
    online_israel_pct NUMERIC,
    online_abroad_pct NUMERIC,
    total_online_pct NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dm.category,
        dm.online_israel_pct,
        dm.online_abroad_pct,
        dm.total_online_pct
    FROM vw_digital_matrix dm
    ORDER BY dm.online_israel_pct DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Get retail battle losers (where supermarket loses)
CREATE OR REPLACE FUNCTION get_supermarket_losses(limit_count INTEGER DEFAULT 5)
RETURNS TABLE(
    category VARCHAR,
    supermarket NUMERIC,
    local_market NUMERIC,
    gap NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rb.category,
        rb.supermarket,
        rb.local_market,
        (rb.local_market - rb.supermarket) as gap
    FROM vw_retail_battle rb
    WHERE rb.local_market > rb.supermarket
    ORDER BY gap DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Strategic CBS schema created successfully!';
    RAISE NOTICE 'Load data using: python backend/etl/load_strategic_data.py';
    RAISE NOTICE 'Refresh views: SELECT refresh_strategic_views();';
    RAISE NOTICE 'Check quintile gap: SELECT * FROM get_quintile_gap_summary();';
END $$;
