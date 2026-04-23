import pytest

from app.rag import (
    classify_question_intent,
    extract_attachment_course_signals,
    get_degree_progress,
    load_department_rows,
    load_program_rows,
    retrieve_relevant_documents,
)


def test_priority_programs_have_clean_program_and_department_grounding():
    rows = load_program_rows()
    expected_programs = {
        "Elementary Education",
        "Accounting",
        "Finance",
        "Business Administration",
        "Marketing",
        "Biology",
        "Psychology",
        "Nursing",
        "Computer Science",
        "Information Science",
        "Cloud Computing",
    }
    canonical_names = {row["canonical_major"] for row in rows}
    assert expected_programs.issubset(canonical_names)

    department_rows = load_department_rows()
    assert any("Criminal Justice" in row.get("major", "") for row in department_rows)


@pytest.mark.parametrize(
    "major_name,expected_required_codes",
    [
        ("Criminal Justice", {"CRJU101"}),
        ("Elementary Education", {"EDUC320"}),
        ("Accounting", {"ACCT201", "ACCT202"}),
        ("Finance", {"FINA300"}),
        ("Biology", {"BIOL101"}),
        ("Psychology", {"PSYC101"}),
        ("Nursing", {"NURS101"}),
    ],
)
def test_degree_progress_has_major_specific_remaining_courses(major_name, expected_required_codes):
    progress = get_degree_progress(major_name, [])
    remaining = set(progress["remaining_courses"])
    assert expected_required_codes & remaining


@pytest.mark.parametrize(
    "question,expected_text",
    [
        ("Who should I contact about Nursing?", "nursingdept@morgan.edu"),
        ("What department handles Biology?", "Department of Biology"),
        ("Who should I contact about Criminal Justice?", "443-885-3518"),
        ("What department is Elementary Education in?", "Teacher Education and Professional Development"),
    ],
)
def test_retrieval_has_major_contact_grounding(question, expected_text):
    docs = retrieve_relevant_documents(question, top_k=6)
    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert expected_text in joined


def test_entity_queries_have_structured_morgan_grounding():
    docs = retrieve_relevant_documents(
        "Who is the dean of Computer Science at Morgan State University?",
        user_major="Nursing",
        top_k=6,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "Dean" in joined
    assert "Computer Science" in joined


def test_office_queries_prefer_support_offices():
    docs = retrieve_relevant_documents(
        "What office handles transfer advising?",
        top_k=6,
    )

    assert any(doc.source_type in {"office", "support_resource"} for doc in docs)


def test_organization_queries_return_supported_team_or_contact_context():
    docs = retrieve_relevant_documents(
        "Who is in charge of the robotics team at Morgan?",
        top_k=6,
    )

    assert docs
    assert any(doc.source_type in {"organization", "faculty", "department"} for doc in docs[:4])


def test_retrieval_supports_undergraduate_research_contact_queries():
    docs = retrieve_relevant_documents(
        "Who should I contact about undergraduate research in Computer Science?",
        top_k=6,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "Computer Science" in joined
    assert "undergraduate" in joined.lower() or "research" in joined.lower()


def test_retrieval_supports_tutoring_and_accessibility_questions():
    tutoring_docs = retrieve_relevant_documents("What office helps with tutoring?", top_k=6)
    accessibility_docs = retrieve_relevant_documents(
        "Who helps with accessibility accommodations?",
        top_k=6,
    )

    tutoring_joined = "\n".join(f"{doc.title} {doc.content}" for doc in tutoring_docs)
    accessibility_joined = "\n".join(f"{doc.title} {doc.content}" for doc in accessibility_docs)

    assert "Academic Success" in tutoring_joined or "tutoring" in tutoring_joined.lower()
    assert "accessibility" in accessibility_joined.lower()


def test_retrieval_supports_robotics_and_lab_adjacent_queries():
    docs = retrieve_relevant_documents(
        "Is there a robotics or AI lab contact at Morgan?",
        top_k=6,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "robotics" in joined.lower() or "artificial intelligence" in joined.lower() or "Computer Science" in joined


def test_retrieval_supports_student_organizations_and_get_involved_queries():
    docs = retrieve_relevant_documents(
        "How do I get involved in student organizations at Morgan?",
        top_k=6,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "Student Life" in joined or "student organizations" in joined.lower()


def test_retrieval_surfaces_named_ai_and_robotics_labs():
    docs = retrieve_relevant_documents(
        "Is there a robotics or AI lab at Morgan State University?",
        top_k=8,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "RAIN" in joined or "MINDS" in joined or "CEAMLS" in joined


def test_retrieval_supports_internship_and_career_questions():
    docs = retrieve_relevant_documents(
        "Where do I go for internships and career help at Morgan?",
        top_k=8,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "Handshake" in joined or "Career Development" in joined or "internship" in joined.lower()


def test_retrieval_supports_scholarship_and_funding_questions():
    docs = retrieve_relevant_documents(
        "Where should I start for scholarships or research funding at Morgan?",
        top_k=8,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "ScholarshipUniverse" in joined or "CreativeEdge" in joined or "Financial Aid" in joined


def test_retrieval_supports_student_success_questions():
    docs = retrieve_relevant_documents(
        "Who helps if I am struggling academically and need support?",
        top_k=8,
    )

    joined = "\n".join(f"{doc.title} {doc.content}" for doc in docs)
    assert "Student Success" in joined or "CASA" in joined or "tutoring" in joined.lower()


def test_retrieval_supports_registrar_and_process_questions():
    transcript_docs = retrieve_relevant_documents(
        "How do I get my transcript from Morgan?",
        top_k=8,
    )
    withdrawal_docs = retrieve_relevant_documents(
        "How do I withdraw from a class at Morgan?",
        top_k=8,
    )

    transcript_joined = "\n".join(f"{doc.title} {doc.content}" for doc in transcript_docs)
    withdrawal_joined = "\n".join(f"{doc.title} {doc.content}" for doc in withdrawal_docs)

    assert "Registrar" in transcript_joined or "transcript" in transcript_joined.lower()
    assert "withdraw" in withdrawal_joined.lower() or "Registrar" in withdrawal_joined


def test_retrieval_supports_transfer_override_and_accommodations_processes():
    transfer_docs = retrieve_relevant_documents(
        "Who handles transfer credit evaluation at Morgan?",
        top_k=8,
    )
    override_docs = retrieve_relevant_documents(
        "Who do I contact for a registration override?",
        top_k=8,
    )
    accommodations_docs = retrieve_relevant_documents(
        "How do I request accommodations at Morgan?",
        top_k=8,
    )

    transfer_joined = "\n".join(f"{doc.title} {doc.content}" for doc in transfer_docs)
    override_joined = "\n".join(f"{doc.title} {doc.content}" for doc in override_docs)
    accommodations_joined = "\n".join(f"{doc.title} {doc.content}" for doc in accommodations_docs)

    assert "Transfer Evaluation" in transfer_joined or "transfercredit@morgan.edu" in transfer_joined
    assert "override" in override_joined.lower() or "Registrar" in override_joined or "University Advising" in override_joined
    assert "accessibility" in accommodations_joined.lower()


def test_retrieval_supports_workflow_entrypoint_questions():
    transcript_docs = retrieve_relevant_documents(
        "What page do I use for transcript requests at Morgan?",
        top_k=8,
    )
    withdrawal_docs = retrieve_relevant_documents(
        "Where is the withdrawal form at Morgan?",
        top_k=8,
    )
    organization_docs = retrieve_relevant_documents(
        "What page do I use to form a student organization at Morgan?",
        top_k=8,
    )

    transcript_joined = "\n".join(f"{doc.title} {doc.content}" for doc in transcript_docs)
    withdrawal_joined = "\n".join(f"{doc.title} {doc.content}" for doc in withdrawal_docs)
    organization_joined = "\n".join(f"{doc.title} {doc.content}" for doc in organization_docs)

    assert "Transcripts" in transcript_joined or "Official Transcript" in transcript_joined
    assert "Service Request Forms" in withdrawal_joined or "withdrawal" in withdrawal_joined.lower()
    assert "Forming a New Student Organization" in organization_joined or "new student organization" in organization_joined.lower()


def test_retrieval_supports_research_and_accessibility_entrypoint_questions():
    accommodations_docs = retrieve_relevant_documents(
        "Where do I start the accommodations process at Morgan?",
        top_k=8,
    )
    research_docs = retrieve_relevant_documents(
        "Where should I start if I want undergraduate research at Morgan?",
        top_k=8,
    )

    accommodations_joined = "\n".join(f"{doc.title} {doc.content}" for doc in accommodations_docs)
    research_joined = "\n".join(f"{doc.title} {doc.content}" for doc in research_docs)

    assert "Student Disability Support Services" in accommodations_joined or "sdss" in accommodations_joined.lower()
    assert "Office of Undergraduate Research" in research_joined or "undergraduate research" in research_joined.lower()


@pytest.mark.parametrize(
    "question,expected_intent",
    [
        ("What should I take next?", "degree_planning"),
        ("What do I need before COSC242?", "course_prerequisite"),
        ("Who is the dean of Computer Science?", "people_contact_leadership"),
        ("What office handles transfer advising?", "office_resource"),
        ("How do I withdraw from a class?", "policy_process"),
        ("What page do I use for transcript requests?", "workflow_entrypoint"),
        ("Who runs the robotics team?", "organization_team"),
        ("What is my GPA?", "transcript_import"),
        ("How are you?", "small_talk"),
    ],
)
def test_classify_question_intent(question, expected_intent):
    assert classify_question_intent(question) == expected_intent


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


def test_cs_degree_progress_does_not_recommend_math141_after_higher_math_completion():
    progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC112", "COSC241", "MATH241", "MATH242"],
        planning_interest="What should I take next for Computer Science?",
    )

    assert "MATH141" not in progress["recommended_next_courses"]
    assert "MATH141" not in progress["remaining_courses"]


def test_marketing_student_with_foundations_gets_upper_level_marketing_next():
    progress = get_degree_progress(
        "Marketing",
        ["ACCT201", "ECON201", "ECON202", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "MKTG331"
    assert "MKTG210" not in progress["remaining_courses"]

def test_accounting_student_keeps_intermediate_work_blocked_until_lower_sequence_is_complete():
    progress = get_degree_progress(
        "Accounting",
        ["ACCT201", "ECON201", "STAT302", "ENGL101", "ENGL102"],
    )

    assert "ACCT202" in progress["recommended_next_courses"]
    assert "ACCT301" in progress["blocked_courses"]


def test_finance_student_with_foundations_gets_fina300_next():
    progress = get_degree_progress(
        "Finance",
        ["ACCT201", "ACCT202", "ECON201", "ECON202", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "FINA300"
    assert any("finance" in note.lower() for note in progress.get("program_guidance", []))

def test_retrieve_relevant_documents_prefers_major_docs_for_hrm_questions():
    docs = retrieve_relevant_documents(
        "What should I take next for HRM?",
        user_major="Human Resource Management",
    )

    titles = [doc.title for doc in docs[:3]]
    assert any("Human Resource Management" in title for title in titles)


def test_retrieve_relevant_documents_prefers_information_science_docs_for_short_query():
    docs = retrieve_relevant_documents(
        "What should I take next?",
        user_major="Information Science",
    )

    assert any("Information Science" in doc.title for doc in docs[:3])


def test_retrieve_relevant_documents_prefers_psychology_docs_for_short_query():
    docs = retrieve_relevant_documents(
        "What should I take next?",
        user_major="Psychology",
    )

    assert any("Psychology" in doc.title for doc in docs[:3])


def test_retrieve_relevant_documents_respects_explicit_cross_major_question_context():
    docs = retrieve_relevant_documents(
        "Who is the Dean of Computer Science at Morgan State University?",
        user_major="Nursing",
        top_k=6,
    )

    top_docs = docs[:4]
    assert any(doc.source_type == "faculty" for doc in top_docs)
    assert any(
        (doc.department or "") == "Computer Science"
        and any(token in doc.title.lower() for token in ("chair", "director"))
        for doc in top_docs
    )
    assert all("Nursing" not in doc.title for doc in top_docs)
