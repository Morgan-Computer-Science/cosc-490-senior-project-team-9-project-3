# Presentation Major Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the six demo majors browse cleanly in the catalog, shrink the real PDF `Needs confirmation` list, and make casual chat greetings behave naturally before tomorrow's presentation.

**Architecture:** Tighten the backend around three focused seams instead of attempting a broad catalog rebuild: a major-family catalog filter, targeted dataset enrichment for six demo majors, and a lightweight small-talk bypass in chat. Keep the frontend changes minimal by reusing the existing catalog and chat surfaces while strengthening the data and response selection behind them.

**Tech Stack:** React, Vite, FastAPI, SQLAlchemy, pytest, CSV-backed Morgan catalog data

---

### Task 1: Lock the catalog behavior for the six demo majors

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\conftest.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\catalog.py`

- [ ] **Step 1: Extend the failing catalog tests for the remaining demo majors**

Add tests that assert major-family filtering for Biology, Nursing, and Psychology stays within the dominant family instead of leaking support courses:

```python
def test_course_major_filter_returns_biology_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Biology", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("BIOL") for course in payload)


def test_course_major_filter_returns_psychology_family_courses(client, auth_headers):
    response = client.get("/catalog/courses?major=Psychology", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("PSYC") for course in payload)
```

- [ ] **Step 2: Seed the test database with the demo-major course rows needed for the new tests**

Extend the existing `seed_course_rows(...)` call in `conftest.py` with verified Biology, Nursing, and Psychology codes that already exist in `backend/data/courses.csv`.

```python
seed_course_rows(
    db,
    [
        "COSC111", "COSC241", "COSC242", "COSC310", "COSC331", "COSC332", "COSC350", "COSC490",
        "INSS201", "INSS220", "INSS310", "INSS340",
        "BIOL101", "BIOL102", "BIOL201", "BIOL301",
        "NURS101", "NURS201", "NURS301",
        "PSYC101", "PSYC210", "PSYC301", "PSYC302",
    ],
)
```

- [ ] **Step 3: Run the targeted catalog tests to verify the new cases fail for the right reason**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_catalog.py -q"`

Expected: one or more failures showing the missing major-family filtering or missing seeded rows for the new demo-major assertions.

- [ ] **Step 4: Tighten the major filter implementation if any demo-major family still leaks or returns empty**

Keep the implementation in `catalog.py` centered on dominant course-family prefixes derived from the selected major's requirement rows and alias resolution. If needed, add a small helper to fall back to the program's department-family rows only when no major-family prefix exists.

```python
def _catalog_prefixes_for_major(major: Optional[str]) -> list[str]:
    required_codes = _required_course_codes_for_major(major)
    if not required_codes:
        return []

    prefix_counts = Counter(_course_prefix(code) for code in required_codes if _course_prefix(code))
    non_general_counts = Counter(
        {prefix: count for prefix, count in prefix_counts.items() if prefix not in GENERAL_CATALOG_PREFIXES}
    )
    effective_counts = non_general_counts or prefix_counts
    dominant_count = max(effective_counts.values())
    return sorted(prefix for prefix, count in effective_counts.items() if count == dominant_count)
```

- [ ] **Step 5: Re-run the catalog test file and make sure it is green**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_catalog.py -q"`

Expected: `... passed`

- [ ] **Step 6: Commit the catalog filter stabilization**

```bash
git add backend/app/catalog.py backend/tests/test_catalog.py backend/tests/conftest.py
git commit -m "Tighten major catalog filtering for demo majors"
```

### Task 2: Enrich the six demo majors in the Morgan course dataset

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\degree_requirements.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py`
- Optional Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\faculty.csv`

- [ ] **Step 1: Identify the exact missing rows for the six demo majors**

Use the user's test flows plus the real PDF unknown list to make a short checklist of missing major-family codes for:

- Computer Science
- Information Science
- Cloud Computing
- Nursing
- Biology
- Psychology

The working checklist should prioritize codes that make major browsing non-empty and codes currently appearing in `Needs confirmation`.

- [ ] **Step 2: Add verified course rows for those missing codes in `courses.csv`**

Follow the existing CSV schema and only fill fields that are supported by the current Morgan data quality. Prefer accurate minimal rows over speculative rich rows.

```csv
code,title,description,credits,department,level,semester_offered,instructor
PSYC210,Research Methods in Psychology,Introduction to psychology research design and evidence-based analysis,3,Psychology,200,Fall/Spring,
BIOL201,Genetics,Study of inheritance molecular genetics and applied biological analysis,4,Biology,200,Fall/Spring,
```

- [ ] **Step 3: Add or tighten requirement rows only if a demo major still cannot resolve to a clean course family**

If a major is too sparse to compute a stable dominant prefix, patch its row in `degree_requirements.csv` with the verified major-family codes needed for catalog browsing.

```csv
major,department,required_courses,notes,advising_tips
Psychology,Psychology,PSYC101;PSYC210;PSYC301;PSYC302,Official undergraduate psychology core used for demo-safe advising,Finish intro and research/stat preparation before upper-level psych work.
```

- [ ] **Step 4: Add a focused regression test for at least one newly enriched major that was previously sparse**

Add a test that proves the newly enriched major now returns non-empty, major-family results.

```python
def test_course_major_filter_returns_non_empty_cloud_computing_family(client, auth_headers):
    response = client.get("/catalog/courses?major=Cloud Computing", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all(course["code"].startswith("COSC") for course in payload)
```

- [ ] **Step 5: Run catalog tests again to verify the data enrichment fixed the sparse-major paths**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_catalog.py -q"`

Expected: `... passed`

- [ ] **Step 6: Commit the demo-major dataset enrichment**

```bash
git add backend/data/courses.csv backend/data/degree_requirements.csv backend/tests/test_catalog.py backend/data/faculty.csv
git commit -m "Enrich demo majors in the Morgan course dataset"
```

### Task 3: Shrink the real PDF `Needs confirmation` list

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\course_aliases.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_auth.py`
- Optional Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\attachments.py`

- [ ] **Step 1: Capture the real unknown-code checklist from the user's PDF screenshot and current preview output**

Use the visible `Needs confirmation` set as the checklist. Group them into:

- real Morgan course codes we should add
- alias/mapping candidates
- codes we should intentionally leave unresolved for now

- [ ] **Step 2: Add or map the verified codes that belong in the dataset**

Use `courses.csv` for genuinely missing rows and `course_aliases.csv` for codes that should resolve to an existing canonical course.

```csv
alias_code,canonical_code,notes
COSC001,COSC111,Legacy or transcript shorthand that should resolve to the intro CS path
```

- [ ] **Step 3: Add a regression test that proves the import preview recognizes at least one newly patched code**

Add a focused import-preview test in `test_auth.py`.

```python
def test_import_preview_recognizes_newly_added_transcript_code(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={"import_source": "websis_export", "source_text": "Completed COSC323 with grade B"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "COSC323" in payload["completed_course_codes"] or "COSC323" in payload["matched_course_codes"]
```

- [ ] **Step 4: Run the focused import tests to verify the cleanup works**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_auth.py -q"`

Expected: `... passed`

- [ ] **Step 5: Re-test the real PDF import manually in the UI and confirm the `Needs confirmation` block is dramatically smaller**

Manual check:
- upload `Great.pdf`
- click preview
- compare the `Needs confirmation` block to the current baseline screenshot

Expected: only a small leftover set remains, ideally none for the demo-major codes.

- [ ] **Step 6: Commit the transcript import cleanup**

```bash
git add backend/data/courses.csv backend/data/course_aliases.csv backend/tests/test_auth.py backend/app/attachments.py
git commit -m "Reduce transcript unknowns for the presentation flow"
```

### Task 4: Make casual chat greetings feel normal

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\chat.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py`

- [ ] **Step 1: Add failing tests for greeting and small-talk prompts**

Create tests that prove `hello`, `how are you`, and similar prompts do not produce degree-progress dumps.

```python
def test_chat_small_talk_returns_brief_friendly_reply(client, auth_headers):
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Greetings"}).json()
    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        files={"content": (None, "Hello how are you?")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "recommended next courses" not in payload["assistant_message"]["content"].lower()
    assert "completion is" not in payload["assistant_message"]["content"].lower()
```

- [ ] **Step 2: Run the chat tests and verify they fail for the current advising-dump behavior**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_chat.py -q"`

Expected: failure because the current reply still includes major-aware advising context.

- [ ] **Step 3: Add a narrow small-talk bypass in `chat.py`**

Introduce a small helper near the top of the message flow that recognizes common greetings and returns a short conversational answer before retrieval or degree-progress context is built.

```python
SMALL_TALK_PATTERNS = (
    "hello",
    "hi",
    "how are you",
    "what's up",
    "good morning",
)


def _small_talk_reply(content: str) -> str | None:
    lowered = content.strip().lower()
    if any(pattern in lowered for pattern in SMALL_TALK_PATTERNS):
        return "Hey, I'm doing well. I'm your Morgan State advisor whenever you're ready. What would you like help with today?"
    return None
```

Call it before the major-aware advising and retrieval path.

- [ ] **Step 4: Re-run the focused chat tests and confirm the greeting tests now pass**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest tests\test_chat.py -q"`

Expected: `... passed`

- [ ] **Step 5: Commit the chat tone cleanup**

```bash
git add backend/app/chat.py backend/tests/test_chat.py
git commit -m "Make casual chat prompts feel conversational"
```

### Task 5: Final verification and demo readiness sweep

**Files:**
- Modify if needed: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\frontend\src\App.jsx`
- Modify if needed: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\frontend\src\components\DegreeProgressView.jsx`
- Modify if needed: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\frontend\src\components\Chatbot.jsx`

- [ ] **Step 1: Run the full backend suite after all changes**

Run: `cmd /c "cd /d C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend && .venv\Scripts\python.exe -m pytest -q"`

Expected: full suite passes.

- [ ] **Step 2: Run the frontend production build**

Run: `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe -Command "npm.cmd run build"`
Workdir: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\frontend`

Expected: `vite build` completes successfully.

- [ ] **Step 3: Manual demo smoke test in the UI**

Verify these flows:

1. `Computer Science + 300 level`
2. `Information Science + All levels`
3. `Cloud Computing + All levels`
4. `Nursing + All levels`
5. `Biology + 100 level`
6. `Psychology + 200 level`
7. upload `Great.pdf` and check the reduced `Needs confirmation` block
8. ask `Hello how are you?` in chat and confirm the reply is conversational

- [ ] **Step 4: Make only minimal presentation-safe UI touchups if a smoke-test issue is obvious**

Examples of acceptable touchups:

```jsx
<p>Try a different major core, clear the search, or switch back to all course levels.</p>
```

Keep this limited to copy or tiny rendering fixes that directly improve the demo.

- [ ] **Step 5: Commit the final presentation sweep**

```bash
git add frontend/src/App.jsx frontend/src/components/DegreeProgressView.jsx frontend/src/components/Chatbot.jsx
git commit -m "Polish presentation flows for the demo"
```
