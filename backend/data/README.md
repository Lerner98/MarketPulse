# Backend Data Directory
**MarketPulse V10 - CBS Household Expenditure Pipeline**

This directory contains all data exports, logs, and verification reports from the V10 ETL pipeline implementation.

---

## Directory Structure

```
data/
├── v10_exports/           # Database exports and sample data
├── v10_logs/              # ETL pipeline execution logs
├── v10_verification/      # Validation reports and test results
└── README.md              # This file
```

---

## v10_exports/

**Purpose:** CSV exports of loaded database data for quality verification and documentation.

### Files:

- **2024-11-22_complete_database_export_6420_records.csv** (427 KB)
  - Complete export of all 6,420 records from fact_segment_expenditure
  - Columns: segment_type, segment_value, segment_order, item_name, expenditure_value, is_income_metric, is_consumption_metric
  - Use for: Data quality checks, manual verification, external analysis

- **2024-11-22_income_quintile_sample.csv**
  - Sample data showing Income Quintile segment structure
  - Use for: Understanding data format, testing, documentation

- **2024-11-22_segment_summary.csv**
  - Summary of all 55 segment combinations with record counts
  - Use for: Quick overview of loaded data, verification of segment coverage

---

## v10_logs/

**Purpose:** Execution logs from ETL pipeline runs and database operations.

### Files:

- **2024-11-22_etl_pipeline_run.log**
  - Complete output from running `python etl/load_segmentation.py`
  - Shows: File processing, column detection, record counts, database inserts
  - Use for: Debugging ETL issues, understanding data transformation process

- **2024-11-22_clear_and_reload.log**
  - Output from clearing duplicate data and reloading database
  - Shows: TRUNCATE operations, ETL re-run, final verification
  - Use for: Understanding how duplicates were fixed

---

## v10_verification/

**Purpose:** Validation reports proving data integrity and correctness.

### Files:

- **2024-11-22_complete_verification_report.md**
  - Comprehensive report answering all verification requirements:
    - Record count breakdown (why 6,420 not 27,456)
    - ETL processing status (7/7 files successful)
    - Database query results (all CBS test values PASS)
  - Use for: Reference documentation, proof of data quality

- **2024-11-22_data_verification_report.txt**
  - Raw text output of record counts per file and segment type
  - Use for: Quick reference, command-line verification

---

## How to Use This Directory

### For Verification:
```bash
# View complete database export
head -20 data/v10_exports/2024-11-22_complete_database_export_6420_records.csv

# Check ETL logs for any issues
grep "ERROR" data/v10_logs/2024-11-22_etl_pipeline_run.log

# Read verification report
cat data/v10_verification/2024-11-22_complete_verification_report.md
```

### For Debugging:
1. Check ETL logs to see which files loaded successfully
2. Compare database export CSV with original CBS Excel files
3. Review verification report to confirm CBS test values match

### For Documentation:
- Include verification report in project documentation
- Reference export CSV when explaining data structure
- Use logs to show ETL processing steps

---

## Key Metrics (2024-11-22)

| Metric | Value |
|--------|-------|
| Total Records Loaded | 6,420 |
| Files Processed | 7/7 (100%) |
| Segment Types | 7 |
| Unique Segments | 55 |
| CBS Test Values | All PASS ✅ |
| Q1 Income | 7510.00 ✅ |
| Q5 Spending | 20076.00 ✅ |
| Q1 Burn Rate | 146.2% ✅ |
| Q5 Burn Rate | 59.8% ✅ |

---

## Notes

- **File naming convention:** `YYYY-MM-DD_description.ext`
- **All files use UTF-8 encoding**
- **CSV files include headers**
- **Logs preserve original console output (including emojis if UTF-8)**

---

*Last Updated: November 22, 2024*
*Pipeline Version: V10 Normalized Star Schema*
