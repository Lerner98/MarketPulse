# Infrastructure Setup - MarketPulse V10

**The Golden Trio for Production Deployment**

Updated for V10 Normalized Star Schema - November 2025

---

## Overview

This guide covers the infrastructure setup for deploying MarketPulse V10 to production using modern, industry-standard tools.

---

## The Golden Trio Architecture

```
Frontend  → Vercel (React/Vite CDN)
Backend   → Render (Docker Container)
Database  → Neon.tech (PostgreSQL)
```

**Why This Stack:**
- ✅ Industry standard tools
- ✅ True microservices architecture
- ✅ $0 monthly cost (generous free tiers)
- ✅ Professional DevOps practices
- ✅ Persistent data (Neon doesn't delete after 90 days)

---

## 1. Database: Neon.tech (PostgreSQL)

### Why Neon.tech?

**Advantages:**
- ✅ Serverless PostgreSQL (auto-scaling)
- ✅ Generous free tier (3GB storage, 100 hours compute/month)
- ✅ **Never deletes your data** (unlike Render's free DB)
- ✅ Production-grade features (branching, point-in-time recovery)
- ✅ Fast autoscaling (spins up in <1 second)

### Setup Steps:

1. **Create Account**
   - Go to [neon.tech](https://neon.tech)
   - Sign up with GitHub (free, no credit card)

2. **Create Project**
   - Click **New Project**
   - Project name: `marketpulse-v10`
   - Region: `US East (N. Virginia)` or `EU Central (Frankfurt)` (closest to your users)
   - PostgreSQL version: `15` (recommended)

3. **Get Connection String**
   ```
   postgres://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

   **Important:** Save this securely - you'll need it for:
   - Local development (`.env`)
   - Render backend (environment variable)
   - Database migrations

4. **Create Database Schema**
   ```bash
   # Connect to Neon database
   psql "postgres://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require"

   # Run V10 schema
   \i backend/models/schema_v10_normalized.sql
   ```

   Or use Alembic migrations (recommended):
   ```bash
   cd backend
   alembic upgrade head
   ```

### Free Tier Limits:
- **Storage:** 3 GB
- **Compute hours:** 100 hours/month
- **Projects:** 1 project
- **Branches:** 10 branches (great for dev/staging)

**V10 Usage:** ~50 MB for 6,420 records + materialized views (well within limits)

---

## 2. Backend: Render (Docker)

### Why Render?

**Advantages:**
- ✅ Native Docker support (no buildpacks, uses your Dockerfile)
- ✅ Auto-deploy from GitHub (push to `main` = automatic deployment)
- ✅ Free tier: 750 hours/month (enough for 1 service running 24/7)
- ✅ Built-in health checks, metrics, and logs
- ✅ Easy environment variable management

### Setup Steps:

1. **Create Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free, no credit card)
   - Authorize Render to access your repositories

2. **Connect Repository**
   - Dashboard → **New** → **Web Service**
   - Connect your GitHub repository: `GuyCohen85/MarketPulse`
   - Branch: `main`

3. **Configure Service**

   **Basic Settings:**
   - Name: `marketpulse-backend-v10`
   - Region: `Frankfurt` (or `Oregon` if US-based users)
   - Runtime: **Docker**
   - Dockerfile path: `./backend/Dockerfile`
   - Docker context: `./backend`

   **Instance Type:**
   - Plan: **Free**
   - Resources: 512 MB RAM, 0.1 CPU (sufficient for V10)

   **Auto-Deploy:**
   - ✅ Auto-deploy: **Yes** (deploy on push to `main`)

4. **Environment Variables** (Add in Render Dashboard)
   ```
   DATABASE_URL=postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require
   ENVIRONMENT=production
   CORS_ORIGINS=https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app
   SECRET_KEY=<generate with: openssl rand -hex 32>
   ```

5. **Health Check**
   - Path: `/health`
   - Interval: 30 seconds
   - Render will restart service if health check fails

### Free Tier Limits:
- **Services:** 1 free web service
- **Hours:** 750 hours/month (31 days × 24 hours = 744 hours)
- **RAM:** 512 MB
- **Spins down after 15 minutes of inactivity** (spins up automatically on request)

**V10 Performance:** API responses < 300ms (with materialized views)

---

## 3. Frontend: Vercel

### Why Vercel?

**Advantages:**
- ✅ Zero-config React/Vite deployment
- ✅ Global CDN (fast worldwide)
- ✅ Free tier: Unlimited bandwidth (yes, really)
- ✅ Automatic HTTPS
- ✅ Preview deployments for every PR (test before merging)

### Setup Steps:

1. **Create Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub (free, no credit card)

2. **Import Project**
   - Dashboard → **New Project**
   - Import `GuyCohen85/MarketPulse`
   - Framework Preset: **Vite**
   - Root Directory: `frontend2`

3. **Build Configuration**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Environment Variables**
   ```
   VITE_API_URL=https://marketpulse-backend-v10.onrender.com
   ```

5. **Deploy**
   - Click **Deploy**
   - Vercel builds and deploys to: `https://marketpulse.vercel.app`
   - Production URL is stable (never changes)

### Free Tier Limits:
- **Bandwidth:** Unlimited ✅
- **Builds:** 100 hours/month (build time, not runtime)
- **Team members:** 1 (for personal projects)
- **Preview deployments:** Unlimited

**V10 Build Time:** ~2 minutes per deployment

---

## 4. Infrastructure as Code (render.yaml)

### Why Use render.yaml?

**Benefits:**
- ✅ Configuration versioned in Git
- ✅ Reproducible deployments
- ✅ Team members can see all settings
- ✅ One-click redeploy (delete + recreate from yaml)

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
    repo: https://github.com/GuyCohen85/MarketPulse
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

### How to Deploy with render.yaml:

1. **Commit to Git**
   ```bash
   git add render.yaml
   git commit -m "feat(infra): add render.yaml for V10 infrastructure"
   git push origin main
   ```

2. **Deploy via Blueprint**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **Blueprints** in sidebar
   - Click **New Blueprint Instance**
   - Select your GitHub repository
   - Render auto-detects `render.yaml`
   - Click **Apply**

3. **Add Secrets in Dashboard**
   - Go to service → **Environment**
   - Add `DATABASE_URL` and `SECRET_KEY`

---

## 5. URL Format

### Connection URLs

**Format:**
```
postgresql://[user]:[password]@[host]:[port]/[database]?[parameters]
```

**Neon.tech Example:**
```
postgres://user:password@ep-xyz-123.us-east-2.aws.neon.tech:5432/neondb?sslmode=require
```

**For Async (FastAPI):**
```python
# Replace postgresql:// with postgresql+asyncpg://
DATABASE_URL = "postgresql+asyncpg://user:password@ep-xyz-123.us-east-2.aws.neon.tech:5432/neondb?sslmode=require"
```

---

## 6. Cost Breakdown (Free Tier)

| Service | Free Tier | V10 Usage | Cost |
|---------|-----------|-----------|------|
| **Neon.tech** | 3 GB storage, 100 hours compute/month | ~50 MB, ~40 hours/month | $0 |
| **Render** | 750 hours/month, 512 MB RAM | 744 hours/month | $0 |
| **Vercel** | Unlimited bandwidth, 100 build hours | ~2 min/build | $0 |
| **Total** | - | - | **$0/month** |

**Upgrade Costs (if needed):**
- Neon.tech Pro: $19/month (3 projects, 10 GB storage)
- Render Pro: $7/month (no spin-down, 512 MB RAM)
- Vercel Pro: $20/month (team features, priority support)

---

## 7. Environment Variables Summary

### Local Development (`.env`)
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/marketpulse
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SECRET_KEY=dev-secret-key-change-in-prod
```

### Production (Render)
```bash
DATABASE_URL=postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require
ENVIRONMENT=production
CORS_ORIGINS=https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app
SECRET_KEY=<openssl rand -hex 32>
```

### Production (Vercel)
```bash
VITE_API_URL=https://marketpulse-backend-v10.onrender.com
```

---

## 8. Deployment Checklist

### Initial Setup (One Time):
```
□ Create Neon.tech account and database
□ Run V10 schema (schema_v10_normalized.sql)
□ Create Render account
□ Create render.yaml in repo root
□ Create Vercel account
□ Configure environment variables in Render
□ Configure environment variables in Vercel
□ Test health check endpoint (/health)
□ Verify CORS origins
```

### Every Deployment:
```
□ Push to main branch
□ Render auto-deploys backend
□ Vercel auto-deploys frontend
□ Check logs in Render dashboard
□ Test production URLs
□ Verify materialized views refreshed
```

---

## 9. Troubleshooting

### Database Connection Issues

**Error:** `SSL connection is required`
**Solution:** Add `?sslmode=require` to Neon.tech URL

**Error:** `asyncpg.exceptions.InvalidPasswordError`
**Solution:** URL-encode special characters in password

**Error:** `relation "dim_segment" does not exist`
**Solution:** Run migrations: `alembic upgrade head`

### Render Deployment Issues

**Error:** `Health check failed`
**Solution:** Ensure `/health` endpoint returns 200 OK

**Error:** `Port 10000 is not available`
**Solution:** Use `PORT` env var from Render (injected automatically)

**Error:** `docker build failed`
**Solution:** Check `backend/Dockerfile` syntax and `.dockerignore`

### Vercel Build Issues

**Error:** `VITE_API_URL is not defined`
**Solution:** Add environment variable in Vercel dashboard

**Error:** `Build exceeded maximum duration`
**Solution:** Optimize dependencies, check for circular imports

---

## 10. Next Steps

After infrastructure is set up:

1. **Read:** [DAILY_WORKFLOW.md](DAILY_WORKFLOW.md) - Development workflow
2. **Read:** [DOCKER_AND_DEPLOYMENT.md](DOCKER_AND_DEPLOYMENT.md) - Docker setup
3. **Deploy:** Follow deployment steps above
4. **Monitor:** Check Render logs and Vercel analytics

---

**Last Updated:** November 2025
**Version:** V10 Normalized Star Schema
**Status:** Production-Ready ✅
