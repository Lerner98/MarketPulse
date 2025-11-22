# MarketPulse V9 Production Pipeline Documentation

## Overview

The V9 Pipeline is a complete ETL system that processes CBS (Israeli Central Bureau of Statistics) household expenditure data from raw Excel files to a production-ready PostgreSQL database with FastAPI endpoints and React frontend visualization.

**Pipeline Status:** ✅ PRODUCTION READY

**Last Updated:** November 21, 2024

---

## Architecture

```
Raw CBS Data (Excel)
    ↓
Python ETL Scripts (Pandas)
    ↓
PostgreSQL Database (3 Tables + 3 Views)
    ↓
FastAPI REST API (6 Endpoints)
    ↓
React Frontend (TypeScript)
```

---

## Key Features

1. **Auto-split Detection**: Automatically separates demographics from spending data
2. **Data Quality**: Handles NaN values, duplicates, statistical notation
3. **Business Insights**: 3 materialized views with pre-calculated metrics
4. **Real-time API**: < 300ms response times
5. **Production Ready**: Validated against CBS official data

---

## Pipeline Components

### 1. Data Sources
- **Table 11 (v9)**: 558 rows of household profiles + expenditures
- **Table 38 (v6)**: 14 food categories × 8 store types

### 2. Database Schema
- **3 Tables**: household_profiles, household_expenditures, retail_competition
- **3 Materialized Views**: vw_inequality_gap, vw_burn_rate, vw_fresh_food_battle
- **Helper Functions**: refresh_all_views(), get_inequality_summary(), etc.

### 3. API Endpoints
- `/api/strategic/inequality-gap` - Top spending gaps by quintile
- `/api/strategic/burn-rate` - Financial pressure metrics
- `/api/strategic/fresh-food-battle` - Traditional vs Supermarket competition
- `/api/strategic/retail-competition` - Full 8 store types breakdown
- `/api/strategic/household-profiles` - Demographics
- `/api/strategic/expenditures` - All spending categories

### 4. Frontend Pages
- Dashboard: Overview with key metrics
- Revenue: Category analysis
- Customers: Quintile segmentation
- Products: Product performance

---

## Quick Start

### Step 1: Apply Schema
```bash
cd backend
python apply_schema_v9.py
```

### Step 2: Load Data
```bash
cd backend
python etl/load_v9_production.py
```

### Step 3: Start Backend
```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

### Step 4: Start Frontend
```bash
cd frontend2
npm run dev
```

---

## Detailed Documentation

- **Backend Pipeline**: See [backend/BACKEND_PIPELINE.md](backend/BACKEND_PIPELINE.md)
- **Frontend Integration**: See [frontend/FRONTEND_PIPELINE.md](frontend/FRONTEND_PIPELINE.md)

---

## Verification

### Test Endpoints
```bash
curl http://localhost:8000/api/strategic/inequality-gap
curl http://localhost:8000/api/strategic/burn-rate
curl http://localhost:8000/api/strategic/retail-competition
```

### Expected Results
- ✅ Inequality Gap: 528 expenditure categories
- ✅ Burn Rate: Q1 = 166.4%, Q5 = 74.8%
- ✅ Retail Competition: 14 food categories with 8 store types

---

## Key Insights

1. **Highest Inequality**: Domestic help - Q5 spends 18.11x more than Q1
2. **Financial Crisis**: Q1 households spend 166.4% of income (debt spiral)
3. **Retail Battle**: Supermarkets dominate packaged goods (60%), lose fresh food to butchers (45%)

---

## Migration from Old System

**Old Files (Moved to OLD/):**
- ❌ strategic_endpoints_db.py
- ❌ schema_strategic.sql
- ❌ load_strategic_data.py
- ❌ create_strategic_schema.py
- ❌ test_strategic_api.py

**New V9 Files (Active):**
- ✅ strategic_endpoints_v9.py
- ✅ schema_v9_production.sql
- ✅ load_v9_production.py
- ✅ apply_schema_v9.py

---

## Troubleshooting

### ETL Fails
- Check CSV files exist: `data/raw/table_11_v9_flat.csv`, `data/processed/table_38_retail.csv`
- Verify database connection: Check `.env` for DATABASE_URL

### API Returns 404
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check endpoints registered: Look for "Strategic CBS V9 endpoints registered" in logs

### Frontend Shows No Data
- Check API is accessible: Open browser to `http://localhost:8000/docs`
- Verify CORS settings in `backend/api/main.py`

---

## Contact

For issues or questions, see project README or check the GitHub repository.
