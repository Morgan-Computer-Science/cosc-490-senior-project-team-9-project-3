from app.rag import extract_attachment_course_signals, get_degree_progress, retrieve_relevant_documents


def test_retrieve_relevant_documents_supports_cloud_computing_queries():
    docs = retrieve_relevant_documents(
        "Help me plan cloud infrastructure and DevOps courses.",
        user_major="Cloud Computing",
        top_k=5,
    )

    assert docs
    assert any(
        (doc.major or "") == "Cloud Computing" or (doc.department or "") == "Cloud Computing"
        for doc in docs
    )


def test_retrieve_relevant_documents_supports_architecture_queries():
    docs = retrieve_relevant_documents(
        "What studio and building systems classes should I take next for architecture?",
        user_major="Architecture",
        top_k=5,
    )

    assert docs
    assert any(
        (doc.major or "") == "Architecture" or (doc.department or "") == "Architecture"
        for doc in docs
    )


def test_degree_audit_signal_extraction_recognizes_grades_and_ip_status():
    text = (
        "Major in Computer Science IN-PROGRESS\n"
        "Introduction to Computer Science II COSC 112 INTRO TO COMPUTER SCIENCE II A 4 SPRING 2021\n"
        "Computer Systems & Digital Logic COSC 241 COMPUTER SYSTEMS & DIG LOGIC A 3 SPRING 2025\n"
        "Database Design COSC 459 DATABASE DESIGN IP (3) SPRING 2026\n"
        "Senior Project COSC 490 SENIOR PROJECT IP (3) SPRING 2026\n"
    )

    signals = extract_attachment_course_signals(text, "degree_audit", limit=20)

    assert "COSC241" in signals.completed_codes
    assert "COSC459" in signals.planned_codes
    assert "COSC490" in signals.planned_codes
    assert "COSC241" not in signals.planned_codes
    assert "COSC459" not in signals.completed_codes
    assert "COSC490" not in signals.completed_codes


def test_retrieve_relevant_documents_supports_actuarial_science_queries():
    docs = retrieve_relevant_documents(
        "What should I know about the actuarial science program and advising path?",
        user_major="Actuarial Science",
        top_k=5,
    )

    assert docs
    assert any((doc.major or "") == "Actuarial Science" for doc in docs)


def test_degree_progress_supports_official_program_aliases():
    architecture = get_degree_progress("Architecture and Environmental Design", [])
    electrical = get_degree_progress("Electrical and Computer Engineering", [])
    business = get_degree_progress("Management and Business Administration", [])

    assert architecture["required_courses"]
    assert electrical["required_courses"]
    assert business["required_courses"]


def test_degree_progress_supports_official_actuarial_science_requirements():
    actuarial = get_degree_progress("Actuarial Science", [])

    assert "MATH331" in actuarial["required_courses"]
    assert "MATH363" in actuarial["required_courses"]
    assert actuarial["advising_tips"]


def test_degree_progress_supports_additional_official_programs():
    economics = get_degree_progress("Economics", [])
    chemistry = get_degree_progress("Chemistry", [])
    political_science = get_degree_progress("Political Science", [])

    assert "ECON301" in economics["required_courses"]
    assert "CHEM201" in chemistry["required_courses"]
    assert "POSC101" in political_science["required_courses"]
