# Morgan Entities Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen the Morgan entity layer so the advisor answers people, office, organization, robotics, lab, and research-contact questions with more specific and better grounded Morgan responses.

**Architecture:** Extend the current entity-aware retrieval system by adding richer office, organization, and faculty coverage while preserving the lightweight intent-routing model already in place.

**Tech Stack:** Python, FastAPI, CSV-backed Morgan datasets, pytest

---

## File Structure

### Existing files to modify
- `backend/app/rag.py`
  - Tune retrieval scoring for deeper office/org/lab/research coverage.
- `backend/app/chat.py`
  - Strengthen fallback phrasing where the closest official path is more useful than a generic answer.
- `backend/data/offices.csv`
  - Add more official office and support paths.
- `backend/data/organizations.csv`
  - Add more supported org, robotics, and lab-adjacent contact routes.
- `backend/data/faculty.csv`
  - Add public-facing faculty or leadership contacts where they improve retrieval.
- `backend/tests/test_rag.py`
  - Add retrieval regressions for deeper entity questions.
- `backend/tests/test_chat.py`
  - Add fallback regressions for deeper office and organization questions.

### New files to add
- None required beyond the doc files for this pass.

## Task 1: Add the missing spec/plan docs and baseline tests

**Files:**
- Add: `docs/superpowers/specs/morgan-entities-depth-design.md`
- Add: `docs/superpowers/plans/morgan-entities-depth-plan.md`
- Modify: `backend/tests/test_rag.py`
- Modify: `backend/tests/test_chat.py`

- [ ] **Step 1: Write the missing design and plan docs to the repo**

- [ ] **Step 2: Add failing retrieval tests for deeper entity questions**

Examples:

```python
def test_retrieval_supports_undergraduate_research_contact_queries():
    docs = retrieve_relevant_documents(
        "Who should I contact about undergraduate research in Computer Science?",
        top_k=6,
    )
    assert docs


def test_retrieval_supports_tutoring_and_accessibility_questions():
    tutoring_docs = retrieve_relevant_documents("What office helps with tutoring?", top_k=6)
    accessibility_docs = retrieve_relevant_documents("Who helps with accessibility accommodations?", top_k=6)
    assert tutoring_docs
    assert accessibility_docs


def test_retrieval_supports_robotics_and_lab_adjacent_queries():
    docs = retrieve_relevant_documents(
        "Is there a robotics or AI lab contact at Morgan?",
        top_k=6,
    )
    assert docs
```

- [ ] **Step 3: Add failing fallback tests for office and org/lab questions**

Examples:

```python
def test_chat_fallback_returns_tutoring_contact_path(...):
    ...


def test_chat_fallback_returns_research_or_robotics_support_path(...):
    ...
```

## Task 2: Expand office and support-path coverage

**Files:**
- Modify: `backend/data/offices.csv`
- Modify: `backend/data/support_resources.csv`

- [ ] **Step 1: Add more official office paths**

Priority additions:
- tutoring / academic success
- accessibility accommodations
- career / internship support
- financial aid / registrar-adjacent support
- advising center / student support routes

- [ ] **Step 2: Keep fields consistent and contact-first**

Each row should preserve:
- office name
- category
- email or phone where possible
- location if known
- concise Morgan-specific overview
- source URL

## Task 3: Expand organization, robotics, and lab-adjacent coverage

**Files:**
- Modify: `backend/data/organizations.csv`
- Modify if useful: `backend/data/faculty.csv`
- Modify if useful: `backend/data/departments.csv`

- [ ] **Step 1: Add more supported organization and team-adjacent paths**

Priority additions:
- robotics support path
- research or lab-adjacent support paths
- department-supported student-community paths

- [ ] **Step 2: Add faculty or department contacts where they make those paths better**

Do this only where the contact path is defensible and public-facing.

- [ ] **Step 3: Prefer nearest official routes over invented exact leads**

If a specific “team lead” or “lab director” is not publicly grounded, point to:
- the department chair
- undergraduate studies director
- department office
- nearest official program contact

## Task 4: Tune retrieval and fallback behavior for the richer entity layer

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/app/chat.py`

- [ ] **Step 1: Tune retrieval scoring for deeper entity coverage**

Make sure questions about:
- tutoring
- accessibility
- internships
- research
- robotics
- labs

prefer the most relevant offices, organizations, departments, and faculty.

- [ ] **Step 2: Tune fallback phrasing**

Fallback should:
- answer directly when possible
- otherwise give the nearest supported Morgan contact path
- avoid generic advising language for clearly non-degree-planning questions

## Task 5: Verify the slice end to end

**Files:**
- No new files required unless implementation differences need doc updates

- [ ] **Step 1: Run targeted retrieval and fallback tests**

Run:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py backend/tests/test_chat.py -k "research or tutoring or accessibility or robotics or leadership or office" -q
```

- [ ] **Step 2: Run the broader backend suite**

Run:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
```

- [ ] **Step 3: Summarize what entity questions are now materially stronger**

Examples:
- robotics / research
- tutoring / accessibility
- transfer / registrar / advising
- leadership / chair / dean
