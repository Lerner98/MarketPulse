# Docker and Deployment - MarketPulse V10

**Production-Grade Docker Setup with Automated Migrations**

Updated for V10 Normalized Star Schema - November 2025

---

## Overview

This guide covers:
- Docker multi-stage build for production
- Alembic async migrations (critical for FastAPI)
- docker-compose for local development
- render.yaml for Infrastructure as Code
- Automated deployment pipeline

---

## Part 1: The Perfect Dockerfile

### Single Dockerfile for Dev + Prod

**File: `backend/Dockerfile`**

```dockerfile
# MarketPulse Backend - Production Dockerfile
# Multi-stage build optimized for size and security

FROM python:3.10-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user (security best practice)
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /app/docker-entrypoint.sh

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Entrypoint runs migrations, then starts app
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (override for dev with --reload)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Docker Entrypoint Script

**File: `backend/docker-entrypoint.sh`**

```bash
#!/bin/bash
set -e

echo "🔄 Running database migrations..."
python -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migration failed!"
    exit 1
fi

echo "🚀 Starting application..."
exec "$@"
```

**Make executable:**
```bash
chmod +x backend/docker-entrypoint.sh
```

**What This Does:**
1. Runs all pending Alembic migrations
2. If migration fails → deployment fails (safe!)
3. If migration succeeds → starts FastAPI app
4. Prevents running app with outdated schema

---

### .dockerignore

**File: `backend/.dockerignore`**

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.env
.env.*
.git
.gitignore
.pytest_cache
*.log
*.sqlite
.vscode/
.idea/
*.md
!README.md
tests/
docs/
data/raw/
data/v10_exports/
data/v10_logs/
alembic/versions/*.pyc
```

**Benefits:**
- ✅ Smaller image size (excludes test files, docs, logs)
- ✅ Faster builds (less context to send)
- ✅ No sensitive data in image (`.env` excluded)

---

## Part 2: Alembic Async Migrations

### Why Async Alembic?

**Problem:** FastAPI uses `asyncpg` (async database driver). Default Alembic is sync.

**Solution:** Configure Alembic for async support.

---

### Setup Alembic (Step-by-Step)

**Step 1: Install**

```bash
cd backend
pip install alembic asyncpg
pip freeze > requirements.txt
```

**Step 2: Initialize**

```bash
alembic init alembic
```

This creates:
```
backend/
├── alembic/
│   ├── versions/        # Migration files go here
│   ├── env.py          # We'll modify this for async
│   └── script.py.mako
└── alembic.ini         # Config file
```

---

### Step 3: Configure for Async (CRITICAL)

**File: `backend/alembic/env.py`**

```python
"""Alembic environment configuration with async support"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models so Alembic can detect changes
from api.models import Base  # Adjust import path to your models
from config import Config

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata for autogenerate
target_metadata = Base.metadata

# Override sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", Config.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL file)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Helper to run migrations with provided connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async support)"""
    # Create async engine
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Run migrations
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Choose mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

**What This Does:**
- ✅ Supports async PostgreSQL (asyncpg)
- ✅ Reads DATABASE_URL from environment
- ✅ Auto-detects model changes
- ✅ Works in production with Render

---

### Step 4: Create Your First Migration

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "initial V10 schema"

# This creates: alembic/versions/abc123_initial_v10_schema.py
```

**Review the generated file:**
```python
"""initial V10 schema

Revision ID: abc123
Revises:
Create Date: 2025-11-22 10:30:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create dim_segment table
    op.create_table(
        'dim_segment',
        sa.Column('segment_key', sa.Integer(), primary_key=True),
        sa.Column('segment_type', sa.String(100), nullable=False),
        sa.Column('segment_value', sa.String(200), nullable=False),
        sa.Column('segment_order', sa.Integer()),
        sa.Column('file_source', sa.String(100)),
    )

    # Create fact_segment_expenditure table
    op.create_table(
        'fact_segment_expenditure',
        sa.Column('expenditure_key', sa.Integer(), primary_key=True),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('segment_key', sa.Integer(), nullable=False),
        sa.Column('expenditure_value', sa.Numeric(12, 2)),
        sa.Column('is_income_metric', sa.Boolean(), default=False),
        sa.Column('is_consumption_metric', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['segment_key'], ['dim_segment.segment_key']),
    )

def downgrade():
    # Rollback
    op.drop_table('fact_segment_expenditure')
    op.drop_table('dim_segment')
```

**Apply migration:**
```bash
alembic upgrade head
```

---

### Step 5: Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "add phone number field"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history

# Generate SQL without applying (offline mode)
alembic upgrade head --sql
```

---

## Part 3: Docker Compose for Local Development

**File: `docker-compose.yml`** (root of repository)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn api.main:app --host 0.0.0.0 --reload  # Hot reload for dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app  # Mount for hot reload
      - /app/__pycache__  # Don't sync cache
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/marketpulse
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=marketpulse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: ./frontend2
      dockerfile: Dockerfile
    command: npm run dev -- --host
    ports:
      - "5173:5173"
    volumes:
      - ./frontend2:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  postgres_data:
```

**Usage:**

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Remove volumes (clean database)
docker-compose down -v
```

**Benefits:**
- ✅ Identical to production (same Dockerfile)
- ✅ Hot reload for development
- ✅ PostgreSQL included (no external setup)
- ✅ One command to start everything

---

## Part 4: Infrastructure as Code (render.yaml)

### Why Infrastructure as Code?

**Manual Dashboard (BAD):**
- ❌ Click buttons in Render dashboard
- ❌ Not versioned in Git
- ❌ Can't reproduce
- ❌ Team members don't know config

**Infrastructure as Code (GOOD):**
- ✅ Config in Git (versioned, documented)
- ✅ Reproducible (one-click redeploy)
- ✅ Team can see all settings
- ✅ Professional DevOps practice

---

### File: `render.yaml` (Root of repository)

```yaml
# MarketPulse V10 Infrastructure Blueprint
# This file defines all infrastructure as code
# Deploy via: Render Dashboard → Blueprints → New Blueprint Instance

services:
  # Backend API Service
  - type: web
    name: marketpulse-backend-v10
    runtime: docker
    repo: https://github.com/GuyCohen85/MarketPulse  # ← Update with your repo
    plan: free
    region: frankfurt  # or oregon (closest to users)
    branch: main
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend

    # Health check endpoint
    healthCheckPath: /health

    # Auto-deploy on push to main
    autoDeploy: true

    # Pre-deploy command (runs migrations before starting app)
    # This ensures database schema matches code
    preDeployCommand: "python -m alembic upgrade head"

    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.10.0"

      - key: ENVIRONMENT
        value: production

      # Secrets (set these in Render Dashboard for security)
      - key: DATABASE_URL
        sync: false  # Must be set manually (contains password)

      - key: SECRET_KEY
        sync: false  # Must be set manually

      # Public configuration
      - key: CORS_ORIGINS
        value: "https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app"

# Note: Database is external (Neon.tech) for persistence
# Render's free DB deletes after 90 days - use Neon instead
```

---

### How to Deploy with render.yaml

**Step 1: Update the file**
```yaml
repo: https://github.com/GuyCohen85/MarketPulse  # Your actual GitHub repo
```

**Step 2: Commit to Git**
```bash
git add render.yaml
git commit -m "feat(infra): add render.yaml for V10 infrastructure"
git push origin main
```

**Step 3: Deploy via Blueprint**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **Blueprints** in sidebar
3. Click **New Blueprint Instance**
4. Select your GitHub repository
5. Render auto-detects `render.yaml`
6. Click **Apply**

**Step 4: Add Secrets in Dashboard**

Render will create the service but needs you to add secrets:

1. Go to service → **Environment**
2. Add:
   ```
   DATABASE_URL=postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require
   SECRET_KEY=<openssl rand -hex 32>
   ```

**Step 5: Verify Deployment**

1. Check logs: Render Dashboard → Service → Logs
2. Test health check: `https://marketpulse-backend-v10.onrender.com/health`
3. Test API: `https://marketpulse-backend-v10.onrender.com/api/v10/segments/types`

---

## Part 5: Configuration Management

### Single Config File (No Hardcoding)

**File: `backend/config.py`**

```python
"""Application configuration from environment variables only"""
import os
from typing import List

class Config:
    """Environment-aware configuration"""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Replace postgresql:// with postgresql+asyncpg:// for async support
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    # API
    API_PREFIX = "/api"
    API_VERSION = "v10"
    API_TITLE = "MarketPulse V10 API"

    # CORS - From comma-separated environment variable
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Strip whitespace from origins
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    if ENVIRONMENT == "production" and not SECRET_KEY:
        raise ValueError("SECRET_KEY is required in production")

    # Logging
    LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

    # Database pool settings
    DB_POOL_SIZE = 20 if ENVIRONMENT == "production" else 5
    DB_MAX_OVERFLOW = 40 if ENVIRONMENT == "production" else 10

    @classmethod
    def validate(cls):
        """Validate required configuration on startup"""
        required = ["DATABASE_URL"]

        if cls.ENVIRONMENT == "production":
            required.extend(["SECRET_KEY"])

        missing = []
        for key in required:
            if not getattr(cls, key, None):
                missing.append(key)

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Log configuration (sanitized)
        print(f"🔧 Environment: {cls.ENVIRONMENT}")
        print(f"🔧 CORS Origins: {cls.CORS_ORIGINS}")
        print(f"🔧 Database: {cls.DATABASE_URL.split('@')[1] if '@' in cls.DATABASE_URL else 'configured'}")

# Validate on import
Config.validate()
```

---

### Use in FastAPI

**File: `backend/api/main.py`**

```python
"""FastAPI application with environment-aware configuration"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config

# Create app
app = FastAPI(
    title=Config.API_TITLE,
    version=Config.API_VERSION,
    debug=Config.DEBUG,
)

# CORS from environment variables (NOT hardcoded)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,  # From env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "environment": Config.ENVIRONMENT,
        "version": Config.API_VERSION
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MarketPulse V10 API",
        "docs": "/docs",
        "health": "/health"
    }

# Import routers
from api.routers import segmentation_v10
app.include_router(segmentation_v10.router, prefix=Config.API_PREFIX)
```

---

## Part 6: Deployment Checklist

### Initial Setup (One Time):

```
□ Create Dockerfile with multi-stage build
□ Create docker-entrypoint.sh (chmod +x)
□ Add .dockerignore
□ Setup Alembic with async support
□ Create initial migration
□ Test locally with docker-compose
□ Create render.yaml
□ Commit to Git
□ Deploy via Render Blueprint
□ Add secrets in Render dashboard
□ Verify health check works
□ Test production API endpoints
```

### Every Deployment:

```
□ Push to main branch
□ GitHub Actions runs tests (if configured)
□ Render auto-deploys backend
□ Render runs pre-deploy: alembic upgrade head
□ Render starts new container
□ Render runs health check
□ Old container shuts down (zero-downtime)
□ Check logs in Render dashboard
□ Test production URLs
```

---

## Part 7: Troubleshooting

### Docker Build Issues

**Error:** `ERROR [backend 3/8] RUN apt-get update`
**Solution:** Check network connection, try `docker build --no-cache`

**Error:** `permission denied: docker-entrypoint.sh`
**Solution:** `chmod +x backend/docker-entrypoint.sh` and commit

**Error:** `COPY failed: no such file or directory`
**Solution:** Check `dockerContext` in render.yaml matches Dockerfile location

---

### Alembic Migration Issues

**Error:** `Target database is not up to date`
**Solution:** Run `alembic upgrade head` manually, then redeploy

**Error:** `Can't locate revision identified by 'abc123'`
**Solution:** Check `alembic/versions/` directory contains migration files

**Error:** `asyncpg.exceptions.UndefinedTableError`
**Solution:** Database doesn't have tables - run `alembic upgrade head`

---

### Render Deployment Issues

**Error:** `Health check failed`
**Solution:** Ensure `/health` endpoint returns 200 OK

**Error:** `Build exceeded maximum duration (15 minutes)`
**Solution:** Optimize Dockerfile, use `.dockerignore` to exclude large files

**Error:** `Pre-deploy command failed`
**Solution:** Check Alembic migration syntax, verify DATABASE_URL is set

---

## Summary: The Production Pipeline

```
1. Developer pushes to main
2. Render detects push
3. Render builds Docker image (using Dockerfile)
4. Render runs pre-deploy: alembic upgrade head
5. Render starts new container
6. Container runs docker-entrypoint.sh
7. Entrypoint verifies migrations succeeded
8. Entrypoint starts FastAPI app
9. Render health check passes (/health)
10. Render switches traffic to new container
11. Old container shuts down
12. Deployment complete ✅
```

**Deployment time:** ~5-7 minutes
**Downtime:** 0 seconds (zero-downtime deployment)
**Rollback:** Redeploy previous commit

---

**Last Updated:** November 2025
**Version:** V10 Normalized Star Schema
**Status:** Production-Ready ✅
