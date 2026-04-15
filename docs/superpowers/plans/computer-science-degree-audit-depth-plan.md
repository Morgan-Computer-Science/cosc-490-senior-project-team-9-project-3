# Computer Science Degree-Audit Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Computer Science-specific degree-audit interpretation layer that classifies CS coursework accurately, improves capstone and pathway reasoning, and feeds clearer CS summaries into import preview and chat.

**Architecture:** Add a focused `cs_audit.py` module and a small CS audit bucket dataset instead of burying more rules inside the generic OCR and RAG functions. Reuse existing CS pathway and capstone data, then thread a structured CS audit summary through import preview, degree-progress logic, and chat context so the backend becomes both more accurate and easier to explain.

**Tech Stack:** FastAPI, Pydantic, Python CSV data loaders, existing OCR/import pipeline, pytest, SQLite-backed backend tests.

---

## File Structure

**Create:**
- `backend/app/cs_audit.py` — Computer Science-specific audit interpretation functions and helpers.
- `backend/data/cs_audit_buckets.csv` — CS course-to-audit-bucket definitions for foundations, core progression, math/stat support, upper-level requirements, and capstone role.
- `backend/tests/test_cs_audit.py` — focused unit tests for CS audit interpretation behavior.

**Modify:**
- `backend/app/rag.py` — call the CS audit interpreter from degree-progress and audit-heavy planning paths.
- `backend/app/auth.py` — enrich import preview responses with CS-specific audit summaries when the user or uploaded audit is CS-related.
- `backend/app/chat.py` — include the structured CS audit interpretation in chat context without adding visible UI clutter.
- `backend/app/schemas.py` — add response models for the CS audit summary and compact student-facing explanation blocks.
- `backend/tests/test_rag.py` — verify CS degree-progress now surfaces deeper audit interpretation.
- `backend/tests/test_auth.py` — verify CS import preview includes CS-specific audit explanation.
- `backend/tests/test_chat.py` — verify chat uses CS audit interpretation for capstone and pathway questions.

## Task 1: Add the CS Audit Contract and Failing Tests

**Files:**
- Create: `backend/data/cs_audit_buckets.csv`
- Create: `backend/tests/test_cs_audit.py`
- Modify: `backend/app/schemas.py`

- [ ] **Step 1: Add the CS audit bucket dataset**

Create `backend/data/cs_audit_buckets.csv` with the first pass of Computer Science audit groupings:

```csv
course_code,bucket,role,notes
COSC111,foundation,intro_programming,Intro programming foundation
COSC112,foundation,intro_programming,Second programming foundation
COSC241,core,systems_foundation,Computer systems and digital logic
COSC242,core,data_structures,Data structures and algorithms backbone
COSC310,core,software_foundation,Upper-level core before capstone
COSC331,core,systems_core,Core systems sequence
COSC332,core,software_core,Core software sequence
COSC350,core,theory_core,Core theory sequence
MATH141,math_support,calculus_foundation,Required lower-division math
MATH241,math_support,advanced_calculus,Supports upper-level CS work
MATH242,math_support,linear_algebra_support,Supports AI/data and upper-level CS
STAT302,math_support,statistics_support,Supports AI/data work
COSC459,upper_level,database_elective,Upper-level database planning signal
COSC470,upper_level,ai_data_elective,AI and data focus-area elective
COSC475,upper_level,cybersecurity_elective,Cybersecurity focus-area elective
COSC480,upper_level,cloud_systems_elective,Cloud and systems focus-area elective
COSC490,capstone,capstone,Senior project capstone
```

- [ ] **Step 2: Write the failing CS audit tests**

Create `backend/tests/test_cs_audit.py`:

```python
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
```

- [ ] **Step 3: Run the new test file and verify it fails**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_cs_audit.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.cs_audit'` or missing-key errors from the new summary shape.

- [ ] **Step 4: Add the response models needed by the new summary**

Extend `backend/app/schemas.py` with compact CS audit models:

```python
class CSAuditBucket(BaseModel):
    completed: list[str] = Field(default_factory=list)
    in_progress: list[str] = Field(default_factory=list)
    remaining: list[str] = Field(default_factory=list)


class CSAuditDirection(BaseModel):
    primary_pathway: Optional[str] = None
    aligned_courses: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class CSAuditSummary(BaseModel):
    foundations: CSAuditBucket = Field(default_factory=CSAuditBucket)
    core_progress: CSAuditBucket = Field(default_factory=CSAuditBucket)
    math_support: CSAuditBucket = Field(default_factory=CSAuditBucket)
    upper_level_progress: CSAuditBucket = Field(default_factory=CSAuditBucket)
    capstone_readiness: CapstoneReadiness = Field(default_factory=CapstoneReadiness)
    pathway_direction: CSAuditDirection = Field(default_factory=CSAuditDirection)
    unmapped_courses: list[str] = Field(default_factory=list)
    summary_lines: list[str] = Field(default_factory=list)
```

- [ ] **Step 5: Commit the contract and failing tests**

```powershell
git add backend/data/cs_audit_buckets.csv backend/tests/test_cs_audit.py backend/app/schemas.py
git commit -m "Add the Computer Science audit contract"
```

## Task 2: Implement the CS Audit Interpreter

**Files:**
- Create: `backend/app/cs_audit.py`
- Test: `backend/tests/test_cs_audit.py`
- Modify: `backend/app/rag.py`

- [ ] **Step 1: Implement the CS audit loader and bucket helpers**

Create `backend/app/cs_audit.py`:

```python
import csv
from functools import lru_cache
from pathlib import Path

from .rag import build_cs_pathway_recommendations, evaluate_cs_capstone_readiness

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CS_AUDIT_BUCKETS_PATH = DATA_DIR / "cs_audit_buckets.csv"


@lru_cache(maxsize=1)
def load_cs_audit_bucket_rows() -> tuple[dict[str, str], ...]:
    with CS_AUDIT_BUCKETS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_cs_audit_bucket_map() -> dict[str, dict[str, str]]:
    bucket_map: dict[str, dict[str, str]] = {}
    for row in load_cs_audit_bucket_rows():
        code = (row.get("course_code") or "").strip().upper()
        if code:
            bucket_map[code] = row
    return bucket_map


def _empty_bucket() -> dict[str, list[str]]:
    return {"completed": [], "in_progress": [], "remaining": []}
```

- [ ] **Step 2: Implement the CS audit interpreter**

Continue `backend/app/cs_audit.py` with the main function:

```python
def interpret_computer_science_audit(
    *,
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
    planning_interest: str | None,
) -> dict[str, object]:
    bucket_map = load_cs_audit_bucket_map()
    summary = {
        "foundations": _empty_bucket(),
        "core_progress": _empty_bucket(),
        "math_support": _empty_bucket(),
        "upper_level_progress": _empty_bucket(),
        "capstone_readiness": {"status": "unknown", "missing_foundations": [], "notes": None},
        "pathway_direction": {"primary_pathway": None, "aligned_courses": [], "notes": None},
        "unmapped_courses": [],
        "summary_lines": [],
    }

    for status_name, codes in {
        "completed": completed_codes,
        "in_progress": in_progress_codes,
        "remaining": remaining_codes,
    }.items():
        for code in codes:
            row = bucket_map.get(code)
            if not row:
                if code.startswith("COSC") and code not in summary["unmapped_courses"]:
                    summary["unmapped_courses"].append(code)
                continue
            bucket_name = row["bucket"]
            if bucket_name == "foundation":
                summary["foundations"][status_name].append(code)
            elif bucket_name == "core":
                summary["core_progress"][status_name].append(code)
            elif bucket_name == "math_support":
                summary["math_support"][status_name].append(code)
            elif bucket_name in {"upper_level", "capstone"}:
                summary["upper_level_progress"][status_name].append(code)

    pathways = build_cs_pathway_recommendations(
        completed_codes,
        planning_interest=planning_interest,
        recommended_next_courses=remaining_codes,
    )
    if pathways:
        summary["pathway_direction"] = {
            "primary_pathway": pathways[0]["pathway"],
            "aligned_courses": pathways[0]["recommended_courses"],
            "notes": pathways[0].get("notes"),
        }

    capstone = evaluate_cs_capstone_readiness(completed_codes, in_progress_codes)
    summary["capstone_readiness"] = capstone

    if summary["foundations"]["remaining"]:
        summary["summary_lines"].append(
            "You still need to finish the early CS programming foundations before the strongest upper-level progression opens up."
        )
    if capstone["status"] == "not_ready":
        summary["summary_lines"].append(
            "COSC490 still looks early based on the current core Computer Science record."
        )
    if summary["pathway_direction"]["primary_pathway"]:
        summary["summary_lines"].append(
            f"Your current CS record is leaning toward {summary['pathway_direction']['primary_pathway']}."
        )

    return summary
```

- [ ] **Step 3: Expose a small wrapper in `backend/app/rag.py`**

Add the import and wrapper in `backend/app/rag.py`:

```python
from .cs_audit import interpret_computer_science_audit


def get_computer_science_audit_summary(
    completed_codes: list[str],
    in_progress_codes: list[str],
    remaining_codes: list[str],
    planning_interest: str | None = None,
) -> dict[str, object]:
    return interpret_computer_science_audit(
        completed_codes=completed_codes,
        in_progress_codes=in_progress_codes,
        remaining_codes=remaining_codes,
        planning_interest=planning_interest,
    )
```

- [ ] **Step 4: Run the CS audit tests and verify they pass**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_cs_audit.py -q
```

Expected: PASS for all tests in `test_cs_audit.py`.

- [ ] **Step 5: Commit the interpreter**

```powershell
git add backend/app/cs_audit.py backend/app/rag.py backend/tests/test_cs_audit.py
git commit -m "Add a dedicated Computer Science audit interpreter"
```

## Task 3: Wire the CS Audit Summary into Degree Progress and Import Preview

**Files:**
- Modify: `backend/app/rag.py`
- Modify: `backend/app/auth.py`
- Modify: `backend/app/schemas.py`
- Test: `backend/tests/test_rag.py`
- Test: `backend/tests/test_auth.py`

- [ ] **Step 1: Add failing integration tests for degree progress and import preview**

Add to `backend/tests/test_rag.py`:

```python
from app.rag import get_degree_progress


def test_cs_degree_progress_surfaces_audit_summary():
    progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC112", "COSC241", "MATH141"],
        planning_interest="I want to know if I am on track for capstone.",
    )

    assert progress["cs_audit_summary"]["capstone_readiness"]["status"] == "not_ready"
    assert "COSC241" in progress["cs_audit_summary"]["core_progress"]["completed"]
```

Add to `backend/tests/test_auth.py`:

```python
def test_cs_import_preview_returns_cs_specific_audit_summary(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import-preview",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "text": "Computer Science degree audit\nCOSC 111 A\nCOSC 241 A\nCOSC 490 IP\nMATH 141 A",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cs_audit_summary"]["capstone_readiness"]["status"] == "not_ready"
    assert payload["cs_audit_summary"]["summary_lines"]
```

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_rag.py tests\test_auth.py -q
```

Expected: FAIL with missing `cs_audit_summary` keys or schema validation errors.

- [ ] **Step 3: Extend schemas to carry the CS audit summary**

Update `backend/app/schemas.py`:

```python
class CompletedCoursesImportPreview(BaseModel):
    import_source: str = "manual"
    detected_document_type: str = "text_document"
    extraction_method: str = "text_local"
    summary: Optional[str] = None
    confidence_note: Optional[str] = None
    matched_course_codes: list[str] = Field(default_factory=list)
    completed_course_codes: list[str] = Field(default_factory=list)
    planned_course_codes: list[str] = Field(default_factory=list)
    remaining_course_codes: list[str] = Field(default_factory=list)
    unknown_course_codes: list[str] = Field(default_factory=list)
    matched_count: int = 0
    source_summary: Optional[str] = None
    cs_audit_summary: Optional[CSAuditSummary] = None


class DegreeProgressSummary(BaseModel):
    major: Optional[str] = None
    required_courses: list[str] = Field(default_factory=list)
    completed_courses: list[str] = Field(default_factory=list)
    remaining_courses: list[str] = Field(default_factory=list)
    recommended_next_courses: list[str] = Field(default_factory=list)
    blocked_courses: list[str] = Field(default_factory=list)
    pathway_recommendations: list[PathwayRecommendation] = Field(default_factory=list)
    capstone_readiness: CapstoneReadiness = Field(default_factory=CapstoneReadiness)
    cs_audit_summary: Optional[CSAuditSummary] = None
    completion_percent: float = 0.0
    notes: Optional[str] = None
    advising_tips: Optional[str] = None
```

- [ ] **Step 4: Thread the CS audit summary into degree progress and import preview**

Update `backend/app/rag.py` inside `get_degree_progress(...)`:

```python
    cs_audit_summary = None
    if normalized_major == "Computer Science":
        cs_audit_summary = get_computer_science_audit_summary(
            completed_codes=completed_courses,
            in_progress_codes=[],
            remaining_codes=remaining_courses,
            planning_interest=planning_interest,
        )

    return {
        "major": normalized_major,
        "required_courses": required_courses,
        "completed_courses": completed_courses,
        "remaining_courses": remaining_courses,
        "recommended_next_courses": recommended_next_courses,
        "blocked_courses": blocked_courses,
        "pathway_recommendations": pathway_recommendations,
        "capstone_readiness": capstone_readiness,
        "cs_audit_summary": cs_audit_summary,
        "completion_percent": completion_percent,
        "notes": notes,
        "advising_tips": advising_tips,
    }
```

Update `backend/app/auth.py` when building the import preview:

```python
    cs_audit_summary = None
    if (current_user.major or "").strip().lower() == "computer science" or any(
        code.startswith("COSC") for code in combined_candidates
    ):
        cs_audit_summary = get_computer_science_audit_summary(
            completed_codes=completed,
            in_progress_codes=planned,
            remaining_codes=remaining,
            planning_interest="Import preview interpretation",
        )

    return schemas.CompletedCoursesImportPreview(
        import_source=import_source,
        detected_document_type=document_type,
        extraction_method=extraction_method,
        summary=summary,
        confidence_note=confidence_note,
        matched_course_codes=combined_candidates,
        completed_course_codes=completed,
        planned_course_codes=planned,
        remaining_course_codes=remaining,
        unknown_course_codes=unknown_course_codes,
        matched_count=len(combined_candidates),
        source_summary=source_summary,
        cs_audit_summary=cs_audit_summary,
    )
```

- [ ] **Step 5: Run the targeted integration tests and verify they pass**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_rag.py tests\test_auth.py -q
```

Expected: PASS for the new CS audit integration tests.

- [ ] **Step 6: Commit the import and degree-progress integration**

```powershell
git add backend/app/rag.py backend/app/auth.py backend/app/schemas.py backend/tests/test_rag.py backend/tests/test_auth.py
git commit -m "Thread Computer Science audit summaries into planning flows"
```

## Task 4: Feed the CS Audit Summary into Chat Context

**Files:**
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Add the failing chat test**

Add to `backend/tests/test_chat.py`:

```python
def test_chat_uses_cs_audit_summary_for_capstone_question(client, auth_headers):
    client.put(
        "/auth/me",
        headers=auth_headers,
        json={"major": "Computer Science"},
    )
    client.put(
        "/auth/me/completed-courses",
        headers=auth_headers,
        json={"course_codes": ["COSC111", "COSC112", "COSC241", "MATH141"]},
    )
    session = client.post("/chat/sessions", headers=auth_headers, json={"title": "CS Audit"}).json()

    response = client.post(
        f"/chat/sessions/{session['id']}/messages",
        headers=auth_headers,
        data={"content": "Am I ready for COSC490 based on my CS record so far?"},
    )

    assert response.status_code == 200
    assert response.json()["advisor_insights"]["capstone_readiness"]["status"] == "not_ready"
```

- [ ] **Step 2: Run the chat test and verify it fails**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_chat.py -q
```

Expected: FAIL because chat does not yet pass the richer CS audit interpretation through the audit-aware context path.

- [ ] **Step 3: Enrich the chat context with the CS audit summary**

Update `backend/app/chat.py` where degree progress context is assembled:

```python
    if summary.get("cs_audit_summary"):
        cs_audit = summary["cs_audit_summary"]
        lines.append("- Computer Science audit interpretation:")
        if cs_audit["foundations"]["remaining"]:
            lines.append(
                f"  Foundations still missing: {', '.join(cs_audit['foundations']['remaining'])}"
            )
        if cs_audit["core_progress"]["remaining"]:
            lines.append(
                f"  Core CS courses still missing: {', '.join(cs_audit['core_progress']['remaining'])}"
            )
        if cs_audit["pathway_direction"]["primary_pathway"]:
            lines.append(
                f"  Current pathway leaning: {cs_audit['pathway_direction']['primary_pathway']}"
            )
        if cs_audit["unmapped_courses"]:
            lines.append(
                f"  CS courses still needing advisor confirmation: {', '.join(cs_audit['unmapped_courses'])}"
            )
```

Update `_build_advisor_insights(...)` if needed so the capstone readiness and pathway data continue to reflect the richer CS-specific interpretation.

- [ ] **Step 4: Run the chat test again and verify it passes**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_chat.py -q
```

Expected: PASS, with the chat response still clean but the backend context and advisor insights improved.

- [ ] **Step 5: Commit the chat integration**

```powershell
git add backend/app/chat.py backend/tests/test_chat.py
git commit -m "Use Computer Science audit depth in advisor chat"
```

## Task 5: Run Full Verification and Clean Up Any Regressions

**Files:**
- Modify only as needed based on test failures found in this task.
- Test: `backend/tests/test_cs_audit.py`
- Test: `backend/tests/test_rag.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Run the focused backend test set**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests\test_cs_audit.py tests\test_rag.py tests\test_auth.py tests\test_chat.py -q
```

Expected: PASS for all targeted CS audit tests.

- [ ] **Step 2: Run the full backend suite**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
.\.venv312\Scripts\python.exe -m pytest tests -q
```

Expected: PASS with the full backend suite green.

- [ ] **Step 3: Run the compile check**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend
py -3.12 -m compileall app
```

Expected: `Listing 'app'...` followed by successful compilation with no syntax errors.

- [ ] **Step 4: Commit the final verified slice**

```powershell
git add backend/app/cs_audit.py backend/app/rag.py backend/app/auth.py backend/app/chat.py backend/app/schemas.py backend/data/cs_audit_buckets.csv backend/tests/test_cs_audit.py backend/tests/test_rag.py backend/tests/test_auth.py backend/tests/test_chat.py
git commit -m "Deepen Computer Science degree-audit interpretation"
```

## Self-Review Notes

- Spec coverage: the plan covers the new CS audit interpretation layer, stronger CS audit accuracy, student-facing summary clarity for import preview, richer chat context, unmapped-course preservation, and testing.
- Placeholder scan: no TBD/TODO language remains in the tasks.
- Type consistency: the plan uses `CSAuditSummary`, `CSAuditBucket`, `CSAuditDirection`, and `get_computer_science_audit_summary(...)` consistently across tasks.
