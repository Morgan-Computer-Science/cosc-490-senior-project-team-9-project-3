from app.cs_audit import interpret_computer_science_audit


def test_interpret_cs_audit_groups_foundations_core_and_capstone():
    summary = interpret_computer_science_audit(
        completed_codes=["COSC111", "COSC112", "COSC241", "MATH141", "MATH241"],
        in_progress_codes=["COSC242"],
        remaining_codes=["COSC310", "COSC331", "COSC332", "COSC350", "COSC490"],
        planning_interest="I want to know if I am ready for capstone.",
    )

    assert summary["foundations"]["completed"] == ["COSC111", "COSC112"]
    assert "COSC241" in summary["core_progress"]["completed"]
    assert "COSC242" in summary["core_progress"]["in_progress"]
    assert summary["capstone_readiness"]["status"] == "not_ready"
    assert "COSC310" in summary["capstone_readiness"]["missing_foundations"]


def test_interpret_cs_audit_infers_ai_direction_from_upper_level_work():
    summary = interpret_computer_science_audit(
        completed_codes=["COSC111", "COSC112", "COSC241", "COSC242", "MATH141", "MATH241", "STAT302"],
        in_progress_codes=["COSC470"],
        remaining_codes=["COSC490"],
        planning_interest="I want to go into AI and data science.",
    )

    assert summary["pathway_direction"]["primary_pathway"] == "AI and Data"
    assert "COSC470" in summary["pathway_direction"]["aligned_courses"]


def test_interpret_cs_audit_preserves_unknown_cs_codes():
    summary = interpret_computer_science_audit(
        completed_codes=["COSC111", "COSC241", "COSC499"],
        in_progress_codes=[],
        remaining_codes=["COSC490"],
        planning_interest=None,
    )

    assert "COSC499" in summary["unmapped_courses"]
