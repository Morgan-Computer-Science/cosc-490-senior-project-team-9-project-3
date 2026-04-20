# Morgan Entities and Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen the Morgan advisor so it can answer people, leadership, office, and organization questions with more specific Morgan grounding while routing degree-planning, transcript, and small-talk questions to the correct retrieval path.

**Architecture:** Extend the current CSV-backed Morgan data layer with structured entities and contact sources, then add lightweight question-type routing ahead of retrieval scoring. Keep the existing FastAPI, SQLAlchemy, and retrieval architecture intact while making retrieval source-aware and intent-aware.

**Tech Stack:** Python, FastAPI, SQLAlchemy, SQLite, CSV-backed data files, pytest, React/Vite (verification only unless rendering changes are needed later)

---

## File Structure

### Existing files to modify
- `backend/app/rag.py`
  - Add question-type routing and intent-aware retrieval source preference.
- `backend/app/chat.py`
  - Ensure chat uses routed retrieval behavior cleanly and formats stronger fallback responses.
- `backend/data/faculty.csv`
  - Expand leadership and advisor grounding where needed.
- `backend/data/departments.csv`
  - Ensure department contact paths are strong enough for entity questions.
- `backend/data/support_resources.csv`
  - Extend support-office and resource coverage where relevant.
- `backend/tests/test_rag.py`
  - Add routing and entity retrieval regressions.
- `backend/tests/test_chat.py`
  - Add chat-level regressions for people/contact/team questions.

### New files likely to add
- `backend/data/offices.csv`
  - Structured support offices, advising offices, registrar-adjacent offices, and tutoring/contact routes.
- `backend/data/organizations.csv`
  - Selected Morgan student organizations and teams with officially supported contact/page grounding.
- `backend/data/leadership.csv`
  - Optional dedicated leadership dataset if this is cleaner than overloading faculty rows.

## Task 1: Add structured Morgan entity datasets

**Files:**
- Add: `backend/data/offices.csv`
- Add: `backend/data/organizations.csv`
- Optional add: `backend/data/leadership.csv`
- Modify: `backend/data/faculty.csv`
- Modify: `backend/data/departments.csv`
- Test: `backend/tests/test_rag.py`

- [ ] **Step 1: Write the failing retrieval tests for entities and contacts**

```python
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
```

- [ ] **Step 2: Run the targeted tests to expose current gaps**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k "entity_queries or office_queries or organization_queries" -q`
Expected: FAIL because the current retrieval layer is still biased toward academic advising rows.

- [ ] **Step 3: Add structured entity datasets**

Create or extend CSVs for:
- chairs
- deans
- directors
- advising offices
- transfer/tutoring/support offices
- selected student organizations and teams where official public Morgan support exists

Suggested CSV shapes:

```csv
name,title,department,school,email,phone,office,profile_url,notes,source_url
Dr. Example Dean,Dean,School of Computer Mathematical and Natural Sciences,SCMNS,dean@example.edu,443-555-0000,Key Hall 100,https://...,Official school dean,https://...
```

```csv
name,category,owner_department,email,phone,office,url,notes,source_url
Transfer Center,office,Enrollment Management,transfer@example.edu,443-555-0001,Montebello Hall 200,https://...,Primary transfer support path,https://...
```

```csv
name,category,owner_department,contact_email,contact_phone,url,notes,source_url
Robotics Team,organization,Computer Science,robotics@example.edu,,https://...,Official robotics team contact page,https://...
```

Use only official Morgan public grounding where available. If the exact owner is not clear, prefer a nearby official contact path rather than inventing specifics.

- [ ] **Step 4: Run the targeted tests again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k "entity_queries or office_queries or organization_queries" -q`
Expected: PASS

## Task 2: Add lightweight question-type routing

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_rag.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Write failing routing tests**

```python
@pytest.mark.parametrize(
    "question,expected_intent",
    [
        ("What should I take next?", "degree_planning"),
        ("What do I need before COSC242?", "course_prerequisite"),
        ("Who is the dean of Computer Science?", "people_contact_leadership"),
        ("What office handles transfer advising?", "office_resource"),
        ("Who runs the robotics team?", "organization_team"),
        ("What is my GPA?", "transcript_import"),
        ("How are you?", "small_talk"),
    ],
)
def test_classify_question_intent(question, expected_intent):
    assert classify_question_intent(question) == expected_intent
```

- [ ] **Step 2: Run the targeted tests to confirm missing routing behavior**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k classify_question_intent -q`
Expected: FAIL until intent classification exists.

- [ ] **Step 3: Implement lightweight routing helpers**

Add a small classifier in `rag.py` or a nearby helper that detects intent families:
- `degree_planning`
- `course_prerequisite`
- `people_contact_leadership`
- `office_resource`
- `organization_team`
- `transcript_import`
- `small_talk`

Keep it heuristic and lightweight. Do not overengineer it into a separate ML system.

- [ ] **Step 4: Make retrieval source preferences intent-aware**

Adjust retrieval scoring so:
- people/contact questions boost leadership, faculty, departments, and offices first
- office/resource questions boost offices and support resources first
- organization/team questions boost organizations first, then nearby department/faculty context
- transcript questions boost saved import context first
- degree-planning questions keep the current major-aware and requirement-aware behavior

- [ ] **Step 5: Run routing-focused tests again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py backend/tests/test_chat.py -k "classify_question_intent or dean or robotics or transfer advising or GPA" -q`
Expected: PASS

## Task 3: Improve fallback behavior for entity and office questions

**Files:**
- Modify: `backend/app/chat.py`
- Modify: `backend/app/rag.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Write failing fallback-behavior tests**

```python
def test_contact_question_fallback_returns_best_morgan_contact_not_generic_dump(...):
    ...


def test_team_question_fallback_returns_nearest_valid_context(...):
    ...
```

- [ ] **Step 2: Run the targeted fallback tests**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_chat.py -k "fallback and (contact or team)" -q`
Expected: FAIL if fallback still sounds too generic.

- [ ] **Step 3: Improve fallback phrasing and nearest-valid-result handling**

When the exact answer is missing:
- say what was found
- return the strongest valid Morgan contact, page, or office
- avoid broad generic advising language when the question is clearly not about degree planning

Examples of desired behavior:
- “I do not see an official robotics team lead in the current Morgan dataset, but the closest official path I found is the Computer Science department contact...”
- “I do not see a direct dean page for that phrasing, but the school dean listed for the school that houses Computer Science is...”

- [ ] **Step 4: Run the targeted fallback tests again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_chat.py -k "fallback and (contact or team)" -q`
Expected: PASS

## Task 4: Verify end-to-end behavior and document the new layer

**Files:**
- Modify if needed: `README.md`
- Modify if needed: `docs/...` only if implementation details differ from plan
- Verify: backend tests and selected manual flows

- [ ] **Step 1: Run the focused verification suite**

Run:
- `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py backend/tests/test_chat.py backend/tests/test_catalog.py -q`
Expected: PASS

- [ ] **Step 2: Run the full backend suite**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests -q`
Expected: PASS

- [ ] **Step 3: Run backend compile check**

Run from `backend/`:
- `& .\.venv\Scripts\python.exe -m compileall app`
Expected: PASS

- [ ] **Step 4: Verify frontend build still passes**

Run from `frontend/`:
- `npm run build`
Expected: PASS

- [ ] **Step 5: Manual sanity-check queries**

Verify these questions behave better than before:
- `Who is the dean of Computer Science at Morgan State University?`
- `Who should I contact about Nursing?`
- `What office handles transfer advising?`
- `Who is in charge of the robotics team at Morgan?`
- `How are you?`
- `What should I take next?`

- [ ] **Step 6: Commit**

```bash
git add backend/app/rag.py backend/app/chat.py backend/data/*.csv backend/tests/*.py README.md
git commit -m "Strengthen Morgan entities retrieval and question routing"
```

## Notes

- Prefer official Morgan public sources for people, offices, organizations, and support resources.
- If the exact team/organization owner is not clearly documented, return the nearest supported Morgan contact rather than inventing a direct owner.
- Keep the routing lightweight and testable.
- Do not let this pass turn into a deployment or Docker refactor.
- The whole purpose is to reduce vague answers and make the product feel more like a real Morgan information system.
