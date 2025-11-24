# Claude Code Agent Rules for MarketPulse V2

## Project Context
- **Project**: MarketPulse - Israeli Household Expenditure Analytics Platform
- **Version**: V2 (Strategic CBS Analysis)
- **Stack**: FastAPI + React + PostgreSQL + Pandas + Recharts
- **Goal**: Production-ready analytics dashboard showcasing ETL expertise with real CBS data

## Project Purpose & Narrative
This is a **portfolio project** demonstrating professional data engineering and analysis skills:
- **Data Source**: Israeli Central Bureau of Statistics (CBS) Household Expenditure Survey 2022
- **Core Value Proposition**: Transform messy government Excel files into clean strategic business insights
- **Differentiator**: NOT just visualizations - shows the complete **ETL journey** from raw to refined

## The Strategic "Winning Trio" - 3 CBS Datasets

### Table 1.1: Income Quintile Expenditure
- **File**: `הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx`
- **What it provides**: 88 product categories broken down by income quintile (Q1-Q5)
- **Business Insight**: "The 2.62x Rule" - High-income households spend 2.62x more than low-income
- **Strategic Value**: Guides marketing budget allocation (40% to Q4-Q5 for highest ROI)

### Table 40: Purchase Methods (Digital vs Physical)
- **File**: `רכישות מוצרים נבחרים לפי אופן.xlsx`
- **What it provides**: 55 product categories with online Israel %, online abroad %, physical %
- **Business Insight**: "Digital Opportunity Matrix" - Which products go online vs stay physical
- **Strategic Value**: E-commerce strategy (gadgets → Amazon, furniture → local, opportunity gaps)

### Table 38: Store Type Competition (Retail Battle)
- **File**: `הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx`
- **What it provides**: 13 food categories by store type (supermarket, local market, butcher, bakery)
- **Business Insight**: "Retail Battle" - Supermarkets lose fresh food to specialists (0.4% vs 76.6%)
- **Strategic Value**: Retail positioning (supermarkets own packaged, lose fresh → need premium branding)

## Data Pipeline Architecture

### Complete Flow (The Story to Tell Recruiters):
```
Raw CBS Excel Files (Messy)
    ↓ [ETL Challenge: Multi-level headers, Hebrew encoding, statistical notation]
Python ETL Scripts
    ↓ [Clean: parse_cbs_headers(), fix_hebrew_encoding(), clean_statistical_values()]
PostgreSQL Tables
    ↓ [Optimize: Materialized views for fast queries]
FastAPI REST Endpoints
    ↓ [Serve: JSON responses < 500ms]
React Dashboard
    ↓ [Visualize: Recharts with Hebrew RTL support]
Business Insights
```

### Key ETL Challenges Solved:
1. **Multi-level headers**: Rows 1-6 are metadata, rows 7-9 are hierarchical headers (Hebrew/English/Units)
2. **Hebrew encoding**: Windows-1255 → UTF-8 conversion (mojibake detection)
3. **Statistical notation**: "5.8±0.3" (error margins), ".." (suppressed data), "(42.3)" (low reliability)
4. **Data validation**: Automated quality checks before database load

## File Structure

### Backend (`backend/`)
```
backend/
├── etl/
│   ├── extract_table_1_1.py     # Quintile expenditure extractor
│   ├── extract_table_40.py      # Digital purchase method extractor
│   ├── extract_table_38.py      # Retail competition extractor
│   └── load_strategic_data.py   # Master loader (Excel → PostgreSQL)
├── api/
│   ├── main.py                  # FastAPI app with strategic endpoints
│   ├── strategic_endpoints_db.py # The 3 core insight endpoints
│   └── cbs_models.py            # Pydantic models
├── models/
│   ├── schema_strategic.sql     # PostgreSQL schema for 3 tables + views
│   └── database.py              # SQLAlchemy DB manager
└── tests/
    └── test_strategic_api.py    # Professional test suite (500+ lines)
```

### Frontend (`frontend2/`)
```
frontend2/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx        # Main dashboard with 3 strategic insights
│   │   ├── Revenue.tsx          # Category analysis
│   │   ├── Customers.tsx        # Quintile segmentation
│   │   └── Products.tsx         # Product performance
│   ├── components/
│   │   ├── BusinessInsight.tsx  # Reusable insight cards (4 color variants)
│   │   ├── CategoryPieChart.tsx # Pie chart with Hebrew legends
│   │   └── MetricCard.tsx       # KPI cards
│   └── hooks/
│       └── useCBSData.ts        # React Query hooks for API
```

### Data (`CBS Household Expenditure Data Strategy/`)
```
CBS Household Expenditure Data Strategy/
├── הוצאה לתצרוכת למשק בית עם מוצרים מפורטים.xlsx  # Table 1.1
├── רכישות מוצרים נבחרים לפי אופן.xlsx              # Table 40
└── הוצאה למזון ללא ארוחות מחוץ לבית לפי סוג חנות.xlsx # Table 38
```

## Database Schema

### Tables:
- `quintile_expenditure` - 88 categories × 5 quintiles (Table 1.1)
- `purchase_methods` - 55 categories × 3 purchase channels (Table 40)
- `store_competition` - 13 food categories × 5 store types (Table 38)

### Materialized Views (Fast Queries):
- `vw_quintile_gap` - Pre-calculated 2.62x ratio
- `vw_digital_matrix` - Pre-sorted by online penetration
- `vw_retail_battle` - Pre-calculated market shares

### Stored Procedures:
- `refresh_strategic_views()` - Refresh all materialized views
- `get_quintile_gap_summary()` - Get quintile analysis with insight text
- `get_digital_leaders()` - Top N online categories
- `get_supermarket_losses()` - Categories where supermarkets lose

## API Endpoints

### Strategic Insights (V2):
```
GET /api/strategic/quintile-gap
GET /api/strategic/digital-matrix
GET /api/strategic/retail-battle
```

### Legacy CBS Endpoints (V1):
```
GET /api/cbs/quintiles
GET /api/cbs/categories
GET /api/cbs/insights
```

## Core Development Principles

### 1. ETL Excellence
- **Never hardcode row numbers** - Use dynamic header detection
- **Always validate** - Check encoding, data ranges, business rules
- **Document challenges** - The "messy → clean" journey is the story
- **Test data quality** - Automated checks before database load

### 2. Production-Ready Code
- **Use stored procedures** for database operations (SQL injection prevention)
- **Materialized views** for performance (< 500ms response times)
- **Comprehensive tests**: Unit + Integration + Performance + Security
- **Professional error handling** with proper HTTP status codes

### 3. Hebrew/RTL Support
- **Text encoding**: Always use UTF-8, handle Windows-1255 conversion
- **UI direction**: `dir="rtl"` on Hebrew text elements
- **Number formatting**: Use Hebrew locale (`he-IL`) for thousands separators

### 4. Test Coverage
- **Backend**: pytest with fixtures, mocks, and real DB tests
- **API**: FastAPI TestClient for integration tests
- **Performance**: Assert response times < 500ms
- **Security**: Test CORS, SQL injection protection

## Development Workflow

### When Adding New CBS Data:
1. **Understand the Excel structure** (inspect first 20 rows)
2. **Write extraction function** (`extract_table_X.py`)
3. **Update database schema** (`schema_strategic.sql`)
4. **Update loader** (`load_strategic_data.py`)
5. **Create API endpoint** (`strategic_endpoints_db.py`)
6. **Add tests** (`test_strategic_api.py`)
7. **Update frontend** (React hooks + components)

### When Fixing Bugs:
1. **Check data first** - Is the issue in extraction, database, or API?
2. **Use validation functions** - Run data quality checks
3. **Check materialized views** - May need refresh after data changes
4. **Test end-to-end** - ETL → DB → API → Frontend

## Important References

### Project Documentation:
- `PRESENTATION_README.md` - Full portfolio narrative (what to tell recruiters)
- `Refactor Data and Presentation.md` - V2 strategy and implementation guide
- `BACKEND_API_TEST_RESULTS.md` - API test results and validation
- `CBS_DATA_STRATEGY.md` - CBS data structure and business insights

### Knowledge Base (READ-ONLY):
- `02_SECURITY_COMPREHENSIVE.md` - Security best practices
- `05_APPLICATION_ARCHITECTURE.md` - Architecture patterns
- `data-analyst-portfolio.md` - ETL and analysis techniques

## Key Numbers (For Reference)

### Data Volume:
- **88 product categories** in quintile analysis
- **55 product categories** in digital/physical analysis
- **13 food categories** in retail competition
- **Total: 156 data points** across 3 strategic analyses

### Business Insights:
- **2.62x multiplier** - Q5 vs Q1 spending gap
- **69.9% online Israel** - Highest digital penetration (software/games)
- **76.6% local market share** - Dominance in fresh food retail

### Technical Performance:
- **< 500ms** - API response time (materialized views)
- **80%+ test coverage** - Backend test suite
- **3/3 integration tests passed** - Real database validation

## Common Tasks

### Refresh Data After Excel Update:
```bash
cd backend
python etl/load_strategic_data.py  # Extracts + Loads + Refreshes views
```

### Run Test Suite:
```bash
cd backend
pytest tests/test_strategic_api.py -v  # All tests
pytest tests/test_strategic_api.py::TestStrategicAPIIntegration -v  # Integration only
```

### Start Backend API:
```bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

### Start Frontend Dev Server:
```bash
cd frontend2
npm run dev  # Vite dev server on port 5173
```

## Project Status (Current State)

### ✅ Completed (V2 Backend):
- ETL pipeline for 3 CBS Excel files
- PostgreSQL schema with materialized views
- FastAPI endpoints serving strategic insights
- Professional test suite (500+ lines)
- Data validation and quality checks

### 🚧 In Progress:
- Frontend integration with new strategic endpoints
- Update Dashboard visualizations for 3 insights
- Replace BusinessInsight text with new narratives

### 📋 Next Steps:
1. Create React hooks for strategic endpoints
2. Build visualizations: Bar chart (quintiles), Scatter plot (digital), Stacked bar (retail)
3. Update all pages with new insights
4. Final testing and documentation

## Notes for Claude

- **This is a portfolio project** - Focus on showing professional skills, not just working code
- **The ETL journey is the story** - Document challenges and solutions
- **Keep existing UI/UX** - It's 80-90% perfect, just change data sources
- **Hebrew support is critical** - Always test RTL, encoding, and locale formatting
- **Test everything** - Professional test coverage is a key differentiator
