# Graves Business Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen Morgan State advising for Accounting, Finance, Hospitality Management, and Human Resource Management by extending the shared Graves business-core planner and adding weighted program-specific sequencing.

**Architecture:** Extend the existing business-planning layer in the backend so all Graves undergraduate business majors share a coherent lower-division business core, while Accounting and Finance get the deepest sequencing logic. Feed the richer recommendations and guidance into degree progress and chat context without requiring a frontend redesign in this phase.

**Tech Stack:** Python, FastAPI, CSV-backed planning data, pytest

---

## File Map

### Likely modify
- `backend/app/rag.py` — extend the business planner from the current Business Administration family to the broader Graves ecosystem
- `backend/app/chat.py` — expose richer Graves-specific guidance in advising context
- `backend/app/schemas.py` — extend structured outputs only if new Graves guidance fields are needed beyond current business guidance
- `backend/data/degree_requirements.csv` — tighten the required-course structure for Accounting, Finance, Hospitality Management, and Human Resource Management
- `backend/data/prerequisites.csv` — add or correct prerequisite relationships that materially affect sequencing
- `backend/data/business_pathways.csv` — expand the business-planning rules to cover the broader Graves ecosystem
- `backend/tests/test_rag.py` — add regression coverage for Graves majors and sequencing expectations
- `backend/tests/test_chat.py` — add focused Graves chat-context coverage if needed

### Likely create
- `backend/tests/test_graves_business_depth.py` — isolated tests for the new Graves advising logic
- `docs/superpowers/plans/graves-business-depth-plan.md` — this plan document

---

### Task 1: Expand Graves Business Planning Data

**Files:**
- Modify: `backend/data/business_pathways.csv`
- Modify: `backend/data/degree_requirements.csv`
- Modify: `backend/data/prerequisites.csv`
- Create: `backend/tests/test_graves_business_depth.py`

- [ ] **Step 1: Write the failing test**

```python
from app.rag import get_degree_progress


def test_accounting_keeps_upper_accounting_out_until_sequence_is_ready():
    progress = get_degree_progress("Accounting", ["ACCT201", "ENGL101", "ENGL102"])

    assert "ACCT202" in progress["recommended_next_courses"]
    assert "ACCT301" not in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py::test_accounting_keeps_upper_accounting_out_until_sequence_is_ready -v`
Expected: FAIL because the current planner does not yet apply Graves-wide weighted sequencing for Accounting.

- [ ] **Step 3: Add minimal Graves rule data**

Expand `backend/data/business_pathways.csv` with rules like:

```csv
Accounting,core,accounting_foundation,ACCT201,1,Accounting students should begin with Principles of Accounting I.
Accounting,core,accounting_foundation,ACCT202,2,Accounting II should follow the first accounting course before intermediate work.
Accounting,upper,accounting_progression,ACCT301,3,Intermediate Accounting I should wait until the lower accounting sequence is complete.
Accounting,upper,accounting_progression,ACCT302,4,Intermediate Accounting II should follow Intermediate Accounting I.
Finance,core,finance_foundation,ACCT201,1,Finance students should build accounting literacy before finance-heavy work.
Finance,core,finance_foundation,ECON201,2,Finance students should build economics foundations early.
Finance,core,finance_foundation,ECON202,3,Finance students should complete the introductory economics sequence.
Finance,upper,finance_progression,FINA300,4,Corporate finance should follow accounting and economics foundations.
Hospitality Management,core,hospitality_foundation,ACCT201,1,Hospitality students benefit from the shared business core before upper-level operations planning.
Hospitality Management,core,hospitality_foundation,MGMT220,2,Management foundations should come before upper-level hospitality planning.
Human Resource Management,core,hrm_foundation,MGMT220,1,HRM students need management foundations before upper-level organizational work.
Human Resource Management,core,hrm_foundation,ACCT201,2,HRM students still benefit from shared business literacy in the Graves core.
```

Tighten degree requirements if needed, for example:

```csv
Accounting,Accounting,"ACCT201; ACCT202; ACCT301; ACCT302; ECON201; ECON202; STAT302; MGMT220; ENGL101; ENGL102","Accounting students should complete the business and quantitative core early to stay ready for internship and CPA-oriented planning.","Move through accounting and economics in sequence and use junior-year advising to plan for internships public accounting or corporate finance roles."
Finance,Accounting and Finance,"ACCT201; ACCT202; ECON201; ECON202; FINA300; MGMT220; MKTG210; STAT302; ENGL101; ENGL102","Finance at Morgan builds on accounting economics and quantitative reasoning with strong career preparation in corporate and investment settings.","Finish accounting and economics first so finance planning is grounded in the full lower-division business core."
Hospitality Management,Business Administration,"ACCT201; ECON201; MGMT220; MKTG210; STAT302; ENGL101; ENGL102; COMM200","Hospitality Management students combine a shared business core with service operations and leadership preparation.","Build the business core first so upper-level hospitality planning has enough operational context."
Human Resource Management,Business Administration,"ACCT201; ECON201; MGMT220; MGMT330; STAT302; ENGL101; ENGL102; COMM200","Human Resource Management students combine shared business preparation with organizational behavior and people-management direction.","Use the lower-division business and management core as the base for later HR-focused planning."
```

Add or tighten prerequisites such as:

```csv
ACCT301,ACCT202,Intermediate Accounting I should follow the lower accounting sequence.
ACCT302,ACCT301,Intermediate Accounting II should follow Intermediate Accounting I.
FINA300,ACCT201; ECON201,Finance is stronger after accounting and economics.
MGMT330,MGMT220,Organizational behavior should follow the lower-division management core.
```

- [ ] **Step 4: Run the test to verify it still fails for logic reasons**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py::test_accounting_keeps_upper_accounting_out_until_sequence_is_ready -v`
Expected: FAIL because the new data exists but the planner is not using it yet.

- [ ] **Step 5: Commit**

```bash
git add backend/data/business_pathways.csv backend/data/degree_requirements.csv backend/data/prerequisites.csv backend/tests/test_graves_business_depth.py
git commit -m "Expand Graves business planning data"
```

### Task 2: Add Weighted Graves Sequencing for Accounting and Finance

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/tests/test_graves_business_depth.py`

- [ ] **Step 1: Write the failing tests**

Append these tests:

```python
from app.rag import get_degree_progress


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py -v`
Expected: FAIL because the current business planner does not yet weight Accounting and Finance sequencing appropriately.

- [ ] **Step 3: Implement minimal Graves sequencing logic**

In `backend/app/rag.py`, extend the current business-major detection and priority map so it covers:
- `Accounting`
- `Finance`
- `Hospitality Management`
- `Human Resource Management`

Add a helper that emits weighted guidance for high-depth majors, shaped like:

```python
def _is_graves_business_major(major: Optional[str]) -> bool:
    return _normalize(major) in {
        "Business Administration",
        "Marketing",
        "Entrepreneurship",
        "Accounting",
        "Finance",
        "Hospitality Management",
        "Human Resource Management",
    }
```

Then extend the planner so:
- Accounting sorts `ACCT201 -> ACCT202 -> ACCT301 -> ACCT302`
- Finance sorts `ACCT201 / ECON201 / ECON202` ahead of `FINA300`
- blocked courses still respect the prerequisite map
- recommendations stay capped to a small next-step list

- [ ] **Step 4: Run the Graves business tests**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/tests/test_graves_business_depth.py
git commit -m "Add weighted Graves sequencing for accounting and finance"
```

### Task 3: Add Lighter Hospitality and HRM Guidance

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/tests/test_graves_business_depth.py`

- [ ] **Step 1: Write the failing tests**

Append these tests:

```python
from app.rag import get_degree_progress


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py -v`
Expected: FAIL because Hospitality and HRM are not yet using Graves-specific sequencing/guidance.

- [ ] **Step 3: Implement minimal Hospitality and HRM guidance**

Extend the Graves guidance helper in `backend/app/rag.py` so it emits lighter-but-real messaging such as:

```python
if normalized_major == "Hospitality Management":
    guidance.append(
        "Hospitality Management works best after the shared business core is underway, so operations and service-focused planning stays grounded in business fundamentals."
    )

if normalized_major == "Human Resource Management":
    guidance.append(
        "Human Resource Management builds on management and organizational foundations, so lower-division business preparation should lead into upper-level people and organizational planning."
    )
```

If needed, keep using the existing `program_guidance` list in `backend/app/schemas.py`. Only modify the schema if a new structured field is absolutely necessary.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/app/schemas.py backend/tests/test_graves_business_depth.py
git commit -m "Add hospitality and HRM Graves guidance"
```

### Task 4: Feed Graves Business Guidance into Chat

**Files:**
- Modify: `backend/app/chat.py`
- Modify: `backend/tests/test_chat.py`

- [ ] **Step 1: Write the failing test**

Add a focused test like this to `backend/tests/test_chat.py`:

```python
def test_chat_context_includes_graves_guidance_for_finance_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put("/auth/me", headers=auth_headers, json={"major": "Finance"})
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["ACCT201", "ECON201", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Finance Path"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next for finance?"},
    )

    assert response.status_code == 200
    assert "Business planning guidance:" in captured_context["extra_context"]
```

- [ ] **Step 2: Run test to verify it fails or proves missing context**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_chat.py::test_chat_context_includes_graves_guidance_for_finance_student -v`
Expected: FAIL or prove Finance is not yet receiving Graves-specific chat context.

- [ ] **Step 3: Implement minimal chat-context support**

Reuse the existing business-guidance context path in `backend/app/chat.py` and ensure the broader Graves majors flow through it. If the context builder already emits `Business planning guidance`, confirm it is fed by the expanded Graves guidance and does not require a separate parallel path.

- [ ] **Step 4: Run the focused chat test**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_chat.py::test_chat_context_includes_graves_guidance_for_finance_student -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/chat.py backend/tests/test_chat.py
git commit -m "Use Graves business guidance in chat advising"
```

### Task 5: Full Regression and Verification

**Files:**
- Modify: `backend/tests/test_rag.py`
- Test: `backend/tests/test_graves_business_depth.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Add one broad regression test for Graves recommendation quality**

Add to `backend/tests/test_rag.py`:

```python
from app.rag import get_degree_progress


def test_accounting_student_with_lower_sequence_gets_intermediate_accounting_next():
    progress = get_degree_progress(
        "Accounting",
        ["ACCT201", "ACCT202", "ECON201", "ECON202", "MGMT220", "STAT302", "ENGL101", "ENGL102"],
    )

    assert progress["recommended_next_courses"][0] == "ACCT301"
```

- [ ] **Step 2: Run focused Graves tests**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_graves_business_depth.py backend/tests/test_rag.py -v`
Expected: PASS

- [ ] **Step 3: Run chat verification**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 4: Run full backend verification**

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m pytest backend/tests -q`
Expected: PASS for the full suite

Run: `& '.\\backend\\.venv\\Scripts\\python.exe' -m compileall backend/app`
Expected: compile success with no syntax errors

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_rag.py backend/tests/test_graves_business_depth.py backend/tests/test_chat.py
git commit -m "Verify Graves business advising depth"
```
