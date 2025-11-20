# MarketPulse

E-commerce analytics platform with ETL pipeline, REST API, and interactive visualizations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![CI/CD](https://github.com/Lerner98/MarketPulse/workflows/MarketPulse%20CI/CD/badge.svg)](https://github.com/Lerner98/MarketPulse/actions)

## Overview

Production-ready analytics platform that processes transaction data, provides REST APIs for business intelligence, and delivers interactive dashboards for data-driven decision making.

### Key Features

- ETL pipeline with data validation and cleaning
- PostgreSQL database with optimized queries and stored procedures
- FastAPI REST endpoints with authentication
- Interactive D3.js visualizations
- Docker containerization with PostgreSQL and Redis
- Automated CI/CD pipeline with security scanning

## Architecture

```
Frontend (React) → Backend (FastAPI) → Database (PostgreSQL) + Cache (Redis)
```

**Data Flow:**
1. Raw CSV data → ETL Pipeline → PostgreSQL
2. Client request → FastAPI → Redis Cache / PostgreSQL
3. Response → React → D3.js Visualization

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/Lerner98/MarketPulse.git
cd MarketPulse

# Start infrastructure
docker-compose up -d

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run ETL pipeline
python backend/data_pipeline/cleaner.py
```

### Verify Installation

```bash
# Check services
docker-compose ps

# Verify database
python -c "from backend.models.database import DatabaseManager; db = DatabaseManager(); print('✓' if db.test_connection() else '✗')"
```

## Project Structure

```
MarketPulse/
├── .github/workflows/    # CI/CD pipeline
├── backend/
│   ├── api/             # REST endpoints
│   ├── data_pipeline/   # ETL implementation
│   │   └── cleaner.py   # Data cleaning & validation
│   ├── models/          # Database layer
│   │   ├── database.py  # Connection manager
│   │   └── schema.sql   # Database schema
│   └── tests/           # Test suite
├── frontend/            # React application
├── data/
│   ├── raw/            # Source data (CSV)
│   └── processed/      # Cleaned data
├── docs/
│   ├── PHASE2_COMPLETE.md
│   ├── QUICK_REFERENCE.md
│   └── CI_CD_SETUP.md
├── scripts/
│   └── generate_synthetic_data.py
└── docker-compose.yml   # PostgreSQL + Redis
```

## Development Status

**Phase 3 Complete (Backend API):**
- ✅ Infrastructure setup (Docker, PostgreSQL, Redis)
- ✅ ETL pipeline (10,000 transactions processed)
- ✅ Database schema with stored procedures
- ✅ FastAPI REST API (5 endpoints, <200ms response time)
- ✅ Comprehensive test suite (65 tests, 74% coverage)
- ✅ Multi-stage Docker build (180MB production image)
- ✅ CI/CD pipeline (GitHub Actions, passing all checks)
- ✅ Security implementation (SQL injection prevention, input validation, Trivy scanning)
- ✅ Connection pooling and environment-based configuration
- ✅ API documentation (Swagger UI at /docs)

**In Progress:**
- 🔄 Frontend Development (Phase 4)

**Planned:**
- ⏳ React frontend with Vite
- ⏳ D3.js visualizations (Sankey diagrams, time-series)
- ⏳ Redis caching layer
- ⏳ JWT authentication

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL 15 (database)
- Redis 7 (caching)
- SQLAlchemy (ORM)
- Pandas (data processing)

**Frontend:**
- React 18
- D3.js (visualization)
- Vite (build tool)

**Infrastructure:**
- Docker Compose
- GitHub Actions (CI/CD)
- Pytest (testing)

**Security:**
- Stored procedures (SQL injection prevention)
- Whitelist validation (products, currencies, statuses)
- Environment variables (credential management)
- Connection pooling (DoS prevention)
- Trivy (vulnerability scanning)

## ETL Pipeline

**Features:**
- UTF-8 encoding for Hebrew text support
- Whitelist validation for products, currencies, and statuses
- Duplicate detection by transaction ID
- Data type enforcement and range validation
- Batch insertion with prepared statements

**Performance:**
- 10,000 records processed in <5 seconds
- 100% validation success rate
- Zero data loss

**Command:**
```bash
python backend/data_pipeline/cleaner.py
```

## API Endpoints

**Base URL:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs` (Swagger UI)

```
GET  /api/health        # Service health check (no auth)
GET  /api/dashboard     # Dashboard metrics (revenue, transactions, top products)
GET  /api/revenue       # Daily revenue breakdown with date filtering
GET  /api/customers     # Customer analytics (paginated, sortable)
GET  /api/products      # Product performance ordered by revenue
```

**Performance:** All endpoints respond in <200ms with indexed database views and connection pooling (5 base + 10 overflow connections).

## Database Schema

**Tables:**
- `transactions` - Core transaction data with indexes
- Views: `v_daily_revenue`, `v_product_performance`, `v_customer_analytics`

**Security:**
- Stored procedures for all write operations
- Prepared statements via SQLAlchemy
- Input validation via CHECK constraints
- Connection pooling (max 5 + 10 overflow)

## Performance Metrics

- ETL: 10,000 records in <5 seconds ✅
- API response: <200ms average ✅
  - /health: 2-5ms
  - /dashboard: 120-180ms
  - /revenue: 80-140ms
  - /customers: 95-160ms
  - /products: 75-130ms
- Database: Indexed queries with connection pooling ✅
- Docker image: 180MB (multi-stage build) ✅
- Test coverage: 74% (65 tests passing) ✅

## Testing

```bash
# Backend tests
cd backend
pytest tests/ --cov=. --cov-report=term

# Run CI/CD locally
docker-compose -f .github/workflows/docker-compose.test.yml up
```

## Documentation

- [Phase 2 Complete](docs/PHASE2_COMPLETE.md) - ETL pipeline implementation
- [Phase 3 Complete](docs/PHASE3_COMPLETE.md) - Backend API implementation
- [Quick Reference](docs/QUICK_REFERENCE.md) - Architecture and commands
- [CI/CD Setup](docs/CI_CD_SETUP.md) - Pipeline configuration and lessons learned
- [Architecture Decisions](docs/ADR/) - Technical decisions (planned)

## Security

**Implemented:**
- SQL injection prevention via stored procedures
- Input validation with whitelist approach
- Connection pooling to prevent exhaustion attacks
- Environment-based configuration (no hardcoded secrets)
- Security scanning in CI/CD (Trivy)
- Password redaction in logs

**Following:**
- [Knowledge Base: Security & Attack Prevention](https://github.com/Lerner98/MarketPulse/blob/main/.claude/CLAUDE.md)
- OWASP Top 10 guidelines
- PostgreSQL security best practices

## CI/CD Pipeline

**Jobs:**
- Backend tests (PostgreSQL + Redis services)
- Frontend tests (Node.js 18)
- Docker build validation
- Trivy security scanning

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`

**View Results:** [GitHub Actions](https://github.com/Lerner98/MarketPulse/actions)

## Author

Guy Lerner
[GitHub](https://github.com/Lerner98) | [LinkedIn](https://linkedin.com/in/guy-lerner)

## License

MIT
