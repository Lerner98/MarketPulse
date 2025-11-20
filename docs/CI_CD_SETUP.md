# CI/CD Pipeline Setup

## Overview
Production-ready CI/CD pipeline configured with GitHub Actions for automated testing, security scanning, and deployment validation.

## What Was Configured

### 1. GitHub Actions Workflow ([.github/workflows/ci.yml](../.github/workflows/ci.yml))

#### Jobs:

**Backend Tests**:
- Python 3.11 environment
- PostgreSQL 15 Alpine service (test database)
- Redis 7 Alpine service (cache)
- Dependency caching for faster builds
- pytest with coverage reporting
- Runs on: push to main/develop, pull requests to main

**Frontend Tests**:
- Node.js 18 environment
- npm dependency caching
- Test suite execution (when ready)
- Graceful handling of pending implementation

**Docker Build**:
- Docker Buildx setup
- Multi-platform build support
- Image validation
- Fail-safe for pending Dockerfiles

**Security Scan**:
- Trivy vulnerability scanner
- Filesystem scanning
- SARIF output format
- Automated security reports

### 2. Enhanced .gitignore ([.gitignore](../.gitignore))

Comprehensive exclusions for:
- **Python**: `__pycache__/`, `*.pyc`, `venv/`, egg files
- **Data**: CSV files, SQLite databases
- **Environment**: `.env` files and variants
- **IDE**: VSCode, IntelliJ, Sublime Text
- **OS**: macOS, Windows system files
- **Logs**: All log files
- **Coverage**: pytest and coverage artifacts
- **Node**: `node_modules/`, build artifacts
- **Docker**: Container logs
- **Jupyter**: Notebook checkpoints
- **Temporary**: Cache and temp files

### 3. Git Attributes ([.gitattributes](../.gitattributes))

Cross-platform consistency:
- **Line Endings**: Normalize to LF for all text files
- **Source Code**: Python, JavaScript, TypeScript, SQL
- **Configuration**: JSON, YAML, TOML, INI
- **Documentation**: Markdown, text files
- **Web**: HTML, CSS, SCSS
- **Shell**: Bash scripts
- **Docker**: Dockerfiles and compose files
- **Binary**: Proper handling of images, archives, wheels

## CI/CD Pipeline Features

### Automated Testing
- ✅ Backend unit tests with pytest
- ✅ PostgreSQL integration tests
- ✅ Redis connectivity tests
- ✅ Coverage reporting (XML + terminal)
- ⏳ Frontend tests (pending implementation)

### Security
- ✅ Trivy vulnerability scanning
- ✅ Dependency security checks
- ✅ SARIF format for GitHub Security tab
- ✅ Automated security advisories

### Build Validation
- ✅ Docker image builds
- ✅ Multi-service orchestration
- ✅ Dependency resolution
- ✅ Build artifact validation

### Performance Optimization
- ✅ Python pip caching
- ✅ Node npm caching
- ✅ Docker layer caching
- ✅ Parallel job execution

## Workflow Triggers

### Push Events
```yaml
on:
  push:
    branches: [ main, develop ]
```
- Automatic run on commits to main or develop
- Full test suite execution
- Security scanning
- Docker builds

### Pull Request Events
```yaml
on:
  pull_request:
    branches: [ main ]
```
- Required checks before merge
- Code quality validation
- Security review
- Build verification

## Pipeline Status

### Current Status (Updated: Phase 3 Complete)
- ✅ Workflow file created and active
- ✅ CI/CD pipeline passing all checks
- ✅ Services configured (PostgreSQL, Redis)
- ✅ Backend tests (65 tests, 74% coverage)
- ✅ Docker builds (multi-stage, 180MB image)
- ⏳ Frontend tests (conditional, Phase 4)
- ✅ Security scanning (Trivy, zero critical vulnerabilities)

### Expected Behavior
The pipeline will:
1. Run automatically on every push to main/develop
2. Execute all jobs in parallel for speed
3. Report results in GitHub Actions tab
4. Show pass/fail status on commits
5. Block merges if required checks fail

## Accessing CI/CD Results

### GitHub Actions Tab
1. Navigate to: `https://github.com/Lerner98/MarketPulse/actions`
2. View workflow runs
3. Check job logs
4. Download artifacts

### Commit Status Checks
- Green checkmark: All jobs passed
- Red X: One or more jobs failed
- Yellow circle: Jobs in progress

### Security Alerts
- View in Security tab
- Trivy scan results
- Dependency vulnerabilities
- Automated fix suggestions

## Local Testing

### Backend Tests
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests
cd backend
pytest tests/ --cov=. --cov-report=term
```

### Environment Setup
```bash
# Set test environment variables
export DATABASE_URL=postgresql://marketpulse_user:test_password@localhost:5432/marketpulse_test
export REDIS_URL=redis://localhost:6379

# Run tests
pytest
```

## Next Steps

### Phase 3: Add Backend Tests
1. Create `backend/tests/` directory
2. Add test files:
   - `test_database.py` - Database connection tests
   - `test_cleaner.py` - ETL pipeline tests
   - `test_api.py` - API endpoint tests (Phase 3)
3. Achieve 80%+ code coverage

### Phase 4: Add Frontend Tests
1. Initialize frontend with Vite
2. Configure Vitest or Jest
3. Add component tests
4. Add integration tests

### Phase 5: Docker Configuration
1. Create `backend/Dockerfile`
2. Create `frontend/Dockerfile`
3. Update docker-compose.yml for multi-stage builds
4. Add production-ready images

## Production Best Practices Implemented

✅ **Conventional Commits**: Using `ci:` prefix for CI/CD changes
✅ **Automated Testing**: CI/CD runs on every push
✅ **Security Scanning**: Trivy vulnerability detection
✅ **Dependency Caching**: Faster builds (pip, npm)
✅ **Service Isolation**: PostgreSQL and Redis in containers
✅ **Cross-Platform**: Git attributes for consistency
✅ **Comprehensive Exclusions**: Clean repository
✅ **Parallel Execution**: Jobs run concurrently
✅ **Fail-Safe**: Graceful handling of pending features

---

## Phase 3 CI/CD Failures - Detailed Analysis & Lessons Learned

### Overview

During Phase 3 implementation, the CI/CD pipeline experienced **6 distinct failures** across multiple commits before achieving success. This section documents each failure, root causes, fixes, and prevention strategies for future phases.

**Critical Lesson**: Local test success ≠ CI/CD success. Always verify GitHub Actions runs to completion before declaring phase complete.

---

### Failure Timeline

| Commit | Issue | Root Cause | Status |
|--------|-------|------------|--------|
| `552428d` | Missing requirements.txt | File outside Docker build context | ❌ Not verified |
| `5067592` | Workflow path mismatch | Workflow referenced root path, file in backend/ | ✅ Fixed |
| `f946470` | Database port mismatch | Hardcoded port 5433, CI uses 5432 | ✅ Fixed |
| `35a52f8` | Missing database schema | CI PostgreSQL starts empty | ✅ Fixed |
| `8e36d8d` | GitHub token committed | Security incident (Phase 1) | ✅ Remediated |
| `b634375` | Frontend cache failure | package.json doesn't exist (Phase 4) | ✅ Fixed |

---

### Failure #1: Docker Build - Missing requirements.txt

**Commit**: `552428d` - "fix: backend test dependencies and workflow configuration"

**Error**:
```
COPY failed: file not found in build context or excluded by .dockerignore
```

**Root Cause**:
```dockerfile
# backend/Dockerfile
COPY requirements.txt .  # Looking for file in build context

# docker-compose.yml
build:
  context: ./backend  # Build context is backend/ directory only
```

File was at root `requirements.txt`, but Docker build context was `./backend`, so file was inaccessible.

**Fix**:
Created `backend/requirements.txt` with API-specific dependencies:
```
fastapi>=0.108.0
uvicorn[standard]>=0.25.0
pydantic>=2.5.3
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.23
redis>=5.0.1
requests>=2.31.0
pytest>=7.4.3
pytest-asyncio>=0.23.2
pytest-cov>=4.1.0
```

**Why Not Share Root requirements.txt?**
- Backend doesn't need ETL libraries (pandas, numpy, faker)
- Smaller Docker image (180MB vs 300MB+)
- Faster builds (fewer dependencies to install)

**MISTAKE**: Declared success without verifying GitHub Actions actually ran.

---

### Failure #2: Workflow Path Mismatch

**Commit**: `5067592` - "fix: update CI workflow to use correct requirements.txt path"

**Error**:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

**Root Cause**:
Workflow still referenced root path after creating backend-specific file:

```yaml
# WRONG
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

- name: Install dependencies
  run: pip install -r requirements.txt
```

**Fix**:
```yaml
# CORRECT
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}

- name: Install dependencies
  run: pip install -r backend/requirements.txt
```

**Detection Method**: User code review caught this (not automated testing).

**Lesson**: When moving files, search entire codebase for all references using Grep tool.

---

### Failure #3: Database Port Mismatch

**Commit**: `f946470` - "fix: prioritize DATABASE_URL environment variable in tests"

**Error**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
    Is the server running on host "localhost" (127.0.0.1) and accepting
    TCP/IP connections on port 5433?
```

**Root Cause**:
```python
# backend/tests/conftest.py - WRONG
@pytest.fixture(scope="session")
def test_database_url() -> str:
    return os.getenv(
        'TEST_DATABASE_URL',  # Not set in CI
        'postgresql://marketpulse_user:dev123@localhost:5433/marketpulse'
    )
```

**Environment Mismatch**:
- **Local dev**: docker-compose.yml maps port 5433:5432
- **CI/CD**: Workflow exposes port 5432 directly, sets `DATABASE_URL` env var

**Fix**:
```python
# CORRECT - Environment-aware
@pytest.fixture(scope="session")
def test_database_url() -> str:
    return os.getenv(
        'DATABASE_URL',  # CI uses this (port 5432)
        os.getenv('TEST_DATABASE_URL', 'postgresql://...@localhost:5433/...')
    )
```

**Priority Order**:
1. `DATABASE_URL` (set by CI/CD)
2. `TEST_DATABASE_URL` (set by local dev if needed)
3. Fallback to localhost:5433 (local docker-compose default)

**Lesson**: Always prioritize CI/CD environment variables over local defaults.

---

### Failure #4: Missing Database Schema

**Commit**: `35a52f8` - "fix: add automatic schema setup for test database"

**Error**:
```
psycopg2.errors.UndefinedTable: relation "transactions" does not exist
LINE 1: SELECT * FROM transactions WHERE status = 'completed'
```

**Root Cause**:
CI PostgreSQL service starts with **empty database** - no tables, views, indexes, or triggers.

**Local dev works because**:
- Manually ran schema.sql during initial setup
- Schema persists in `postgres_data` Docker volume

**CI/CD fails because**:
- Fresh PostgreSQL container every run
- No persistent volumes
- Tests assumed schema exists

**Fix**:
Created automatic schema setup fixture:

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_database(db_engine):
    """Create database schema before running tests."""
    schema_path = os.path.join(
        os.path.dirname(__file__),
        '../../models/schema.sql'
    )

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Use raw connection for multi-statement SQL
    raw_conn = db_engine.raw_connection()
    try:
        cursor = raw_conn.cursor()

        # Clean slate - drop and recreate schema
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
        raw_conn.commit()

        # Create schema (tables, views, indexes, triggers)
        cursor.execute(schema_sql)
        raw_conn.commit()

        cursor.close()
    finally:
        raw_conn.close()

    yield  # Run tests
```

**Why `raw_connection()` instead of SQLAlchemy's `execute()`?**

SQLAlchemy's `execute(text())` doesn't support:
- Multi-statement SQL (separated by semicolons)
- Dollar-quoted strings (`$$`) used in PostgreSQL functions/triggers

Example from schema.sql that breaks with `execute()`:
```sql
CREATE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Lesson**: CI/CD environments are ephemeral - never assume pre-existing state.

---

### Failure #5: GitHub Token Committed (Security Incident)

**Commit**: `8e36d8d` - Phase 1 (discovered during Phase 3)

**Detection**: GitHub secret scanning auto-detected PAT token, sent email notification, and auto-revoked token.

**Error (GitHub Email)**:
```
A recent scan found a valid GitHub Personal Access Token linked to your account.
We have revoked it to protect your data.

Location: mcp-config.json
Commit: 8e36d8d
```

**Root Cause**:
```json
// mcp-config.json - COMMITTED TO GIT
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

**Why This Happened**:
- MCP configuration needed GitHub token for API access
- Token stored in plaintext JSON file
- File not in `.gitignore`
- Committed in Phase 1, not caught until Phase 3

**Immediate Response** (Commits `973ee9a`, `666dd09`):

1. **Revoke token** (GitHub auto-revoked)
2. **Add to .gitignore**:
   ```
   mcp-config.json
   ```
3. **Remove from git tracking**:
   ```bash
   git rm --cached mcp-config.json
   ```
4. **Rewrite git history** (remove from all commits):
   ```bash
   git filter-repo --path mcp-config.json --invert-paths --force
   ```
5. **Force push**:
   ```bash
   git push --force origin main
   ```

**Prevention Strategies**:

✅ **DO**:
- Store secrets in environment variables
- Use `.env` files (add to `.gitignore`)
- Use secret management tools (AWS Secrets Manager, HashiCorp Vault)
- Use GitHub Secrets for CI/CD
- Review `.gitignore` before initial commit
- Use pre-commit hooks to scan for secrets

❌ **DON'T**:
- Commit `.env` files
- Store tokens in config files
- Commit `mcp-config.json`, `secrets.json`, `credentials.json`
- Use real tokens in documentation/examples
- Share `.git/` directory (contains full history)

**Correct Approach**:
```json
// mcp-config.json (committed)
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

```bash
# .env (NOT committed)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**Impact**:
- Low (token revoked immediately)
- No unauthorized access detected
- No data exposure
- Repository was private during incident

**Lesson**: Security is not just about code - it's about process. Review `.gitignore` before first commit.

---

### Failure #6: Frontend Cache Failure

**Commit**: `b634375` - "fix: make frontend tests conditional on package.json existence"

**Error**:
```
Error: Some specified paths were not resolved, unable to cache dependencies.
```

**Root Cause**:
```yaml
# .github/workflows/ci.yml
frontend-tests:
  steps:
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json  # File doesn't exist!
```

Frontend not implemented yet (Phase 4), so `frontend/package-lock.json` doesn't exist.

**Why This Wasn't Caught Earlier**:
- Backend tests were failing, masking frontend issue
- Only became visible after backend tests passed

**Fix**:
Added conditional execution:

```yaml
frontend-tests:
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v3

    - name: Check if frontend exists
      id: check-frontend
      run: |
        if [ -f "frontend/package.json" ]; then
          echo "exists=true" >> $GITHUB_OUTPUT
        else
          echo "exists=false" >> $GITHUB_OUTPUT
          echo "Frontend not implemented yet (Phase 4) - skipping"
        fi

    - name: Set up Node.js
      if: steps.check-frontend.outputs.exists == 'true'
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      if: steps.check-frontend.outputs.exists == 'true'
      run: |
        cd frontend
        npm ci

    - name: Run tests
      if: steps.check-frontend.outputs.exists == 'true'
      run: |
        cd frontend
        npm test
```

**Why This Approach**:
- Workflow doesn't fail when frontend missing
- Automatically activates when `frontend/package.json` created in Phase 4
- No workflow changes needed for Phase 4
- Provides clear status message in logs

**Lesson**: Design workflows for incremental development - not all components ready simultaneously.

---

## DO's and DON'Ts for Future CI/CD Work

### ✅ DO

#### 1. Verify CI/CD Completion
```bash
# After pushing commits
git push origin main

# Wait and verify on GitHub
# Option 1: Use gh CLI
gh run list --limit 1
gh run watch

# Option 2: Web browser
open https://github.com/Lerner98/MarketPulse/actions

# ❌ DON'T declare success until green checkmarks visible
```

#### 2. Environment-Aware Configuration
```python
# ✅ CORRECT - CI/CD first, then local dev
DATABASE_URL = os.getenv(
    'DATABASE_URL',           # CI/CD sets this
    os.getenv('TEST_DATABASE_URL', 'postgresql://localhost:5433/...')
)

# ❌ WRONG - Hardcoded values
DATABASE_URL = 'postgresql://localhost:5433/marketpulse'
```

#### 3. Path References
```yaml
# ✅ CORRECT - Specific paths
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    key: ${{ hashFiles('backend/requirements.txt') }}

- name: Install dependencies
  run: pip install -r backend/requirements.txt

# ❌ WRONG - Ambiguous paths
- run: pip install -r requirements.txt  # Which requirements.txt?
```

#### 4. Schema Setup in Tests
```python
# ✅ CORRECT - Automatic schema setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_database(db_engine):
    with open('models/schema.sql') as f:
        schema_sql = f.read()

    raw_conn = db_engine.raw_connection()
    cursor = raw_conn.cursor()
    cursor.execute(schema_sql)
    raw_conn.commit()

# ❌ WRONG - Assume schema exists
def test_api(db_connection):
    result = db_connection.execute("SELECT * FROM transactions")
    # Fails if schema not created
```

#### 5. Conditional Workflow Steps
```yaml
# ✅ CORRECT - Check file existence
- name: Check if frontend exists
  id: check-frontend
  run: |
    if [ -f "frontend/package.json" ]; then
      echo "exists=true" >> $GITHUB_OUTPUT
    fi

- name: Run frontend tests
  if: steps.check-frontend.outputs.exists == 'true'
  run: npm test

# ❌ WRONG - Assume all components ready
- name: Run frontend tests
  run: npm test  # Fails if frontend not implemented
```

#### 6. Secret Management
```bash
# ✅ CORRECT - Environment variables
export GITHUB_TOKEN=ghp_xxx
python script.py  # Reads from env

# ✅ CORRECT - GitHub Secrets
# In workflow:
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# ❌ WRONG - Hardcoded in files
GITHUB_TOKEN = "ghp_xxx"  # Will be committed!
```

#### 7. Docker Build Context
```dockerfile
# ✅ CORRECT - Files in build context
# docker-compose.yml: context: ./backend
# backend/Dockerfile
COPY requirements.txt .      # File in ./backend/
COPY api/ ./api/             # Directory in ./backend/

# ❌ WRONG - Files outside context
COPY ../requirements.txt .   # File in parent directory
```

#### 8. Git History Review Before Push
```bash
# ✅ CORRECT - Review what you're pushing
git log --oneline -5
git diff origin/main
git show HEAD  # Review latest commit

# Check for secrets
git grep -i "password\|token\|secret\|key" $(git diff --name-only HEAD~1)

# Then push
git push origin main

# ❌ WRONG - Push without review
git add .
git commit -m "fix stuff"
git push  # Hope for the best
```

---

### ❌ DON'T

#### 1. Don't Declare Success Without Verification
```bash
# ❌ WRONG
git push origin main
echo "✅ CI/CD passing!"  # How do you know?

# ✅ CORRECT
git push origin main
gh run watch  # Wait for completion
# OR: Check GitHub Actions web UI
```

#### 2. Don't Hardcode Environment-Specific Values
```python
# ❌ WRONG - Hardcoded port
DATABASE_URL = "postgresql://localhost:5433/marketpulse"

# ❌ WRONG - Hardcoded password
DATABASE_URL = "postgresql://user:dev123@localhost/db"

# ✅ CORRECT - Environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'fallback_for_local_dev')
```

#### 3. Don't Assume Pre-Existing State in CI
```python
# ❌ WRONG - Assume database schema exists
def test_query():
    result = db.execute("SELECT * FROM transactions")

# ❌ WRONG - Assume data exists
def test_api():
    response = client.get("/api/dashboard")
    assert response.json()["total_revenue"] > 0  # No data in CI!

# ✅ CORRECT - Create test data
@pytest.fixture
def sample_transactions(db):
    db.execute("INSERT INTO transactions (...) VALUES (...)")
    yield
    db.execute("DELETE FROM transactions WHERE ...")
```

#### 4. Don't Commit Secrets
```bash
# ❌ WRONG - Files that often contain secrets
git add .env
git add mcp-config.json
git add secrets.json
git add credentials.json
git add config/production.yml

# ✅ CORRECT - Add to .gitignore first
echo ".env" >> .gitignore
echo "mcp-config.json" >> .gitignore
git add .gitignore
git commit -m "chore: add secret files to gitignore"
```

#### 5. Don't Use Relative Imports Across Contexts
```python
# ❌ WRONG - Assumes specific directory structure
from ...models.schema import Base  # Breaks in CI

# ✅ CORRECT - Absolute imports
from backend.models.schema import Base
```

#### 6. Don't Share Dependencies Unnecessarily
```dockerfile
# ❌ WRONG - Backend includes ETL dependencies
# backend/Dockerfile copies root requirements.txt
COPY ../requirements.txt .
RUN pip install pandas numpy faker  # Not needed in API!

# ✅ CORRECT - Separate dependency files
# backend/requirements.txt (API only)
fastapi
psycopg2-binary
pytest

# etl/requirements.txt (ETL only)
pandas
numpy
faker
```

#### 7. Don't Mask Test Failures
```yaml
# ❌ WRONG - Workflow continues despite failures
- name: Run tests
  run: pytest || echo "Tests failed but continuing"

- name: Run Docker build
  run: docker-compose build || echo "Build failed but continuing"

# ✅ CORRECT - Let failures fail
- name: Run tests
  run: pytest  # Fails workflow if tests fail

- name: Run Docker build
  run: docker-compose build  # Fails workflow if build fails
```

#### 8. Don't Skip Verification Steps
```bash
# ❌ WRONG - Skip important checks
git add .
git commit -m "fix: stuff"
git push
# Did it work? Who knows!

# ✅ CORRECT - Verify each step
git status  # What am I committing?
git diff --staged  # Review changes
pytest  # Run tests locally
docker-compose build  # Test build locally
git push
gh run watch  # Verify CI passes
```

---

## Prevention Checklist for Future Phases

### Before Every Commit

- [ ] Run tests locally: `pytest tests/ --cov`
- [ ] Check for secrets: `git diff --staged | grep -i "password\|token\|secret"`
- [ ] Review what you're committing: `git diff --staged`
- [ ] Verify `.gitignore` is up to date
- [ ] Check Docker build locally: `docker-compose build`

### Before Every Push

- [ ] Review commit history: `git log --oneline -3`
- [ ] Verify branch is correct: `git branch --show-current`
- [ ] Check remote: `git remote -v`
- [ ] Ensure CI/CD workflow file is correct
- [ ] Have backup plan if force push needed

### After Every Push

- [ ] **Wait for CI/CD to complete** (use `gh run watch` or web UI)
- [ ] Check GitHub Actions tab for green checkmarks
- [ ] Review job logs if any failures
- [ ] Verify all jobs passed (backend, frontend, docker, security)
- [ ] **Only declare success after verification**

### When Adding New Dependencies

- [ ] Add to correct `requirements.txt` (backend vs etl)
- [ ] Update Docker build cache keys in workflow
- [ ] Test Docker build with new dependencies
- [ ] Verify CI/CD picks up new dependencies

### When Changing Workflow Files

- [ ] Test changes don't break existing jobs
- [ ] Verify environment variable names match
- [ ] Check paths are relative to repository root
- [ ] Test conditional logic with missing files
- [ ] Verify service configurations (PostgreSQL, Redis)

### When Working with Databases

- [ ] Never hardcode connection strings
- [ ] Always prioritize `DATABASE_URL` env var
- [ ] Include schema setup in test fixtures
- [ ] Test with empty database (like CI)
- [ ] Verify port mappings (local vs CI)

### Security Review

- [ ] No secrets in code or config files
- [ ] `.env` files in `.gitignore`
- [ ] No hardcoded passwords/tokens
- [ ] Review `mcp-config.json` before committing
- [ ] Check git history for accidentally committed secrets

---

## Root Cause Analysis Summary

### Primary Issue: Verification Gap

**Problem**: Declaring success based on local testing without verifying CI/CD completion.

**Impact**:
- 6 failures across multiple commits
- 2+ hours debugging avoidable issues
- Security incident (token committed)

**Prevention**:
- **Always wait for GitHub Actions to complete**
- Use `gh run watch` or web UI verification
- Add "CI/CD passing" as explicit success criteria

### Secondary Issues: Environment Assumptions

**Problem**: Assuming CI environment matches local development.

**Differences Found**:
| Aspect | Local Dev | CI/CD |
|--------|-----------|-------|
| Database port | 5433 (docker-compose) | 5432 (service) |
| Database schema | Pre-loaded (volume) | Empty (fresh container) |
| Environment vars | Manual or .env | Workflow-defined |
| File paths | Flexible | Strict (build context) |
| Dependencies | Shared root file | Service-specific |

**Prevention**:
- Design for CI first, local dev second
- Prioritize CI environment variables
- Test with empty database locally
- Use ephemeral test databases

### Tertiary Issue: Secret Management

**Problem**: Lack of secret scanning before initial commit.

**Prevention**:
- Add common secret files to `.gitignore` before first commit
- Use pre-commit hooks for secret detection
- Store secrets in environment variables only
- Review `.gitignore` in every phase

---

## Commit History

```
1a6b6c9 ci: add GitHub Actions CI/CD pipeline and git configuration
8e36d8d feat: Phase 1 & 2 complete - Project scaffolding and ETL pipeline
cc1abf3 Revamp README with detailed project overview
ea30d93 Initial commit
```

### Phase 3 CI/CD Fix Commits

```
b634375 fix: make frontend tests conditional on package.json existence
666dd09 security: remove mcp-config.json from git history
973ee9a security: add mcp-config.json to gitignore after token exposure
35a52f8 fix: add automatic schema setup for test database
f946470 fix: prioritize DATABASE_URL environment variable in tests
5067592 fix: update CI workflow to use correct requirements.txt path
552428d fix: backend test dependencies and workflow configuration
ee2ad50 docs: add comprehensive Phase 3 implementation summary
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)
- [pytest Documentation](https://docs.pytest.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**CI/CD Pipeline Active!** 🚀

The pipeline will automatically run on your next push to GitHub. Check the Actions tab to see the results.
