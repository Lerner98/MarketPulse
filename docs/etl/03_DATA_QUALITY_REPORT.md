# Data Quality Report

**Generated:** 2025-11-20 10:40:10

## Executive Summary

This report documents the data quality assessment and cleaning pipeline for CBS transaction data.

### Quality Improvement

| Metric | Before Cleaning | After Cleaning | Improvement |
|--------|-----------------|----------------|-------------|
| **Total Rows** | 10,300 | 10,000 | -300 |
| **Quality Score** | 98.69/100 | 100.00/100 | +1.31 |
| **Missing Values** | 1,054 | 0 | -1,054 |
| **Duplicates** | 600 | 0 | -600 |
| **Completeness** | 98.98% | 100.00% | +1.02% |

## Issues Detected (Before Cleaning)

### Missing Values

| Column | Missing Count | Percentage |
|--------|---------------|------------|
| customer_name | 257 | 2.50% |
| category | 270 | 2.62% |
| currency | 268 | 2.60% |
| customer_city | 259 | 2.51% |


### Duplicates

**Total duplicate rows:** 600

Duplicates were identified based on `transaction_id` field.

### Outliers

| Column | Outlier Count | Method |
|--------|---------------|--------|
| amount | 1,243 | IQR (1.5x) |


## Cleaning Actions Performed

1. Filled 257 missing 'customer_name' with mode: אברהם דהן
2. Filled 270 missing 'category' with mode: אחר
3. Filled 268 missing 'currency' with mode: ILS
4. Filled 259 missing 'customer_city' with mode: תל אביב
5. Removed 300 duplicate records
6. Capped 1203 outliers in 'amount' at IQR boundaries


## Quality Metrics (After Cleaning)

### Completeness by Column

| Column | Non-Null Count | Completeness |
|--------|----------------|--------------|
| transaction_id | 10,000 | 100.00% |
| customer_name | 10,000 | 100.00% |
| product | 10,000 | 100.00% |
| category | 10,000 | 100.00% |
| amount | 10,000 | 100.00% |
| currency | 10,000 | 100.00% |
| transaction_date | 10,000 | 100.00% |
| status | 10,000 | 100.00% |
| customer_city | 10,000 | 100.00% |
| income_quintile | 10,000 | 100.00% |


### Data Distribution

**Total transactions:** 10,000
**Date range:** 2024-01-01 to 2024-12-31
**Total revenue:** ILS 1,272,842.90
**Average transaction value:** ILS 127.28

## Validation

### Before Cleaning
- Rows: 10,300
- Missing values: 1,054
- Duplicates: 600
- Quality score: 98.69/100

### After Cleaning
- Rows: 10,000
- Missing values: 0
- Duplicates: 0
- Quality score: 100.00/100

## Methodology

### Missing Value Handling
- **Categorical fields**: Filled with mode (most common value) or 'Unknown'
- **Numeric fields**: Filled with median value
- **Rationale**: Preserves data distribution while maintaining row count

### Duplicate Removal
- **Method**: Remove duplicates based on `transaction_id`
- **Keep**: First occurrence
- **Rationale**: Transaction ID should be unique; duplicates indicate system errors

### Outlier Treatment
- **Method**: IQR-based capping (Winsorization)
- **Threshold**: Q1 - 1.5*IQR to Q3 + 1.5*IQR
- **Rationale**: Preserves data points while limiting extreme values from skewing analysis

## Next Steps

1. Load cleaned data to PostgreSQL database
2. Create data quality monitoring dashboard
3. Implement automated quality checks in production pipeline
4. Setup alerting for quality degradation

---

*This report was generated as part of the MarketPulse data engineering pipeline.*
