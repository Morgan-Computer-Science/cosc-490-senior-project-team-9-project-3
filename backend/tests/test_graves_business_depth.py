from app.rag import get_degree_progress


def test_accounting_keeps_upper_accounting_out_until_sequence_is_ready():
    progress = get_degree_progress("Accounting", ["ACCT201", "ENGL101", "ENGL102"])

    assert "ACCT202" in progress["recommended_next_courses"]
    assert "ACCT301" not in progress["recommended_next_courses"]


def test_hospitality_management_uses_shared_business_core_before_upper_direction():
    progress = get_degree_progress("Hospitality Management", ["ENGL101", "ENGL102"])

    assert "ACCT201" in progress["recommended_next_courses"]
    assert "MGMT220" in progress["recommended_next_courses"]


def test_hrm_returns_program_guidance_after_management_foundation():
    progress = get_degree_progress(
        "Human Resource Management",
        ["ACCT201", "ECON201", "MGMT220", "STAT302", "ENGL101", "ENGL102"],
    )

    notes = " ".join(progress.get("program_guidance", []))
    assert "organizational" in notes.lower() or "human resource" in notes.lower()


def test_finance_prefers_accounting_and_economics_before_finance_coursework():
    progress = get_degree_progress("Finance", ["ENGL101", "ENGL102"])

    assert "ACCT201" in progress["recommended_next_courses"]
    assert "ECON201" in progress["recommended_next_courses"]
    assert "FINA300" not in progress["recommended_next_courses"]


def test_finance_unlocks_fina300_after_foundations_are_in_place():
    progress = get_degree_progress(
        "Finance",
        ["ACCT201", "ACCT202", "ECON201", "ECON202", "MGMT220", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "FINA300"
