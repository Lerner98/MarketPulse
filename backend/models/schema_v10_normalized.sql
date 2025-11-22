-- ============================================================================
-- PHASE 6: NORMALIZED STAR SCHEMA FOR CBS SEGMENTATION DATA
-- ============================================================================
-- Purpose: Support 14+ demographic segmentation dimensions (Age, Income, Education, etc.)
--          using a scalable normalized structure instead of 14 separate tables
--
-- Data Source: CBS 2022 Household Expenditure Survey
-- - Original Table 1.1: 558 rows (29 demographics + 528 spending categories)
-- - New Tables (ta2-ta13+): Same 528 categories, different demographic slices
--
-- Star Schema Design:
-- - dim_segment (Dimension): WHO - Age groups, Income deciles, Education levels, etc.
-- - fact_segment_expenditure (Fact): WHAT + HOW MUCH - Expenditures per segment
-- ============================================================================

-- Drop existing tables if re-creating
DROP TABLE IF EXISTS fact_segment_expenditure CASCADE;
DROP TABLE IF EXISTS dim_segment CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_segment_inequality CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_segment_burn_rate CASCADE;

-- ============================================================================
-- DIMENSION TABLE: Segment Groups (The "WHO")
-- ============================================================================
CREATE TABLE dim_segment (
    segment_key SERIAL PRIMARY KEY,
    segment_type VARCHAR(100) NOT NULL,         -- e.g., 'Income Quintile', 'Age Group', 'Education Level'
    segment_value VARCHAR(200) NOT NULL,        -- e.g., 'Q5 (Rich)', '25-34 years', '16+ Years of Education'
    segment_order INTEGER,                      -- For proper sorting (Q1=1, Q2=2, Age 18-24=1, Age 25-34=2, etc.)
    file_source VARCHAR(100),                   -- e.g., 'table_11_v9_flat.csv', 'ta5.csv' (Age), 'ta12.csv' (Employment)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure no duplicate segments
    CONSTRAINT uq_segment UNIQUE (segment_type, segment_value)
);

-- Index for fast lookups by segment type
CREATE INDEX idx_segment_type ON dim_segment(segment_type);
CREATE INDEX idx_segment_order ON dim_segment(segment_type, segment_order);

-- ============================================================================
-- FACT TABLE: Expenditure Data (The "WHAT" + "HOW MUCH")
-- ============================================================================
CREATE TABLE fact_segment_expenditure (
    expenditure_key SERIAL PRIMARY KEY,
    item_name VARCHAR(500) NOT NULL,            -- e.g., 'Mortgage', 'Food and beverages', 'Transportation'
    segment_key INTEGER NOT NULL,               -- Foreign key to dim_segment
    expenditure_value NUMERIC(12, 2) NOT NULL,  -- Monthly spending in NIS
    metric_type VARCHAR(50) DEFAULT 'Monthly Spend',  -- e.g., 'Monthly Spend', 'Annual Spend', 'Percentage'

    -- CRITICAL DATA INTEGRITY FLAGS (Gemini Fix)
    is_income_metric BOOLEAN DEFAULT FALSE,     -- TRUE only for "Net money income per household"
    is_consumption_metric BOOLEAN DEFAULT FALSE, -- TRUE only for "Money expenditure per household"

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_segment
        FOREIGN KEY (segment_key)
        REFERENCES dim_segment(segment_key)
        ON DELETE CASCADE
);

-- Indexes for fast queries
CREATE INDEX idx_expenditure_segment ON fact_segment_expenditure(segment_key);
CREATE INDEX idx_expenditure_item ON fact_segment_expenditure(item_name);
CREATE INDEX idx_expenditure_segment_item ON fact_segment_expenditure(segment_key, item_name);

-- ============================================================================
-- MATERIALIZED VIEW: Segment Inequality Gap
-- ============================================================================
-- Purpose: Calculate spending gap between richest and poorest segments
--          Works for ANY segmentation type (Income, Age, Education, etc.)
-- IMPORTANT: Excludes non-consumption categories (income, tax, insurance payments)
--            to avoid nonsensical comparisons (e.g., non-workers paying insurance)
-- ============================================================================
CREATE MATERIALIZED VIEW vw_segment_inequality AS
WITH segment_spending AS (
    SELECT
        f.item_name,
        s.segment_type,
        s.segment_value,
        s.segment_order,
        f.expenditure_value,
        -- Get max and min segment orders for this type
        MAX(s.segment_order) OVER (PARTITION BY s.segment_type) AS max_order,
        MIN(s.segment_order) OVER (PARTITION BY s.segment_type) AS min_order
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE s.segment_order IS NOT NULL
      -- CRITICAL FIX: Exclude non-consumption categories
      AND f.item_name NOT LIKE '%income%'
      AND f.item_name NOT LIKE '%payment%'
      AND f.item_name NOT LIKE '%tax%'
      AND f.item_name NOT LIKE '%insurance%'
      AND f.item_name NOT LIKE '%National Insurance%'
      AND f.item_name NOT LIKE '%Compulsory payment%'
      AND f.item_name NOT LIKE '%Median%'
      AND f.item_name NOT LIKE '%Average age%'
      AND f.item_name NOT LIKE '%Average earners%'
      AND f.item_name NOT LIKE '%Average persons%'
      AND f.item_name NOT LIKE '%Average years of schooling%'
      AND f.item_name NOT LIKE '%Average standard persons%'
      AND f.item_name NOT LIKE '%mortgage%'
      AND f.item_name NOT LIKE '%Arnona%'
      AND f.item_name NOT LIKE '%From %'  -- Excludes "From National Insurance", "From pensions", etc.
),
gap_calc AS (
    SELECT
        item_name,
        segment_type,
        MAX(CASE WHEN segment_order = max_order THEN expenditure_value END) AS high_spend,
        MAX(CASE WHEN segment_order = max_order THEN segment_value END) AS high_segment,
        MAX(CASE WHEN segment_order = min_order THEN expenditure_value END) AS low_spend,
        MAX(CASE WHEN segment_order = min_order THEN segment_value END) AS low_segment,
        AVG(expenditure_value) AS avg_spend
    FROM segment_spending
    GROUP BY item_name, segment_type
)
SELECT
    item_name,
    segment_type,
    high_segment,
    high_spend,
    low_segment,
    low_spend,
    ROUND(high_spend / NULLIF(low_spend, 0), 2) AS inequality_ratio,
    ROUND(avg_spend, 2) AS avg_spend
FROM gap_calc
WHERE high_spend IS NOT NULL AND low_spend IS NOT NULL
ORDER BY segment_type, inequality_ratio DESC;

-- ============================================================================
-- MATERIALIZED VIEW: Segment Burn Rate (GEMINI CORRECTED)
-- ============================================================================
-- Purpose: Calculate financial pressure (spending / income) for income-based segments
-- Note: Uses ONLY the flagged aggregate summary rows, NOT sum of all categories
-- ============================================================================
CREATE MATERIALIZED VIEW vw_segment_burn_rate AS
WITH income_data AS (
    -- Use ONLY the flagged income metric row
    SELECT
        s.segment_key,
        s.segment_type,
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS income
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE f.is_income_metric = TRUE  -- CRITICAL: Use flag instead of LIKE pattern
),
spending_data AS (
    -- Use ONLY the flagged consumption metric row
    SELECT
        s.segment_key,
        s.segment_type,
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS spending
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE f.is_consumption_metric = TRUE  -- CRITICAL: Use flag instead of SUM
)
SELECT
    i.segment_type,
    i.segment_value,
    i.income,
    s.spending,
    ROUND((s.spending / NULLIF(i.income, 0)) * 100, 1) AS burn_rate_pct,
    ROUND(i.income - s.spending, 2) AS surplus_deficit,
    CASE
        WHEN (s.spending / NULLIF(i.income, 0)) * 100 > 100 THEN 'לחץ פיננסי (גירעון)'
        WHEN (s.spending / NULLIF(i.income, 0)) * 100 > 90 THEN 'נקודת איזון'
        WHEN (s.spending / NULLIF(i.income, 0)) * 100 > 75 THEN 'חסכון נמוך'
        ELSE 'חסכון בריא'
    END AS financial_status
FROM income_data i
JOIN spending_data s ON i.segment_key = s.segment_key
ORDER BY i.segment_type, i.segment_order;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_segment_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW vw_segment_inequality;
    REFRESH MATERIALIZED VIEW vw_segment_burn_rate;
    RAISE NOTICE 'All segment materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- Function: Get expenditure by segment type (flexible query)
CREATE OR REPLACE FUNCTION get_expenditure_by_segment_type(
    p_segment_type VARCHAR(100),
    p_item_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    item_name VARCHAR(500),
    segment_value VARCHAR(200),
    expenditure_value NUMERIC(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.item_name,
        s.segment_value,
        f.expenditure_value
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE s.segment_type = p_segment_type
    ORDER BY f.item_name, s.segment_order
    LIMIT p_item_limit;
END;
$$ LANGUAGE plpgsql;

-- Function: Get top inequality items for a segment type
CREATE OR REPLACE FUNCTION get_top_inequality_by_segment(
    p_segment_type VARCHAR(100),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    item_name VARCHAR(500),
    high_segment VARCHAR(200),
    high_spend NUMERIC(12, 2),
    low_segment VARCHAR(200),
    low_spend NUMERIC(12, 2),
    inequality_ratio NUMERIC(10, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.item_name,
        v.high_segment,
        v.high_spend,
        v.low_segment,
        v.low_spend,
        v.inequality_ratio
    FROM vw_segment_inequality v
    WHERE v.segment_type = p_segment_type
    ORDER BY v.inequality_ratio DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA SEED (for testing)
-- ============================================================================
-- Insert sample segments for Income Quintile (from original V9 data)
INSERT INTO dim_segment (segment_type, segment_value, segment_order, file_source) VALUES
    ('Income Quintile', 'Q5 (Top 20%)', 5, 'table_11_v9_flat.csv'),
    ('Income Quintile', 'Q4', 4, 'table_11_v9_flat.csv'),
    ('Income Quintile', 'Q3 (Middle 20%)', 3, 'table_11_v9_flat.csv'),
    ('Income Quintile', 'Q2', 2, 'table_11_v9_flat.csv'),
    ('Income Quintile', 'Q1 (Bottom 20%)', 1, 'table_11_v9_flat.csv')
ON CONFLICT (segment_type, segment_value) DO NOTHING;

-- Insert sample Age Group segments (placeholder for ta5 data)
INSERT INTO dim_segment (segment_type, segment_value, segment_order, file_source) VALUES
    ('Age Group', '18-24 years', 1, 'ta5.csv'),
    ('Age Group', '25-34 years', 2, 'ta5.csv'),
    ('Age Group', '35-44 years', 3, 'ta5.csv'),
    ('Age Group', '45-54 years', 4, 'ta5.csv'),
    ('Age Group', '55-64 years', 5, 'ta5.csv'),
    ('Age Group', '65+ years', 6, 'ta5.csv')
ON CONFLICT (segment_type, segment_value) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Check segment counts
SELECT segment_type, COUNT(*) AS segment_count
FROM dim_segment
GROUP BY segment_type
ORDER BY segment_type;

-- Check expenditure data volume
SELECT
    s.segment_type,
    COUNT(DISTINCT f.item_name) AS item_count,
    COUNT(*) AS total_records
FROM fact_segment_expenditure f
JOIN dim_segment s ON f.segment_key = s.segment_key
GROUP BY s.segment_type
ORDER BY s.segment_type;

-- ============================================================================
-- NOTES FOR PHASE 6 IMPLEMENTATION
-- ============================================================================
-- 1. ETL Strategy:
--    - First, migrate existing V9 data (household_profiles + household_expenditures)
--      into the new normalized structure
--    - Then, add ta2-ta13 data using the generalized load_segmentation.py script
--
-- 2. Backward Compatibility:
--    - Keep V9 tables (household_profiles, household_expenditures) temporarily
--    - Create views that map old table structure to new normalized structure
--    - Gradually deprecate old endpoints
--
-- 3. Scalability:
--    - Adding new segmentation files (ta14, ta15, etc.) requires:
--      a) Adding new segment_type entries to dim_segment
--      b) Loading data via load_segmentation.py (no schema changes!)
--    - No API changes needed - existing /api/segmentation/by/{segment_type} works
--
-- 4. Performance:
--    - Materialized views cache expensive calculations
--    - Indexes on segment_key + item_name ensure fast lookups
--    - Refresh views after bulk data loads
-- ============================================================================
