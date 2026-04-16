# Backend Hardening Design

## Goal
Add a real backend test suite and a focused hardening pass so the Morgan State AI Advisor backend is safer, more reliable, and easier to change without regressions.

## Scope
This pass covers:
- first-party backend tests
- env-driven CORS configuration
- upload validation for file-backed endpoints
- targeted request rate limiting

This pass does not cover:
- Canvas or WebSIS integration
- deployment and infrastructure
- a full auth redesign
- unrelated refactors

## Current State
The backend already provides:
- user registration and login
- JWT-based authenticated routes
- profile and completed-course updates
- degree progress and import preview flows
- catalog endpoints for courses, departments, faculty, and support resources
- chat sessions, messages, RAG-backed advising, and multimodal file handling

The main gaps are:
- no real project-owned backend test suite
- permissive CORS configuration in `backend/app/main.py`
- limited guardrails around upload inputs
- no explicit rate limiting on abuse-prone endpoints

## Approach
Use a test-first hardening pass:
1. create a dedicated `backend/tests/` suite around the current app behavior
2. tighten configuration and validation where behavior is too open or unsafe
3. add rate limiting to the highest-risk endpoints
4. verify everything with targeted test runs

This keeps the scope focused and gives the project a real regression safety net before more backend expansion.

## Architecture Changes

### 1. Test Harness
Create a first-party test harness that can instantiate the FastAPI app against an isolated test database.

The test harness should:
- build a test client for the app
- override database/session dependencies when needed
- allow authenticated requests without touching production data
- support repeated runs without manual cleanup

Tests should focus on app-owned behavior, not library internals.

### 2. CORS Configuration
Replace hardcoded wildcard CORS with environment-driven configuration.

Behavior:
- allow a comma-separated env var for explicit origins
- keep a sensible local-development default such as the Vite frontend origin
- avoid broad `*` defaults once explicit origins are available

This keeps development smooth while making the app safer and more launch-oriented.

### 3. Upload Validation
Add a shared validation layer for upload-backed endpoints.

Validation should include:
- allowed extensions and/or content types
- max file size cap
- clear client-facing errors for unsupported files

Target endpoints:
- completed-course import preview
- chat message attachments

The goal is to reject obviously unsupported or abusive inputs before deeper processing.

### 4. Rate Limiting
Add lightweight rate limiting to sensitive endpoints.

Priority endpoints:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/me/completed-courses/import`
- `POST /chat/{session_id}/messages`

Behavior goals:
- stop high-frequency abuse and accidental rapid-fire requests
- be permissive enough for normal demo and classroom use
- return a clear error when the limit is hit

A simple in-process limiter is acceptable for this project phase.

## Test Coverage Plan

### Auth
Cover:
- successful registration
- duplicate email rejection
- successful login
- invalid password rejection
- authenticated `/auth/me` access
- rejected `/auth/me` without a valid token

### Profile and Progress Inputs
Cover:
- profile update flow
- completed course update flow
- import preview with text input
- import preview rejection for invalid or oversized files

### Catalog
Cover:
- courses endpoint
- departments endpoint
- faculty endpoint
- support resources endpoint

### Chat
Cover:
- session creation
- session listing
- basic message send flow
- attachment-backed message validation
- rate-limit behavior on chat send

### Rate Limit
Add explicit tests that confirm rate limiting triggers on at least one auth endpoint and one chat/import endpoint.

## Error Handling Expectations
Responses should stay consistent with existing API style:
- validation failures should return clear `400` or `422` class errors where appropriate
- authentication failures should remain `401`
- rate limit hits should use a clear client-facing error and appropriate status code

## Implementation Notes
Keep this pass focused:
- do not refactor large backend modules unless a small extraction directly supports testing or hardening
- prefer adding shared helpers for CORS, uploads, and rate limiting rather than duplicating logic in routes
- preserve existing frontend-facing response shapes unless a change is necessary for correctness

## Verification
At minimum verify with:
- backend compile check
- targeted pytest runs for the new backend tests
- a quick sanity run of the affected endpoints if needed

## Success Criteria
This hardening pass is successful when:
- the backend has a project-owned test suite for the core API flows
- CORS is no longer hardcoded to unrestricted wildcard behavior
- unsafe or unsupported file uploads are rejected cleanly
- sensitive endpoints have working rate limits
- the new tests pass and protect these behaviors from regression
