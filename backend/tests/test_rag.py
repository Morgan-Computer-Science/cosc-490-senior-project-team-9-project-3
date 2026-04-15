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


def test_degree_progress_supports_next_high_impact_programs():
    physics = get_degree_progress("Physics", [])
    philosophy = get_degree_progress("Philosophy", [])
    marketing = get_degree_progress("Marketing", [])

    assert "PHYS201" in physics["required_courses"]
    assert "PHIL201" in philosophy["required_courses"]
    assert "MKTG331" in marketing["required_courses"]


def test_retrieve_relevant_documents_supports_construction_management_queries():
    docs = retrieve_relevant_documents(
        "What construction estimating and scheduling classes should I take next?",
        user_major="Construction Management",
        top_k=5,
    )

    assert docs
    assert any((doc.major or "") == "Construction Management" for doc in docs)


def test_cs_degree_progress_recommends_foundational_next_courses_after_cosc241():
    cs_progress = get_degree_progress("Computer Science", ["COSC111", "COSC241", "MATH141"])

    assert "COSC242" in cs_progress["recommended_next_courses"]
    assert "MATH241" in cs_progress["recommended_next_courses"]
    assert cs_progress["pathway_recommendations"]
    assert any(pathway["pathway"] == "AI and Data" for pathway in cs_progress["pathway_recommendations"])


def test_cs_degree_progress_flags_capstone_as_blocked_without_core_readiness():
    cs_progress = get_degree_progress("Computer Science", ["COSC111", "COSC241", "COSC242"])

    assert "COSC490" in cs_progress["blocked_courses"]
    assert cs_progress["capstone_readiness"]["status"] == "not_ready"
    assert "COSC310" in cs_progress["capstone_readiness"]["missing_foundations"]


def test_retrieve_relevant_documents_supports_cs_ai_pathway_queries():
    docs = retrieve_relevant_documents(
        "I am a Computer Science major interested in AI and machine learning. What classes should I line up next?",
        user_major="Computer Science",
        top_k=6,
    )

    assert docs
    assert any((doc.department or "") == "Computer Science" for doc in docs)


def test_cs_degree_progress_prioritizes_ai_pathway_when_interest_is_explicit():
    cs_progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC241", "COSC242", "MATH141", "MATH241"],
        planning_interest="I am most interested in AI and machine learning.",
    )

    assert cs_progress["pathway_recommendations"]
    assert cs_progress["pathway_recommendations"][0]["pathway"] == "AI and Data"


def test_cs_degree_progress_surfaces_cybersecurity_focus_area():
    cs_progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC241", "COSC242", "MATH141", "MATH241"],
        planning_interest="I want to focus on cybersecurity and secure systems.",
    )

    assert cs_progress["pathway_recommendations"]
    assert cs_progress["pathway_recommendations"][0]["pathway"] == "Cybersecurity"
    assert any(
        course in cs_progress["pathway_recommendations"][0]["recommended_courses"]
        for course in ["COSC360", "COSC459"]
    )


def test_retrieve_relevant_documents_supports_cs_focus_area_faculty_context():
    docs = retrieve_relevant_documents(
        "Who in Morgan Computer Science is most relevant to AI and cloud computing?",
        user_major="Computer Science",
        top_k=8,
    )

    assert docs
    assert any(doc.source_type == "faculty" and (doc.department or "") == "Computer Science" for doc in docs)


def test_cs_degree_progress_surfaces_audit_summary():
    progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC112", "COSC241", "MATH141"],
        planning_interest="I want to know if I am on track for capstone.",
    )

    assert progress["cs_audit_summary"]["capstone_readiness"]["status"] == "not_ready"
    assert "COSC241" in progress["cs_audit_summary"]["core_progress"]["completed"]
