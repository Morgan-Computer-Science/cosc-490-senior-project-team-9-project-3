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
    from app import rate_limit

    monkeypatch.setattr(rate_limit, "CHAT_RATE_LIMIT", 2)
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Rate limited"}).json()["id"]
    client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "One"})
    client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "Two"})
    limited = client.post(f"/chat/sessions/{session_id}/messages", headers=auth_headers, data={"content": "Three"})
    assert limited.status_code == 429
