# Recognizable Undergrad Breadth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the app's Morgan-specific undergraduate coverage across a broader set of recognizable majors and one supported criminal justice path so catalog browsing, degree progress, and advising responses feel fuller and more credible.

**Architecture:** Extend the existing CSV-backed Morgan data foundation rather than introducing a new ingestion system. Strengthen program mappings, course-family coverage, department grounding, and degree-requirement usefulness for a focused set of high-traffic undergraduate majors, then verify that retrieval and progress logic use the richer dataset correctly.

**Tech Stack:** Python, FastAPI, SQLAlchemy, SQLite, CSV-backed data files, pytest, React/Vite (verification only unless a UI adjustment becomes necessary)

---

## File Structure

### Existing files to modify
- `backend/data/programs.csv`
  - Canonical undergraduate program names, aliases, school mappings, and source URLs.
- `backend/data/courses.csv`
  - Course catalog rows used by catalog browsing, retrieval, transcript recognition, and advising context.
- `backend/data/degree_requirements.csv`
  - Major requirement rows used by degree progress and advising recommendations.
- `backend/data/departments.csv`
  - Department names, school associations, contact routes, and advising grounding.
- `backend/data/faculty.csv`
  - Faculty and leadership contacts where needed for stronger department grounding.
- `backend/data/prerequisites.csv`
  - Prerequisite relationships for majors where sequencing materially affects advising.
- `backend/app/catalog.py`
  - Catalog loading and filtering behavior for major/family coverage.
- `backend/app/rag.py`
  - Retrieval and advising-context assembly across the expanded majors.
- `backend/tests/test_catalog.py`
  - Catalog behavior regressions for major and level browsing.
- `backend/tests/test_rag.py`
  - Retrieval and advising-context regressions for the newly strengthened majors.
- `backend/tests/test_auth.py`
  - Degree-progress usefulness and requirement grounding regressions where applicable.

### Optional helper file if needed
- `backend/scripts/build_program_catalog.py`
  - Only update if the new major/program mappings should remain generator-driven rather than hand-maintained.

## Priority Majors

This plan focuses on these undergraduate majors and one supported path:
- `Criminal Justice` (supported track / certificate path)
- `Elementary Education`
- `Accounting`
- `Finance`
- `Business Administration`
- `Marketing`
- `Biology`
- `Psychology`
- `Nursing`
- `Computer Science`
- `Information Science`
- `Cloud Computing`

## Task 1: Normalize the priority-major program layer

**Files:**
- Modify: `backend/data/programs.csv`
- Modify: `backend/data/departments.csv`
- Modify: `backend/data/faculty.csv`
- Test: `backend/tests/test_rag.py`

- [ ] **Step 1: Write the failing retrieval test for recognizable program presence**

```python
def test_priority_programs_have_clean_program_and_department_grounding():
    catalog = load_program_catalog()
    expected = {
        "Elementary Education",
        "Accounting",
        "Finance",
        "Business Administration",
        "Marketing",
        "Biology",
        "Psychology",
        "Nursing",
        "Computer Science",
        "Information Science",
        "Cloud Computing",
    }
    names = {program.canonical_major for program in catalog}
    assert expected.issubset(names)
    department_rows = load_department_rows()
    assert any("Criminal Justice" in row.get("major", "") for row in department_rows)
```

- [ ] **Step 2: Run the targeted test to confirm gaps or mismatches**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k priority_programs_have_clean_program_and_department_grounding -q`
Expected: FAIL if one or more majors still use weak names, aliases, missing department grounding, or if the criminal justice path lacks supported-track visibility.

- [ ] **Step 3: Tighten program, department, and faculty grounding data**

Add or correct rows so each priority major has:
- a canonical program entry
- aliases where needed (`Information Science` vs `Information Systems`)
- a valid department/school association
- a department contact route or leadership contact if available

For `Criminal Justice`, do not invent a standalone bachelor's degree if the official Morgan undergraduate pages only support a track, minor, or certificate presence. Model it honestly as a supported undergraduate criminal justice path.

Example CSV shape to preserve:

```csv
canonical_major,degree_type,department,school,aliases,notes,source_url
Information Science,BS,Department of Information Science and Systems,School of Computer, Mathematical and Natural Sciences,"Information Systems;INSS",Official undergraduate Morgan program mapping,https://www.morgan.edu/academics/undergraduate-studies/undergraduate-programs
```

- [ ] **Step 4: Run the targeted test again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k priority_programs_have_clean_program_and_department_grounding -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/data/programs.csv backend/data/departments.csv backend/data/faculty.csv backend/tests/test_rag.py
git commit -m "Strengthen recognizable undergraduate program grounding"
```

## Task 2: Enrich course-family coverage for the priority majors

**Files:**
- Modify: `backend/data/courses.csv`
- Modify: `backend/app/catalog.py`
- Test: `backend/tests/test_catalog.py`

- [ ] **Step 1: Write the failing catalog tests for major-family browsing**

```python
@pytest.mark.parametrize(
    "major_name,level,prefixes",
    [
        ("Computer Science", 300, {"COSC"}),
        ("Information Science", None, {"INSS"}),
        ("Cloud Computing", None, {"CLOU", "COSC"}),
        ("Nursing", None, {"NURS"}),
        ("Biology", 100, {"BIOL"}),
        ("Psychology", 300, {"PSYC"}),
        ("Criminal Justice", None, {"CRJU", "SOCI"}),
        ("Elementary Education", 300, {"EDUC"}),
        ("Accounting", 300, {"ACCT"}),
        ("Finance", 300, {"FINA"}),
        ("Business Administration", None, {"BUSN", "MGMT"}),
        ("Marketing", 300, {"MKTG"}),
    ],
)
def test_catalog_major_filter_stays_inside_priority_major_family(major_name, level, prefixes):
    rows = list_catalog_courses(major=major_name, level=level)
    assert rows
    assert {row.code[:4] for row in rows}.issubset(prefixes)
```

- [ ] **Step 2: Run the targeted catalog test to verify which majors are still sparse or noisy**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_catalog.py -k priority_major_family -q`
Expected: FAIL for majors with thin or mixed course families.

- [ ] **Step 3: Add missing course-family rows in `courses.csv`**

Add enough real rows so the selected majors can browse cleanly by level without looking empty.

Preserve the existing CSV shape, for example:

```csv
code,title,credits,department,level,semester_offered,instructor,description
CRJU101,Introduction to Criminal Justice,3,Criminal Justice,100,Fall/Spring,,Survey of the criminal justice system and its institutions.
EDUC310,Methods of Teaching in Elementary Schools,3,Education,300,Fall,,Methods and field-based preparation for elementary classroom instruction.
NURS220,Health Assessment,3,Nursing,200,Fall,Dr. Renee Coleman,Techniques for patient assessment and clinical judgment in nursing settings.
```

- [ ] **Step 4: Tighten major-to-prefix mapping in `catalog.py` only where data alone is insufficient**

Keep the major browser aligned to dominant major families rather than broad requirement sheets.

Minimal shape to preserve:

```python
MAJOR_PREFIX_FAMILIES = {
    "Computer Science": {"COSC"},
    "Information Science": {"INSS"},
    "Cloud Computing": {"CLOU", "COSC"},
    "Nursing": {"NURS"},
    "Biology": {"BIOL"},
    "Psychology": {"PSYC"},
    "Criminal Justice": {"CRJU"},
    "Elementary Education": {"EDUC"},
    "Accounting": {"ACCT"},
    "Finance": {"FINA"},
    "Business Administration": {"BUSN", "MGMT"},
    "Marketing": {"MKTG"},
}
```

- [ ] **Step 5: Run the targeted catalog test again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_catalog.py -k priority_major_family -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/data/courses.csv backend/app/catalog.py backend/tests/test_catalog.py
git commit -m "Expand course families for recognizable undergraduate majors"
```

## Task 3: Improve degree-requirement usefulness for the priority majors

**Files:**
- Modify: `backend/data/degree_requirements.csv`
- Modify: `backend/data/prerequisites.csv`
- Modify: `backend/app/rag.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_rag.py`

- [ ] **Step 1: Write failing tests for less-generic progress and advising on the new breadth majors**

```python
@pytest.mark.parametrize(
    "major_name,expected_required_codes",
    [
        ("Criminal Justice", {"CRJU101", "SOCI305"}),
        ("Elementary Education", {"EDUC310"}),
        ("Accounting", {"ACCT201", "ACCT202"}),
        ("Finance", {"FINA300"}),
        ("Biology", {"BIOL101"}),
        ("Psychology", {"PSYC101"}),
        ("Nursing", {"NURS101"}),
    ],
)
def test_degree_progress_has_major_specific_remaining_courses(major_name, expected_required_codes):
    summary = get_degree_progress_for_major(major_name)
    remaining = set(summary["remaining_courses"])
    assert expected_required_codes & remaining
```

- [ ] **Step 2: Run the targeted tests to confirm the currently thin majors**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_auth.py backend/tests/test_rag.py -k major_specific_remaining_courses -q`
Expected: FAIL for majors whose requirement model is still too sparse.

- [ ] **Step 3: Enrich `degree_requirements.csv` and `prerequisites.csv` for the selected majors**

Add enough core rows to support believable degree progress and next-course guidance.

Preserve the existing CSV shape, for example:

```csv
major,required_course,category,notes
Criminal Justice,CRJU101,Core,Introductory criminal justice foundation or supported criminal justice path anchor.
Elementary Education,EDUC310,Methods,Upper-level elementary methods sequence.
Accounting,ACCT201,Accounting Core,Foundational financial accounting.
```

Use `prerequisites.csv` only for relationships that materially affect planning quality.

- [ ] **Step 4: Tighten retrieval/advising assembly in `rag.py` where the richer requirement rows need better surfacing**

Keep the logic data-driven. Only add code if the existing pipeline still underuses the improved requirement data.

Minimal expectation:

```python
if major_name in RECOGNIZABLE_UNDERGRAD_MAJORS:
    context.append(build_major_requirement_summary(major_name, degree_requirements))
```

- [ ] **Step 5: Run the targeted tests again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_auth.py backend/tests/test_rag.py -k major_specific_remaining_courses -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/data/degree_requirements.csv backend/data/prerequisites.csv backend/app/rag.py backend/tests/test_auth.py backend/tests/test_rag.py
git commit -m "Improve degree progress for recognizable undergraduate majors"
```

## Task 4: Verify contact and department grounding in retrieval

**Files:**
- Modify: `backend/data/departments.csv`
- Modify: `backend/data/faculty.csv`
- Modify: `backend/app/rag.py`
- Test: `backend/tests/test_rag.py`

- [ ] **Step 1: Write failing retrieval tests for department/contact grounding**

```python
@pytest.mark.parametrize(
    "question,expected_text",
    [
        ("Who should I contact about Nursing?", "nursingdept@morgan.edu"),
        ("What department handles Biology?", "Department of Biology"),
        ("Who should I contact about Criminal Justice?", "443-885-3518"),
        ("What department is Elementary Education in?", "Education"),
    ],
)
def test_retrieval_has_major_contact_grounding(question, expected_text):
    snippets = retrieve_relevant_context(question)
    joined = "\n".join(snippets)
    assert expected_text in joined
```

- [ ] **Step 2: Run the targeted retrieval test to see which majors still lack contact grounding**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k major_contact_grounding -q`
Expected: FAIL for majors without strong department/contact rows.

- [ ] **Step 3: Fill remaining department/faculty grounding gaps**

Update `departments.csv` and `faculty.csv` so the selected majors have a reasonable contact route.

Preserve the current data shapes, for example:

```csv
major,department,office,email,phone,overview
Nursing,Department of Nursing,Jenkins Hall 122,nursingdept@morgan.edu,443-885-3230,Nursing advises students on clinical progression and licensure-oriented planning.
```

- [ ] **Step 4: Run the targeted retrieval test again**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rag.py -k major_contact_grounding -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/data/departments.csv backend/data/faculty.csv backend/tests/test_rag.py
git commit -m "Strengthen contact grounding for recognizable undergraduate majors"
```

## Task 5: Full verification and product sanity check

**Files:**
- Modify if needed: any file touched above to fix regressions uncovered in verification
- Test: `backend/tests/test_catalog.py`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_rag.py`

- [ ] **Step 1: Run focused backend verification**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/test_catalog.py backend/tests/test_auth.py backend/tests/test_rag.py -q`
Expected: PASS

- [ ] **Step 2: Run the full backend suite**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests -q`
Expected: PASS

- [ ] **Step 3: Run backend compile verification**

Run: `py -3.12 -m compileall app`
Workdir: `backend`
Expected: compile succeeds without syntax failures

- [ ] **Step 4: If any frontend file changed indirectly, verify the frontend still builds**

Run: `npm run build`
Workdir: `frontend`
Expected: production build succeeds

- [ ] **Step 5: Commit any verification-driven fixes**

```bash
git add backend/data backend/app backend/tests frontend/src
git commit -m "Finalize recognizable undergraduate breadth expansion"
```

## Self-Review

- Spec coverage: the plan covers program presence, course-family coverage, requirement usefulness, contact grounding, and testing.
- Placeholder scan: removed vague placeholders and gave concrete files, tests, commands, and expected outputs.
- Type consistency: the plan keeps naming aligned around `programs.csv`, `courses.csv`, `degree_requirements.csv`, `departments.csv`, `faculty.csv`, `prerequisites.csv`, `catalog.py`, and `rag.py`.
