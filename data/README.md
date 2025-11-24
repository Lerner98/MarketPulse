# Production Data Files

This folder contains the **actual CBS (Israeli Central Bureau of Statistics) data files** used in the MarketPulse project.

## Folder Structure

```
data/
├── raw/                    # Raw CBS Excel files (source data)
└── processed/              # Cleaned/processed CSV files ready for ETL
```

## Raw Data (`raw/`)

### All CBS Files Used in Production (8 files, 420 KB total)

1. **הוצאה_לתצרוכת_למשק_בית_עם_מוצרים_מפורטים.xlsx** (115 KB)
   - **Translation**: "Household Consumption Expenditure by Detailed Products"
   - **Segment Type**: Income Quintile (Q1-Q5)
   - **CBS Table**: 1.1
   - **ETL Script**: `backend/etl/extract_table_1_1.py`

2. **Income_Decile.xlsx** (46 KB)
   - **Segment Type**: Income Decile (Net) - 10 income groups (D1-D10)
   - **CBS Table**: 2
   - **Used for**: Fine-grained income inequality analysis (10 segments vs 5)

3. **Household_Size2.xlsx** (46 KB)
   - **Segment Type**: Income Decile (Gross) - before taxes
   - **CBS Table**: 3
   - **Used for**: Comparison of gross vs net income patterns

4. **WorkStatus-IncomeSource.xlsx** (61 KB)
   - **Segment Type**: Geographic Region - 14 districts across Israel
   - **CBS Table**: 10
   - **Used for**: Regional disparity analysis (Tel Aviv vs periphery)
   - **ETL Script**: `backend/etl/extract_geographic.py`

5. **Household_Size.xlsx** (39 KB)
   - **Segment Type**: Country of Birth - Immigration patterns
   - **CBS Table**: 11
   - **Used for**: Economic integration analysis (USSR immigrants, Israel-born)

6. **WorkStatus-IncomeSource2.xlsx** (31 KB)
   - **Segment Type**: Work Status - Employee, Self-Employed, Not Working
   - **CBS Table**: 12
   - **Used for**: Employment stability and burn rate analysis

7. **Education.xlsx** (35 KB)
   - **Segment Type**: Religiosity Level - Secular to Ultra-Orthodox
   - **CBS Table**: 13
   - **Used for**: Cultural-economic segmentation

8. **הוצאה_למזון_ללא_ארוחות_מחוץ_לבית_לפי_סוג_חנות.xlsx** (29 KB)
   - **Segment Type**: Store Type Competition - Retail analysis
   - **CBS Table**: 38
   - **ETL Script**: `backend/etl/extract_table_38.py`

### Data Characteristics

**Challenges in Raw Data:**
- Multi-level headers (rows 7-9: Hebrew/English/Units)
- Statistical notation: `5.8±0.3`, `..`, `(42.3)`
- Windows-1255 encoding (requires UTF-8 conversion)
- Coded values: `'471'` instead of "Jerusalem"
- Metadata rows (1-6) must be skipped

## Processed Data (`processed/`)

### table_11_v9_flat.csv (28 KB)
- **Source**: Processed from raw CBS Excel files
- **Format**: Flattened CSV ready for database load
- **Columns**: segment_type, segment_value, income, spending, burn_rate_pct, etc.
- **Used by**: `backend/etl/load_v10_data.py` → PostgreSQL

## Data Pipeline Flow

```
Raw Excel Files (data/raw/)
    ↓ [Python ETL Scripts in backend/etl/]
Processed CSV (data/processed/)
    ↓ [Database Loader]
PostgreSQL Tables
    ↓ [FastAPI Endpoints]
React Dashboard
```

## Data Provenance

- **Source**: Israeli Central Bureau of Statistics (CBS / הלמ"ס)
- **Survey**: Household Expenditure Survey 2022
- **Sample Size**: 6,420 Israeli households
- **Official Publication**: CBS Publication Table 1.1, Table 38
- **License**: Public government data (open use for research/analysis)

## Why These Files Stay in Production

These files are **essential for the project story** because:
1. They demonstrate the "messy data → clean insights" journey
2. The README.md references these as examples of ETL challenges
3. Screenshots show the raw Excel structure
4. They're the actual source of all analytics in the dashboard
5. Reproducibility - anyone can re-run the ETL pipeline

## Archive vs Production

**What's in Production (this folder):**
- **8 CBS Excel files** (raw/) - All segment types used in V10 dashboard
- **1 processed CSV** (processed/) - Flattened data ready for database

**What's in ARCHIVE/:**
- **deprecated-code/** - Old experimental CSV files (ta4-ta9.xlsx, table_11_v6-v8.csv)
- **old-versions/CBS-Strategy/** - Python ETL development scripts, temp files

---

*For more details on the ETL process, see `backend/etl/README.md`*
