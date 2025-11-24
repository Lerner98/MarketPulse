# ETL Pipeline - CBS Household Expenditure Data

This directory contains the Extract, Transform, Load (ETL) pipeline for processing Israeli Central Bureau of Statistics (CBS) household expenditure data into a normalized PostgreSQL star schema.

## Overview

The ETL pipeline transforms messy CBS Excel files with inconsistent structures into a clean, queryable database optimized for analytics.

### The Challenge

CBS Excel files are notoriously difficult to process:
- **Multi-level headers**: Rows 1-6 are metadata, row 7 has Hebrew labels, row 8 has English labels
- **Statistical notation**: "5.8±0.3" (error margins), ".." (suppressed data), "(42.3)" (low reliability)
- **Hebrew encoding**: Windows-1255 → UTF-8 conversion issues
- **Inconsistent structures**: Each of 8 files has different header rows, column layouts, and segment definitions
- **Metadata rows**: Table numbers, publication dates, footnotes mixed with data

### The Solution

A configuration-driven universal processor that:
1. **Adapts to each file**: Configurable header rows, segment patterns, and column mappings
2. **Cleans statistical notation**: Removes ±, handles .., strips parentheses
3. **Normalizes structure**: Converts wide format (500 items × 5 quintiles) to long format (2,500 rows)
4. **Flags special rows**: Identifies income/consumption for burn rate analysis
5. **Loads efficiently**: Idempotent inserts with duplicate checking

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CBS Excel Files                          │
│  (8 files with varying structures, Hebrew/English, ±/..)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  EXTRACT              │
         │  - Read Excel         │
         │  - Parse headers      │
         │  - Handle encoding    │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  TRANSFORM            │
         │  - Clean notation     │
         │  - Filter metadata    │
         │  - Reshape to long    │
         │  - Flag metrics       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  LOAD                 │
         │  - Insert segments    │
         │  - Insert facts       │
         │  - Create indexes     │
         └───────────┬───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Star Schema                          │
│                                                               │
│  dim_segment (segment_key, segment_type, segment_value)     │
│         ↓                                                    │
│  fact_segment_expenditure (item_name, segment_key, value)   │
└─────────────────────────────────────────────────────────────┘
```

## Files

### Core ETL Scripts

| File | Purpose | Input | Output |
|------|---------|-------|--------|
| **load_segmentation.py** | Universal CBS file processor | 8 Excel files | PostgreSQL star schema |
| **extract_geographic.py** | Geographic region extractor | CSV exports | Normalized segments |
| **extract_table_38.py** | Retail competition extractor | Table 38 Excel | retail_competition table |
| **load_from_csv.py** | CSV-based loader (legacy) | CSV files | Database tables |

### Configuration

**SEGMENTATION_FILES** dictionary in `load_segmentation.py` defines:
- File paths and segment types
- Header row numbers (varies: 5, 6, 8, 10, 11)
- Segment identification (pattern-based or mapping-based)
- Income/consumption keywords for burn rate analysis

Example configuration:
```python
'הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx': {
    'segment_type': 'Income Quintile',
    'table_number': '1.1',
    'header_row': 6,
    'segment_pattern': r'^[1-5]$|^Total$',
    'income_row_keyword': 'Net money income per household',
    'consumption_row_keyword': 'Money expenditure per household',
}
```

## Data Transformations

### 1. Statistical Notation Cleaning

| Input | Output | Description |
|-------|--------|-------------|
| `5.8±0.3` | `5.8` | Remove error margin (±) |
| `..` | `NULL` | Suppressed data |
| `(42.3)` | `42.3` | Low reliability flag (keep value) |
| `1,234.5` | `1234.5` | Remove thousands separators |
| `-5.2` | `5.2` | Absolute value (CBS rounding artifact) |

### 2. Row Filtering

**Skipped rows:**
- Error margin rows (contain ±)
- Footnotes: "(1) Source: CBS"
- Metadata: "TABLE 1.1", "PUBLICATION DATE"
- Hebrew metadata: "חמישונים", "עשירונים"
- Empty rows (NaN item names)

**Result**: ~20-30 metadata rows removed per file, leaving 500-600 expenditure categories

### 3. Data Reshaping

**Wide Format (Input):**
```
Item                  | 5    | 4    | 3    | 2    | 1    | Total
───────────────────────┼──────┼──────┼──────┼──────┼──────┼──────
Food and Beverages    | 1500 | 1200 | 1000 | 800  | 600  | 1020
Housing               | 3500 | 2800 | 2200 | 1800 | 1400 | 2340
```

**Long Format (Output):**
```
item_name          | segment_value | expenditure_value
───────────────────┼───────────────┼──────────────────
Food and Beverages | 5             | 1500.0
Food and Beverages | 4             | 1200.0
Food and Beverages | 1             | 600.0
Housing            | 5             | 3500.0
Housing            | 4             | 2800.0
Housing            | 1             | 1400.0
```

### 4. Burn Rate Flagging

Identifies special rows for financial pressure analysis:
- **Income rows**: "Net money income per household" → `is_income_metric = TRUE`
- **Consumption rows**: "Money expenditure per household" → `is_consumption_metric = TRUE`

Enables burn rate calculation: `(Consumption / Income) × 100%`

## Database Schema

### Star Schema Design

**Dimension Table: dim_segment**
```sql
CREATE TABLE dim_segment (
    segment_key SERIAL PRIMARY KEY,
    segment_type VARCHAR(100),           -- "Income Quintile", "Age Group", etc.
    segment_value VARCHAR(100),          -- "Q1 (Lowest)", "35-54", etc.
    segment_order INT,                   -- For sorting (1, 2, 3, 4, 5)
    file_source VARCHAR(255)             -- Original filename for audit
);

-- Index for fast lookups
CREATE INDEX idx_segment_type_value ON dim_segment(segment_type, segment_value);
```

**Fact Table: fact_segment_expenditure**
```sql
CREATE TABLE fact_segment_expenditure (
    expenditure_key SERIAL PRIMARY KEY,
    item_name VARCHAR(255),              -- "Food and Beverages"
    segment_key INT REFERENCES dim_segment(segment_key),
    expenditure_value NUMERIC(12, 2),    -- Monthly spending in ₪
    is_income_metric BOOLEAN,            -- For burn rate calculation
    is_consumption_metric BOOLEAN,       -- For burn rate calculation
    metric_type VARCHAR(50)              -- "Monthly Spend"
);

-- Indexes for fast queries
CREATE INDEX idx_segment_key ON fact_segment_expenditure(segment_key);
CREATE INDEX idx_item_name ON fact_segment_expenditure(item_name);
```

### Materialized Views (Pre-calculated Analytics)

**vw_segment_burn_rate**: Financial pressure by segment
```sql
CREATE MATERIALIZED VIEW vw_segment_burn_rate AS
SELECT
    s.segment_type,
    s.segment_value,
    MAX(CASE WHEN f.is_income_metric THEN f.expenditure_value END) AS income,
    MAX(CASE WHEN f.is_consumption_metric THEN f.expenditure_value END) AS spending,
    (MAX(CASE WHEN f.is_consumption_metric THEN f.expenditure_value END) /
     MAX(CASE WHEN f.is_income_metric THEN f.expenditure_value END) * 100) AS burn_rate_pct
FROM fact_segment_expenditure f
JOIN dim_segment s ON f.segment_key = s.segment_key
GROUP BY s.segment_type, s.segment_value;
```

**vw_segment_inequality**: Spending gaps between segments
```sql
CREATE MATERIALIZED VIEW vw_segment_inequality AS
SELECT
    s.segment_type,
    f.item_name,
    MAX(f.expenditure_value) AS high_spend,
    MIN(f.expenditure_value) AS low_spend,
    MAX(f.expenditure_value) / MIN(f.expenditure_value) AS inequality_ratio
FROM fact_segment_expenditure f
JOIN dim_segment s ON f.segment_key = s.segment_key
GROUP BY s.segment_type, f.item_name
HAVING MIN(f.expenditure_value) > 0;
```

## Usage

### Running the Complete Pipeline

```bash
# Navigate to backend directory
cd backend

# Set up environment (first time only)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure database connection
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run complete ETL pipeline
python etl/load_segmentation.py
```

### Expected Output

```
================================================================================
CBS DATA ETL - COMPLETE PIPELINE
================================================================================

Processing: הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx
Segment Type: Income Quintile
Table: 1.1
================================================================================
✅ Loaded 650 rows
✅ Found 6 segment columns: ['5', '4', '3', '2', '1', 'Total']
✅ Item column: Item
✅ After filtering: 612 rows
✅ Long format: 3672 records
✅ Flagged 6 income rows
✅ Flagged 6 consumption rows

================================================================================
Loading to Database: Income Quintile
================================================================================
  ✅ Inserted segment: 5
  ✅ Inserted segment: 4
  ✅ Inserted segment: 1
✅ Inserted 3672 expenditure records
✅ SUCCESS: הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx (3672 records)

================================================================================
SUMMARY
================================================================================
✅ Loaded: 1 files
❌ Failed: 0 files
📊 Total records: 3,672

================================================================================
DATABASE VERIFICATION
================================================================================

📊 Database Statistics:
  Segments: 6
  Expenditures: 3,672

📊 Records by Segment Type:
  Income Quintile: 3,672
```

### Programmatic Usage

```python
from pathlib import Path
from etl.load_segmentation import process_segmentation_file, load_to_database

# Define configuration
config = {
    'segment_type': 'Income Quintile',
    'table_number': '1.1',
    'header_row': 6,
    'segment_pattern': r'^[1-5]$|^Total$',
    'income_row_keyword': 'Net money income per household',
    'consumption_row_keyword': 'Money expenditure per household',
}

# Process file
file_path = Path('CBS Household Expenditure Data Strategy/file.xlsx')
df_long = process_segmentation_file(file_path, config)

# Load to database
load_to_database(df_long, config['segment_type'], file_path.name)
```

## Performance

### Processing Times

| File | Items | Segments | Records | Time |
|------|-------|----------|---------|------|
| Income Quintile | 612 | 6 | 3,672 | ~8s |
| Income Decile | 612 | 11 | 6,732 | ~12s |
| Geographic Region | 500 | 15 | 7,500 | ~15s |
| **Total** | **~1,800** | **52** | **~20,000** | **~45s** |

### Optimization Tips

1. **Batch inserts**: Current implementation uses row-by-row inserts (slow). Consider using `executemany()` or pandas `to_sql()` for 10x speedup.
2. **Disable indexes**: Drop indexes before bulk load, recreate after (faster for large datasets).
3. **Materialized views**: Refresh CONCURRENTLY to avoid locking tables.

```sql
-- Faster refresh (no table locks)
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_burn_rate;
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_inequality;
```

## Data Quality

### Validation Checks

After ETL completion, run these queries to verify data quality:

```sql
-- 1. Check for duplicate segment-item pairs (should be 0)
SELECT item_name, segment_key, COUNT(*)
FROM fact_segment_expenditure
GROUP BY item_name, segment_key
HAVING COUNT(*) > 1;

-- 2. Verify all segments have income/consumption data (for burn rate)
SELECT s.segment_type, s.segment_value,
       SUM(CASE WHEN f.is_income_metric THEN 1 ELSE 0 END) AS income_rows,
       SUM(CASE WHEN f.is_consumption_metric THEN 1 ELSE 0 END) AS consumption_rows
FROM dim_segment s
LEFT JOIN fact_segment_expenditure f ON s.segment_key = f.segment_key
GROUP BY s.segment_type, s.segment_value;

-- 3. Check for missing values (should be 0)
SELECT COUNT(*) FROM fact_segment_expenditure WHERE expenditure_value IS NULL;

-- 4. Verify reasonable value ranges (monthly spending in ₪)
SELECT MIN(expenditure_value), MAX(expenditure_value), AVG(expenditure_value)
FROM fact_segment_expenditure
WHERE NOT is_income_metric AND NOT is_consumption_metric;
```

### Expected Results

- **No duplicates**: Each (item_name, segment_key) pair is unique
- **All segments have burn rate data**: At least 1 income row and 1 consumption row per segment
- **No NULL values**: All expenditure_value fields are non-NULL floats
- **Reasonable ranges**: Monthly spending 0-50,000 ₪ (outliers indicate parsing errors)

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'openpyxl'`
```bash
pip install openpyxl
```

**Issue**: `UnicodeDecodeError` when reading Hebrew filenames
```python
# Windows: Use raw string or forward slashes
file_path = r'C:\Users\...\הוצאה.xlsx'  # OR
file_path = Path('C:/Users/.../הוצאה.xlsx')
```

**Issue**: "Segment already exists" warnings (not an error)
- ETL is idempotent - re-running checks for existing segments
- To force clean reload: `DELETE FROM fact_segment_expenditure; DELETE FROM dim_segment;`

**Issue**: Burn rate returns NULL
- Check that income/consumption rows were flagged correctly
- Verify keywords match: "Net money income per household" (case-sensitive)

## Testing

Run ETL pipeline tests:

```bash
cd backend
pytest tests/test_etl_pipeline.py -v
```

**Test coverage (44 tests):**
- ✅ Statistical notation cleaning (10 tests)
- ✅ Row skipping logic (8 tests)
- ✅ Segment pattern matching (4 tests)
- ✅ File configuration validation (5 tests)
- ✅ Data validation rules (3 tests)
- ✅ Hebrew encoding (2 tests)
- ✅ Integration tests (3 tests)
- ✅ Edge cases (6 tests)
- ✅ Business logic (3 tests)

## Future Enhancements

### Planned Features

1. **Incremental Load**: Only insert new/changed records (CDC)
2. **Data Lineage**: Track transformations from source to database
3. **Quality Dashboard**: Visualize data quality metrics (missing values, outliers)
4. **Parallel Processing**: Process 8 files concurrently (reduce total time to ~15s)
5. **Data Versioning**: Support multiple CBS survey years (2020, 2021, 2022)

### Additional CBS Tables

Extend ETL to handle:
- **Table 40**: Purchase methods (online Israel, online abroad, physical)
- **Table 38**: Retail competition (8 store types)
- **Table 28**: Income sources (wages, benefits, investments)

## References

- **CBS Data Source**: [Israeli Central Bureau of Statistics - Household Expenditure Survey](https://www.cbs.gov.il/)
- **Star Schema Design**: Kimball dimensional modeling methodology
- **Pandas Documentation**: [DataFrame.melt()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.melt.html)

## Contact

For questions or issues with the ETL pipeline, refer to:
- Main project README: `../../README.md`
- Test documentation: `../tests/TEST_COVERAGE_STATUS.md`
- Architecture docs: `../../docs/APPLICATION_ARCHITECTURE.md`
