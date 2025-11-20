# Contributing to MarketPulse

Thank you for your interest in contributing to MarketPulse! This guide will help you get started with our development workflow.

## CI/CD Status

[![CI/CD](https://github.com/Lerner98/MarketPulse/workflows/MarketPulse%20CI%2FCD/badge.svg)](https://github.com/Lerner98/MarketPulse/actions)

**Current Build:** ![Build Status](https://github.com/Lerner98/MarketPulse/actions/workflows/ci.yml/badge.svg?branch=main)

---

## 📋 Table of Contents

1. [Development Philosophy](#development-philosophy)
2. [Getting Started](#getting-started)
3. [Local Development Workflow](#local-development-workflow)
4. [Testing Strategy](#testing-strategy)
5. [Code Quality Standards](#code-quality-standards)
6. [Commit Guidelines](#commit-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Troubleshooting](#troubleshooting)
9. [Common Mistakes](#-common-mistakes-learn-from-others)
10. [Quick Wins](#-quick-wins---do-these-first)

---

## Development Philosophy

**We follow the "Shift-Left" testing approach:**

```
Local Testing → Pre-commit Hooks → CI/CD → Deployment
    (Fast)          (Automatic)    (Safety Net)  (Confidence)
```

**Golden Rule**: If CI catches a bug, that's a failure. The bug should have been caught locally.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse

# 2. Set up pre-commit hooks (IMPORTANT!)
pip install pre-commit
pre-commit install

# 3. Start infrastructure
docker-compose up -d postgres redis

# 4. Set up backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# 5. Set up frontend
cd frontend
npm install
cd ..

# 6. Verify setup
pytest backend/tests/unit -v
cd frontend && npm test -- --run
```

---

## Local Development Workflow

### Daily Workflow

```bash
# 1. Start your day
git pull origin main
docker-compose up -d postgres redis

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Develop (write code + tests)
vim backend/api/main.py
vim backend/tests/test_your_feature.py

# 4. Test LOCALLY (before committing)
pytest backend/tests/test_your_feature.py -v

# 5. Run full test suite
pytest backend/tests/ -v

# 6. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add your feature"
# → Pre-commit hooks run (10-30 seconds)
# → If hooks fail, fix issues and retry

# 7. Push (triggers CI/CD)
git push origin feature/your-feature-name
# → CI runs (3-5 minutes)
# → Should pass on first try if you tested locally!

# 8. Create Pull Request
gh pr create --title "Add your feature" --body "Description..."
```

### Before Every Commit - Checklist

✅ **Run tests locally**
```bash
# Backend
pytest backend/tests/ -v

# Frontend
cd frontend && npm test -- --run
```

✅ **Check code formatting**
```bash
# Backend (automatic with pre-commit)
black backend/
flake8 backend/

# Frontend (automatic with pre-commit)
cd frontend && npx prettier --write src/
```

✅ **Verify build works**
```bash
# Frontend
cd frontend && npm run build
```

---

## Testing Strategy

### Testing Pyramid

```
    /\
   /E2E\      5-10%   (Critical user flows)
  /______\
 /Integr.\   20-30%  (API calls, component interactions)
/__________\
/   Unit    \ 60-70%  (Pure functions, hooks, utilities)
```

### Backend Testing

```bash
# Fast unit tests only (< 5 seconds)
pytest backend/tests/unit -v

# Full test suite (8-15 seconds)
pytest backend/tests/ -v

# With coverage report
pytest backend/tests/ --cov=api --cov=models --cov-report=html
open htmlcov/index.html

# Integration tests (requires Docker)
docker-compose up -d postgres redis
pytest backend/tests/integration/ -v
docker-compose down

# Specific test file
pytest backend/tests/test_specific.py -v

# Specific test function
pytest backend/tests/test_specific.py::test_function_name -v
```

### Frontend Testing

```bash
cd frontend

# Unit tests (fast)
npm test -- --run

# Watch mode (during development)
npm test

# With UI
npm run test:ui

# E2E tests (requires backend running)
npm run test:e2e

# Coverage report
npm run coverage
```

### Coverage Requirements

- **Backend**: 70% minimum (enforced by CI)
- **Frontend**: 70% minimum (enforced by CI)

**Check coverage locally:**
```bash
# Backend
pytest backend/tests/ --cov=api --cov=models --cov-fail-under=70

# Frontend
cd frontend && npm run coverage
```

---

## Code Quality Standards

### Python (Backend)

**Formatting**: Black (line length: 88)
```bash
# Check formatting
black --check backend/

# Auto-format
black backend/
```

**Linting**: Flake8
```bash
flake8 backend/ --max-line-length=88 --extend-ignore=E203,W503
```

**Type Checking**: MyPy (optional but recommended)
```bash
mypy backend/api/ backend/models/
```

### TypeScript/JavaScript (Frontend)

**Formatting**: Prettier
```bash
cd frontend
npx prettier --check src/
npx prettier --write src/
```

**Linting**: ESLint (if configured)
```bash
cd frontend
npm run lint
```

**Type Checking**: TypeScript
```bash
cd frontend
npx tsc --noEmit
```

### Code Review Checklist

Before submitting a PR, ensure:

- [ ] All tests pass locally
- [ ] Code is properly formatted (Black/Prettier)
- [ ] No linting errors (Flake8/ESLint)
- [ ] Coverage is maintained or improved
- [ ] No debug statements (`console.log`, `print`, `pdb.set_trace`)
- [ ] No secrets or API keys in code
- [ ] Meaningful commit messages
- [ ] Documentation updated if needed

---

## Commit Guidelines

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, tooling, dependencies

**Examples:**

```bash
# Good commits
git commit -m "feat(api): add customer search endpoint"
git commit -m "fix(dashboard): resolve chart rendering issue"
git commit -m "test(api): add integration tests for revenue endpoint"
git commit -m "docs: update API documentation with new endpoints"

# Bad commits (avoid)
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

### Pre-Commit Hooks

**What runs automatically on every commit:**

✅ Trailing whitespace removal
✅ End-of-file fixer
✅ YAML/JSON validation
✅ Secret scanning (Gitleaks)
✅ Black formatting (Python)
✅ Prettier formatting (TypeScript/JavaScript)
✅ Fast unit tests (if files changed)
✅ Debug statement check
✅ TypeScript type check

**If pre-commit hooks fail:**

```bash
# Hooks auto-fix some issues (formatting)
git add .
git commit -m "your message"
# → Hooks modify files
# → Commit fails
# → Files are now formatted

# Re-add and commit
git add .
git commit -m "your message"
# → Hooks pass
# → Commit succeeds
```

**Bypass hooks (EMERGENCY ONLY):**
```bash
git commit --no-verify -m "hotfix: critical production issue"
```

---

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/descriptive-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes + Test Locally

```bash
# Write code
vim backend/api/main.py

# Write tests
vim backend/tests/test_feature.py

# Test locally
pytest backend/tests/test_feature.py -v

# Run full suite
pytest backend/tests/ -v
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add feature description"
# → Pre-commit hooks run automatically
```

### 4. Push to Remote

```bash
git push origin feature/descriptive-name
```

### 5. Create Pull Request

**Using GitHub CLI:**
```bash
gh pr create --title "Add feature X" --body "Description of changes..."
```

**Using GitHub Web:**
1. Go to https://github.com/yourusername/MarketPulse
2. Click "Pull requests" → "New pull request"
3. Select your branch
4. Fill in description
5. Submit

### 6. PR Requirements

**Before merging, ensure:**

✅ All CI checks pass (backend-tests, frontend-tests, docker-build, security-scan)
✅ At least 1 approval from reviewer
✅ Branch is up to date with `main`
✅ No merge conflicts
✅ All conversations resolved

**CI/CD will automatically:**
- Run full test suite (backend + frontend)
- Check code formatting
- Validate Docker builds
- Run security scans (Trivy)
- Check test coverage

---

## Troubleshooting

### Pre-Commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run manually
pre-commit run --all-files
```

### Tests Pass Locally but Fail in CI

**Common Causes:**

1. **Environment differences** (Mac vs Linux)
   ```bash
   # Use Docker to match CI environment
   docker-compose up -d postgres redis
   pytest backend/tests/
   ```

2. **Cached dependencies**
   ```bash
   # Clean cache and reinstall
   rm -rf ~/.cache/pip
   pip install -r backend/requirements.txt

   # Frontend
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Missing environment variables**
   ```bash
   # Check CI environment variables
   # Set them locally in .env (not committed)
   ```

### Docker Issues

```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

### Frontend Build Fails

```bash
# Clear cache and rebuild
cd frontend
rm -rf dist node_modules package-lock.json
npm install
npm run build
```

---

## Advanced Workflows

### Local CI Simulation (Optional)

**Tool**: `act` - Run GitHub Actions locally

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run CI workflow locally
act -j backend-tests
act -j frontend-tests

# Run entire workflow
act push
```

**When to use:**
- After major CI/CD changes
- Debugging CI-specific failures
- Before pushing risky changes (e.g., dependency updates)

---

## Getting Help

### Resources

- **Documentation**: [`docs/`](./docs/)
- **CI/CD Best Practices**: [`docs/CI_CD_BEST_PRACTICES.md`](./docs/CI_CD_BEST_PRACTICES.md)
- **Phase 4 Frontend**: [`docs/PHASE4_FRONTEND.md`](./docs/PHASE4_FRONTEND.md)
- **API Documentation**: http://localhost:8000/docs (when running)

### Common Commands Quick Reference

```bash
# Backend
pytest backend/tests/ -v                    # Run tests
black backend/                              # Format code
flake8 backend/                            # Lint code
pytest backend/tests/ --cov=api --cov=models  # Coverage

# Frontend
cd frontend
npm test -- --run                          # Run tests
npm run build                              # Build
npm run dev                                # Dev server
npx prettier --write src/                  # Format code

# Docker
docker-compose up -d                       # Start services
docker-compose down                        # Stop services
docker-compose logs -f postgres            # View logs

# Git
git checkout -b feature/name               # New branch
git add .                                  # Stage changes
git commit -m "feat: description"          # Commit
git push origin feature/name               # Push
gh pr create                               # Create PR
```

---

## ❌ Common Mistakes (Learn from Others!)

### DON'T: Push Without Local Testing

```bash
# ❌ BAD APPROACH
git add .
git commit -m "feat: new feature"
git push  # Crosses fingers, hopes CI passes
# → Wait 5 minutes
# → CI fails
# → Fix bug
# → Wait 5 more minutes
# Total time wasted: 10-15 minutes
```

**Why bad:** Wastes your time and clogs CI queue for teammates.

```bash
# ✅ GOOD APPROACH
pytest backend/tests/ -v  # 30 seconds
cd frontend && npm test -- --run  # 2 seconds
git add .
git commit -m "feat: new feature"
git push  # Confident it will pass
# Total time: 3 minutes
```

**Time saved:** 7-12 minutes per feature!

---

### DON'T: Commit Secrets or API Keys

```bash
# ❌ BAD
echo "API_KEY=sk_live_abc123" > .env
git add .env  # Contains API keys!
git commit -m "config: update settings"
git push  # 🚨 SECRET EXPOSED IN GIT HISTORY
```

**Consequences:**
- Secret is permanently in git history (even if deleted later)
- GitHub will detect and disable the key
- Security incident to explain to your team

**Prevention:**
- ✅ Pre-commit hooks will catch this (Gitleaks)
- ✅ `.env` files are in `.gitignore`
- ✅ Use environment variables, never hardcode secrets

```bash
# ✅ GOOD
echo "API_KEY=sk_live_abc123" > .env  # Not tracked by git
git status  # Shows .env is ignored
git commit -m "config: update settings"  # Safe
```

**If you accidentally commit a secret:**
```bash
# Immediately rotate the secret (change it on the service)
# Then remove from git history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

---

### DON'T: Skip Code Review (Even for "Small Changes")

```bash
# ❌ BAD
git commit -m "fix: typo in comment"
git push origin main  # Directly to main, no PR
```

**Why bad:**
- No CI validation before merging
- No git history/discussion
- Breaks branch protection (if enabled)
- Bad habit for team environments

```bash
# ✅ GOOD
git checkout -b fix/typo-in-dashboard
git commit -m "fix: typo in dashboard comment"
git push origin fix/typo-in-dashboard
gh pr create --title "Fix typo in dashboard" --body "Corrected spelling in comment"
# → CI runs
# → Merge when green
```

**Benefits (even for solo projects):**
- CI validates every change
- Git history is clean and documented
- Practice for real team workflows
- Easy to revert if needed

---

### DON'T: Bypass Pre-Commit Hooks Without Good Reason

```bash
# ❌ BAD
git commit --no-verify -m "WIP: broken tests, will fix later"
# Bypasses all safety checks
# Commits broken code
# Teammates pull broken main branch
```

**When `--no-verify` is acceptable:**
- ✅ **Hotfix for production outage** (critical, time-sensitive)
- ✅ **Git operation only** (e.g., `git commit --amend` to fix commit message)

**99% of the time:** Fix the issue that's blocking the hook.

```bash
# ✅ GOOD
git commit -m "WIP: broken tests"
# → Pre-commit hooks fail
# → Fix tests or code
git commit -m "feat: complete feature with passing tests"
# → Pre-commit hooks pass
# → Commit succeeds
```

---

### DON'T: Ignore Linting/Formatting Errors

```bash
# ❌ BAD
flake8 backend/
# → 15 linting errors found
# "I'll fix them later" (never happens)
git add .
git commit --no-verify -m "feat: new endpoint"
```

**Why bad:**
- Code quality degrades over time
- Teammates have to fix your mess
- CI will fail anyway

```bash
# ✅ GOOD
flake8 backend/
# → 15 linting errors found
black backend/  # Auto-fixes most issues
flake8 backend/
# → 2 remaining errors (manual fix)
# Fix remaining 2 errors
git add .
git commit -m "feat: new endpoint"  # Hooks pass
```

**Pro tip:** Use `black` for auto-formatting (saves 90% of manual work).

---

### DON'T: Commit Debug Statements

```bash
# ❌ BAD
# In your code:
console.log("DEBUG: user data", user)  # Frontend
print("DEBUG:", response)              # Backend
debugger;                              # JavaScript
import pdb; pdb.set_trace()            # Python

git commit -m "feat: add feature"
# Debug statements committed to production code
```

**Why bad:**
- Exposes internal data in logs
- Slows down production code
- Looks unprofessional

**Pre-commit hooks catch this!** But if bypassed:

```bash
# ✅ GOOD - Remove before committing
# Use proper logging instead:

# Frontend
import { logger } from '@/utils/logger'
logger.debug('User data', user)  # Only logs in dev mode

# Backend
import logging
logging.debug(f"Response: {response}")  # Configurable log level
```

---

### DON'T: Make Massive PRs

```bash
# ❌ BAD
git diff --stat
#  50 files changed, 5000 insertions(+), 2000 deletions(-)
# "Refactored entire codebase + added 3 features + fixed 10 bugs"
```

**Why bad:**
- Impossible to review properly
- High chance of bugs slipping through
- Merge conflicts nightmare
- Takes days to get approved

```bash
# ✅ GOOD - Break into smaller PRs
# PR 1: "Refactor authentication module (500 lines)"
# PR 2: "Add customer search feature (300 lines)"
# PR 3: "Fix validation bugs (200 lines)"
# Each PR: Easy to review, quick to merge
```

**Rule of thumb:** Keep PRs under 400 lines of code changes.

---

### DON'T: Commit Commented-Out Code

```bash
# ❌ BAD
def process_order(order):
    # Old implementation (keeping just in case)
    # if order.status == 'pending':
    #     send_email(order.customer)
    #     order.status = 'processing'

    # New implementation
    send_notification(order.customer)
    order.status = 'confirmed'
```

**Why bad:**
- Clutters codebase
- Confuses future developers
- Git already has the history

```bash
# ✅ GOOD - Delete it, git remembers
def process_order(order):
    send_notification(order.customer)
    order.status = 'confirmed'

# If you need old code: git log, git blame
```

---

### DON'T: Use Vague Commit Messages

```bash
# ❌ BAD
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "WIP"
git commit -m "asdfasdf"
git commit -m "final version"
git commit -m "final version 2"
git commit -m "final final version"
```

**Why bad:** Impossible to understand what changed 6 months later.

```bash
# ✅ GOOD - Use Conventional Commits
git commit -m "fix(api): resolve 500 error in customer endpoint"
git commit -m "feat(dashboard): add revenue trend chart"
git commit -m "refactor(auth): simplify JWT token validation"
git commit -m "test(api): add integration tests for products endpoint"
git commit -m "docs: update API documentation with examples"
```

---

## Code of Conduct

- Be respectful and constructive in reviews
- Focus on code, not people
- Help others learn and grow
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/)

---

## 🎯 Quick Wins - Do These First!

1. **Install pre-commit hooks** (5 minutes, saves hours)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Test locally before every push** (30 seconds, prevents CI failures)
   ```bash
   pytest backend/tests/ -v
   cd frontend && npm test -- --run
   ```

3. **Use conventional commit messages** (10 seconds, improves git history)
   ```bash
   git commit -m "feat: add feature"
   git commit -m "fix: resolve bug"
   ```

4. **Create small, focused PRs** (easier reviews, faster merges)
   - Target: <400 lines changed per PR

5. **Review the CI/CD Best Practices doc** (one-time, 15 minutes)
   - Read: [`docs/CI_CD_BEST_PRACTICES.md`](./docs/CI_CD_BEST_PRACTICES.md)

---

**Questions?** Open an issue or reach out to the team!

Happy coding! 🚀
