# Tech and Health Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen the backend advising logic for Information Science, Cloud Computing, Nursing, Biology, and Psychology so degree progress and chat recommendations feel major-aware and presentation-ready.

**Architecture:** Extend the existing backend planning layer in `backend/app/rag.py` using two advising families: a technology family for Information Science and Cloud Computing, and a health/science family for Nursing, Biology, and Psychology. Keep the existing Morgan dataset as the foundation, add only the minimum course/prerequisite data needed to support stronger sequencing, and verify the behavior through targeted RAG/chat regressions before running the full backend suite.

**Tech Stack:** Python, FastAPI, SQLAlchemy, pytest, CSV-backed Morgan data, Gemini fallback-aware chat pipeline

---

## File Map

- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/app/rag.py`
  - Extend major-family planning rules, recommendation ordering, and program guidance.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/app/chat.py`
  - Ensure stronger major guidance is reflected in the degree-progress context used by chat.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/data/degree_requirements.csv`
  - Make small requirement-row adjustments only if current rows are too thin for stronger sequencing.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/data/courses.csv`
  - Add missing course rows only when required by failing tests.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/data/prerequisites.csv`
  - Add or correct prerequisite links only when required by failing tests.
- Create: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/data/tech_health_pathways.csv`
  - Store major-specific sequencing priorities for the five target majors if the logic becomes too dense for inline rules.
- Create: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_tech_health_depth.py`
  - Hold the new degree-progress regressions for all five majors.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_chat.py`
  - Add chat-context regressions for at least one technology major and one health/science major.
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_rag.py`
  - Add retrieval/progress regressions if needed for short major-specific questions.

### Task 1: Add the technology-family regression tests

**Files:**
- Create: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_tech_health_depth.py`
- Test: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_tech_health_depth.py`

- [ ] **Step 1: Write the failing tests for Information Science and Cloud Computing**

```python
from app.rag import get_degree_progress


def test_information_science_prefers_the_inss_progression_before_later_work():
    progress = get_degree_progress("Information Science", ["INSS141", "ENGL101", "ENGL102"])

    assert "INSS201" in progress["recommended_next_courses"]
    assert "INSS340" not in progress["recommended_next_courses"]


def test_cloud_computing_holds_upper_cloud_work_until_foundations_are_ready():
    progress = get_degree_progress("Cloud Computing", ["CLDC101", "COSC111", "ENGL101", "ENGL102"])

    assert "CLDC220" in progress["recommended_next_courses"]
    assert "CLDC340" in progress["blocked_courses"] or "CLDC340" not in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run the focused technology tests to verify they fail**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_tech_health_depth.py -q
```

Expected: FAIL because the new technology-major sequencing rules do not exist yet.

- [ ] **Step 3: Add the minimal technology sequencing logic**

Implement the shared technology-family recognition and program guidance in `backend/app/rag.py`. If a small CSV-backed priority map is cleaner than inline conditionals, add `backend/data/tech_health_pathways.csv` with rows like:

```csv
major,stage,focus_area,required_course,priority,notes
Information Science,core,tech_foundation,INSS141,1,Information Science students should move through the early INSS sequence before later systems planning.
Information Science,upper,inss_progression,INSS201,2,INSS201 should come before upper Information Science work.
Information Science,upper,inss_progression,INSS310,3,Students should build enough lower-division context before advanced Information Science planning.
Cloud Computing,core,cloud_foundation,CLDC101,1,Cloud Computing students should start with core cloud concepts.
Cloud Computing,upper,cloud_progression,CLDC220,2,Infrastructure and platform foundations should come before advanced cloud work.
Cloud Computing,upper,cloud_progression,CLDC310,3,Mid-level cloud progression should precede platform design and security-heavy coursework.
Cloud Computing,upper,cloud_progression,CLDC340,4,Advanced cloud/platform work should wait for lower progression.
```

And add logic shaped like:

```python
def _is_tech_health_depth_major(major: Optional[str]) -> bool:
    return _normalize(major) in {
        "Information Science",
        "Cloud Computing",
        "Nursing",
        "Biology",
        "Psychology",
    }
```

```python
def _build_tech_health_program_guidance(
    major: Optional[str],
    completed: list[str],
    remaining: list[str],
) -> list[str]:
    normalized_major = _normalize(major)
    completed_set = set(completed)
    guidance: list[str] = []

    if normalized_major == "Information Science":
        if {"INSS141", "INSS201"}.issubset(completed_set):
            guidance.append(
                "Your Information Science foundation is in place, so you can start moving toward more advanced systems and information-flow coursework."
            )
        else:
            guidance.append(
                "Information Science should move through the early INSS sequence before upper-level systems and data-oriented planning."
            )

    if normalized_major == "Cloud Computing":
        if {"CLDC101", "CLDC220"}.issubset(completed_set):
            guidance.append(
                "Your cloud foundation is underway, so upper cloud/platform planning is starting to make sense."
            )
        else:
            guidance.append(
                "Cloud Computing should stay grounded in lower-division cloud and technical foundations before upper-level platform work."
            )

    return guidance
```

- [ ] **Step 4: Run the focused technology tests again**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_tech_health_depth.py -q
```

Expected: PASS for the two technology-family tests.

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/data/tech_health_pathways.csv backend/tests/test_tech_health_depth.py
git commit -m "Deepen technology advising for Information Science and Cloud Computing"
```

### Task 2: Add the health/science-family regression tests

**Files:**
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_tech_health_depth.py`
- Test: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_tech_health_depth.py`

- [ ] **Step 1: Write the failing tests for Nursing, Biology, and Psychology**

```python
def test_nursing_keeps_progression_orderly_before_upper_nursing_work():
    progress = get_degree_progress("Nursing", ["NURS200", "BIOL101", "ENGL101", "ENGL102"])

    assert "NURS210" in progress["recommended_next_courses"]
    assert "NURS310" not in progress["recommended_next_courses"]


def test_biology_requires_foundations_before_upper_biology():
    progress = get_degree_progress("Biology", ["BIOL101", "ENGL101", "ENGL102"])

    assert "BIOL102" in progress["recommended_next_courses"]
    assert "BIOL301" not in progress["recommended_next_courses"]


def test_psychology_prefers_intro_and_methods_before_later_psych_planning():
    progress = get_degree_progress("Psychology", ["PSYC101", "ENGL101", "ENGL102"])

    assert "STAT302" in progress["recommended_next_courses"] or "PSYC201" in progress["recommended_next_courses"]
    assert "PSYC330" not in progress["recommended_next_courses"]
```

- [ ] **Step 2: Run the health/science tests to verify they fail**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_tech_health_depth.py -q
```

Expected: FAIL because the new health/science-family sequencing rules do not exist yet.

- [ ] **Step 3: Add the minimal health/science sequencing logic**

Extend the same family-aware planning logic in `backend/app/rag.py`. If you introduced `tech_health_pathways.csv`, add rows like:

```csv
major,stage,focus_area,required_course,priority,notes
Nursing,core,nursing_foundation,NURS200,1,Nursing students should progress through the lower-division nursing setup before upper nursing work.
Nursing,upper,nursing_progression,NURS210,2,NURS210 should come before later nursing progression.
Nursing,upper,nursing_progression,NURS310,3,Upper nursing work should wait until the early nursing sequence is in place.
Biology,core,biology_foundation,BIOL101,1,Biology starts with the intro sequence.
Biology,core,biology_foundation,BIOL102,2,Students should finish the intro biology progression before upper biology.
Biology,upper,biology_progression,BIOL301,3,Upper biology should wait for the intro sequence and supporting preparation.
Psychology,core,psych_foundation,PSYC101,1,Psychology should start with the intro course.
Psychology,core,psych_foundation,STAT302,2,Statistics or methods preparation should come before later psychology planning.
Psychology,upper,psych_progression,PSYC201,3,Core psychology progression should stay ahead of upper-level psychology topics.
Psychology,upper,psych_progression,PSYC330,4,Advanced psychology planning should wait for intro and preparation.
```

And extend guidance:

```python
    if normalized_major == "Nursing":
        if {"NURS200", "NURS210"}.issubset(completed_set):
            guidance.append(
                "Your lower-division nursing progression is underway, so the next nursing step can be planned more confidently."
            )
        else:
            guidance.append(
                "Nursing should stay orderly and foundation-first so upper nursing coursework is not recommended too early."
            )

    if normalized_major == "Biology":
        if {"BIOL101", "BIOL102"}.issubset(completed_set):
            guidance.append(
                "Your introductory biology foundation is in place, so upper biology planning can begin more naturally."
            )
        else:
            guidance.append(
                "Biology should complete the intro science sequence before upper-level biology recommendations take priority."
            )

    if normalized_major == "Psychology":
        if "PSYC101" in completed_set and ("STAT302" in completed_set or "PSYC201" in completed_set):
            guidance.append(
                "Your psychology foundation is taking shape, so more advanced psychology planning is starting to make sense."
            )
        else:
            guidance.append(
                "Psychology should build through intro and methods-oriented preparation before more advanced psych planning."
            )
```

- [ ] **Step 4: Run the health/science tests again**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_tech_health_depth.py -q
```

Expected: PASS for all five major-depth tests.

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/data/tech_health_pathways.csv backend/tests/test_tech_health_depth.py
git commit -m "Deepen health and science advising for tomorrow's demo"
```

### Task 3: Add chat-context regressions for one technology major and one health/science major

**Files:**
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_chat.py`
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/app/chat.py`
- Test: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_chat.py`

- [ ] **Step 1: Write the failing chat-context tests**

```python
def test_chat_context_includes_program_guidance_for_cloud_computing_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put("/auth/me", headers=auth_headers, json={"major": "Cloud Computing"})
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["CLDC101", "COSC111", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Cloud QA"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next in cloud computing?"},
    )

    assert response.status_code == 200
    assert "Business planning guidance:" not in captured_context["extra_context"]
    assert "Cloud Computing" in captured_context["extra_context"]


def test_chat_context_includes_program_guidance_for_psychology_student(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    client.put("/auth/me", headers=auth_headers, json={"major": "Psychology"})
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["PSYC101", "ENGL101", "ENGL102"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "Psych QA"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "What should I take next in psychology?"},
    )

    assert response.status_code == 200
    assert "Psychology" in captured_context["extra_context"]
```

- [ ] **Step 2: Run the chat tests to verify they fail if context is too generic**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py -q
```

Expected: FAIL if the degree-progress context does not reflect the new guidance clearly enough.

- [ ] **Step 3: Adjust the degree-progress context formatting only if needed**

If the tests fail, update `backend/app/chat.py` minimally so `_build_degree_progress_context(...)` includes the new major guidance without adding noisy metadata. The target shape is:

```python
    if summary.get("program_guidance"):
        lines.append(
            f"- Program guidance: {' '.join(summary['program_guidance'][:3])}"
        )
```

If existing business-specific wording is too narrow, replace it with:

```python
    if summary.get("program_guidance"):
        lines.append(
            f"- Program guidance: {' '.join(summary['program_guidance'][:3])}"
        )
```

This keeps business guidance working while making the field reusable for the new five majors.

- [ ] **Step 4: Run the chat tests again**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py -q
```

Expected: PASS with the updated context.

- [ ] **Step 5: Commit**

```bash
git add backend/app/chat.py backend/tests/test_chat.py
git commit -m "Expose new tech and health guidance in chat context"
```

### Task 4: Add a retrieval regression for short major-specific questions if needed

**Files:**
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests/test_rag.py`
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/app/rag.py`
- Test: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-9-project-3/backend/tests/test_rag.py`

- [ ] **Step 1: Write the failing retrieval tests for short major-specific prompts**

```python
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
```

- [ ] **Step 2: Run the retrieval tests to verify whether they fail**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py -q
```

Expected: Either PASS because the current major-aware retrieval already covers this, or FAIL and reveal a gap.

- [ ] **Step 3: Adjust retrieval scoring only if the tests fail**

If needed, extend the existing major-aware scoring in `backend/app/rag.py` rather than adding a separate retrieval path. Follow the pattern already used for recent HRM retrieval improvements:

```python
    user_major_tokens = _tokenize(user_major or "")
    major_overlap = user_major_tokens & doc_tokens
    exact_major_match = bool(
        user_major
        and doc.major
        and _normalize(user_major).lower() == _normalize(doc.major).lower()
    )
```

Then keep the current rule shape:

```python
    if not overlap and not major_overlap and not exact_major_match:
        return 0.0
```

This keeps retrieval consistent instead of inventing another scoring system.

- [ ] **Step 4: Run the retrieval tests again**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/tests/test_rag.py
git commit -m "Improve retrieval for short major-specific advising questions"
```

### Task 5: Run final verification and summarize demo-readiness

**Files:**
- Modify: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/docs/superpowers/plans/tech-and-health-depth-plan.md`
- Test: `C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3/backend/tests`

- [ ] **Step 1: Run the focused tests for this slice**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest `
  C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_tech_health_depth.py `
  C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py `
  C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py -q
```

Expected: PASS.

- [ ] **Step 2: Run the full backend suite**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests -q
```

Expected: PASS.

- [ ] **Step 3: Run the backend compile check**

Run:
```powershell
& 'C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv\Scripts\python.exe' -m compileall C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app
```

Expected: compileall lists backend app files with no errors.

- [ ] **Step 4: Record demo-readiness notes inline for handoff**

Add a short note at the bottom of this plan after execution describing:

```markdown
## Execution Notes
- Information Science and Cloud Computing now return major-aware next-course guidance.
- Nursing, Biology, and Psychology now return stronger sequencing-aware recommendations.
- Chat context now carries the new program guidance cleanly.
- Full backend verification passed before presentation testing.
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag.py backend/app/chat.py backend/data/degree_requirements.csv backend/data/courses.csv backend/data/prerequisites.csv backend/data/tech_health_pathways.csv backend/tests/test_tech_health_depth.py backend/tests/test_chat.py backend/tests/test_rag.py docs/superpowers/plans/tech-and-health-depth-plan.md
git commit -m "Deepen advising for tech and health majors"
```

## Execution Notes
- Information Science and Cloud Computing now return major-aware next-course guidance.
- Nursing, Biology, and Psychology now return stronger sequencing-aware recommendations.
- Chat context now carries the new program guidance cleanly.
- Full backend verification passed before presentation testing.
