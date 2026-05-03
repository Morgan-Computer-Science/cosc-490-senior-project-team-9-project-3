# Docker Portability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a clean Docker-based local launch path for the Morgan State AI Faculty Advisor so another machine can run the frontend and backend consistently without depending on the same Python or Node setup used during development.

**Architecture:** Keep the current app architecture intact. Add a backend Dockerfile, a frontend Dockerfile, and a single `docker-compose.yml` entry point. Make Docker the recommended local path while preserving the current manual setup as a fallback in the README.

**Tech Stack:** Docker, Docker Compose, Python/FastAPI backend, React/Vite frontend, SQLite, Gemini via `backend/.env`

---

## File Structure

### Existing files to modify
- `README.md`
  - Document Docker as the recommended launch path and keep manual setup as fallback.
- `frontend/vite.config.js`
  - Confirm host binding works correctly from a container if needed.
- `frontend/package.json`
  - Only modify if a Docker-friendly frontend script is needed.

### New files to add
- `docker-compose.yml`
  - Main local entry point for frontend + backend.
- `backend/Dockerfile`
  - Backend container build.
- `frontend/Dockerfile`
  - Frontend container build.
- `.dockerignore`
  - Keep builds fast and avoid copying unnecessary local files.
- Optional: `frontend/.dockerignore`
- Optional: `backend/.dockerignore`

## Task 1: Add Docker scaffolding for frontend and backend

**Files:**
- Add: `docker-compose.yml`
- Add: `backend/Dockerfile`
- Add: `frontend/Dockerfile`
- Add: `.dockerignore`

- [ ] **Step 1: Add failing or orienting verification notes before implementation**

Write down the expected Docker behavior:
- backend reachable on `127.0.0.1:8000`
- frontend reachable on `127.0.0.1:5173`
- backend reads `backend/.env`
- app data survives container restarts

This does not need to be a formal automated test first if there is no container coverage yet, but the success conditions should be explicit.

- [ ] **Step 2: Create the backend Dockerfile**

The backend image should:
- use a stable Python version like `3.12`
- install from `backend/requirements.txt`
- expose port `8000`
- run `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- use the backend directory as the working directory

Keep the first version simple and reliable.

- [ ] **Step 3: Create the frontend Dockerfile**

The frontend image should:
- use a stable Node image
- install frontend dependencies
- expose port `5173`
- run Vite in a host-accessible way

The first pass should optimize for clarity and launch reliability, not image-size tuning.

- [ ] **Step 4: Add a root `.dockerignore`**

Exclude:
- `.git`
- `.venv`
- `node_modules`
- local cache folders
- pytest cache
- other machine-specific clutter

This prevents slow or messy builds.

## Task 2: Wire Docker Compose as the recommended launch path

**Files:**
- Add: `docker-compose.yml`
- Modify if needed: `frontend/vite.config.js`

- [ ] **Step 1: Define the backend service**

The backend service should:
- build from `backend/Dockerfile`
- load environment variables from `backend/.env`
- mount or preserve local app data appropriately
- expose port `8000`

If a mounted SQLite file or volume is needed, set that up here.

- [ ] **Step 2: Define the frontend service**

The frontend service should:
- build from `frontend/Dockerfile`
- expose port `5173`
- call the backend correctly from the browser-facing environment

Be careful about hostnames and API base URLs so the app works from the host machine, not just container-to-container.

- [ ] **Step 3: Ensure Vite host binding works in Docker**

If needed, update the frontend dev configuration or launch command so the frontend is reachable from the host browser when running in the container.

- [ ] **Step 4: Verify compose startup locally**

Run:
- `docker compose up --build`

Confirm:
- frontend loads
- backend health endpoint responds
- the app can talk to the API

## Task 3: Preserve local data and environment behavior

**Files:**
- Modify: `docker-compose.yml`
- Modify if needed: backend config files only if persistence paths are unclear

- [ ] **Step 1: Confirm how the backend stores local data**

Identify the current database path and any local files that must survive container restarts.

- [ ] **Step 2: Add persistence for app data**

Use either:
- a named Docker volume
- or a clean bind mount

The key requirement is that user data and degree-progress state should not disappear every time the containers restart.

- [ ] **Step 3: Confirm env handling**

Verify the backend container reads:
- `GEMINI_API_KEY`

and any other backend env values from `backend/.env`.

This is especially important because Gemini/runtime issues have already been a friction point.

## Task 4: Update README to match the real launch path

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Docker as the recommended local run path**

Document a short path like:
1. clone repo
2. create `backend/.env`
3. run `docker compose up --build`
4. open the app

- [ ] **Step 2: Keep manual setup as fallback**

Do not remove the current Windows/macOS/Linux instructions.

Instead, label them clearly as:
- fallback manual path

- [ ] **Step 3: Add brief Docker troubleshooting notes**

Include:
- what ports are used
- where to put the Gemini key
- how to stop/rebuild containers

Keep it concise.

## Task 5: Verify portability behavior end to end

**Files:**
- No new product files required unless fixes are needed

- [ ] **Step 1: Verify backend health under Docker**

Check:
- `http://127.0.0.1:8000/health`

- [ ] **Step 2: Verify frontend under Docker**

Check:
- `http://127.0.0.1:5173`

- [ ] **Step 3: Verify one core user flow**

At minimum:
- log in or sign up
- load the dashboard
- send one chat message

This confirms the app still functions, not just the containers.

- [ ] **Step 4: Summarize any remaining local-only limitations**

Examples:
- Docker is now the recommended path, but manual launch still exists
- some Gemini quota issues remain external to the app

## Verification commands

Run these before calling the Docker portability pass complete:

```powershell
docker compose up --build
```

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health).Content
```

```powershell
npm.cmd run build
```

If needed, also verify the backend still compiles or tests cleanly after any config changes.

## Notes

- Prefer Docker as the recommended launch path after this pass.
- Keep the manual local path documented for debugging and development.
- Do not try to solve cloud deployment in the same slice.
