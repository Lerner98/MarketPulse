# ETL Pipeline Execution Guide

## Prerequisites

**Software:**
- Python 3.8+
- PostgreSQL 15+
- pandas, numpy, openpyxl, matplotlib, seaborn

**Data:**
- CBS Excel file: `הוצאות לתצרוכת למשק בית מוצרים מפורטים.xlsx`
- Must be in: `CBS Household Expenditure Data Strategy/`

**Environment:**
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/marketpulse
```

---

## Execution Order

### Phase 1: Extract CBS Data
```bash
cd backend/etl
python cbs_professional_extractor.py
```

**Outputs:**
- `data/processed/cbs_categories_FIXED.csv` (117 categories)
- `data/processed/cbs_products_mapped.json`
- `docs/etl/01_EXTRACTION_REPORT.md`

**Verify:**
```bash
wc -l ../../data/processed/cbs_categories_FIXED.csv
# Should be 118 lines (117 + header)
```

---

### Phase 2: Generate Transactions
```bash
python cbs_transaction_generator.py
```

**Outputs:**
- `data/processed/transactions_generated.csv` (10,000 rows)

**Verify:**
```bash
wc -l ../../data/processed/transactions_generated.csv
# Should be 10,001 lines (10K + header)
```

---

### Phase 3: Quality Pipeline

**Step 3.1: Inject Issues**
```bash
python inject_quality_issues.py
```

**Outputs:**
- `data/processed/transactions_dirty.csv` (10,300 rows)
- `data/processed/quality_issues_log.json`

**Step 3.2: Clean Data**
```bash
python build_quality_pipeline.py
```

**Outputs:**
- `data/processed/transactions_cleaned.csv` (10,000 rows)

---

### Phase 4: Analysis & Insights

**Step 4.1: EDA Visualizations**
```bash
cd ../analysis
python cbs_eda_complete.py
python cbs_eda_part2.py
```

**Outputs:**
- `docs/analysis/01_quintile_analysis.png`
- `docs/analysis/02_category_performance.png`
- `docs/analysis/03_geographic_analysis.png`
- `docs/analysis/04_temporal_analysis.png`
- `docs/analysis/05_product_performance.png`

**Step 4.2: Export Insights**
```bash
python export_insights.py
```

**Outputs:**
- `data/processed/business_insights.json`

**Verify Hebrew:**
```bash
python3 -c "import json; data=json.load(open('../../data/processed/business_insights.json')); print(list(data['top_categories'].keys())[0])"
# Should print: אחר (Hebrew)
```

---

### Phase 5: Load Database
```bash
cd ../backend
python load_cbs_data.py
```

**What it does:**
1. Applies schema_cbs.sql
2. Loads 10,000 transactions
3. Refreshes materialized views
4. Runs validation checks
5. Calculates quality score (100%)

**Verify:**
```bash
psql -d marketpulse -c "SELECT COUNT(*) FROM transactions;"
# Should be 10000
```

---

### Phase 6: Start API
```bash
python -m uvicorn api.main:app --reload
```

**Test endpoints:**
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/cbs/quintiles
curl http://localhost:8000/api/cbs/insights
```

**Docs:** http://localhost:8000/docs

---

## Troubleshooting

**Issue: Hebrew shows as mojibake**
```bash
# Check CSV encoding
file --mime data/processed/transactions_cleaned.csv
# Should be: text/csv; charset=utf-8

# Regenerate insights
cd backend/analysis
python export_insights.py
```

**Issue: Database connection fails**
```bash
# Check PostgreSQL is running
pg_isready

# Check DATABASE_URL
echo $DATABASE_URL
```

**Issue: API returns empty data**
```bash
# Check database loaded
psql -d marketpulse -c "SELECT COUNT(*) FROM transactions;"

# Refresh materialized views
psql -d marketpulse -c "SELECT refresh_all_materialized_views();"
```

---

## Full Pipeline Reset
```bash
# Drop and recreate database
psql -c "DROP DATABASE IF EXISTS marketpulse;"
psql -c "CREATE DATABASE marketpulse;"

# Re-run entire pipeline
cd backend/etl
python cbs_professional_extractor.py
python cbs_transaction_generator.py
python inject_quality_issues.py
python build_quality_pipeline.py

cd ../analysis
python cbs_eda_complete.py
python cbs_eda_part2.py
python export_insights.py

cd ../backend
python load_cbs_data.py
```

---

## Data Quality Checks
```bash
# Check Hebrew encoding
python3 -c "import json; print(json.load(open('data/processed/business_insights.json'))['top_categories'])"

# Check transaction counts
wc -l data/processed/transactions_*.csv

# Check database quality
psql -d marketpulse -c "SELECT * FROM calculate_data_quality();"
```
