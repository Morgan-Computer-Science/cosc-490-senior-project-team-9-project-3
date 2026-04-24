# Docker Portability Design

## Goal

Make the Morgan State AI Faculty Advisor easier to run on other machines by adding a stable Docker-based local development path for both frontend and backend.

This pass is about portability and consistency, not cloud deployment.

## Why this matters

The app has become much stronger at the product level, but the local setup still depends on:

- the right Python version
- a working virtual environment
- local Node and npm setup
- clean Gemini environment loading

We already ran into this with Gemini and Python runtime compatibility. Docker gives us a more repeatable launch path for teammates and demo machines.

## Scope

This pass should add a recommended Docker-based local launch workflow for:

- `frontend`
- `backend`
- shared environment loading
- local persistence for app data

The desired experience is:

1. clone the repo
2. create the backend env file
3. run one Docker command
4. open the app

## What this pass should include

### 1. Docker Compose as the main entry point

Add a compose-based setup that starts:

- FastAPI backend
- Vite frontend

The compose file should be the recommended local launch path.

### 2. Backend container

The backend container should:

- install Python dependencies from the current backend setup
- run the FastAPI app on the expected API port
- load `backend/.env`
- use the app source cleanly without relying on a host virtual environment

This should reduce the current Python-version fragility and make Gemini setup more consistent.

### 3. Frontend container

The frontend container should:

- install Node dependencies
- run the Vite app in a host-accessible way
- communicate with the backend container correctly

The frontend should still be reachable from the host browser at the normal development URL or a clearly documented Docker URL.

### 4. Persistent local data

The setup should preserve app data across container restarts where reasonable.

At minimum, the local database path should not be wiped every time the containers restart.

### 5. README alignment

Once Docker exists, the README should clearly separate:

- `recommended`: Docker launch path
- `fallback`: manual Windows/macOS/Linux path

The README should be simple enough that another student can pull from `main` and launch the app without guessing.

## Boundaries

This pass should **not** try to do:

- cloud deployment
- Kubernetes
- production hosting
- CI/CD deployment automation
- large infrastructure redesigns

This is a local portability pass only.

## Success criteria

This pass is successful if:

- a teammate can clone the repo and run the app with a small number of predictable Docker steps
- frontend and backend both start from the same compose workflow
- the Gemini key setup is clearly documented
- the app behaves the same on another machine without depending on the exact local Python environment
- the README accurately reflects the working launch options

## Recommended sequencing

1. add Dockerfiles for frontend and backend
2. add compose configuration
3. wire env handling and persistence
4. verify both services run together
5. update README to make Docker the recommended path

## Notes

The manual local path should remain available because it is still useful for development and debugging.

However, Docker should become the default recommendation for portability and demo reliability.
