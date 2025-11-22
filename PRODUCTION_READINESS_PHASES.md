# 🚀 Production Readiness: 5-Phase Implementation Plan

> **IMPORTANT:** Before starting, check the `/plan` folder in the project root. It contains all the reference documents mentioned below (PROJECT_CLEANUP_PROMPT.md, COMPLETE_PRODUCTION_GUIDE.md, etc.). Read through them first to understand the full context.

---

## PHASE 1: The "Spring Cleaning" (Audit)

**Goal:** Remove unused files before we dockerize, so the image is small and clean.  
**Reference:** PROJECT_CLEANUP_PROMPT.md

```
We are moving to the "Production Readiness" phase.
First, I need you to act as a Lead Developer performing a codebase audit. We need to remove unused files to keep our Docker image light and our repo clean.

Please execute the strategy outlined in `PROJECT_CLEANUP_PROMPT.md`.
1. Create a shell script `scripts/find_unused_files.sh` based on the logic in the file.
2. Run it and analyze the output.
3. **Do not delete files yet.** Instead, create a `check-zone/` directory and move the unused files there as described in the guide.
4. Update `files_to_archive.txt` so I can review what we are moving.

**Commit Message requirement:**
When we finalize the move, use this format:
`chore(cleanup): archive unused assets and scripts to check-zone`
```

---

## PHASE 2: The "Professional Standard" (Config & Docker)

**Goal:** Switch from "hardcoded strings" to "Environment Variables" and set up the Multi-Stage Dockerfile.  
**Reference:** COMPLETE_PRODUCTION_GUIDE.md (Parts 4 & 5)

```
Now that the code is clean, let's implement Professional Configuration Management and Containerization.
Refer to `COMPLETE_PRODUCTION_GUIDE.md`.

**Task 1: Configuration**
- Remove any hardcoded URLs (like localhost) from `main.py`.
- Create a single `backend/config.py` that reads from `os.getenv`.
- Ensure it handles `CORS_ORIGINS` as a comma-separated string.
- Validate that `DATABASE_URL` is present on startup.

**Task 2: Docker**
- Create a **Multi-Stage** `Dockerfile` in `backend/` (Builder vs Runtime stage).
- Create a `.dockerignore` to exclude `venv`, `.git`, and `__pycache__`.
- Create a `docker-compose.yml` for local development that mimics production.

**Commit Message:**
`feat(infra): implement environment-based config and multi-stage Docker build`
```

---

## PHASE 3: The "Self-Healing Database" (Alembic)

**Goal:** Set up Async Migrations so you never have to run SQL scripts manually.  
**Reference:** COMPLETE_PRODUCTION_GUIDE.md (Part 2)

```
We need to set up robust Database Migrations using Alembic with **Async support**.
Refer to "Part 2: Database Migrations" in the guide.

**Tasks:**
1. Initialize Alembic in `backend/`.
2. **CRITICAL:** Update `alembic/env.py` to use `async_engine_from_config` (use the code provided in the guide exactly).
3. create the `backend/docker-entrypoint.sh` script that runs `alembic upgrade head` before starting the app.
4. Generate the initial migration `initial_schema`.

**Commit Message:**
`feat(db): setup async alembic migrations and auto-migration entrypoint`
```

---

## PHASE 4: Infrastructure as Code (Render Blueprint)

**Goal:** Prove to recruiters you know "IaC" (Infrastructure as Code).  
**Reference:** COMPLETE_PRODUCTION_GUIDE.md (Part 6)

```
We are ready for deployment configuration. instead of clicking buttons in the Render dashboard, we will use Infrastructure as Code.

**Task:**
Create a `render.yaml` file in the root directory based on Part 6 of the guide.
- Define the Backend (Docker).
- Define the build context.
- Set the `preDeployCommand` to run migrations.
- **Do not commit secrets.** Set `sync: false` for DATABASE_URL and SECRET_KEY.

**Commit Message:**
`feat(ops): add render.yaml blueprint for infrastructure as code`
```

---

## PHASE 5: The "Product Showcase" (Readme)

**Goal:** The "Punchy" presentation we discussed earlier.  
**Reference:** Your previous prompt about the "Presentation/Readme".

```
Final step: We need to overhaul the `README.md` to look like a Product Landing Page, not a student project.

**Requirements:**
- Use the "Punchy and Precise" structure we discussed.
- **Section 1:** The "Dirty vs Clean" data transformation (I will add the screenshots later, just create the placeholders and the narrative).
- **Section 2:** The Architecture Diagram (Use Mermaid.js syntax: `graph LR`).
- **Section 3:** The Stack (Badges).
- **Section 4:** Business Insights (The "Why").
- **NO** "git clone" or installation instructions at the top. Move those to a `docs/DEVELOPMENT.md` file and link to it.

**Commit Message:**
`docs: restructure README to focus on business value and data transformation`
```

---

## 💡 Why this specific order?

1. **Cleanup first:** You don't want to build a Docker image containing 20 unused Python scripts. It bloats the size and slows down deployment.

2. **Config & Docker:** This ensures the app can run in the cloud before we try to put it there.

3. **Alembic:** You need the database migration system working inside the Docker container.

4. **IaC:** This is the instruction manual for Render to read the Dockerfile.

5. **Readme:** The cherry on top once the code is professional.
