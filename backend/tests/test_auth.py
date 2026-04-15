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

def test_import_preview_returns_ocr_metadata(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={"import_source": "transcript_text", "source_text": "Completed: COSC 111"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "detected_document_type" in payload
    assert "extraction_method" in payload
    assert "summary" in payload


def test_degree_progress_supports_launch_visible_majors(client, auth_headers):
    for major in ("Cloud Computing", "Architecture"):
        updated = client.put("/auth/me", headers=auth_headers, json={"major": major})
        assert updated.status_code == 200

        progress = client.get("/auth/me/degree-progress", headers=auth_headers)
        assert progress.status_code == 200
        payload = progress.json()
        assert payload["major"] == major
        assert payload["required_courses"]


def test_canvas_export_preview_prefers_current_schedule_context(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "canvas_export",
            "source_text": (
                "Canvas dashboard export\n"
                "Current Courses: COSC 111, MATH 141\n"
                "Enrolled for Fall Semester\n"
                "Upcoming Assignments in ENGL 101\n"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_document_type"] == "schedule"
    assert payload["completed_course_codes"] == []
    assert {"COSC111", "MATH141", "ENGL101"}.issubset(set(payload["planned_course_codes"]))
    assert "Canvas" in payload["source_summary"]
    assert "current" in payload["summary"].lower()
    assert "current-course context" in payload["confidence_note"].lower()


def test_websis_export_preview_prefers_official_record_context(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": (
                "WebSIS academic record\n"
                "Major: Computer Science\n"
                "Completed Courses: COSC 111, MATH 141\n"
                "Remaining Requirements: COSC 241, MATH 241\n"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_document_type"] == "degree_audit"
    assert {"COSC111", "MATH141"}.issubset(set(payload["completed_course_codes"]))
    assert {"COSC241", "MATH241"}.issubset(set(payload["remaining_course_codes"]))
    assert "WebSIS" in payload["source_summary"]
    assert "official" in payload["summary"].lower()
    assert "academic record" in payload["confidence_note"].lower()


def test_websis_export_preview_recognizes_real_transcript_codes_from_expanded_catalog(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": (
                "Program Audit for Computer Science\n"
                "Major in Computer Science IN-PROGRESS\n"
                "Introduction to Computer Science II COSC 112 INTRO TO COMPUTER SCIENCE II A 4 SPRING 2021\n"
                "Computer Systems & Digital Logic COSC 241 COMPUTER SYSTEMS & DIG LOGIC A 3 SPRING 2025\n"
                "Foundations of Computing COSC 220 FOUNDATIONS OF COMPUTING A 3 FALL 2024\n"
                "Database Design COSC 459 DATABASE DESIGN IP (3) SPRING 2026\n"
                "Discrete Structures MATH 331 DISCRETE STRUCTURES IP (3) SPRING 2026\n"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_document_type"] == "degree_audit"
    assert {"COSC112", "COSC220", "COSC241"}.issubset(set(payload["completed_course_codes"]))
    assert "COSC241" in payload["completed_course_codes"]
    assert {"COSC459", "MATH331"}.issubset(set(payload["planned_course_codes"]))
    assert payload["unknown_course_codes"] == []


def test_import_preview_normalizes_information_systems_alias_codes(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": (
                "WebSIS academic record\n"
                "Major: Information Systems\n"
                "Completed Courses: ISYS 201, ISYS 220\n"
                "Remaining Requirements: ISYS 310, ISYS 340\n"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert {"INSS201", "INSS220"}.issubset(set(payload["completed_course_codes"]))
    assert {"INSS310", "INSS340"}.issubset(set(payload["remaining_course_codes"]))
    assert payload["unknown_course_codes"] == []


def test_import_preview_recognizes_new_political_science_codes(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": "Completed Courses: POSC 101, POSC 201",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert {"POSC101", "POSC201"}.issubset(set(payload["completed_course_codes"]))


def test_cs_import_preview_returns_cs_specific_audit_summary(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": "Computer Science degree audit\nCOSC 111 A\nCOSC 241 A\nCOSC 490 IP\nMATH 141 A",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cs_audit_summary"]["capstone_readiness"]["status"] == "not_ready"
    assert payload["cs_audit_summary"]["summary_lines"]
