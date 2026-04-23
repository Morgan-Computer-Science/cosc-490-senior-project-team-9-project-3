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


def test_chat_handles_small_talk_without_triggering_advising_dump(client, auth_headers):
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Small Talk"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Hello how are you?"},
    )

    assert response.status_code == 200
    reply = response.json()["ai_message"]["content"]
    assert "Morgan State" in reply
    assert "recommended next courses" not in reply.lower()
    assert "completion is" not in reply.lower()
    assert "what would you like help with" in reply.lower()


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


def test_chat_context_includes_business_guidance_for_marketing_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Marketing"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["ACCT201", "ECON201", "MGMT220", "STAT302", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Marketing Path"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next for marketing?"},
    )

    assert response.status_code == 200
    assert "Program guidance:" in captured_context["extra_context"]

def test_chat_context_includes_business_guidance_for_finance_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Finance"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["ACCT201", "ECON201", "ECON202", "STAT302", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Finance Path"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next for finance?"},
    )

    assert response.status_code == 200
    assert "Program guidance:" in captured_context["extra_context"]
    assert "FINA300" in captured_context["extra_context"]


def test_chat_context_includes_program_guidance_for_cloud_computing_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Cloud Computing"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["CLDC101", "COSC111", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Cloud Path"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next in cloud computing?"},
    )

    assert response.status_code == 200
    assert "Program guidance:" in captured_context["extra_context"]
    assert "Cloud Computing" in captured_context["extra_context"]


def test_chat_context_includes_program_guidance_for_psychology_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Psychology"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["PSYC101", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Psych Path"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next in psychology?"},
    )

    assert response.status_code == 200
    assert "Program guidance:" in captured_context["extra_context"]
    assert "Psychology" in captured_context["extra_context"]


def test_chat_fallback_uses_uploaded_transcript_summary_for_gpa_questions(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Transcript GPA"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What's my current GPA?"},
        files={
            "attachment": (
                "transcript.txt",
                BytesIO(
                    b"Morgan State transcript\nCurrent GPA: 3.42\nEarned Credits: 87\nCompleted: COSC 111, MATH 141"
                ),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["ai_message"]["content"] == "Your uploaded document shows a GPA of 3.42."


def test_chat_uses_saved_import_snapshot_context_after_degree_progress_apply(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)

    preview = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": (
                "Degree Audit for Computer Science\n"
                "Current GPA: 3.090\n"
                "Completed: BIOL 101, COSC 111, COSC 112, COSC 220, COSC 241, COSC 243, COSC 320, ENGL 101, ENGL 102, HIST 101, MATH 241, MATH 242, MATH 312\n"
                "Planned / Current: COSC 470, COSC 459, COSC 490, MATH 331\n"
                "Remaining / Needed: COSC 238, ORNS 106, PSYC 101\n"
            ),
        },
    )
    assert preview.status_code == 200
    preview_payload = preview.json()

    applied = client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={
            "course_codes": preview_payload["completed_course_codes"],
            "import_preview": preview_payload,
        },
    )
    assert applied.status_code == 200

    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Degree Works"}).json()["id"]
    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What do you think of my degree works?"},
    )

    effective_done = {
        *preview_payload["completed_course_codes"],
        *preview_payload["planned_course_codes"],
    }
    total_recognized = {
        *effective_done,
        *preview_payload["remaining_course_codes"],
    }
    expected_completion = round((len(effective_done) / len(total_recognized)) * 100, 1)

    assert response.status_code == 200
    assert f"Completion: {expected_completion}%" in captured_context["extra_context"]
    assert "COSC490 Readiness: in progress" in captured_context["extra_context"]
    assert "GPA shown in the uploaded document: 3.090" in captured_context["extra_context"]


def test_chat_fallback_for_leadership_query_prefers_entity_context(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Leadership"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Who is the dean of Computer Science at Morgan State University?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Paul Tchounwou" in body
    assert "Dean" in body
    assert "Most relevant retrieved information" not in body


def test_chat_fallback_for_office_query_prefers_support_contact_language(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Office"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What office handles transfer advising?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Transfer Evaluation Office" in body
    assert "transfercredit@morgan.edu" in body
    assert "Most relevant retrieved information" not in body


def test_chat_fallback_returns_tutoring_contact_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Tutoring"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What office helps with tutoring?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Center for Academic Success and Achievement" in body
    assert "casa@morgan.edu" in body


def test_chat_fallback_returns_research_or_robotics_support_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Research"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Who should I contact about undergraduate research or robotics in Computer Science?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Computer Science" in body or "robotics" in body.lower()
    assert (
        "csdept@morgan.edu" in body
        or "ece@morgan.edu" in body
        or "radhouane.chouchane@morgan.edu" in body
        or "kofi.nyarko@morgan.edu" in body
        or "jamell.dacon@morgan.edu" in body
    )


def test_chat_fallback_returns_student_organizations_contact_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Student Orgs"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "How do I get involved in student organizations at Morgan?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Office of Student Life & Development" in body
    assert "studentlife@morgan.edu" in body


def test_chat_fallback_surfaces_named_lab_paths_when_available(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Labs"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Is there a robotics or AI lab at Morgan State University?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "RAIN" in body or "MINDS" in body or "CEAMLS" in body


def test_chat_fallback_returns_internship_and_career_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Internships"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Where do I go for internships and career help at Morgan?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Handshake" in body or "Center for Career Development" in body
    assert "careers@morgan.edu" in body


def test_chat_fallback_returns_scholarship_or_funding_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Funding"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Where should I start for scholarships or research funding at Morgan?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "ScholarshipUniverse" in body or "CreativeEdge" in body or "Financial Aid" in body
    assert "finaid@morgan.edu" in body or "OUR@morgan.edu" in body


def test_chat_fallback_returns_student_success_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Support"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Who helps if I am struggling academically and need support?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Student Success" in body or "CASA" in body or "tutoring@morgan.edu" in body


def test_chat_fallback_returns_registrar_process_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Registrar"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "How do I get my transcript from Morgan?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Registrar" in body or "transcript" in body.lower()
    assert "registrar@morgan.edu" in body


def test_chat_fallback_returns_transfer_or_override_process_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Process"}).json()["id"]

    transfer_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Who handles transfer credit evaluation at Morgan?"},
    )
    override_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Who do I contact for a registration override?"},
    )

    assert transfer_response.status_code == 200
    assert override_response.status_code == 200

    transfer_body = transfer_response.json()["ai_message"]["content"]
    override_body = override_response.json()["ai_message"]["content"]

    assert "Transfer Evaluation Office" in transfer_body or "transfercredit@morgan.edu" in transfer_body
    assert "override" in override_body.lower() or "University Advising Center" in override_body or "registrar@morgan.edu" in override_body


def test_chat_fallback_returns_accommodations_process_path(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Accessibility"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "How do I request accommodations at Morgan?"},
    )

    assert response.status_code == 200
    body = response.json()["ai_message"]["content"]
    assert "Accessibility Support Services" in body or "accessibility@morgan.edu" in body


def test_chat_fallback_returns_workflow_entrypoint_for_transcripts_and_withdrawal(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Workflow"}).json()["id"]

    transcript_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What page do I use for transcript requests at Morgan?"},
    )
    withdrawal_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Where is the withdrawal form at Morgan?"},
    )

    assert transcript_response.status_code == 200
    assert withdrawal_response.status_code == 200

    transcript_body = transcript_response.json()["ai_message"]["content"]
    withdrawal_body = withdrawal_response.json()["ai_message"]["content"]

    assert "morgan.edu/transcripts" in transcript_body or "Official Transcript" in transcript_body
    assert "registrar/forms" in withdrawal_body or "Withdrawal/Cancellation Request" in withdrawal_body


def test_chat_fallback_returns_workflow_entrypoint_for_student_orgs_and_research(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "app.chat.generate_ai_reply",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Gemini unavailable")),
    )
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "Workflow"}).json()["id"]

    org_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "What page do I use to form a student organization at Morgan?"},
    )
    research_response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Where should I start if I want undergraduate research at Morgan?"},
    )

    assert org_response.status_code == 200
    assert research_response.status_code == 200

    org_body = org_response.json()["ai_message"]["content"]
    research_body = research_response.json()["ai_message"]["content"]

    assert "forming-a-new-organization" in org_body or "Forming a New Student Organization" in org_body
    assert "undergraduateresearch" in research_body or "Office of Undergraduate Research" in research_body
