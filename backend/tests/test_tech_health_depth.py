from app.rag import get_degree_progress


def test_information_science_prefers_the_inss_progression_before_later_work():
    progress = get_degree_progress("Information Science", ["INSS141", "ENGL101", "ENGL102"])

    assert "INSS201" in progress["recommended_next_courses"]
    assert "INSS340" not in progress["recommended_next_courses"]


def test_cloud_computing_holds_upper_cloud_work_until_foundations_are_ready():
    progress = get_degree_progress("Cloud Computing", ["CLDC101", "COSC111", "ENGL101", "ENGL102"])

    assert "CLDC220" in progress["recommended_next_courses"]
    assert "CLDC340" in progress["blocked_courses"] or "CLDC340" not in progress["recommended_next_courses"]


def test_nursing_keeps_progression_orderly_before_upper_nursing_work():
    progress = get_degree_progress("Nursing", ["NURS101", "BIOL101", "ENGL101", "ENGL102"])

    assert "BIOL102" in progress["recommended_next_courses"]
    assert "NURS301" not in progress["recommended_next_courses"]


def test_biology_requires_foundations_before_upper_biology():
    progress = get_degree_progress("Biology", ["BIOL101", "ENGL101", "ENGL102"])

    assert "BIOL102" in progress["recommended_next_courses"]
    assert "BIOL320" not in progress["recommended_next_courses"]


def test_psychology_prefers_intro_and_methods_before_later_psych_planning():
    progress = get_degree_progress("Psychology", ["PSYC101", "ENGL101", "ENGL102"])

    assert "PSYC210" in progress["recommended_next_courses"] or "STAT302" in progress["recommended_next_courses"]
    assert "PSYC302" not in progress["recommended_next_courses"]
