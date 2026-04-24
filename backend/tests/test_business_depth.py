from app.rag import get_degree_progress


def test_business_administration_tracks_shared_core_before_finance_or_strategy():
    progress = get_degree_progress(
        "Business Administration",
        ["ACCT201", "ECON201", "MGMT220", "STAT302", "ENGL101", "ENGL102"],
    )

    assert "MKTG210" in progress["remaining_courses"]
    assert "MGMT330" in progress["remaining_courses"]
    assert "FINA300" not in progress["recommended_next_courses"]


def test_marketing_prioritizes_mktg210_before_supporting_courses():
    progress = get_degree_progress(
        "Marketing",
        ["ACCT201", "ECON201", "MGMT220", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "MKTG210"


def test_marketing_prioritizes_mktg331_once_transition_course_is_done():
    progress = get_degree_progress(
        "Marketing",
        ["ACCT201", "ECON201", "ECON202", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "MKTG331"


def test_business_progress_returns_program_specific_guidance_notes():
    progress = get_degree_progress(
        "Business Administration",
        ["ACCT201", "ACCT202", "ECON201", "ECON202", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    notes = " ".join(progress.get("program_guidance", []))
    assert "shared business core" in notes.lower()


def test_marketing_progress_highlights_transition_into_upper_level_marketing():
    progress = get_degree_progress(
        "Marketing",
        ["ACCT201", "ECON201", "ECON202", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    notes = " ".join(progress.get("program_guidance", []))
    assert "upper-level marketing" in notes.lower()
    assert progress["recommended_next_courses"][0] == "MKTG331"


def test_entrepreneurship_progress_highlights_venture_readiness_when_foundations_exist():
    progress = get_degree_progress(
        "Entrepreneurship",
        ["ACCT201", "ECON201", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    notes = " ".join(progress.get("program_guidance", []))
    assert "venture" in notes.lower()
    assert "ENTR300" in progress["recommended_next_courses"]
