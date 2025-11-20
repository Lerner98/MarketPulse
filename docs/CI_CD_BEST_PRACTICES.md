# CI/CD Best Practices - Industry Standards

**Author**: MarketPulse Development Team
**Date**: November 2025
**Purpose**: Document industry-standard CI/CD practices for catching issues early and maintaining code quality

---

## 📋 Table of Contents

1. [Philosophy: Shift-Left Testing](#philosophy-shift-left-testing)
2. [The Four Layers of Quality Assurance](#the-four-layers-of-quality-assurance)
3. [Layer 1: Local Testing](#layer-1-local-testing-before-commit-)
4. [Layer 2: Pre-Commit Hooks](#layer-2-pre-commit-hooks-automatic-guards-)
5. [Layer 3: Local CI Simulation](#layer-3-local-ci-simulation-optional-but-pro-)
6. [Layer 4: GitHub Actions](#layer-4-github-actions-safety-net-)
7. [Real-World Workflow](#real-world-workflow-example)
8. [What Professional Teams Do](#what-professional-teams-do)
9. [Common Mistakes to Avoid](#common-mistakes-developers-make)
10. [MarketPulse Implementation](#marketpulse-implementation)

---

## Philosophy: Shift-Left Testing

**The Pipeline:**
```
Local Machine → Pre-commit Hooks → CI/CD → Deployment
     ↑              ↑                 ↑          ↑
   Fast          Faster            Slower    Slowest
   Cheap         Cheap            Expensive  Most Expensive
```

**Core Principle**: Catch issues as early (left) as possible in the development pipeline.

**Why?**
- Faster feedback (seconds vs minutes)
- Lower cost (no CI minutes consumed)
- Better developer experience
- Prevents blocking teammates
- Reduces context switching

---

## The Four Layers of Quality Assurance

### Layer Breakdown

| Layer | Purpose | Speed | When to Use | Catches |
|-------|---------|-------|-------------|---------|
| **Local Testing** | Fast feedback | 10s-2min | Every change | 80-90% of issues |
| **Pre-commit Hooks** | Automatic enforcement | 5-30s | Every commit | Format, secrets, fast tests |
| **Local CI Simulation** | Environment validation | 2-10min | Risky changes, CI debugging | Environment mismatches |
| **GitHub Actions** | Safety net | 3-15min | Every push | Cross-platform, clean env, integration |

---

## Layer 1: Local Testing (Before Commit) ✅

### What Developers Run Locally

```bash
# Backend Testing
cd backend
pytest tests/ -v --cov=api --cov=models --cov-report=term

# Frontend Testing
cd frontend
npm test -- --run
npm run build  # Verify build works

# Code Quality
black backend/ --check
flake8 backend/
eslint frontend/src/

# Type Checking
mypy backend/
tsc --noEmit  # TypeScript check without building

# Docker Validation
docker-compose build
docker-compose up -d
# Run integration tests
docker-compose down
```

### MarketPulse Local Test Commands

```bash
# Quick check (before commit)
pytest backend/tests/unit -v  # Fast unit tests only

# Full check (before push)
pytest backend/tests/ -v --cov=api --cov=models
cd frontend && npm test -- --run && npm run build

# Integration check (weekly or before release)
docker-compose up -d postgres redis
pytest backend/tests/integration/
docker-compose down
```

### Why Local Testing Works

✅ **Catches 80-90% of issues before commit**
✅ **Fast feedback (seconds to minutes)**
✅ **No waiting for CI queue**
✅ **Free (no CI minutes consumed)**
✅ **Enables rapid iteration**

---

## Layer 2: Pre-Commit Hooks (Automatic Guards) 🛡️

### The Problem Pre-Commit Solves

**Without Pre-Commit:**
```
Developer → Commits broken code → Pushes → CI fails → 5 min wasted → Fix → Repeat
```

**With Pre-Commit:**
```
Developer → Attempts commit → Hook runs → Fails BEFORE commit → Fix immediately → 30s total
```

### Setup (One-Time)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks into .git/hooks/
pre-commit install
```

### Configuration File: `.pre-commit-config.yaml`

```yaml
repos:
  # Standard hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key

  # Python formatting
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  # Python linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203,W503']

  # Secret scanning
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.1
    hooks:
      - id: gitleaks

  # TypeScript/JavaScript formatting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: \.(ts|tsx|js|jsx|json|css|md)$

  # Local hooks (project-specific)
  - repo: local
    hooks:
      # Backend fast tests
      - id: pytest-fast
        name: Fast backend unit tests
        entry: bash -c 'cd backend && pytest tests/unit -x --tb=short'
        language: system
        pass_filenames: false
        stages: [commit]
        files: ^backend/

      # Frontend fast tests
      - id: vitest-fast
        name: Fast frontend unit tests
        entry: bash -c 'cd frontend && npm test -- --run --reporter=verbose'
        language: system
        pass_filenames: false
        stages: [commit]
        files: ^frontend/

      # Check for debug statements
      - id: no-debug-statements
        name: Check for debug statements
        entry: bash -c 'if git diff --cached | grep -E "console\\.log|debugger|pdb\\.set_trace|breakpoint\\(\\)"; then echo "Debug statements found!"; exit 1; fi'
        language: system
        pass_filenames: false
        stages: [commit]
```

### What Happens on Every Commit

```bash
git add .
git commit -m "feat: add new endpoint"

# Automatically runs:
# ✓ Trailing whitespace removed
# ✓ Black formatting applied
# ✓ Flake8 linting passed
# ✓ No secrets detected (gitleaks)
# ✓ Fast tests passed (< 10 seconds)
# ✓ TypeScript/JavaScript formatted
# ✓ No debug statements
# → Commit succeeds

# Or if issues found:
# ✗ Tests failed
# ✗ Secrets detected
# ✗ Linting errors
# → Commit BLOCKED (must fix first)
```

### Benefits

✅ **Physically prevents committing broken code**
✅ **Consistent code style enforced automatically**
✅ **Secrets caught before reaching git history**
✅ **Zero mental overhead (runs automatically)**
✅ **Fast feedback (< 30 seconds)**

### Bypassing Hooks (Emergency Only)

```bash
# Skip hooks (USE SPARINGLY - only for emergencies)
git commit --no-verify -m "hotfix: critical production issue"

# Better approach: Fix the issue that's blocking the hook
```

---

## Layer 3: Local CI Simulation (Optional but Pro) 🐳

### Tool: `act` - Run GitHub Actions Locally

**What It Does**: Runs your EXACT GitHub Actions workflow on your local machine using Docker.

### Installation

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows
choco install act-cli
```

### Usage

```bash
# Run specific job
act -j backend-tests

# Run entire workflow
act push

# Run with secrets
act -j backend-tests --secret-file .secrets

# Dry run (see what would happen)
act -n
```

### Example Output

```bash
$ act -j backend-tests

[MarketPulse CI/CD/backend-tests] 🚀  Start image=catthehacker/ubuntu:act-latest
[MarketPulse CI/CD/backend-tests]   🐳  docker pull image=catthehacker/ubuntu:act-latest
[MarketPulse CI/CD/backend-tests]   ✅  Success - Main Set up Python
[MarketPulse CI/CD/backend-tests]   ✅  Success - Main Install dependencies
[MarketPulse CI/CD/backend-tests]   ✅  Success - Main Run backend tests
[MarketPulse CI/CD/backend-tests]   ✅  Success - Post Set up Python
```

### When to Use `act`

✅ **After major CI/CD workflow changes**
✅ **When debugging CI-specific failures**
✅ **Before pushing risky changes (e.g., dependency updates)**
✅ **Weekly sanity check**
✅ **When onboarding new developers (validate setup)**

### Why Not Always?

❌ **Slower than local pytest** (spins up Docker containers)
❌ **Still catches most issues with local + pre-commit**
❌ **Requires Docker (resource intensive)**

### What CI Catches That Local Can't

1. **Cross-Platform Issues**
   - Developer on Mac, CI on Linux
   - Different file system case sensitivity
   - Different shell behaviors (`bash` vs `zsh`)

2. **Clean Environment Issues**
   - Local: "Works on my machine" (cached dependencies)
   - CI: Fresh environment every time

3. **Integration Issues**
   - Multiple branches being merged simultaneously
   - Dependency conflicts
   - Race conditions

4. **Security Scanning**
   - Trivy vulnerability scanning
   - Dependency auditing
   - License compliance

---

## Layer 4: GitHub Actions (Safety Net) 🕸️

### Branch Protection Rules

**GitHub Settings → Branches → Branch protection rules**

```yaml
Branch: main

✓ Require a pull request before merging
  ✓ Require approvals: 1
  ✓ Dismiss stale pull request approvals when new commits are pushed

✓ Require status checks to pass before merging
  ✓ Require branches to be up to date before merging
  ✓ Status checks that are required:
    - backend-tests
    - frontend-tests
    - docker-build
    - security-scan

✓ Require conversation resolution before merging

✓ Include administrators (no one bypasses, even you)

✓ Do not allow bypassing the above settings
```

**Result**: **IMPOSSIBLE** to merge broken code to `main`, even if you try.

### Our CI/CD Workflow Breakdown

```yaml
# .github/workflows/ci.yml

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:  # Test database
      redis:     # Test cache
    steps:
      - Checkout code
      - Set up Python 3.11
      - Cache dependencies (pip)
      - Install dependencies
      - Run pytest with coverage
      - Upload coverage report

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Set up Node.js 18
      - Cache dependencies (npm)
      - Install dependencies
      - Run unit tests (Vitest)
      - Build frontend (verify build)
      - Install Playwright
      - Run E2E tests

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Set up Docker Buildx
      - Build backend image
      - Build frontend image
      - Test images start correctly

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Run Trivy scanner
      - Upload SARIF results
```

### CI/CD Performance Optimization

```yaml
# Cache dependencies (saves 30-60 seconds per run)
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}

# Cache npm dependencies (saves 60-90 seconds per run)
- name: Cache npm dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('frontend/package-lock.json') }}

# Run jobs in parallel (not sequential)
jobs:
  backend-tests:   # Runs in parallel
  frontend-tests:  # Runs in parallel
  docker-build:    # Runs in parallel
  security-scan:   # Runs in parallel
```

---

## Real-World Workflow Example

### Scenario: Adding New API Endpoint

```bash
# 1. LOCAL: Write code + tests
vim backend/api/main.py
vim backend/tests/test_new_endpoint.py

# 2. LOCAL: Run tests (Layer 1)
pytest backend/tests/test_new_endpoint.py -v
# ✓ test_new_endpoint_success PASSED (0.3s)
# ✓ test_new_endpoint_validation PASSED (0.2s)
# ✓ test_new_endpoint_error_handling PASSED (0.4s)

# 3. LOCAL: Run full test suite
pytest backend/tests/ -v
# ✓ 68 passed in 8.5 seconds

# 4. LOCAL: Check code quality
black backend/
flake8 backend/

# 5. COMMIT: Triggers pre-commit hooks (Layer 2)
git add .
git commit -m "feat(api): add customer search endpoint"

# → Pre-commit runs (automatic):
#    ✓ Formatting (black)
#    ✓ Linting (flake8)
#    ✓ Fast tests (pytest unit tests)
#    ✓ Secret scanning (gitleaks)
#    ✓ YAML validation
# → Commit succeeds in 8 seconds

# 6. PUSH: Triggers CI/CD (Layer 4)
git push origin feature/customer-search

# → GitHub Actions runs (takes 2-3 minutes):
#    ✓ backend-tests (full suite + coverage)
#    ✓ frontend-tests (no changes, but runs anyway)
#    ✓ docker-build (validates Docker images)
#    ✓ security-scan (Trivy)
# → All green ✅

# 7. CREATE PR
gh pr create --title "Add customer search endpoint" --body "..."

# → Branch protection enforces:
#    ✓ All CI checks must pass
#    ✓ At least 1 approval required
#    ✓ Branch must be up to date
# → Ready to merge

# 8. MERGE
gh pr merge --squash
# → Merged to main
# → Production deployment triggered (if configured)
```

### Timeline Comparison

**Without Best Practices:**
```
Write code → Commit → Push → Wait 5 min → CI fails → Fix → Repeat
Total time: 15-30 minutes (3-5 iterations)
```

**With Best Practices:**
```
Write code → Test locally (30s) → Pre-commit (10s) → Push → CI passes (3 min)
Total time: 5-7 minutes (1 iteration)
```

**Time Saved**: 10-25 minutes per feature × 10 features/week = **2-4 hours saved per week**

---

## What Professional Teams Do

### Tier 1: Startups / Small Teams (5-20 people)

```
✓ Local testing (manual, but encouraged)
✓ Pre-commit hooks (basic formatting + secrets)
✓ CI/CD on push (GitHub Actions)
✓ Branch protection on main
✓ 1 required reviewer

Tools:
- pytest / Vitest
- black / prettier
- GitHub Actions
- Branch protection
```

### Tier 2: Mid-Size Companies (50-200 people)

```
✓ Local testing (mandatory, enforced by team culture)
✓ Pre-commit hooks (comprehensive: format, lint, test, secrets)
✓ CI/CD with parallelization
✓ Branch protection + 2 required reviewers
✓ Staging environment testing
✓ Automated deployment to staging
✓ Manual approval for production

Tools:
- All of Tier 1, PLUS:
- Docker Compose for local development
- Staging environment (AWS/GCP)
- Code coverage requirements (70%+)
- Performance testing (Lighthouse, k6)
```

### Tier 3: Large Tech (Google, Meta, Netflix, etc.)

```
✓ All of Tier 2, PLUS:
✓ Pre-submit testing (runs CI BEFORE allowing push)
✓ Hermetic builds (fully reproducible, no external dependencies)
✓ Continuous deployment (hundreds of deploys/day)
✓ Canary deployments (gradual rollout to 1% → 10% → 100%)
✓ Automated rollbacks (if metrics degrade)
✓ Chaos engineering (intentionally break things to test resilience)
✓ Shadow testing (run new code alongside old, compare results)

Tools:
- All of Tier 2, PLUS:
- Bazel (hermetic builds)
- Custom internal CI/CD (not GitHub Actions)
- Feature flags (LaunchDarkly, etc.)
- Observability (DataDog, New Relic)
- Chaos engineering (Chaos Monkey)
```

---

## Common Mistakes Developers Make

### ❌ Mistake 1: "CI Will Catch It"

**Bad Approach:**
```bash
# Developer skips local tests
git add .
git commit -m "feat: new endpoint"
git push
# → Waits 5 minutes for CI
# → CI fails: "TypeError: expected str, got int"
# → Fix locally
# → Push again
# → Wait 5 more minutes
# → Repeat 2-3 times
# Total time wasted: 15-20 minutes
```

**Better Approach:**
```bash
# Run tests locally (30 seconds)
pytest backend/tests/ -v
# → Catch error immediately
# → Fix
# → Run tests again (30 seconds)
# → Pass
# → Push
# → CI passes first time (3 minutes)
# Total time: 5 minutes
```

### ❌ Mistake 2: "Works on My Machine"

**Problem:**
```
Developer (Mac):  pytest passes ✓
CI (Linux):       pytest fails ✗

Why?
- Mac has case-insensitive filesystem
- Linux has case-sensitive filesystem
- Code imports: from api.Models import User  (capital M)
- File path: api/models.py  (lowercase m)
- Works on Mac, fails on Linux
```

**Solution:**
```bash
# Use Docker locally to match CI environment
docker-compose up -d postgres redis
pytest backend/tests/
docker-compose down

# Or use act to run GitHub Actions locally
act -j backend-tests
```

### ❌ Mistake 3: "I'll Fix It Later"

**Bad Approach:**
```bash
git commit -m "WIP: broken tests, will fix later"
git push
# → Breaks main branch
# → Blocks 5 teammates
# → Wastes 30 minutes of team time
```

**Better Approach:**
```bash
# Pre-commit hook prevents this
git commit -m "WIP: broken tests"
# → Pre-commit runs
# → Tests fail
# → Commit BLOCKED
# → Must fix before committing
```

### ❌ Mistake 4: "Don't Need CI for Small Projects"

**Why This is Wrong:**
- Solo projects NEED CI even MORE than team projects
- No teammate to catch your mistakes
- Easy to forget what broke 6 months ago
- CI is free for public repos (GitHub Actions)
- CI is documentation (shows how to run tests)

**Better Approach:**
```
Even for personal projects:
✓ Set up basic CI/CD (takes 10 minutes)
✓ Use pre-commit hooks
✓ Future you will thank present you
```

### ❌ Mistake 5: "Skip Tests to Move Faster"

**Reality:**
```
Short term: 5 minutes saved
Long term: 2 hours debugging mysterious bug

Tests are NOT overhead. Tests are SPEED.
```

---

## MarketPulse Implementation

### Current Setup (Phase 4 Complete)

#### ✅ Layer 1: Local Testing

**Backend:**
```bash
# Unit tests (fast)
pytest backend/tests/unit -v

# Full test suite
pytest backend/tests/ -v --cov=api --cov=models --cov-report=term

# With coverage report
pytest backend/tests/ --cov=api --cov=models --cov-report=html
open htmlcov/index.html
```

**Frontend:**
```bash
# Unit tests
cd frontend
npm test -- --run

# With UI
npm run test:ui

# E2E tests (requires backend running)
npm run test:e2e

# Build validation
npm run build
```

#### ⏳ Layer 2: Pre-Commit Hooks (TO BE IMPLEMENTED)

**Action Item**: Set up `.pre-commit-config.yaml` with:
- Black formatting
- Flake8 linting
- Prettier (frontend)
- Secret scanning (gitleaks)
- Fast unit tests

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

#### ⏳ Layer 3: Local CI Simulation (OPTIONAL)

**Action Item**: Document `act` usage for team
```bash
brew install act
act -j backend-tests
act -j frontend-tests
```

#### ✅ Layer 4: GitHub Actions

**Current Status:**
- ✅ Backend tests (pytest + coverage)
- ✅ Frontend tests (Vitest + build validation)
- ✅ E2E tests (Playwright)
- ✅ Docker build validation
- ✅ Security scanning (Trivy)
- ✅ Dependency caching (pip + npm)

**To Be Improved:**
- ⏳ Branch protection rules (requires admin access)
- ⏳ Required reviewers
- ⏳ Code coverage requirements in CI

---

## Quick Reference Commands

### Daily Development

```bash
# Before starting work
git pull origin main
docker-compose up -d postgres redis

# During development
pytest backend/tests/unit -v  # Fast feedback
npm test -- --run             # Frontend tests

# Before committing
pytest backend/tests/ -v      # Full backend suite
cd frontend && npm run build  # Verify build

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: description"

# Before pushing (optional, for risky changes)
act -j backend-tests
act -j frontend-tests

# Push
git push origin feature-branch
```

### Weekly Maintenance

```bash
# Update dependencies
pip install --upgrade -r backend/requirements.txt
cd frontend && npm update

# Run full test suite
pytest backend/tests/ -v --cov=api --cov=models
cd frontend && npm test -- --run && npm run test:e2e

# Check for security vulnerabilities
pip-audit
npm audit

# Verify Docker builds
docker-compose build
docker-compose up -d
docker-compose down
```

---

## Success Metrics

### How to Measure CI/CD Effectiveness

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Local test coverage** | 70%+ | 74% (backend) | ✅ |
| **CI/CD pass rate** | >95% | TBD | ⏳ |
| **Average CI duration** | <5 min | 3-4 min | ✅ |
| **Pre-commit hook usage** | 100% | 0% (not set up) | ⏳ |
| **Time to detect issues** | <5 min | <3 min (with local tests) | ✅ |
| **Main branch stability** | 100% passing | 100% | ✅ |

---

## Next Steps for MarketPulse

### Immediate (This Week)

1. **Set up pre-commit hooks**
   - Create `.pre-commit-config.yaml`
   - Install hooks: `pre-commit install`
   - Test with team

2. **Document local testing workflow**
   - Add to README.md
   - Create CONTRIBUTING.md with workflow

3. **Enable branch protection**
   - Require CI checks to pass
   - Require 1 reviewer

### Short Term (This Month)

4. **Introduce `act` for CI simulation**
   - Install on team machines
   - Document usage
   - Use for debugging CI issues

5. **Add coverage requirements to CI**
   - Fail CI if coverage drops below 70%
   - Add coverage badge to README

6. **Set up staging environment**
   - Deploy on PR merge to main
   - Automated smoke tests

### Long Term (Next Quarter)

7. **Implement automated deployment**
   - CD pipeline to production
   - Manual approval gate

8. **Add performance testing**
   - Lighthouse CI for frontend
   - API load testing (k6)

9. **Chaos engineering experiments**
   - Test database failover
   - Test Redis outage handling

---

## Resources

### Tools

- **Pre-commit**: https://pre-commit.com/
- **act**: https://github.com/nektos/act
- **GitHub Actions**: https://docs.github.com/en/actions
- **Trivy**: https://github.com/aquasecurity/trivy

### Reading

- [Continuous Delivery (Humble & Farley)](https://continuousdelivery.com/)
- [Accelerate (Forsgren, Humble, Kim)](https://itrevolution.com/accelerate-book/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

### MarketPulse Docs

- [CI/CD Setup](./CI_CD_SETUP.md)
- [Phase 4 Frontend](./PHASE4_FRONTEND.md)
- [Quick Reference](./QUICK_REFERENCE.md)

---

## Conclusion

**The Golden Rule**:

> "If CI catches a bug, that's a failure. The bug should have been caught locally."

**CI/CD is not a replacement for local testing.**
**CI/CD is a safety net for what local testing misses.**

By following these best practices, MarketPulse will:
- ✅ Catch issues 10-20 minutes earlier
- ✅ Reduce CI failures by 70-80%
- ✅ Improve developer productivity
- ✅ Maintain high code quality
- ✅ Ship features faster with confidence

---

**Last Updated**: November 2025
**Next Review**: December 2025
