# 🚀 Production-Ready Workflow (The CORRECT Way)

**For Solo Developers / Small Teams**  
**Stack:** React + FastAPI + PostgreSQL  
**Based on Modern Best Practices (2025)**

---

## 🎯 THE REAL WORKFLOW

### **Branch Strategy: Trunk-Based Development**

```
main (production) ← The only long-lived branch
  ↓
  ├─ feat/dashboard-quintiles
  ├─ fix/hebrew-encoding
  └─ hotfix/cors-error
```

**Rules:**
1. ✅ `main` is always deployable
2. ✅ Feature branches are short-lived (1-3 days max)
3. ✅ Merge to `main` = deploy to production
4. ✅ No `develop` branch (useless overhead)

**Why This is Professional:**
- Used by Google, Facebook, Amazon
- Fast deployment cycle
- Less merge conflicts
- Simpler CI/CD

---

## 🗄️ DATABASE MIGRATIONS (THE RIGHT WAY)

### **Setup Alembic**

**Install:**
```bash
cd backend
pip install alembic
pip freeze > requirements.txt
```

**Initialize:**
```bash
alembic init alembic
```

**Configure: `alembic/env.py`**
```python
from api.models import Base  # Your SQLAlchemy models
from config import Config

# Set target metadata
target_metadata = Base.metadata

# Get database URL
config.set_main_option("sqlalchemy.url", Config.DATABASE_URL)
```

**Configure: `alembic.ini`**
```ini
# Change this line:
sqlalchemy.url = driver://user:pass@localhost/dbname

# To this:
# sqlalchemy.url is set in env.py from environment variables
```

---

### **Create Migration**

```bash
# After changing models
alembic revision --autogenerate -m "add phone_number to users"

# This generates: alembic/versions/abc123_add_phone_number.py
```

**Review the generated migration:**
```python
"""add phone_number to users

Revision ID: abc123
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(20)))

def downgrade():
    op.drop_column('users', 'phone_number')
```

---

### **Apply Migration**

**Local:**
```bash
alembic upgrade head
```

**Production (Automated):**

**Update `Dockerfile` entrypoint:**
```dockerfile
# Single Dockerfile for dev AND prod
FROM python:3.10-slim as base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Entrypoint with migrations
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Create: `backend/docker-entrypoint.sh`**
```bash
#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
```

**Now every deploy automatically migrates the database before starting the app.**

---

## 🔐 SECRETS MANAGEMENT (THE PROFESSIONAL WAY)

### **Option 1: Doppler (Recommended for Juniors)** ⭐

**Why Doppler:**
- ✅ Free tier (generous)
- ✅ Industry standard
- ✅ Works with Render/Vercel
- ✅ Sync secrets automatically
- ✅ Audit logs (who changed what)

**Setup:**

1. **Go to [doppler.com](https://doppler.com)**
2. **Create project:** `marketpulse`
3. **Create environments:** `development`, `production`
4. **Add secrets:**
   ```
   DATABASE_URL=postgres://...
   CORS_ORIGINS=https://marketpulse.vercel.app
   API_KEY=xyz123
   ```

5. **Install Doppler CLI:**
   ```bash
   # Mac
   brew install dopplerhq/cli/doppler
   
   # Linux
   curl -sLf --retry 3 --tlsv1.2 --proto "=https" \
     'https://packages.doppler.com/public/cli/install.sh' | sh
   ```

6. **Login:**
   ```bash
   doppler login
   doppler setup
   ```

7. **Run locally:**
   ```bash
   # Instead of: python main.py
   doppler run -- python main.py
   
   # Automatically injects secrets
   ```

8. **Deploy to Render:**
   ```bash
   # In Render dashboard → Environment Variables
   # Add only this:
   DOPPLER_TOKEN=dp.st.xyz...
   
   # Then in Dockerfile:
   RUN pip install doppler-python
   
   # In entrypoint:
   doppler run -- uvicorn api.main:app
   ```

**Benefits:**
- ✅ Never commit secrets to git
- ✅ Rotate secrets without redeploying
- ✅ Team members get access automatically
- ✅ Audit trail ("Guy changed DATABASE_URL at 3pm")

---

### **Option 2: GitHub Secrets (Simpler but Less Flexible)**

**For CI/CD only:**

1. **GitHub repo → Settings → Secrets and variables → Actions**
2. **Add secrets:**
   ```
   DATABASE_URL
   VERCEL_TOKEN
   RENDER_DEPLOY_HOOK
   ```

3. **Use in workflows:**
   ```yaml
   - name: Deploy
     env:
       DATABASE_URL: ${{ secrets.DATABASE_URL }}
     run: |
       echo "Deploying with secrets..."
   ```

**Limitations:**
- ❌ Only works in GitHub Actions (not locally)
- ❌ Can't sync to Render/Vercel automatically
- ❌ No audit logs

---

## 📝 CONFIGURATION (NO HARDCODING)

### **File: `backend/config.py`** (Single config file)

```python
"""Environment-aware configuration"""
import os
from typing import List

class Config:
    """Application configuration from environment variables"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # CORS - From comma-separated env var
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # API
    API_PREFIX = "/api"
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    if ENVIRONMENT == "production" and not SECRET_KEY:
        raise ValueError("SECRET_KEY required in production")
    
    # Logging
    LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ["DATABASE_URL"]
        if cls.ENVIRONMENT == "production":
            required.extend(["SECRET_KEY"])
        
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
```

**File: `backend/api/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config

# Validate config on startup
Config.validate()

app = FastAPI(
    title="MarketPulse API",
    debug=Config.DEBUG,
)

# CORS from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,  # From env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": Config.ENVIRONMENT
    }
```

---

## 🐳 ONE DOCKERFILE (Dev + Prod)

### **File: `backend/Dockerfile`**

```dockerfile
# Single Dockerfile for all environments
FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Migrations + Start
COPY --chown=appuser:appuser docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command (override for dev)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **File: `backend/docker-entrypoint.sh`**

```bash
#!/bin/bash
set -e

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Migrations complete"
echo "🚀 Starting application..."

exec "$@"
```

### **Local Development with Hot Reload:**

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    command: uvicorn api.main:app --host 0.0.0.0 --reload  # Override for dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/marketpulse
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
    volumes:
      - ./backend:/app  # Hot reload
    depends_on:
      - db
  
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
  
  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app  # Hot reload
      - /app/node_modules  # Don't override

volumes:
  postgres_data:
```

**Run locally:**
```bash
docker-compose up
```

**Same Docker image, different command = Environment parity** ✅

---

## 🔄 THE CORRECT GIT WORKFLOW

### **Daily Development:**

```bash
# Start feature
git checkout main
git pull origin main
git checkout -b feat/add-phone-number

# Work
# ... code changes ...
git add .
git commit -m "feat(users): add phone number field"

# Push
git push origin feat/add-phone-number

# Create PR to main (NOT develop)
```

### **Pull Request Checklist:**

```markdown
## Changes
- Added phone_number field to User model
- Created Alembic migration
- Updated API endpoints

## Testing
- [x] Tested locally with Docker
- [x] Migration runs successfully
- [x] Tests pass
- [x] No breaking changes

## Deployment Notes
- Migration will run automatically via docker-entrypoint.sh
- No manual steps required
```

### **After PR Approved:**

```bash
# Merge to main
git checkout main
git pull origin main
# PR merged via GitHub UI (squash and merge)

# Tag release
git tag -a v1.2.0 -m "Add phone number field"
git push origin v1.2.0

# This triggers production deployment automatically
```

---

## 🤖 CORRECT CI/CD PIPELINE

### **File: `.github/workflows/deploy.yml`** (One workflow)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          cd backend
          alembic upgrade head
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          cd backend
          pytest tests/ -v
      
      - name: Test frontend build
        run: |
          cd frontend
          npm ci
          npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./frontend
```

**What This Does:**

1. **On PR:** Runs tests only (no deploy)
2. **On merge to main:** Tests + Deploy to production
3. **Migrations:** Tested in CI, run automatically on Render

---

## 🎯 ENVIRONMENT VARIABLES (Complete Setup)

### **Local Development:**

**File: `.env`** (gitignored)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/marketpulse
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SECRET_KEY=dev-secret-key-change-in-prod
```

### **Production (Render):**

**Environment Variables:**
```bash
DATABASE_URL=postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require
ENVIRONMENT=production
CORS_ORIGINS=https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app
SECRET_KEY=<generate with: openssl rand -hex 32>
```

### **Production (Vercel):**

**Environment Variables:**
```bash
VITE_API_URL=https://marketpulse-api.onrender.com
```

### **Using Doppler (Recommended):**

**Render:**
```bash
# Only add this in Render:
DOPPLER_TOKEN=dp.st.production.xyz123
```

**Vercel:**
```bash
# Only add this in Vercel:
DOPPLER_TOKEN=dp.st.production.xyz123
```

**Then all other secrets come from Doppler automatically.**

---

## 🚫 SKIP STAGING ENVIRONMENT

### **Why No Staging:**

**Problem:**
- Free tier burns in 15 days with 2 services
- Double the maintenance
- Rarely catches bugs that local dev doesn't

**Solution:**

1. **Test locally with Docker** (identical to prod)
2. **Use Vercel Preview Deploys** for frontend PRs
3. **If absolutely needed:** Spin up temporary Render instance, test, delete

**Vercel Preview Deploys:**
```
Every PR automatically gets:
https://marketpulse-git-feat-login-yourname.vercel.app

Point it to your local backend for testing.
Delete when merged.
```

---

## ✅ CORRECT PRODUCTION CHECKLIST

### **Setup (One Time):**
```
□ Install Alembic
□ Create initial migration
□ Setup Doppler (or GitHub Secrets)
□ Add docker-entrypoint.sh
□ Configure single Dockerfile
□ Update config.py (no hardcoded values)
□ Add /health endpoint
□ Setup GitHub Actions workflow
```

### **Every Feature:**
```
□ Create feature branch from main
□ Make changes
□ Run migrations locally: alembic upgrade head
□ Test in Docker: docker-compose up
□ Push and create PR to main
□ CI runs tests automatically
□ Merge to main = deploy to production
□ Tag release: git tag v1.x.x
```

### **Database Changes:**
```
□ Change model in code
□ Generate migration: alembic revision --autogenerate
□ Review migration file
□ Test locally: alembic upgrade head
□ Commit migration file
□ Push (will run automatically in production)
```

---

## 🐛 COMMON MISTAKES TO AVOID

### **❌ Don't Do This:**

```python
# Hardcoded URLs
CORS_ORIGINS = ["https://marketpulse.vercel.app"]

# Multiple config files
config/development.py
config/production.py
config/staging.py

# Manual migrations
psql < schema.sql  # This breaks on updates

# Two Dockerfiles
Dockerfile
Dockerfile.dev

# develop branch
git checkout develop
git merge main
```

### **✅ Do This Instead:**

```python
# Environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")

# Single config file
config.py  # Uses env vars

# Automated migrations
alembic upgrade head  # In docker-entrypoint.sh

# One Dockerfile
Dockerfile  # Override CMD for dev

# Trunk-based
git checkout main
git checkout -b feat/new-feature
```

---

## 📊 WHAT RECRUITERS ACTUALLY SEE

### **GitHub:**
- ✅ Trunk-based development (modern)
- ✅ Alembic migrations (professional DB management)
- ✅ Single Dockerfile (environment parity)
- ✅ Automated CI/CD
- ✅ No hardcoded config
- ✅ Secrets management with Doppler

### **In Interviews:**

**Q:** "How do you handle database migrations?"

**Bad Answer:** "I run SQL scripts manually"

**Good Answer:** "I use Alembic to generate migrations from model changes. Migrations run automatically on deployment via the Docker entrypoint script. This ensures schema changes are versioned in Git and applied consistently across environments."

---

**Q:** "How do you manage secrets?"

**Bad Answer:** "I use .env files"

**Good Answer:** "I use Doppler to centrally manage secrets across environments. Developers run `doppler run` locally which injects secrets. In production, I set a single DOPPLER_TOKEN environment variable that pulls all secrets automatically. This allows secret rotation without redeployment and provides an audit trail."

---

**Q:** "What's your branching strategy?"

**Bad Answer:** "I use GitFlow with master, develop, and feature branches"

**Good Answer:** "I use trunk-based development where all features branch from and merge back to main. Main is always deployable. This reduces merge conflicts, speeds up deployment, and is the industry standard at modern tech companies. If a feature needs testing, Vercel provides preview deployments automatically."

---

## 🎯 SUMMARY: THE REAL PRODUCTION WORKFLOW

```
1. ✅ Trunk-based: feat → main (no develop)
2. ✅ Alembic: Auto migrations on deploy
3. ✅ One Dockerfile: Dev/prod parity
4. ✅ Config from env vars: No hardcoding
5. ✅ Doppler: Professional secrets
6. ✅ Health endpoint: /health for monitoring
7. ✅ Skip staging: Use Docker + Vercel previews
```

**Time to Implement:** 2-3 hours  
**Skill Level:** Strong Junior → Mid-level  
**Impact:** Massive (shows you understand production)

---

**End of Corrected Workflow Guide**
