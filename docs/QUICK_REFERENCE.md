# MarketPulse Quick Reference

## Architecture
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React + D3.js + Vite
- **Database**: PostgreSQL 15 (port 5433)
- **Cache**: Redis 7 (port 6379)
- **Container**: Docker Compose

## Data Schema (from data-analyst-portfolio.md)
```python
{
    'transaction_id': int,
    'customer_name': str (Hebrew),
    'product': str (Hebrew),
    'amount': float,
    'currency': 'ILS',
    'date': 'YYYY-MM-DD',
    'status': ['completed', 'pending', 'cancelled']
}
```

## ETL Pipeline (Phase 2)
- **Input**: data/raw/transactions.csv
- **Class**: EcommerceDataCleaner
- **Output**: PostgreSQL tables
- **Features**: Deduplication, validation, Hebrew support

## API Endpoints (Phase 3)
- GET /api/dashboard - Dashboard data
- GET /api/customers - Customer analytics
- GET /api/products - Product metrics
- GET /api/revenue - Revenue analysis

## Visualizations (Phase 4)
- Customer Journey Sankey (D3.js)
- Revenue charts (Recharts)
- Product performance
- Geographic distribution

## Commands
```bash
# Start services
docker-compose up -d

# Run ETL
python backend/data_pipeline/cleaner.py

# Start backend
cd backend && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev
```

## Knowledge Base Files to Reference
- 02_SECURITY_COMPREHENSIVE.md - Security patterns
- 05_APPLICATION_ARCHITECTURE.md - Architecture
- 06_DATABASE_ENGINEERING.md - Database best practices
- 08_BACKEND_DEVELOPMENT.md - FastAPI patterns
- 12_FRONTEND_DEVELOPMENT.md - React patterns
- 11_TESTING_QA.md - Testing strategies
