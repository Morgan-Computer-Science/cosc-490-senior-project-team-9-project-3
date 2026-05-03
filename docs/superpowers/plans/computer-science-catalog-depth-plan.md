# Computer Science Catalog Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen Morgan State Computer Science advising with official focus-area mappings, richer elective coverage, and stronger faculty-context alignment.

**Architecture:** Extend the existing CSV-backed Computer Science planning layer with an official focus-area dataset, selective course/elective additions, and faculty-context mappings grounded in Morgan’s public CS framing. Keep the generic advising engine intact, but let the CS layer use richer focus-area metadata to improve planning, retrieval, and chat guidance.

**Tech Stack:** FastAPI backend, Python 3.12, pytest, CSV-backed data files, existing Morgan RAG/catalog backend

---

### Task 1: Add red tests for CS focus-area depth

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py`

- [ ] **Step 1: Write a failing focus-area recommendation test in `test_rag.py`**

```python
def test_cs_degree_progress_surfaces_cybersecurity_focus_area():
    cs_progress = get_degree_progress(
        "Computer Science",
        ["COSC111", "COSC241", "COSC242", "MATH141", "MATH241"],
        planning_interest="I want to focus on cybersecurity and secure systems.",
    )

    assert cs_progress["pathway_recommendations"]
    assert cs_progress["pathway_recommendations"][0]["pathway"] == "Cybersecurity"
    assert any(course in cs_progress["pathway_recommendations"][0]["recommended_courses"] for course in ["COSC360", "COSC459"])
```

- [ ] **Step 2: Write a failing faculty-context retrieval test in `test_rag.py`**

```python
def test_retrieve_relevant_documents_supports_cs_focus_area_faculty_context():
    docs = retrieve_relevant_documents(
        "Who in Morgan Computer Science is most relevant to AI and cloud computing?",
        user_major="Computer Science",
        top_k=8,
    )

    assert docs
    assert any(doc.source_type == "faculty" and (doc.department or "") == "Computer Science" for doc in docs)
```

- [ ] **Step 3: Write a failing chat-context test in `test_chat.py`**

```python
def test_chat_ai_interest_uses_focus_area_context(client, auth_headers, monkeypatch):
    captured_context = {}

    def fake_generate_ai_reply(**kwargs):
        captured_context["extra_context"] = kwargs["extra_context"]
        return "Test advisor reply"

    monkeypatch.setattr("app.chat.generate_ai_reply", fake_generate_ai_reply)
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "AI path"}).json()["id"]

    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "I want to focus on AI and data science in Computer Science. What should I line up next?"},
    )

    assert response.status_code == 200
    assert "AI and Data" in captured_context["extra_context"]
```

- [ ] **Step 4: Run the targeted tests to verify they fail for the right reason**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py -q
```

Expected: FAIL because the richer CS focus-area mapping and chat context do not exist yet.

### Task 2: Add official CS focus-area metadata

**Files:**
- Create: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\cs_focus_areas.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\cs_pathways.csv`

- [ ] **Step 1: Create `cs_focus_areas.csv` with Morgan-aligned focus areas**

```csv
focus_area,interest_keywords,related_courses,foundational_courses,faculty_contact,notes,source_url
Software Engineering,"software engineering;software;applications;product;development","COSC350;COSC340;COSC430","COSC242;COSC310","Dr. Paul Wang","Aligned with Morgan's public Computer Science software-engineering emphasis.","https://www.morgan.edu/computer-science/degrees-and-programs"
Cybersecurity,"cybersecurity;security;secure systems;network security","COSC360;COSC459;COSC420","COSC220;COSC243;COSC242","Dr. Shuangbao Wang","Aligned with Morgan's public Computer Science cybersecurity emphasis.","https://www.morgan.edu/computer-science/degrees-and-programs"
Artificial Intelligence,"artificial intelligence;ai;machine learning;intelligent systems","COSC455;COSC410","COSC242;COSC331;MATH241","Dr. Radhouane Chouchane","Aligned with Morgan's public Computer Science artificial-intelligence emphasis.","https://www.morgan.edu/computer-science/degrees-and-programs"
Data Science,"data science;data;analytics;modeling","COSC410;STAT302;COSC310","COSC242;MATH241","Dr. Radhouane Chouchane","Aligned with Morgan's public Computer Science data-science emphasis.","https://www.morgan.edu/computer-science/degrees-and-programs"
Quantum Security,"quantum security;quantum-safe;post-quantum","COSC360;COSC459","COSC220;COSC243;COSC242","Dr. Radhouane Chouchane","Use as an advising interest area only where Morgan publicly frames it as a CS focus area.","https://www.morgan.edu/computer-science/degrees-and-programs"
Quantum Computing,"quantum computing;quantum algorithms;quantum systems","COSC455;COSC331","COSC242;COSC331;MATH241","Dr. Radhouane Chouchane","Use as an advising interest area only where Morgan publicly frames it as a CS focus area.","https://www.morgan.edu/computer-science/degrees-and-programs"
Game and Robotics,"robotics;game;games;robotics systems","COSC340;COSC430;COSC455","COSC242;COSC310","Department of Computer Science","Use as an advising interest area only where Morgan publicly frames it as a CS focus area.","https://www.morgan.edu/computer-science/degrees-and-programs"
Cloud Computing,"cloud computing;cloud;distributed systems;devops;infrastructure","COSC440;COSC420;COSC459","COSC220;COSC243;COSC310","Department of Computer Science","Aligned with Morgan's public Computer Science cloud-computing emphasis.","https://www.morgan.edu/computer-science/degrees-and-programs"
```

- [ ] **Step 2: Trim `cs_pathways.csv` so it stays as the advising-layer grouping file**

Update `cs_pathways.csv` only if needed so it complements `cs_focus_areas.csv` instead of duplicating all official metadata. Keep it focused on recommendation behavior.

- [ ] **Step 3: Sanity-check the new focus-area file**

Run:
```bash
Import-Csv C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\cs_focus_areas.csv | Format-Table focus_area,faculty_contact,related_courses -AutoSize
```

Expected: the file shows all intended CS focus areas with related-course mappings.

### Task 3: Expand CS catalog rows where focus-area advising depends on them

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\prerequisites.csv`

- [ ] **Step 1: Add any missing CS upper-level rows needed by the official focus areas**

If missing from `courses.csv`, add rows like:

```csv
COSC470,Information Assurance,Applied information assurance principles secure design and protection of computing assets.,3,Computer Science,400,Fall,Dr. Shuangbao Wang
COSC475,Data Mining,Study of data mining methods pattern discovery and knowledge extraction from large data sets.,3,Computer Science,400,Spring,Dr. Radhouane Chouchane
COSC480,Special Topics in Computer Science,Advanced topical study in emerging Computer Science areas aligned with faculty expertise and departmental focus.,3,Computer Science,400,Fall/Spring,Department of Computer Science
```

Only add rows that materially improve the official Morgan CS focus-area mapping and do not obviously invent a formal catalog beyond the current dataset’s level of detail.

- [ ] **Step 2: Add prerequisite rows for any new CS courses you add**

Example shape:

```csv
COSC470,COSC360; COSC459,Information assurance follows core security and networking preparation.
COSC475,COSC310; STAT302,Data mining is strongest after database and statistics preparation.
COSC480,COSC331; COSC350,Special topics should typically follow upper-level CS core preparation.
```

- [ ] **Step 3: Inspect the new or updated CS rows**

Run:
```bash
Import-Csv C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv | Where-Object {$_.department -eq 'Computer Science'} | Select-Object code,title,level | Format-Table -AutoSize
```

Expected: CS pathway-relevant upper-level rows appear cleanly and stay consistent with the existing dataset style.

### Task 4: Implement CS focus-area loading and recommendation depth

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\rag.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\schemas.py`

- [ ] **Step 1: Add a cached loader for `cs_focus_areas.csv` in `rag.py`**

Add a helper like:

```python
CS_FOCUS_AREAS_PATH = DATA_DIR / "cs_focus_areas.csv"

@lru_cache(maxsize=1)
def load_cs_focus_area_rows() -> tuple[dict[str, str], ...]:
    if not CS_FOCUS_AREAS_PATH.exists():
        return tuple()
    with CS_FOCUS_AREAS_PATH.open(newline="", encoding="utf-8") as file:
        return tuple(csv.DictReader(file))
```

- [ ] **Step 2: Add a richer CS focus-area recommendation builder**

Implement a helper that uses:
- focus-area keywords
- related courses
- foundational courses
- faculty contact
- student interest text
- remaining/completed courses

The return shape should support:
- focus area name
- recommended courses
- missing foundations
- relevant contact
- notes

- [ ] **Step 3: Extend the schema models for the richer focus-area output**

Add fields to support contact-aware focus-area results, for example by extending pathway recommendation output with an optional contact field.

- [ ] **Step 4: Update `get_degree_progress()` to use focus-area data for CS majors**

For Computer Science only:
- prefer official focus-area metadata for interest-sensitive recommendations
- still preserve the earlier CS pathway and capstone logic
- do not weaken existing generic recommendation behavior

### Task 5: Feed focus-area context into chat and verify end-to-end

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\chat.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py`

- [ ] **Step 1: Add focus-area details to the CS degree-progress context in chat**

Make the context include concise lines such as:

```text
- Computer Science focus-area suggestions:
  - Cybersecurity: recommended COSC360, COSC459. Relevant contact: Dr. Shuangbao Wang.
```

- [ ] **Step 2: Keep the student-facing reply natural**

Do not dump internal CSV data verbatim. Keep the extra context structured and concise so the AI can answer naturally.

- [ ] **Step 3: Run targeted tests for the CS focus-area behavior**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py -q
```

Expected: PASS for the new CS focus-area tests.

### Task 6: Final verification

**Files:**
- Verify only

- [ ] **Step 1: Run the full backend suite**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests -q
```

Expected: all backend tests pass.

- [ ] **Step 2: Run the compile check**

Run:
```bash
py -3.12 -m compileall C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app
```

Expected: compile completes without syntax errors.

- [ ] **Step 3: Commit the slice**

```bash
git add backend/data/cs_focus_areas.csv backend/data/courses.csv backend/data/prerequisites.csv backend/app/rag.py backend/app/schemas.py backend/app/chat.py backend/tests/test_rag.py backend/tests/test_chat.py docs/superpowers/specs/computer-science-catalog-depth-design.md docs/superpowers/plans/computer-science-catalog-depth-plan.md
git commit -m "Deepen Computer Science catalog guidance around Morgan focus areas"
```
