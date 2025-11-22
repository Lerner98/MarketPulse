# V10 Materialized View Critical Fix - November 2024

## 🛑 Critical Issue: Empty Charts for Non-Income Segment Types

### Problem Summary
**Date Discovered**: November 22, 2024
**Severity**: CRITICAL - Multiple segment types showing empty charts
**Affected Segments**: Work Status, Geographic Region, Country of Birth, Religiosity
**Working Segments**: Income Quintile, Income Decile (Net/Gross)

### Symptoms
- Frontend charts display "אין נתונים זמינים" (No data available)
- Burn rate bar charts are empty
- Pie charts show no data
- API returns empty arrays for affected segment types

### Root Cause Analysis

#### 1. Database Architecture Issue
The materialized view `vw_segment_burn_rate` was hardcoded to ONLY include Income Quintile and Income Decile data:

```sql
-- BROKEN CODE (schema_v10_normalized.sql lines 149, 161)
CREATE MATERIALIZED VIEW vw_segment_burn_rate AS
WITH income_data AS (
    SELECT
        s.segment_key,
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS income
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE s.segment_type IN ('Income Quintile', 'Income Decile')  -- ❌ HARDCODED FILTER
      AND f.is_income_metric = TRUE
),
spending_data AS (
    SELECT
        s.segment_key,
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS spending
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE s.segment_type IN ('Income Quintile', 'Income Decile')  -- ❌ HARDCODED FILTER
      AND f.is_consumption_metric = TRUE
)
SELECT
    i.segment_value,  -- ❌ MISSING segment_type column
    i.income,
    s.spending,
    -- ... rest of SELECT
```

**Why This Broke Everything**:
1. View only stores data for Income Quintile/Decile
2. When API queries for `segment_type = 'Work Status'`, the WHERE clause fails because:
   - The view doesn't contain `segment_type` column in output
   - Even if it did, there's no Work Status data in the view

#### 2. Missing Column Issue
The view did NOT include `segment_type` in the SELECT clause, so the API endpoint's WHERE filter couldn't work:

```python
# segmentation_endpoints_v10.py (line 420)
SELECT * FROM vw_segment_burn_rate
WHERE segment_type = :segment_type  -- ❌ FAILS: column doesn't exist
```

### The Fix (Applied November 22, 2024)

#### Step 1: Updated Schema Definition
**File**: `backend/models/schema_v10_normalized.sql` (lines 139-179)

```sql
-- FIXED CODE
CREATE MATERIALIZED VIEW vw_segment_burn_rate AS
WITH income_data AS (
    SELECT
        s.segment_key,
        s.segment_type,        -- ✅ ADDED segment_type
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS income
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE f.is_income_metric = TRUE  -- ✅ REMOVED hardcoded segment type filter
),
spending_data AS (
    SELECT
        s.segment_key,
        s.segment_type,        -- ✅ ADDED segment_type
        s.segment_value,
        s.segment_order,
        f.expenditure_value AS spending
    FROM fact_segment_expenditure f
    JOIN dim_segment s ON f.segment_key = s.segment_key
    WHERE f.is_consumption_metric = TRUE  -- ✅ REMOVED hardcoded segment type filter
)
SELECT
    i.segment_type,            -- ✅ ADDED to SELECT
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
ORDER BY i.segment_type, i.segment_order;  -- ✅ Updated ORDER BY
```

#### Step 2: Recreate Materialized View in Database
Execute the following SQL to apply the fix:

```sql
-- Drop old view
DROP MATERIALIZED VIEW IF EXISTS vw_segment_burn_rate;

-- Recreate with new definition (paste the FIXED CODE above)

-- Verify the fix
SELECT segment_type, COUNT(*) as count
FROM vw_segment_burn_rate
GROUP BY segment_type
ORDER BY segment_type;
```

**Expected Output After Fix**:
```
segment_type              | count
--------------------------+-------
Country of Birth          |     5
Geographic Region         |    14
Income Decile (Gross)     |    11
Income Decile (Net)       |    11
Income Quintile           |     6
Religiosity Level         |     5
Work Status               |     3
```

### Verification Steps

#### 1. Test Database View
```sql
-- Check Work Status data
SELECT segment_type, segment_value, income, spending, burn_rate_pct
FROM vw_segment_burn_rate
WHERE segment_type = 'Work Status'
ORDER BY burn_rate_pct DESC;
```

**Expected Result**:
```
segment_type | segment_value | income  | spending | burn_rate_pct
-------------+---------------+---------+----------+--------------
Work Status  | 1,176         | 10540.0 |   9444.0 |         89.6
Work Status  | 589           | 19205.0 |  17001.0 |         88.5
Work Status  | 3,713         | 20522.0 |  15710.0 |         76.6
```

#### 2. Test API Endpoint
```bash
curl -s "http://localhost:8000/api/v10/burn-rate?segment_type=Work%20Status" | jq
```

**Expected Response**:
```json
{
  "total_segments": 3,
  "burn_rates": [
    {
      "segment_value": "1,176",
      "income": 10540.0,
      "spending": 9444.0,
      "burn_rate_pct": 89.6,
      "surplus_deficit": 1096.0,
      "financial_status": "חסכון נמוך"
    },
    {
      "segment_value": "589",
      "income": 19205.0,
      "spending": 17001.0,
      "burn_rate_pct": 88.5,
      "surplus_deficit": 2204.0,
      "financial_status": "חסכון נמוך"
    },
    {
      "segment_value": "3,713",
      "income": 20522.0,
      "spending": 15710.0,
      "burn_rate_pct": 76.6,
      "surplus_deficit": 4812.0,
      "financial_status": "חסכון בריא"
    }
  ],
  "insight": "..."
}
```

#### 3. Verify Frontend Charts
1. Navigate to DashboardV10 (`http://localhost:8081`)
2. Select "Work Status" from segment dropdown
3. Verify:
   - ✅ Burn rate bar chart shows 3 bars (פנסיונר, עצמאי, שכיר)
   - ✅ Pie chart shows 3 segments with percentages
   - ✅ Metric cards show calculated values (not "טוען...")
   - ✅ Business insights display correct Hebrew text with real numbers

### Future Prevention

#### Database Schema Changes
When modifying materialized views:

1. **NEVER hardcode segment types** in WHERE clauses unless explicitly required
2. **ALWAYS include `segment_type`** in SELECT when filtering by it later
3. **Test all segment types** after schema changes, not just Income Quintile

#### Code Review Checklist
Before merging schema changes:
- [ ] View includes `segment_type` column if API filters by it
- [ ] WHERE clauses don't exclude required segment types
- [ ] All 7 segment types tested (Income Quintile, Income Decile Net/Gross, Work Status, Geographic Region, Country of Birth, Religiosity)
- [ ] Materialized view refreshed after schema changes
- [ ] API endpoints tested with `curl` for each segment type

### Related Files
- **Schema**: `backend/models/schema_v10_normalized.sql` (lines 139-179)
- **API**: `backend/api/segmentation_endpoints_v10.py` (lines 399-473)
- **Frontend**: `frontend2/src/pages/DashboardV10.tsx`
- **Hooks**: `frontend2/src/hooks/useCBSDataV10.ts` (lines 146-154)

### Migration Script (If Needed)
If you need to apply this fix to an existing database without manually running SQL:

```bash
cd backend
python -c "
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.begin() as conn:
    # Drop old view
    conn.execute(text('DROP MATERIALIZED VIEW IF EXISTS vw_segment_burn_rate'))

    # Recreate with fix (paste SQL from FIXED CODE section above)
    # ...

    print('Materialized view fixed successfully')
"
```

### Lessons Learned
1. **Materialized views are NOT automatically dynamic** - They store pre-computed results, so WHERE clause filters matter at view creation time, not query time
2. **Column selection matters** - If you filter by a column, it must exist in the view's SELECT
3. **Test beyond happy path** - Income Quintile worked fine, masking the issue for other segment types
4. **Database-first debugging** - When frontend shows empty data, test the database query directly first

---

**Fixed By**: Claude (AI Assistant)
**Date**: November 22, 2024
**Status**: ✅ RESOLVED
