# 🏗️ VISUAL ARCHITECTURE - MarketPulse Data Flow

## 📊 CURRENT STATE (BROKEN)

```
┌─────────────────────────────────────────────────────────────────┐
│                      CBS DATA FILES                              │
│  /mnt/user-data/uploads/                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  ❌ ETL Looking for Wrong Files         │
        │     ta2.xlsx  (doesn't exist)           │
        │     ta5.xlsx  (doesn't exist)           │
        │     ta12.xlsx (doesn't exist)           │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  ✅ Only 1 File Matches                 │
        │     הוצאה_לתצרוכת_למשק_בית...xlsx     │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  📊 DATABASE (PostgreSQL)                │
        │                                          │
        │  dim_segment:         6 rows             │
        │    - Income Quintile only                │
        │                                          │
        │  fact_segment_expenditure: 2,651 rows   │
        │    - Q1-Q5 data only                     │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  🌐 API (FastAPI)                        │
        │                                          │
        │  GET /segments/types                     │
        │    → ["Income Quintile"]  (1 option)    │
        │                                          │
        │  GET /burn-rate                          │
        │    → Works for Q1-Q5 only                │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  🎨 FRONTEND (React)                     │
        │                                          │
        │  Selector: No dropdown (1 option only)  │
        │  Charts: Income Quintile only            │
        └─────────────────────────────────────────┘

PROBLEM: 90.4% of available data NOT being used!
```

---

## 📊 TARGET STATE (FIXED)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                             CBS DATA FILES (8 Total)                           │
│  /mnt/user-data/uploads/                                                      │
│                                                                                │
│  1. הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx  (Income Quintile)       │
│  2. Income_Decile.xlsx                                  (Income Decile Net)   │
│  3. Education.xlsx                                      (Religiosity)         │
│  4. Household_Size.xlsx                                 (Country of Birth)    │
│  5. Household_Size2.xlsx                                (Income Decile Gross) │
│  6. WorkStatus-IncomeSource.xlsx                        (Geographic Region)   │
│  7. WorkStatus-IncomeSource2.xlsx                       (Work Status)         │
│  8. הוצאה_למזון_ללא_ארוחות_מחוץ_לבית_לפי_סוג_חנות.xlsx  (Retail - Table 38)│
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↓
        ┌─────────────────────────────────────────────────────────┐
        │  ✅ CORRECTED ETL SCRIPT                                │
        │     load_segmentation_corrected.py                      │
        │                                                          │
        │  SEGMENTATION_FILES = {                                 │
        │    'Income_Decile.xlsx': {                              │
        │      'segment_type': 'Income Decile (Net)',             │
        │      'header_row': 5,                                   │
        │      'segment_pattern': r'^[1-9]$|^10$|^Total$'         │
        │    },                                                    │
        │    'Education.xlsx': {                                  │
        │      'segment_type': 'Religiosity Level',               │
        │      'header_row': 5,                                   │
        │      'segment_mapping': {0: 'Mixed', 1: 'Ultra-Orth...} │
        │    },                                                    │
        │    ... (all 8 files mapped correctly)                   │
        │  }                                                       │
        └─────────────────────────────────────────────────────────┘
                                      ↓
        ┌─────────────────────────────────────────────────────────┐
        │  🔄 ETL PROCESSING                                       │
        │                                                          │
        │  For each file:                                         │
        │    1. Read Excel with correct header_row                │
        │    2. Identify segment columns (pattern or mapping)     │
        │    3. Extract item names (expenditure categories)       │
        │    4. Clean CBS notation (±, .., parentheses)           │
        │    5. Melt to long format (item × segment × value)      │
        │    6. Flag income/consumption rows (for burn rate)      │
        │    7. Load to database (dim_segment + fact_...)         │
        └─────────────────────────────────────────────────────────┘
                                      ↓
        ┌─────────────────────────────────────────────────────────┐
        │  📊 DATABASE (PostgreSQL Star Schema)                    │
        │                                                          │
        │  ┌────────────────────────────────────┐                 │
        │  │  dim_segment (52 rows)              │                 │
        │  │  ─────────────────────────────────  │                 │
        │  │  segment_key | segment_type | value │                 │
        │  │  ────────────────────────────────── │                 │
        │  │  1           | Income Quintile | 5  │                 │
        │  │  2           | Income Quintile | 4  │                 │
        │  │  ...         | ...             | ... │                 │
        │  │  7           | Income Decile   | 10 │                 │
        │  │  8           | Income Decile   | 9  │                 │
        │  │  ...         | ...             | ... │                 │
        │  │  18          | Religiosity     | Sec│                 │
        │  │  ...         | ...             | ... │                 │
        │  │  52          | Work Status     | Tot│                 │
        │  └────────────────────────────────────┘                 │
        │                      ↓ (1:N)                             │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │  fact_segment_expenditure (27,456 rows)            │ │
        │  │  ──────────────────────────────────────────────────│ │
        │  │  expenditure_key | item_name | segment_key | value │ │
        │  │  ──────────────────────────────────────────────────│ │
        │  │  1 | Mortgage | 1 (Q5) | 2,379                     │ │
        │  │  2 | Mortgage | 2 (Q4) | 1,542                     │ │
        │  │  3 | Food     | 1 (Q5) | 4,234                     │ │
        │  │  ... (27,456 total records)                         │ │
        │  └────────────────────────────────────────────────────┘ │
        │                                                          │
        │  ┌────────────────────────────────────┐                 │
        │  │  Materialized Views                 │                 │
        │  │  ─────────────────────────────────  │                 │
        │  │  vw_segment_burn_rate               │                 │
        │  │    → Income / Consumption by segment│                 │
        │  │                                     │                 │
        │  │  vw_segment_inequality              │                 │
        │  │    → Max/Min spending ratio per item│                 │
        │  └────────────────────────────────────┘                 │
        └─────────────────────────────────────────────────────────┘
                                      ↓
        ┌─────────────────────────────────────────────────────────┐
        │  🌐 API (FastAPI) - Dynamic Endpoints                    │
        │                                                          │
        │  GET /segments/types                                    │
        │    → [                                                   │
        │        "Income Quintile",                                │
        │        "Income Decile (Net)",                            │
        │        "Income Decile (Gross)",                          │
        │        "Religiosity Level",                              │
        │        "Country of Birth",                               │
        │        "Geographic Region",                              │
        │        "Work Status"                                     │
        │      ]                                                   │
        │                                                          │
        │  GET /segmentation/by/{segment_type}                    │
        │    ← Works for ANY segment type!                        │
        │    Example: /segmentation/by/Religiosity%20Level        │
        │    Returns: Secular vs Orthodox spending patterns       │
        │                                                          │
        │  GET /burn-rate?segment_type={type}                     │
        │    ← Calculates for ANY segment type!                   │
        │    Uses: is_income_metric + is_consumption_metric flags │
        │                                                          │
        │  GET /inequality/{segment_type}                         │
        │    ← Inequality analysis for ANY segment!               │
        │    Example: Geographic → Tel Aviv vs Be'er Sheva gap    │
        └─────────────────────────────────────────────────────────┘
                                      ↓
        ┌─────────────────────────────────────────────────────────┐
        │  🎨 FRONTEND (React) - Dynamic UI                        │
        │                                                          │
        │  ┌─────────────────────────────────────────────┐        │
        │  │  Segment Selector (Dropdown)                │        │
        │  │  ─────────────────────────────────────────  │        │
        │  │  View by: [Income Quintile        ▼]       │        │
        │  │                                             │        │
        │  │  Options:                                   │        │
        │  │    - By Income (5 groups)                   │        │
        │  │    - By Income (10 groups - Net)            │        │
        │  │    - By Income (10 groups - Gross)          │        │
        │  │    - By Religiosity                         │        │
        │  │    - By Immigration Status                  │        │
        │  │    - By Region (14 areas)                   │        │
        │  │    - By Employment Type                     │        │
        │  └─────────────────────────────────────────────┘        │
        │                      ↓                                   │
        │  ┌─────────────────────────────────────────────┐        │
        │  │  Charts Update Instantly                     │        │
        │  │  ─────────────────────────────────────────  │        │
        │  │  1. Burn Rate Chart                         │        │
        │  │     - Shows for selected segment            │        │
        │  │     - Example: Secular 68% vs Orthodox 112% │        │
        │  │                                             │        │
        │  │  2. Inequality Chart                        │        │
        │  │     - Top spending gaps in selected segment │        │
        │  │     - Example: Tel Aviv vs Be'er Sheva      │        │
        │  │                                             │        │
        │  │  3. Retail Competition (Table 38)           │        │
        │  │     - Unchanged (separate data source)      │        │
        │  └─────────────────────────────────────────────┘        │
        └─────────────────────────────────────────────────────────┘

RESULT: 100% of available data utilized across 7 demographic dimensions!
```

---

## 🔄 DATA FLOW COMPARISON

### CURRENT (Broken)
```
8 Files → ETL (broken mapping) → 1 File Loaded → 2,651 records → 1 Segment Type → Static Frontend
```

### FIXED (Target)
```
8 Files → ETL (corrected mapping) → 8 Files Loaded → 27,456 records → 7 Segment Types → Dynamic Frontend
```

---

## 📊 FILE → SEGMENT → RECORDS MAPPING

```
┌─────────────────────────────────────────┬───────────────────────┬─────────┬──────────┐
│ File Name                                │ Segment Type          │ Segments│ Records  │
├─────────────────────────────────────────┼───────────────────────┼─────────┼──────────┤
│ הוצאה_לתצרוכת_למשק_בית...xlsx          │ Income Quintile       │    5    │  2,640   │
│ Income_Decile.xlsx                       │ Income Decile (Net)   │   10    │  5,280   │
│ Household_Size2.xlsx                     │ Income Decile (Gross) │   10    │  5,280   │
│ Education.xlsx                           │ Religiosity Level     │    5    │  2,640   │
│ Household_Size.xlsx                      │ Country of Birth      │    5    │  2,640   │
│ WorkStatus-IncomeSource.xlsx             │ Geographic Region     │   14    │  7,392   │
│ WorkStatus-IncomeSource2.xlsx            │ Work Status           │    3    │  1,584   │
├─────────────────────────────────────────┴───────────────────────┴─────────┴──────────┤
│ TOTAL (Expenditure Data)                                           52       27,456   │
└──────────────────────────────────────────────────────────────────────────────────────┘

PLUS:
┌─────────────────────────────────────────┬───────────────────────┬─────────┬──────────┐
│ הוצאה_למזון_ללא_ארוחות...xlsx         │ Retail Competition    │ 13 × 8  │    104   │
│                                          │ (Table 38 - separate) │         │          │
└─────────────────────────────────────────┴───────────────────────┴─────────┴──────────┘

GRAND TOTAL: 27,560 data points
```

---

## 🎯 KEY ARCHITECTURAL DECISIONS

### 1. Star Schema (Not Multiple Tables)
```
❌ BAD: 7 separate tables
   household_expenditures_quintile
   household_expenditures_decile
   household_expenditures_religiosity
   ... (7 tables, maintenance nightmare)

✅ GOOD: Normalized star schema
   dim_segment (52 rows - ALL segment types)
   fact_segment_expenditure (27,456 rows - ALL data)
   
   → Add new dimension = just insert new dim_segment rows, no schema change!
```

### 2. Universal ETL (Not Hardcoded Scripts)
```
❌ BAD: 7 separate ETL scripts
   load_quintile.py
   load_decile.py
   load_religiosity.py
   ... (7 scripts, copy-paste hell)

✅ GOOD: Configuration-driven ETL
   SEGMENTATION_FILES = {
     'Income_Decile.xlsx': {...config...},
     'Education.xlsx': {...config...},
     ... (add new file = add config, no new code)
   }
```

### 3. Dynamic API (Not Fixed Endpoints)
```
❌ BAD: 7 hardcoded endpoints
   GET /quintile-data
   GET /decile-data
   GET /religiosity-data
   ... (7 endpoints, update frontend for each)

✅ GOOD: One universal endpoint
   GET /segmentation/by/{segment_type}
   
   Works for: quintile, decile, religiosity, geography, work status
   → Add new segment = automatic, no API changes!
```

### 4. Frontend Selector (Not Static Pages)
```
❌ BAD: 7 separate dashboard pages
   QuintileDashboard.tsx
   DecileDashboard.tsx
   ReligiosityDashboard.tsx
   ... (7 components, duplicate code)

✅ GOOD: One dynamic dashboard
   <SegmentSelector onChange={updateCharts} />
   
   Charts update based on selected segment
   → Add new segment = appears in dropdown automatically!
```

---

## ✅ VERIFICATION CHECKLIST

After running the fix, verify each layer:

### 1. Database Layer
```sql
-- Should return 7 segment types
SELECT DISTINCT segment_type FROM dim_segment WHERE segment_value != 'Total';

-- Should return 27,456
SELECT COUNT(*) FROM fact_segment_expenditure;

-- Should return records for each segment type
SELECT s.segment_type, COUNT(*) as records
FROM fact_segment_expenditure f
JOIN dim_segment s ON f.segment_key = s.segment_key
GROUP BY s.segment_type;
```

### 2. API Layer
```bash
# Should return 7 types
curl http://localhost:8000/api/segments/types | jq '.segments | length'

# Should work for each type
curl http://localhost:8000/api/segmentation/by/Religiosity%20Level
curl http://localhost:8000/api/segmentation/by/Geographic%20Region
curl http://localhost:8000/api/burn-rate?segment_type=Work%20Status
```

### 3. Frontend Layer
```
1. Open dashboard
2. See 7 options in dropdown ✅
3. Select "By Religiosity" → Charts update ✅
4. Select "By Region" → Charts update ✅
5. Burn rate shows correct % for each ✅
```

---

*This diagram shows the complete data flow from CBS Excel files to React dashboard.*
*Use this as reference when implementing the fix.*

*Last Updated: November 22, 2024*
