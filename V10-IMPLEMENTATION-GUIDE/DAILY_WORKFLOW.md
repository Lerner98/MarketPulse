# Daily Development Workflow - MarketPulse V10

**Modern Trunk-Based Development for Solo Developers**

Updated for V10 Normalized Star Schema - November 2025

---

## Overview

This guide covers the day-to-day development workflow for MarketPulse V10, including:
- Trunk-based development (no `develop` branch)
- Feature branch workflow
- Local development with Docker
- Testing and deployment

---

## The Modern Way: Trunk-Based Development

### Why NOT GitFlow?

**Old Way (WRONG for solo developers):**
```
main
  ↓
develop ← You waste time syncing this
  ↓
feature/xyz
```

**Problems:**
- ❌ Merge conflicts with yourself
- ❌ Staging environment burns free tier in 2 weeks
- ❌ Slow deployment cycle
- ❌ Unnecessary complexity for solo dev

---

### The Modern Way: Trunk-Based Development

```
main (production) ← Only long-lived branch
  ↓
  ├─ feat/add-household-size
  ├─ fix/burn-rate-calculation
  └─ hotfix/cors-error
```

**Rules:**
1. ✅ `main` is always deployable
2. ✅ Feature branches live 1-3 days max
3. ✅ Merge to `main` = automatic production deploy
4. ✅ If you break production, fix forward (new PR, not revert)

**Why This is Professional:**
- Used by Google, Facebook, Amazon
- Faster iterations
- Forces you to keep `main` stable
- Encourages small, frequent commits

---

## Daily Development Workflow

### 1. Start New Feature

```bash
# Always start from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/add-household-size-segment
```

**Branch Naming Convention:**
- `feat/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation only
- `test/description` - Adding tests
- `hotfix/description` - Urgent production fix

---

### 2. Develop Locally

#### Option A: Using Docker Compose (Recommended)

```bash
# Start all services (backend + frontend + database)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

**Services:**
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Database: `localhost:5432`

**Features:**
- ✅ Hot reload for both backend and frontend
- ✅ PostgreSQL included (no external setup)
- ✅ Environment parity (same as production)

#### Option B: Local Development (Without Docker)

**Start Backend:**
```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run migrations
alembic upgrade head

# Start server with hot reload
uvicorn api.main:app --reload --port 8000
```

**Start Frontend (separate terminal):**
```bash
cd frontend2

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

---

### 3. Make Changes

#### Example: Add New Segment Type

**Step 1: Update Database Schema**

```sql
-- Add new file to segmentation_files table
-- (Already handled by load_segmentation.py for new files)
```

**Step 2: Add New CBS File**

```bash
# Place CBS Excel file in:
CBS Household Expenditure Data Strategy/HouseholdSize.xlsx
```

**Step 3: Configure ETL**

```python
# backend/etl/load_segmentation.py already handles this!
# Just need to update FILE_CONFIGS:

FILE_CONFIGS = {
    # ... existing configs ...
    "HouseholdSize.xlsx": {
        "segment_type": "Household Size",
        "header_row": 9,
        "segment_columns": {
            "pattern": r"^\d+$",  # Matches "1", "2", "3", etc.
        },
        # ... rest of config
    }
}
```

**Step 4: Run ETL**

```bash
cd backend
python etl/load_segmentation.py
```

**Step 5: Verify Data**

```bash
# Check database
python verify_unique_items.py

# Expected output:
# Household Size: 99 unique items, 594 total records
```

**Step 6: Update Frontend**

```tsx
// frontend2/src/pages/Dashboard.tsx
// The segment selector already auto-updates!
// Just verify "Household Size" appears in dropdown
```

---

### 4. Test Changes

#### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_segmentation_api.py -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html
```

#### Frontend Tests

```bash
cd frontend2

# Run unit tests
npm test

# Run E2E tests (if configured)
npm run test:e2e
```

#### Manual Testing

1. **Test API Endpoints:**
   ```bash
   # Get segment types
   curl http://localhost:8000/api/v10/segments/types

   # Get burn rate for Household Size
   curl http://localhost:8000/api/v10/burn-rate?segment_type=Household%20Size
   ```

2. **Test Frontend:**
   - Open `http://localhost:5173`
   - Select "Household Size" from dropdown
   - Verify burn rate chart updates
   - Verify inequality metrics load

---

### 5. Commit Changes

**Commit Message Format:**

```
<type>(<scope>): <short description>

<longer description if needed>

<footer: breaking changes, issue references>
```

**Examples:**

```bash
git add .
git commit -m "feat(etl): add Household Size segment type

- Add HouseholdSize.xlsx to FILE_CONFIGS
- Process 594 records across 6 household size groups
- Update dim_segment with new segment type
- Verify burn rate calculation works correctly

Closes #42"
```

```bash
git commit -m "fix(api): correct burn rate calculation for Income Decile

The burn rate was using wrong consumption metric flag.
Changed to use is_consumption_metric=True filter.

Before: 1000% burn rate (incorrect)
After: 146% burn rate (matches CBS data)"
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation
- `test` - Adding tests
- `chore` - Maintenance (deps, build, etc.)
- `perf` - Performance improvement

---

### 6. Push and Create PR

```bash
# Push feature branch
git push origin feat/add-household-size-segment

# Create PR via GitHub CLI (optional)
gh pr create \
  --title "feat(etl): Add Household Size segment type" \
  --body "Adds support for analyzing household expenditure by household size (1-6 members)."

# Or create PR on GitHub web interface
```

**PR Checklist:**

```markdown
## Changes
- [ ] Added new segment type configuration
- [ ] Ran ETL and verified data quality
- [ ] Updated frontend (auto-updates via API)
- [ ] Added tests for new segment type

## Testing
- [ ] Tested locally with Docker
- [ ] Backend tests pass (pytest)
- [ ] Frontend builds successfully
- [ ] Manual testing completed

## Data Quality
- [ ] Verified record count matches CBS file
- [ ] Checked burn rate values are realistic
- [ ] Confirmed no duplicate records
- [ ] Materialized views refreshed correctly

## Deployment Notes
- [ ] No breaking changes
- [ ] No migration required (uses existing schema)
- [ ] Compatible with existing API consumers
```

---

### 7. Review and Merge

**If CI Passes:**

1. Review your own changes (yes, review your own PRs!)
2. Check GitHub Actions logs
3. Merge via GitHub UI: **Squash and merge** (recommended)
4. Delete feature branch

```bash
# After merge, update local main
git checkout main
git pull origin main

# Delete local feature branch
git branch -d feat/add-household-size-segment
```

---

### 8. Automatic Deployment

**What Happens After Merge:**

1. **GitHub Actions** runs tests
2. **Render** detects push to `main`
3. **Render** builds Docker image
4. **Render** runs pre-deploy command: `alembic upgrade head`
5. **Render** deploys new container
6. **Render** runs health check
7. **Vercel** auto-deploys frontend

**Deployment takes:** ~5-7 minutes total

**Check Status:**
- Render: `https://dashboard.render.com`
- Vercel: `https://vercel.com/dashboard`

---

## Common Workflows

### Adding a New CBS File (New Segment Type)

```bash
# 1. Place CBS file in data folder
# 2. Update FILE_CONFIGS in load_segmentation.py
# 3. Run ETL
cd backend && python etl/load_segmentation.py

# 4. Verify data
python verify_unique_items.py

# 5. Test API
curl http://localhost:8000/api/v10/segments/types

# 6. Test frontend (segment auto-appears in dropdown)

# 7. Commit and push
git add .
git commit -m "feat(etl): add new segment type"
git push origin feat/new-segment
```

---

### Fixing a Bug in Production

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/burn-rate-rounding

# 2. Fix the bug
# ... make changes ...

# 3. Test locally
pytest tests/

# 4. Commit with clear description
git commit -m "fix(api): round burn rate to 1 decimal place

Burn rate was showing 146.234567% instead of 146.2%.
Added ROUND() to SQL query in vw_segment_burn_rate."

# 5. Push and create PR
git push origin hotfix/burn-rate-rounding

# 6. Merge immediately (if critical)
# 7. Automatic deployment to production
```

---

### Database Migration

```bash
# 1. Change SQLAlchemy model
# backend/api/models.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20))  # ← New field

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "add phone number to users"

# 3. Review generated migration
# backend/alembic/versions/abc123_add_phone_number.py

# 4. Test migration locally
alembic upgrade head

# 5. Test rollback
alembic downgrade -1
alembic upgrade head

# 6. Commit migration file
git add alembic/versions/
git commit -m "feat(db): add phone number field to users"

# 7. Push (migration runs automatically in production)
git push origin feat/add-phone-number
```

---

### Refreshing Materialized Views

**Automatic (Recommended):**

Views refresh automatically when data changes. The ETL script calls:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_burn_rate;
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_inequality;
```

**Manual (If Needed):**

```bash
# Connect to database
psql $DATABASE_URL

# Refresh views
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_burn_rate;
REFRESH MATERIALIZED VIEW CONCURRENTLY vw_segment_inequality;

# Or run Python script
cd backend
python refresh_views.py
```

---

## Environment Management

### Local Environment (.env)

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/marketpulse
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SECRET_KEY=dev-secret-key-change-in-prod
```

### Production Environment (Render)

**Set in Render Dashboard → Service → Environment:**

```bash
DATABASE_URL=postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require
ENVIRONMENT=production
CORS_ORIGINS=https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app
SECRET_KEY=<openssl rand -hex 32>
```

**Never commit these to Git!**

---

## Troubleshooting

### "Health check failed" on Render

**Cause:** `/health` endpoint not responding

**Fix:**
```python
# backend/api/main.py
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### "CORS error" on Frontend

**Cause:** Frontend URL not in `CORS_ORIGINS`

**Fix:**
```bash
# Render environment variables
CORS_ORIGINS=https://marketpulse.vercel.app,https://marketpulse-git-*.vercel.app
```

### "Alembic migration failed"

**Cause:** Database schema out of sync

**Fix:**
```bash
# Check current revision
alembic current

# Upgrade to latest
alembic upgrade head

# If stuck, check migration history
alembic history
```

---

## Best Practices

### 1. Keep Feature Branches Small

✅ **Good:** Add one segment type per PR
❌ **Bad:** Add 5 segment types + refactor + fix bugs in one PR

### 2. Write Good Commit Messages

✅ **Good:** `feat(etl): add Education Level segment with 5 categories`
❌ **Bad:** `update stuff`

### 3. Test Before Pushing

✅ **Good:** Run `pytest` and `npm test` locally
❌ **Bad:** Push and hope CI catches errors

### 4. Review Your Own PRs

✅ **Good:** Read the diff on GitHub before merging
❌ **Bad:** Merge immediately without review

### 5. Deploy During Low Traffic

✅ **Good:** Deploy during afternoon (if users are mostly in Israel)
❌ **Bad:** Deploy during peak hours (risky)

---

## Summary: The Daily Loop

```
1. git checkout main && git pull
2. git checkout -b feat/new-feature
3. Make changes
4. docker-compose up (test locally)
5. pytest tests/ (run tests)
6. git commit -m "feat: description"
7. git push origin feat/new-feature
8. Create PR on GitHub
9. Merge to main (squash and merge)
10. Automatic deployment to production ✅
```

**Time per feature:** 1-3 days max
**Deployment frequency:** Multiple times per week
**Risk:** Low (main is always stable)

---

**Last Updated:** November 2025
**Version:** V10 Normalized Star Schema
**Status:** Production-Ready ✅
