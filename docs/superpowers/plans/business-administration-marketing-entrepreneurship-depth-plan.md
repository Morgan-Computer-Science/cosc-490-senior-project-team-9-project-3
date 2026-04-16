# Business Administration + Marketing + Entrepreneurship Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen Morgan State advising for Business Administration, Marketing, and Entrepreneurship by adding shared business-core sequencing and program-specific recommendation logic.

**Architecture:** Extend the existing backend planning engine with a business-specific planning layer that activates for the Department of Business Administration programs. Keep the current CSV-backed data model, add focused business-planning rule data if needed, and feed the richer recommendations into degree progress and chat context without changing the frontend structure.

**Tech Stack:** Python, FastAPI, CSV-backed catalog data, pytest

---

## File Map

### Likely modify
- `backend/app/rag.py` — add shared business-core sequencing, business-program-specific recommendation logic, and chat-facing planning context
- `backend/app/chat.py` — expose richer business planning context to live/fallback advising responses
- `backend/app/schemas.py` — extend structured outputs only if the new business planning fields need explicit schema support
- `backend/data/degree_requirements.csv` — tighten the required-course structure for Business Administration, Marketing, and Entrepreneurship where the current data is too shallow
- `backend/data/prerequisites.csv` — add or correct prerequisite relationships that materially affect sequencing
- `backend/tests/test_rag.py` — add regression tests for business-core sequencing and program-specific next-course recommendations
- `backend/tests/test_chat.py` — add focused coverage if business-specific context needs verification in the chat layer

### Likely create
- `backend/data/business_pathways.csv` — shared business-core and program-specific planning hints if a dedicated rules file is cleaner than hardcoding all logic in `rag.py`
- `backend/tests/test_business_depth.py` — isolated tests for the new business advising logic

---

### Task 1: Add Business Planning Rule Data

**Files:**
- Create: `backend/data/business_pathways.csv`
- Modify: `backend/data/degree_requirements.csv`
- Modify: `backend/data/prerequisites.csv`
- Test: `backend/tests/test_business_depth.py`

- [ ] **Step 1: Write the failing test**

```python
from app.rag import get_degree_progress


def test_business_administration_prefers_shared_core_before_upper_level_strategy():
    progress = get_degree_progress("Business Administration", ["ENGL101", "ENGL102"])

    assert "ACCT201" in progress["recommended_next_courses"]
    assert "ECON201" in progress["recommended_next_courses"]
    assert "MGMT410" not in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py::test_business_administration_prefers_shared_core_before_upper_level_strategy -v`
Expected: FAIL because the current planner does not yet prioritize a shared business core ahead of upper-level business strategy work.

- [ ] **Step 3: Add minimal planning data**

Create `backend/data/business_pathways.csv` with seed business rules:

```csv
major,stage,focus_area,required_course,priority,notes
Business Administration,core,business_foundation,ACCT201,1,Accounting foundation should come before upper-level management strategy work.
Business Administration,core,business_foundation,ECON201,2,Economics foundation should come before upper-level management strategy work.
Business Administration,core,business_foundation,STAT302,3,Quantitative preparation should precede advanced business decision and strategy work.
Business Administration,upper,management_progression,MGMT330,4,Organizational behavior is a better upper-level next step than strategic management.
Business Administration,upper,management_progression,MGMT410,5,Strategic management should wait until the broader business core is in place.
Marketing,core,business_foundation,ACCT201,1,Marketing students should complete the shared business core first.
Marketing,core,business_foundation,ECON201,2,Marketing students benefit from economics before advanced marketing strategy.
Marketing,core,marketing_progression,MKTG210,3,Principles of Marketing is the main transition into upper-level marketing.
Marketing,upper,marketing_progression,MKTG331,4,Marketing Management should follow MKTG210 plus enough business-core context.
Entrepreneurship,core,business_foundation,ACCT201,1,Entrepreneurship students need accounting context before venture-heavy planning.
Entrepreneurship,core,business_foundation,ECON201,2,Entrepreneurship students need economics context before venture-heavy planning.
Entrepreneurship,core,business_foundation,MGMT220,3,Management foundations support later venture design and strategy work.
Entrepreneurship,upper,venture_progression,ENTR300,4,Venture creation should follow enough business foundation to be useful.
Entrepreneurship,upper,venture_progression,ENTR410,5,Small-business strategy should come after the earlier venture and business core sequence.
```

Tighten business requirements and prerequisites as needed, for example:

```csv
Business Administration,Business Administration,"ACCT201; ACCT202; ECON201; ECON202; MGMT220; MGMT330; MKTG210; FINA300; STAT302; ENGL101; ENGL102","Students build a shared business core before upper-level management and strategy work.","Complete accounting economics and quantitative foundations before strategic management planning."
Marketing,Business Administration,"ACCT201; ECON201; ECON202; MGMT220; MKTG210; MKTG331; STAT302; ENGL101; ENGL102; COMM200","Morgan marketing students move from business fundamentals into marketing strategy and market analysis.","Use MKTG210 as the transition point into upper-level marketing work."
Entrepreneurship,Business Administration,"ACCT201; ECON201; MGMT220; MKTG210; ENTR300; ENTR410; STAT302; ENGL101; ENGL102","Morgan entrepreneurship students combine a shared business core with venture creation and applied strategy.","Build accounting management and marketing context before venture-heavy coursework."
```

```csv
MGMT330,MGMT220,Organizational behavior should follow the lower-division management core.
MGMT410,MGMT330; ACCT201; ECON201,Strategic management should follow the core business progression.
ENTR300,MGMT220; MKTG210,Entrepreneurship and venture creation should follow foundational management and marketing.
ENTR410,ENTR300,Small business strategy should follow earlier venture creation work.
```

- [ ] **Step 4: Run the test to verify it still fails for logic reasons**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py::test_business_administration_prefers_shared_core_before_upper_level_strategy -v`
Expected: FAIL because the new data exists but the planner is not using it yet.

- [ ] **Step 5: Commit**

```bash
git add backend/data/business_pathways.csv backend/data/degree_requirements.csv backend/data/prerequisites.csv backend/tests/test_business_depth.py
git commit -m "Add business planning rule data for Graves programs"
```

### Task 2: Implement Shared Business-Core Sequencing in the Planner

**Files:**
- Modify: `backend/app/rag.py`
- Test: `backend/tests/test_business_depth.py`

- [ ] **Step 1: Write the failing tests**

Append these tests to `backend/tests/test_business_depth.py`:

```python
from app.rag import get_degree_progress


def test_marketing_requires_mktg210_before_marketing_management():
    progress = get_degree_progress("Marketing", ["ACCT201", "ECON201", "MGMT220", "STAT302", "ENGL101", "ENGL102"])

    assert "MKTG210" in progress["recommended_next_courses"]
    assert "MKTG331" not in progress["recommended_next_courses"]


def test_entrepreneurship_waits_for_business_foundation_before_venture_courses():
    progress = get_degree_progress("Entrepreneurship", ["ENGL101", "ENGL102"])

    assert "ACCT201" in progress["recommended_next_courses"]
    assert "ECON201" in progress["recommended_next_courses"]
    assert "ENTR300" not in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py -v`
Expected: FAIL because Marketing and Entrepreneurship are still using generic recommendation ordering.

- [ ] **Step 3: Implement minimal shared business-core logic**

In `backend/app/rag.py`, add a helper shaped like this and call it from `get_degree_progress(...)` before final recommendation ordering:

```python
BUSINESS_DEPTH_MAJORS = {
    "Business Administration",
    "Marketing",
    "Entrepreneurship",
}


def _apply_business_planning_rules(major: str, completed_course_codes: set[str], remaining_course_codes: list[str]) -> tuple[list[str], list[str], list[str]]:
    if major not in BUSINESS_DEPTH_MAJORS:
        return remaining_course_codes, [], []

    core_priority = []
    blocked = []
    guidance = []

    shared_core = ["ACCT201", "ECON201", "MGMT220", "STAT302"]
    for code in shared_core:
        if code in remaining_course_codes:
            core_priority.append(code)

    if major == "Marketing":
        if "MKTG210" in remaining_course_codes:
            core_priority.append("MKTG210")
        if "MKTG210" not in completed_course_codes and "MKTG331" in remaining_course_codes:
            blocked.append("MKTG331")
            guidance.append("Marketing students should complete MKTG210 before moving into upper-level marketing strategy work.")

    if major == "Entrepreneurship":
        if not {"ACCT201", "ECON201", "MGMT220", "MKTG210"}.issubset(completed_course_codes):
            for code in ["ENTR300", "ENTR410"]:
                if code in remaining_course_codes:
                    blocked.append(code)
            guidance.append("Entrepreneurship students should build the shared business core before venture-heavy coursework.")

    if major == "Business Administration":
        if not {"ACCT201", "ECON201", "STAT302", "MGMT220"}.issubset(completed_course_codes):
            for code in ["MGMT330", "MGMT410"]:
                if code in remaining_course_codes:
                    blocked.append(code)
            guidance.append("Business Administration students should complete the shared business core before upper-level management and strategy work.")

    ordered_remaining = [code for code in core_priority if code in remaining_course_codes]
    ordered_remaining.extend(code for code in remaining_course_codes if code not in ordered_remaining)
    return ordered_remaining, blocked, guidance
```

Then merge this into the existing progress payload by:
- prioritizing `ordered_remaining` when calculating `recommended_next_courses`
- appending `blocked` into the returned blocked-course list without dropping existing prerequisite blocking
- exposing `guidance` through an existing notes/guidance field or a new one if needed

- [ ] **Step 4: Run the business-depth tests**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/tests/test_business_depth.py
git commit -m "Add shared business-core sequencing for Graves advising"
```

### Task 3: Add Program-Specific Recommendation Depth and Structured Guidance

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/app/schemas.py`
- Test: `backend/tests/test_business_depth.py`

- [ ] **Step 1: Write the failing tests**

Append these tests:

```python
from app.rag import get_degree_progress


def test_business_progress_returns_program_specific_guidance_notes():
    progress = get_degree_progress("Business Administration", ["ENGL101", "ENGL102"])

    notes = " ".join(progress.get("program_guidance", []))
    assert "shared business core" in notes.lower()


def test_marketing_progress_highlights_transition_into_upper_level_marketing():
    progress = get_degree_progress("Marketing", ["ACCT201", "ECON201", "MGMT220", "STAT302", "MKTG210", "ENGL101", "ENGL102"])

    notes = " ".join(progress.get("program_guidance", []))
    assert "upper-level marketing" in notes.lower()
    assert "MKTG331" in progress["recommended_next_courses"]


def test_entrepreneurship_progress_highlights_venture_readiness_when_foundations_exist():
    progress = get_degree_progress("Entrepreneurship", ["ACCT201", "ECON201", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"])

    notes = " ".join(progress.get("program_guidance", []))
    assert "venture" in notes.lower()
    assert "ENTR300" in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py -v`
Expected: FAIL because `program_guidance` does not exist or lacks these program-specific messages.

- [ ] **Step 3: Implement minimal program-specific guidance output**

Add or extend a schema field in `backend/app/schemas.py`:

```python
program_guidance: list[str] = Field(default_factory=list)
```

Extend the business helper in `backend/app/rag.py` to emit guidance like:

```python
if major == "Business Administration":
    if {"ACCT201", "ECON201", "STAT302", "MGMT220"}.issubset(completed_course_codes):
        guidance.append("Your shared business core is in place, so upper-level management and strategy planning is starting to make sense.")

if major == "Marketing":
    if "MKTG210" in completed_course_codes:
        guidance.append("You have the principles-level marketing foundation needed to start moving into upper-level marketing strategy work.")
    else:
        guidance.append("Marketing students should use MKTG210 as the transition point into upper-level marketing work.")

if major == "Entrepreneurship":
    if {"ACCT201", "ECON201", "MGMT220", "MKTG210"}.issubset(completed_course_codes):
        guidance.append("You now have enough shared business context for venture-focused coursework to be useful and well-timed.")
```

Return that field from `get_degree_progress(...)`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/app/schemas.py backend/tests/test_business_depth.py
git commit -m "Add program-specific guidance for business advising"
```

### Task 4: Feed Business Planning Context into Chat Advising

**Files:**
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Write the failing test**

Add a focused test like this to `backend/tests/test_chat.py`:

```python
def test_chat_context_includes_business_guidance_for_marketing_student(client, auth_headers, monkeypatch):
    def fake_ai_response(*args, **kwargs):
        return "stubbed"

    monkeypatch.setattr("app.chat.generate_advisor_response", fake_ai_response)

    client.put(
        "/auth/me",
        json={"major": "Marketing"},
        headers=auth_headers,
    )

    response = client.post(
        "/chat/sessions",
        headers=auth_headers,
        json={},
    )
    session_id = response.json()["id"]

    send = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        json={"content": "What should I take next for marketing?"},
    )

    assert send.status_code == 200
    assert "Marketing" in send.text or send.json()
```
```

- [ ] **Step 2: Run test to verify it fails for missing business-specific context**

Run: `py -3.12 -m pytest backend/tests/test_chat.py::test_chat_context_includes_business_guidance_for_marketing_student -v`
Expected: FAIL or prove the chat context does not yet explicitly carry the new business guidance.

- [ ] **Step 3: Implement minimal chat-context wiring**

In `backend/app/chat.py`, when building the student progress/advising context, include the new field if present:

```python
if degree_progress.get("program_guidance"):
    advisor_context_sections.append(
        "Business planning guidance: " + " ".join(degree_progress["program_guidance"])
    )
```

If there is already a structured context builder, fold the same string into the relevant section instead of creating a parallel ad hoc path.

- [ ] **Step 4: Run the focused chat test**

Run: `py -3.12 -m pytest backend/tests/test_chat.py::test_chat_context_includes_business_guidance_for_marketing_student -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/chat.py backend/tests/test_chat.py
git commit -m "Use business planning context in chat advising"
```

### Task 5: Full Regression and Data-Slice Verification

**Files:**
- Modify: `backend/tests/test_rag.py`
- Test: `backend/tests/test_business_depth.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Add one broad regression test for overall recommendation quality**

Add to `backend/tests/test_rag.py`:

```python
from app.rag import get_degree_progress


def test_marketing_student_with_foundations_gets_upper_level_marketing_next():
    progress = get_degree_progress(
        "Marketing",
        ["ACCT201", "ECON201", "ECON202", "MGMT220", "MKTG210", "STAT302", "ENGL101", "ENGL102"],
    )

    assert "MKTG331" in progress["recommended_next_courses"]
    assert "MKTG210" not in progress["remaining_courses"]
```

- [ ] **Step 2: Run focused business tests**

Run: `py -3.12 -m pytest backend/tests/test_business_depth.py backend/tests/test_rag.py -v`
Expected: PASS

- [ ] **Step 3: Run chat verification**

Run: `py -3.12 -m pytest backend/tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 4: Run full backend verification**

Run: `py -3.12 -m pytest backend/tests -q`
Expected: PASS for the full suite

Run: `py -3.12 -m compileall backend/app`
Expected: compile success with no syntax errors

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_rag.py backend/tests/test_business_depth.py backend/tests/test_chat.py
git commit -m "Verify business advising depth across planning and chat"
```
