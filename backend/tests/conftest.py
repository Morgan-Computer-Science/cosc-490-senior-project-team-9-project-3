import csv
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import models
from app.db import Base, get_db
from app.main import app

TEST_DB_PATH = BACKEND_DIR / "test_morgan_ai.db"
COURSE_CSV_PATH = BACKEND_DIR / "data" / "courses.csv"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_course_rows(db):
    with COURSE_CSV_PATH.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            code = (row.get("code") or "").strip().upper()
            if not code:
                continue
            credits = (row.get("credits") or "").strip()
            db.add(
                models.Course(
                    code=code,
                    title=(row.get("title") or "").strip(),
                    description=(row.get("description") or "").strip(),
                    credits=int(credits) if credits.isdigit() else None,
                    department=(row.get("department") or "").strip() or None,
                    level=(row.get("level") or "").strip() or None,
                    semester_offered=(row.get("semester_offered") or "").strip() or None,
                    instructor=(row.get("instructor") or "").strip() or None,
                )
            )


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def fresh_db():
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    Base.metadata.create_all(bind=engine)

    try:
        from app.rate_limit import reset_rate_limits
        reset_rate_limits()
    except Exception:
        pass

    db = TestingSessionLocal()
    seed_course_rows(db)
    db.commit()
    db.close()

    yield

    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


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
    login = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
