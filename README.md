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

**Completed:**
- ✅ Infrastructure setup (Docker, PostgreSQL, Redis)
- ✅ ETL pipeline (10,000 transactions processed)
- ✅ Database schema with stored procedures
- ✅ Security implementation (SQL injection prevention, input validation)
- ✅ CI/CD pipeline (GitHub Actions, Trivy security scanning)
- ✅ Connection pooling and environment-based configuration

**In Progress:**
- 🔄 FastAPI REST API endpoints
- 🔄 API authentication and rate limiting

**Planned:**
- ⏳ React frontend with Vite
- ⏳ D3.js visualizations (Sankey diagrams, time-series)
- ⏳ API documentation (OpenAPI/Swagger)

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

## API Endpoints (Phase 3)

```
GET  /api/dashboard      # Dashboard overview
GET  /api/customers      # Customer analytics
GET  /api/products       # Product performance
GET  /api/revenue        # Revenue analysis
GET  /api/transactions   # Transaction list with filters
```

## Database Schema

**Tables:**
- `transactions` - Core transaction data with indexes
- Views: `v_daily_revenue`, `v_product_performance`, `v_customer_analytics`

**Security:**
- Stored procedures for all write operations
- Prepared statements via SQLAlchemy
- Input validation via CHECK constraints
- Connection pooling (max 5 + 10 overflow)

## Performance Targets

- ETL: 10,000 records in <5 seconds ✅
- API response: <200ms average
- Database: Indexed queries, connection pooling
- Cache hit rate: >85%

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
- [Quick Reference](docs/QUICK_REFERENCE.md) - Architecture and commands
- [CI/CD Setup](docs/CI_CD_SETUP.md) - Pipeline configuration
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
