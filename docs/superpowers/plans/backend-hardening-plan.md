# Backend Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a project-owned backend test suite plus focused hardening for CORS, file uploads, and rate limiting without breaking the current API.

**Architecture:** Keep the existing FastAPI structure, add small shared helpers for config, upload validation, and rate limiting, and cover the current routes with a dedicated pytest harness against an isolated SQLite database. The hardening work stays incremental: protect the existing auth, import, catalog, and chat flows rather than refactoring the whole backend.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, pytest, FastAPI TestClient, python-multipart, existing Gemini integration with test-time monkeypatching.

---

## File Structure

**Create**
- `backend/app/config.py`
  - central env-driven app settings for CORS, upload limits, and rate-limit values
- `backend/app/rate_limit.py`
  - small in-memory limiter helper and route-facing `Depends` wrappers
- `backend/tests/conftest.py`
  - test app/client/database fixtures and auth helpers
- `backend/tests/test_auth.py`
  - register/login/auth/profile tests
- `backend/tests/test_catalog.py`
  - course/department/faculty/support route tests
- `backend/tests/test_chat.py`
  - chat flow, attachment validation, and chat rate-limit tests

**Modify**
- `backend/requirements.txt`
  - add pytest test dependency if missing
- `backend/app/main.py`
  - replace hardcoded wildcard CORS with config-driven origins
- `backend/app/attachments.py`
  - move upload rules behind config, add stricter extension/type validation helper
- `backend/app/auth.py`
  - apply auth/import rate limits and preserve current behavior
- `backend/app/chat.py`
  - apply chat send rate limit and preserve current behavior
- `backend/app/db.py`
  - allow database URL override for tests

---

### Task 1: Add shared backend configuration

**Files:**
- Create: `backend/app/config.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/db.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add a small config module**

```python
# backend/app/config.py
import os


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


DEFAULT_FRONTEND_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

ALLOWED_CORS_ORIGINS = _split_csv(os.getenv("ALLOWED_CORS_ORIGINS")) or DEFAULT_FRONTEND_ORIGINS
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./morgan_ai.db")
MAX_ATTACHMENT_BYTES = int(os.getenv("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024)))
AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "5"))
AUTH_RATE_WINDOW_SECONDS = int(os.getenv("AUTH_RATE_WINDOW_SECONDS", "60"))
CHAT_RATE_LIMIT = int(os.getenv("CHAT_RATE_LIMIT", "12"))
CHAT_RATE_WINDOW_SECONDS = int(os.getenv("CHAT_RATE_WINDOW_SECONDS", "60"))
IMPORT_RATE_LIMIT = int(os.getenv("IMPORT_RATE_LIMIT", "6"))
IMPORT_RATE_WINDOW_SECONDS = int(os.getenv("IMPORT_RATE_WINDOW_SECONDS", "60"))
```

- [ ] **Step 2: Point the database layer at config-driven URLs**

```python
# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- [ ] **Step 3: Replace permissive wildcard CORS with configured origins**

```python
# backend/app/main.py
from .config import ALLOWED_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step 4: Add the test dependency**

```text
# backend/requirements.txt
pytest==8.4.1
```

- [ ] **Step 5: Run backend compile to verify config wiring**

Run: `py -3.12 -m compileall app`
Expected: `Compiling 'app\\config.py'...` and no syntax errors.

- [ ] **Step 6: Commit**

```bash
git add backend/app/config.py backend/app/db.py backend/app/main.py backend/requirements.txt
git commit -m "Add backend config defaults for hardening"
```

### Task 2: Add shared rate limiting

**Files:**
- Create: `backend/app/rate_limit.py`
- Modify: `backend/app/auth.py`
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Add an in-memory limiter helper**

```python
# backend/app/rate_limit.py
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from .config import (
    AUTH_RATE_LIMIT,
    AUTH_RATE_WINDOW_SECONDS,
    CHAT_RATE_LIMIT,
    CHAT_RATE_WINDOW_SECONDS,
    IMPORT_RATE_LIMIT,
    IMPORT_RATE_WINDOW_SECONDS,
)

_REQUEST_LOG: dict[str, deque[datetime]] = defaultdict(deque)


def _hit(bucket: str, limit: int, window_seconds: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    queue = _REQUEST_LOG[bucket]
    while queue and queue[0] < window_start:
        queue.popleft()
    if len(queue) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment and try again.",
        )
    queue.append(now)


def _client_key(request: Request, prefix: str) -> str:
    return f"{prefix}:{request.client.host if request.client else 'unknown'}"


def limit_auth(request: Request) -> None:
    _hit(_client_key(request, "auth"), AUTH_RATE_LIMIT, AUTH_RATE_WINDOW_SECONDS)


def limit_chat(request: Request) -> None:
    _hit(_client_key(request, "chat"), CHAT_RATE_LIMIT, CHAT_RATE_WINDOW_SECONDS)


def limit_import(request: Request) -> None:
    _hit(_client_key(request, "import"), IMPORT_RATE_LIMIT, IMPORT_RATE_WINDOW_SECONDS)


def reset_rate_limits() -> None:
    _REQUEST_LOG.clear()
```

- [ ] **Step 2: Apply auth and import limits to the route signatures**

```python
# backend/app/auth.py
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from .rate_limit import limit_auth, limit_import

@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    request: Request,
    _: None = Depends(limit_auth),
    db: Session = Depends(get_db),
):
    ...

@router.post("/login", response_model=schemas.Token)
def login(
    request: Request,
    _: None = Depends(limit_auth),
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ...

@router.post("/me/completed-courses/import", response_model=schemas.CompletedCoursesImportPreview)
async def import_completed_courses_preview(
    request: Request,
    _: None = Depends(limit_import),
    import_source: str = Form(default="manual"),
    ...
):
    ...
```

- [ ] **Step 3: Apply chat send rate limiting**

```python
# backend/app/chat.py
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from .rate_limit import limit_chat

@router.post("/sessions/{session_id}/messages", response_model=schemas.ChatSendResponse)
async def send_message(
    session_id: int,
    request: Request,
    _: None = Depends(limit_chat),
    content: str = Form(...),
    attachment: UploadFile | None = File(default=None),
    ...
):
    ...
```

- [ ] **Step 4: Compile to make sure the route signatures still parse**

Run: `py -3.12 -m compileall app`
Expected: no syntax errors in `auth.py`, `chat.py`, or `rate_limit.py`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/rate_limit.py backend/app/auth.py backend/app/chat.py
git commit -m "Add targeted backend rate limits"
```

### Task 3: Tighten upload validation

**Files:**
- Modify: `backend/app/attachments.py`
- Modify: `backend/app/auth.py`
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Move file-size config and allowed upload rules into shared constants**

```python
# backend/app/attachments.py
from pathlib import Path

from .config import MAX_ATTACHMENT_BYTES

ALLOWED_ATTACHMENT_SUFFIXES = {".pdf", ".txt", ".md", ".csv", ".json", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_ATTACHMENT_MIME_PREFIXES = ("text/", "image/")
ALLOWED_ATTACHMENT_MIME_TYPES = {
    "application/pdf",
    "application/json",
    "application/xml",
    "application/javascript",
}


def validate_attachment_upload(filename: str, content_type: str, file_bytes: bytes) -> None:
    suffix = Path(filename).suffix.lower()
    if len(file_bytes) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Attachments must be 10 MB or smaller.")
    allowed_mime = content_type in ALLOWED_ATTACHMENT_MIME_TYPES or content_type.startswith(ALLOWED_ATTACHMENT_MIME_PREFIXES)
    if suffix not in ALLOWED_ATTACHMENT_SUFFIXES and not allowed_mime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported attachment type.")
```

- [ ] **Step 2: Call the validator before deeper extraction**

```python
# backend/app/attachments.py
file_bytes = await attachment.read()
await attachment.close()
validate_attachment_upload(filename, content_type, file_bytes)
```

- [ ] **Step 3: Keep auth/chat routes on the same helper path**

```python
# backend/app/auth.py and backend/app/chat.py
attachment_context = await extract_attachment_context(attachment) if attachment else None
```

This step is a no-op logic check: do not duplicate file validation in the routes. Keep the validation centralized inside `extract_attachment_context()`.

- [ ] **Step 4: Compile to verify the validator path**

Run: `py -3.12 -m compileall app`
Expected: no syntax errors in `attachments.py`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/attachments.py
git commit -m "Validate backend upload types and size limits"
```

### Task 4: Create the test harness

**Files:**
- Create: `backend/tests/conftest.py`
- Modify: `backend/app/db.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_catalog.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Add test database fixtures and app overrides**

```python
# backend/tests/conftest.py
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import Base, get_db
from app.main import app
from app.rate_limit import reset_rate_limits

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_morgan_ai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_rate_limits()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(monkeypatch):
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.chat.generate_ai_reply", lambda **_: "Test advisor reply")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    payload = {
        "email": "student@morgan.edu",
        "password": "password123",
        "full_name": "Jordan Smith",
        "major": "Computer Science",
        "year": "Junior",
    }
    client.post("/auth/register", json=payload)
    login = client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

- [ ] **Step 2: Install dependencies before running tests**

Run: `pip install -r requirements.txt`
Expected: pytest installs into the local backend environment.

- [ ] **Step 3: Run pytest once to confirm the harness imports even before full coverage exists**

Run: `pytest backend/tests -q`
Expected: collection works, with failures only because test modules are not added yet.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/conftest.py backend/app/db.py backend/requirements.txt
git commit -m "Add backend pytest harness"
```

### Task 5: Add auth and import tests

**Files:**
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Add auth coverage**

```python
# backend/tests/test_auth.py
from io import BytesIO


def test_register_and_login_flow(client):
    payload = {
        "email": "newstudent@morgan.edu",
        "password": "password123",
        "full_name": "New Student",
        "major": "Computer Science",
        "year": "Freshman",
    }
    register = client.post("/auth/register", json=payload)
    assert register.status_code == 201
    assert register.json()["email"] == payload["email"]

    login = client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_duplicate_registration_is_rejected(client):
    payload = {
        "email": "duplicate@morgan.edu",
        "password": "password123",
        "full_name": "Dup Student",
        "major": "Computer Science",
        "year": "Freshman",
    }
    client.post("/auth/register", json=payload)
    duplicate = client.post("/auth/register", json=payload)
    assert duplicate.status_code == 400


def test_auth_me_requires_valid_token(client, auth_headers):
    ok = client.get("/auth/me", headers=auth_headers)
    assert ok.status_code == 200
    unauthorized = client.get("/auth/me")
    assert unauthorized.status_code == 401


def test_profile_update_and_completed_courses(client, auth_headers):
    update = client.put("/auth/me", headers=auth_headers, json={"full_name": "Jordan Updated", "year": "Senior"})
    assert update.status_code == 200
    assert update.json()["full_name"] == "Jordan Updated"

    completed = client.put("/auth/me/completed-courses", headers=auth_headers, json={"course_codes": ["COSC111", "MATH141"]})
    assert completed.status_code == 200
    assert sorted(item["course_code"] for item in completed.json()) == ["COSC111", "MATH141"]


def test_import_preview_accepts_text_and_rejects_bad_files(client, auth_headers):
    ok = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={"import_source": "transcript_text", "source_text": "Completed: COSC 111, MATH 141"},
    )
    assert ok.status_code == 200
    assert "COSC111" in ok.json()["matched_course_codes"]

    bad = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={"import_source": "manual", "source_text": ""},
        files={"attachment": ("malware.exe", BytesIO(b"fake"), "application/octet-stream")},
    )
    assert bad.status_code == 400
```

- [ ] **Step 2: Add auth rate-limit coverage**

```python
def test_login_rate_limit_triggers(client, monkeypatch):
    monkeypatch.setenv("AUTH_RATE_LIMIT", "2")
    payload = {
        "email": "limited@morgan.edu",
        "password": "password123",
        "full_name": "Limited User",
        "major": "Computer Science",
        "year": "Junior",
    }
    client.post("/auth/register", json=payload)
    client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    limited = client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    assert limited.status_code == 429
```

- [ ] **Step 3: Run the auth tests**

Run: `pytest backend/tests/test_auth.py -q`
Expected: all auth tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_auth.py
git commit -m "Test backend auth and import flows"
```

### Task 6: Add catalog tests

**Files:**
- Create: `backend/tests/test_catalog.py`

- [ ] **Step 1: Add catalog endpoint tests**

```python
# backend/tests/test_catalog.py

def test_catalog_endpoints_return_data(client, auth_headers):
    courses = client.get("/catalog/courses", headers=auth_headers)
    assert courses.status_code == 200
    assert isinstance(courses.json(), list)

    departments = client.get("/catalog/departments", headers=auth_headers)
    assert departments.status_code == 200
    assert isinstance(departments.json(), list)
    assert departments.json()

    faculty = client.get("/catalog/faculty", headers=auth_headers)
    assert faculty.status_code == 200
    assert isinstance(faculty.json(), list)
    assert faculty.json()

    support = client.get("/catalog/support-resources", headers=auth_headers)
    assert support.status_code == 200
    assert isinstance(support.json(), list)
    assert support.json()
```

- [ ] **Step 2: Add a search filter assertion**

```python
def test_course_search_filters_results(client, auth_headers):
    response = client.get("/catalog/courses?search=COSC", headers=auth_headers)
    assert response.status_code == 200
    assert all("COSC" in (course["code"] + course["title"]) for course in response.json())
```

- [ ] **Step 3: Run the catalog tests**

Run: `pytest backend/tests/test_catalog.py -q`
Expected: catalog tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_catalog.py
git commit -m "Test backend catalog endpoints"
```

### Task 7: Add chat tests

**Files:**
- Create: `backend/tests/test_chat.py`

- [ ] **Step 1: Add basic chat flow coverage**

```python
# backend/tests/test_chat.py
from io import BytesIO


def test_chat_session_flow(client, auth_headers):
    created = client.post("/chat/sessions", headers=auth_headers, json={"title": "Planning"})
    assert created.status_code == 200
    session_id = created.json()["id"]

    sessions = client.get("/chat/sessions", headers=auth_headers)
    assert sessions.status_code == 200
    assert any(session["id"] == session_id for session in sessions.json())

    sent = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What should I take after COSC 111?"},
    )
    assert sent.status_code == 200
    assert sent.json()["ai_message"]["content"] == "Test advisor reply"

    history = client.get(f"/chat/sessions/{session_id}/messages", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()) == 2
```

- [ ] **Step 2: Add attachment validation and chat rate-limit tests**

```python
def test_chat_rejects_unsupported_attachment(client, auth_headers):
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Uploads"}).json()["id"]
    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Please read this"},
        files={"attachment": ("bad.exe", BytesIO(b"fake"), "application/octet-stream")},
    )
    assert response.status_code == 400


def test_chat_rate_limit_triggers(client, auth_headers, monkeypatch):
    monkeypatch.setenv("CHAT_RATE_LIMIT", "2")
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Rate limited"}).json()["id"]
    client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "One"})
    client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "Two"})
    limited = client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "Three"})
    assert limited.status_code == 429
```

- [ ] **Step 3: Run the chat tests**

Run: `pytest backend/tests/test_chat.py -q`
Expected: chat tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_chat.py
git commit -m "Test backend chat and upload protections"
```

### Task 8: Run the full verification pass

**Files:**
- Verify only

- [ ] **Step 1: Run the full backend test suite**

Run: `pytest backend/tests -q`
Expected: all backend tests pass.

- [ ] **Step 2: Run the backend compile check again**

Run: `py -3.12 -m compileall app`
Expected: no compile errors.

- [ ] **Step 3: Check git status for only expected backend changes**

Run: `git status --short`
Expected: only the planned backend files are modified or added.

- [ ] **Step 4: Commit the final hardening sweep**

```bash
git add backend/app backend/tests backend/requirements.txt
git commit -m "Harden backend inputs and add API test coverage"
```
