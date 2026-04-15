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

    login = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
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
    update = client.put(
        "/auth/me",
        headers=auth_headers,
        json={"full_name": "Jordan Updated", "year": "Senior"},
    )
    assert update.status_code == 200
    assert update.json()["full_name"] == "Jordan Updated"

    completed = client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["COSC111", "MATH141"]},
    )
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


def test_login_rate_limit_triggers(client, monkeypatch):
    from app import rate_limit

    monkeypatch.setattr(rate_limit, "AUTH_RATE_LIMIT", 2)
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
