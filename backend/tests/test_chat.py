from io import BytesIO

from app.attachments import AttachmentContext, DocumentCourseSignals
from app.chat import _replace_attachment_document_type


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


def test_refined_attachment_document_type_preserves_ocr_metadata():
    context = AttachmentContext(
        filename="image.png",
        content_type="image/png",
        context_text="Uploaded image screenshot.",
        summary="Screenshot review ready.",
        extracted_text="Completed: COSC 111",
        document_type="image_screenshot",
        extraction_method="image_gemini",
        confidence_note="Used OCR because the image did not contain machine-readable text.",
        signals=DocumentCourseSignals(),
    )

    refined = _replace_attachment_document_type(context, "transcript")

    assert refined.document_type == "transcript"
    assert refined.extraction_method == "image_gemini"
    assert refined.confidence_note == context.confidence_note
    assert refined.summary != context.summary
    assert refined.signals.completed_codes == ("COSC111",)


def test_chat_ai_interest_uses_focus_area_context(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "AI path"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "I want to focus on AI and data science in Computer Science. What should I line up next?"},
    )

    assert response.status_code == 200
    assert "AI and Data" in captured_context["extra_context"]


def test_chat_uses_cs_audit_summary_for_capstone_question(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Computer Science"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["COSC111", "COSC112", "COSC241", "MATH141"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "CS Audit"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "Am I ready for COSC490 based on my CS record so far?"},
    )

    assert response.status_code == 200
    assert response.json()["advisor_insights"]["capstone_readiness"]["status"] == "not_ready"
    assert "Computer Science audit interpretation" in captured_context["extra_context"]
