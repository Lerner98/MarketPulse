-- ============================================================================
-- MARKETPULSE V9 PRODUCTION SCHEMA
-- ============================================================================
-- Based on table_11_v9_flat.csv (558 rows, clean, no negatives, full tail)
-- and table_38_v6.csv (8 real CBS store types)
--
-- Design: 3-table split for business insights
-- - household_profiles: WHO they are (demographics)
-- - household_expenditures: WHAT they spend (products/services)
-- - retail_competition: WHERE they buy (8 CBS store types)
-- ============================================================================

-- Drop existing tables
DROP TABLE IF EXISTS household_profiles CASCADE;
DROP TABLE IF EXISTS household_expenditures CASCADE;
DROP TABLE IF EXISTS retail_competition CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_inequality_gap CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_burn_rate CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_fresh_food_battle CASCADE;

-- ============================================================================
-- 1. HOUSEHOLD PROFILES (Demographics - "Who")
-- ============================================================================
-- Top ~20-30 rows from Table 11: household size, income, age, education

CREATE TABLE household_profiles (
    metric_name VARCHAR(500) PRIMARY KEY,
    q5_val NUMERIC(12, 2),  -- Top 20% income quintile
    q4_val NUMERIC(12, 2),
    q3_val NUMERIC(12, 2),
    q2_val NUMERIC(12, 2),
    q1_val NUMERIC(12, 2),  -- Bottom 20% income quintile
    total_val NUMERIC(12, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_profiles_metric ON household_profiles(metric_name);

COMMENT ON TABLE household_profiles IS 'Demographics: household size, income, age, education by quintile';
COMMENT ON COLUMN household_profiles.q5_val IS 'Top 20% income quintile (richest)';
COMMENT ON COLUMN household_profiles.q1_val IS 'Bottom 20% income quintile (poorest)';

-- ============================================================================
-- 2. HOUSEHOLD EXPENDITURES (Spending - "What")
-- ============================================================================
-- Bottom ~530 rows from Table 11: actual spending on products/services
-- CRITICAL: Includes Mortgage, Savings, Renovations (from v9 tail)

CREATE TABLE household_expenditures (
    item_name VARCHAR(500) PRIMARY KEY,
    q5_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,  -- Top 20% spending
    q4_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,
    q3_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,
    q2_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,
    q1_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,  -- Bottom 20% spending
    total_spend NUMERIC(12, 2) NOT NULL DEFAULT 0,

    -- Business metric: Inequality Index (Q5/Q1 ratio)
    inequality_index NUMERIC(10, 2) GENERATED ALWAYS AS (
        CASE
            WHEN q1_spend > 0 THEN ROUND(q5_spend / q1_spend, 2)
            ELSE 0
        END
    ) STORED,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expenditures_item ON household_expenditures(item_name);
CREATE INDEX idx_expenditures_total ON household_expenditures(total_spend DESC);
CREATE INDEX idx_expenditures_inequality ON household_expenditures(inequality_index DESC);

COMMENT ON TABLE household_expenditures IS 'Spending by product/service category with inequality metrics';
COMMENT ON COLUMN household_expenditures.inequality_index IS 'Q5/Q1 spending ratio - shows wealth gap per category';

-- ============================================================================
-- 3. RETAIL COMPETITION (Store Types - "Where")
-- ============================================================================
-- From Table 38: 8 REAL CBS store types (fixed from v6)
-- PERCENTAGES (sum to 100 per category)

CREATE TABLE retail_competition (
    category VARCHAR(500) PRIMARY KEY,

    -- 8 CBS Store Types (Column B-I in original Excel)
    other_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,                    -- Column B
    special_shop_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,            -- Column C (wine/specialty)
    butcher_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,                 -- Column D
    veg_fruit_shop_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,          -- Column E
    online_supermarket_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,      -- Column F
    supermarket_chain_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,       -- Column G (MAIN CHANNEL)
    market_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,                  -- Column H (outdoor markets)
    grocery_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,                 -- Column I (corner stores)

    total_pct NUMERIC(5, 2) NOT NULL,  -- Should equal 100

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT check_total_pct CHECK (total_pct BETWEEN 99.0 AND 101.0)
);

CREATE INDEX idx_retail_category ON retail_competition(category);
CREATE INDEX idx_retail_supermarket ON retail_competition(supermarket_chain_pct DESC);
CREATE INDEX idx_retail_market ON retail_competition(market_pct DESC);

COMMENT ON TABLE retail_competition IS 'Food retail market share by 8 CBS store types (percentages)';
COMMENT ON COLUMN retail_competition.supermarket_chain_pct IS 'Main retail channel - supermarket chains';
COMMENT ON COLUMN retail_competition.market_pct IS 'Traditional outdoor markets (shuk)';

-- ============================================================================
-- MATERIALIZED VIEWS (Business Insights)
-- ============================================================================

-- View 1: Inequality Gap Analysis
-- Shows which categories have the biggest spending gap between rich and poor
CREATE MATERIALIZED VIEW vw_inequality_gap AS
SELECT
    item_name,
    q5_spend as rich_spend,
    q1_spend as poor_spend,
    inequality_index as gap_ratio,
    total_spend
FROM household_expenditures
WHERE q1_spend > 20  -- Filter noise (statistical reliability)
  AND inequality_index > 2  -- Only show meaningful gaps
ORDER BY inequality_index DESC;

CREATE INDEX ON vw_inequality_gap(gap_ratio DESC);

COMMENT ON MATERIALIZED VIEW vw_inequality_gap IS 'Categories with highest spending inequality (Q5/Q1 ratio)';

-- View 2: Burn Rate Analysis
-- Shows how much of income is consumed by spending (financial pressure)
CREATE MATERIALIZED VIEW vw_burn_rate AS
WITH income AS (
    SELECT
        q5_val as inc_q5,
        q4_val as inc_q4,
        q3_val as inc_q3,
        q2_val as inc_q2,
        q1_val as inc_q1,
        total_val as inc_total
    FROM household_profiles
    WHERE metric_name LIKE '%Net money income per household%'
),
spending AS (
    SELECT
        q5_spend as sp_q5,
        q4_spend as sp_q4,
        q3_spend as sp_q3,
        q2_spend as sp_q2,
        q1_spend as sp_q1,
        total_spend as sp_total
    FROM household_expenditures
    WHERE item_name LIKE '%Consumption expenditures%total%'
)
SELECT
    ROUND((sp_q5 / NULLIF(inc_q5, 0)) * 100, 1) as q5_burn_rate_pct,
    ROUND((sp_q4 / NULLIF(inc_q4, 0)) * 100, 1) as q4_burn_rate_pct,
    ROUND((sp_q3 / NULLIF(inc_q3, 0)) * 100, 1) as q3_burn_rate_pct,
    ROUND((sp_q2 / NULLIF(inc_q2, 0)) * 100, 1) as q2_burn_rate_pct,
    ROUND((sp_q1 / NULLIF(inc_q1, 0)) * 100, 1) as q1_burn_rate_pct,
    ROUND((sp_total / NULLIF(inc_total, 0)) * 100, 1) as total_burn_rate_pct
FROM income, spending;

COMMENT ON MATERIALIZED VIEW vw_burn_rate IS 'Percentage of income consumed by spending (financial pressure indicator)';

-- View 3: Fresh Food Battle
-- Shows where traditional retail (markets) beats supermarkets
CREATE MATERIALIZED VIEW vw_fresh_food_battle AS
SELECT
    category,
    market_pct,
    grocery_pct,
    (market_pct + grocery_pct + special_shop_pct) as traditional_retail_pct,
    supermarket_chain_pct,
    (market_pct + grocery_pct + special_shop_pct - supermarket_chain_pct) as traditional_advantage,
    CASE
        WHEN (market_pct + grocery_pct) > supermarket_chain_pct THEN 'Traditional Wins'
        ELSE 'Supermarket Wins'
    END as winner
FROM retail_competition
WHERE (market_pct + grocery_pct + special_shop_pct) > 20  -- Significant traditional presence
ORDER BY (market_pct + grocery_pct + special_shop_pct) DESC;

CREATE INDEX ON vw_fresh_food_battle(traditional_retail_pct DESC);

COMMENT ON MATERIALIZED VIEW vw_fresh_food_battle IS 'Categories where traditional retail outcompetes supermarkets';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW vw_inequality_gap;
    REFRESH MATERIALIZED VIEW vw_burn_rate;
    REFRESH MATERIALIZED VIEW vw_fresh_food_battle;

    RAISE NOTICE 'All materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- Get inequality gap summary with business insight
CREATE OR REPLACE FUNCTION get_inequality_summary(limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    category VARCHAR,
    rich_spend NUMERIC,
    poor_spend NUMERIC,
    gap_ratio NUMERIC,
    insight TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        item_name::VARCHAR,
        rich_spend,
        poor_spend,
        gap_ratio,
        ('Q5 spends ' || gap_ratio::TEXT || 'x more than Q1 on ' || item_name)::TEXT
    FROM vw_inequality_gap
    ORDER BY gap_ratio DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Get burn rate with financial pressure insight
CREATE OR REPLACE FUNCTION get_burn_rate_summary()
RETURNS TABLE(
    quintile TEXT,
    burn_rate_pct NUMERIC,
    financial_pressure TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'Q5 (Richest)'::TEXT,
        q5_burn_rate_pct,
        CASE
            WHEN q5_burn_rate_pct > 80 THEN 'High Pressure'
            WHEN q5_burn_rate_pct > 60 THEN 'Moderate Pressure'
            ELSE 'Low Pressure'
        END::TEXT
    FROM vw_burn_rate
    UNION ALL
    SELECT
        'Q1 (Poorest)'::TEXT,
        q1_burn_rate_pct,
        CASE
            WHEN q1_burn_rate_pct > 100 THEN 'Debt/Crisis'
            WHEN q1_burn_rate_pct > 90 THEN 'Critical Pressure'
            WHEN q1_burn_rate_pct > 80 THEN 'High Pressure'
            ELSE 'Moderate Pressure'
        END::TEXT
    FROM vw_burn_rate;
END;
$$ LANGUAGE plpgsql;

-- Get fresh food battle winners
CREATE OR REPLACE FUNCTION get_fresh_food_winners(limit_count INTEGER DEFAULT 5)
RETURNS TABLE(
    category VARCHAR,
    traditional_pct NUMERIC,
    supermarket_pct NUMERIC,
    advantage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        category::VARCHAR,
        traditional_retail_pct,
        supermarket_chain_pct,
        traditional_advantage
    FROM vw_fresh_food_battle
    WHERE winner = 'Traditional Wins'
    ORDER BY traditional_advantage DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DATA QUALITY CONSTRAINTS
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_timestamp
    BEFORE UPDATE ON household_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenditures_timestamp
    BEFORE UPDATE ON household_expenditures
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_retail_timestamp
    BEFORE UPDATE ON retail_competition
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ MarketPulse V9 Production Schema Created';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables:';
    RAISE NOTICE '  - household_profiles (demographics)';
    RAISE NOTICE '  - household_expenditures (spending with inequality_index)';
    RAISE NOTICE '  - retail_competition (8 CBS store types)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views:';
    RAISE NOTICE '  - vw_inequality_gap';
    RAISE NOTICE '  - vw_burn_rate';
    RAISE NOTICE '  - vw_fresh_food_battle';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Load data: python backend/etl/load_v9_production.py';
    RAISE NOTICE '  2. Refresh views: SELECT refresh_all_views();';
    RAISE NOTICE '  3. Test insights: SELECT * FROM get_inequality_summary(5);';
END $$;
