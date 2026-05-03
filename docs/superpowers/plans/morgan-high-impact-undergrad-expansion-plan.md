# Morgan High-Impact Undergraduate Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Morgan State backend dataset for the next highest-impact undergraduate majors using official public undergraduate sources, while improving advising usefulness in degree progress, imports, and chat retrieval.

**Architecture:** Build on the existing CSV-backed catalog model by adding the next batch of undergraduate programs, department contacts, requirement paths, course rows, and prerequisites. Keep runtime behavior simple and fast by updating committed datasets plus retrieval logic only where needed, and verify every addition through backend tests before moving on.

**Tech Stack:** FastAPI, Python 3.12, pytest, CSV-backed data files, existing Morgan RAG/catalog backend

---

### Task 1: Lock Scope and Baseline Data Gaps

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py`

- [ ] **Step 1: Write failing degree-progress tests for the next target majors**

```python
def test_degree_progress_supports_next_high_impact_programs():
    physics = get_degree_progress("Physics", [])
    philosophy = get_degree_progress("Philosophy", [])
    marketing = get_degree_progress("Marketing", [])

    assert "PHYS201" in physics["required_courses"]
    assert "PHIL201" in philosophy["required_courses"]
    assert "MKTG331" in marketing["required_courses"]
```

- [ ] **Step 2: Write failing catalog-contact tests for department coverage**

```python
def test_catalog_departments_include_new_high_impact_program_contacts(client, auth_headers):
    response = client.get("/catalog/departments", headers=auth_headers)
    rows_by_major = {row["major"]: row for row in response.json()}

    assert rows_by_major["Physics"]["email"]
    assert rows_by_major["Philosophy"]["email"]
    assert rows_by_major["Construction Management"]["office"]
```

- [ ] **Step 3: Run the tests to verify they fail for the right reason**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py -q
```

Expected: FAIL because the new majors are not fully modeled yet.

- [ ] **Step 4: Commit the red test checkpoint**

```bash
git add backend/tests/test_rag.py backend/tests/test_catalog.py
git commit -m "Add failing tests for the next Morgan program slice"
```

### Task 2: Expand Program and Department Coverage for the New Slice

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\scripts\build_program_catalog.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\programs.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\departments.csv`

- [ ] **Step 1: Add official-contact overrides for the next target programs**

```python
DEPARTMENT_OVERRIDES.update(
    {
        "Physics": {
            "office": "Key Hall 213",
            "email": "physicsdept@morgan.edu",
            "phone": "443-885-3118",
            "overview": "Physics advises students on theoretical and applied physics study, laboratory progression, research preparation, and quantitative problem-solving.",
            "source_url": "https://www.morgan.edu/physics-and-engineering-physics/undergraduate-programs",
        },
        "Philosophy": {
            "office": "Holmes Hall 407",
            "email": "philosophydept@morgan.edu",
            "phone": "443-885-3185",
            "overview": "Philosophy advises students on ethics, logic, religion, critical reasoning, and preparation for law, graduate school, and public service pathways.",
            "source_url": "https://www.morgan.edu/philosophy-and-religious-studies",
        },
        "Construction Management": {
            "office": "CBEIS 242",
            "email": "constructionmanagement@morgan.edu",
            "phone": "443-885-1952",
            "overview": "Construction Management advises students on project delivery, estimating, scheduling, construction technology, and professional practice in the built environment.",
            "source_url": "https://www.morgan.edu/construction-management",
        },
        "Interior Design": {
            "office": "Banneker Hall 138",
            "email": "interiordesign@morgan.edu",
            "phone": "443-885-3475",
            "overview": "Interior Design advises students on studio progression, materials, space planning, and professional preparation for interior environments.",
            "source_url": "https://www.morgan.edu/undergraduate-design",
        },
        "Marketing": {
            "office": "Earl G. Graves School 311",
            "email": "marketing@morgan.edu",
            "phone": "443-885-3407",
            "overview": "Marketing advises students on branding, consumer insight, strategy, analytics, and preparation for internships in business and communication-focused industries.",
            "source_url": "https://www.morgan.edu/school-of-business-and-management/academics/undergraduate-programs",
        },
        "Entrepreneurship": {
            "office": "Earl G. Graves School 311",
            "email": "entrepreneurship@morgan.edu",
            "phone": "443-885-3407",
            "overview": "Entrepreneurship advises students on venture creation, innovation, small-business strategy, and applied business development planning.",
            "source_url": "https://www.morgan.edu/school-of-business-and-management/academics/undergraduate-programs",
        },
    }
)
```

- [ ] **Step 2: Regenerate programs and departments from the updated script**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\scripts\build_program_catalog.py
```

Expected: `programs.csv` and `departments.csv` rewrite successfully.

- [ ] **Step 3: Inspect the regenerated rows for the new target majors**

Run:
```bash
Import-Csv C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\departments.csv | Where-Object {$_.major -in @('Physics','Philosophy','Construction Management','Interior Design','Marketing','Entrepreneurship')} | Format-Table major,email,phone,office,source_url -AutoSize
```

Expected: each targeted major shows a non-empty contact path.

- [ ] **Step 4: Commit the updated official program/department coverage**

```bash
git add backend/scripts/build_program_catalog.py backend/data/programs.csv backend/data/departments.csv
git commit -m "Add official contact coverage for more Morgan programs"
```

### Task 3: Add Course and Prerequisite Coverage for the New Programs

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\prerequisites.csv`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\course_aliases.csv` (only if an official-prefix alias is needed)

- [ ] **Step 1: Add the missing core course rows for the new target majors**

```csv
PHYS201,Modern Physics,Study of relativity quantum foundations and early modern physics experiments.,3,Physics,200,Fall,Dr. Daniel Thompson
PHYS310,Electromagnetism,Electric and magnetic fields Maxwell relationships and applied physical modeling.,3,Physics,300,Fall,Dr. Daniel Thompson
PHYS320,Thermodynamics and Statistical Physics,Energy entropy heat engines and statistical models of physical systems.,3,Physics,300,Spring,Dr. Daniel Thompson
PHYS401,Senior Physics Seminar,Capstone-style research and presentation course for advanced undergraduate physics majors.,3,Physics,400,Spring,Dr. Daniel Thompson
PHIL201,Logic,Critical reasoning symbolic logic and argument analysis for philosophical and interdisciplinary study.,3,Philosophy,200,Fall/Spring,Dr. Monica Evans
PHIL310,Social and Political Philosophy,Study of justice rights institutions and social thought in philosophical traditions.,3,Philosophy,300,Fall,Dr. Monica Evans
PHIL330,Philosophy of Religion,Examination of philosophical questions surrounding religion belief and religious experience.,3,Philosophy,300,Spring,Dr. Monica Evans
PHIL401,Senior Seminar in Philosophy,Capstone-style writing and seminar discussion for advanced philosophy majors.,3,Philosophy,400,Spring,Dr. Monica Evans
CMGT210,Construction Materials and Methods,Introduction to construction systems materials methods and field documentation.,3,Construction Management,200,Fall,Prof. Leonard Harris
CMGT220,Construction Estimating,Fundamentals of quantity takeoff cost estimation and bid preparation in construction projects.,3,Construction Management,200,Spring,Prof. Leonard Harris
CMGT310,Construction Scheduling and Control,Project scheduling resource coordination and progress control for construction delivery.,3,Construction Management,300,Fall,Prof. Leonard Harris
CMGT410,Construction Project Management,Integrated management of contracts teams risk and delivery performance in construction projects.,3,Construction Management,400,Spring,Prof. Leonard Harris
INTD210,Interior Design Studio I,Studio-based introduction to interior space planning representation and design process.,4,Interior Design,200,Fall,Prof. Camille Porter
INTD220,Interior Materials and Finishes,Study of interior materials finishes and specification decisions for designed environments.,3,Interior Design,200,Spring,Prof. Camille Porter
INTD310,Interior Design Studio II,Continuation of studio work with deeper emphasis on user needs codes and systems integration.,4,Interior Design,300,Fall,Prof. Camille Porter
INTD410,Professional Practice in Interior Design,Professional standards documentation and project coordination for interior design practice.,3,Interior Design,400,Spring,Prof. Camille Porter
ENTR300,Entrepreneurship and Venture Creation,Development of venture concepts customer validation and business-model formation.,3,Entrepreneurship,300,Fall,Dr. Nia Roberts
ENTR410,Small Business Strategy,Applied strategy growth planning and entrepreneurial decision-making for venture leadership.,3,Entrepreneurship,400,Spring,Dr. Nia Roberts
```

- [ ] **Step 2: Add prerequisite relationships that materially improve planning quality**

```csv
PHYS201,PHYS102; MATH241,Modern physics follows the introductory physics sequence and calculus preparation.
PHYS310,PHYS102; MATH243,Electromagnetism is strongest after the introductory physics sequence and multivariable calculus.
PHYS320,PHYS102; MATH243,Thermodynamics and statistical physics benefit from physics foundations and multivariable calculus.
PHYS401,PHYS201; PHYS310,Senior seminar should follow upper-level physics preparation.
PHIL310,PHIL101,Social and political philosophy is strongest after introductory philosophical foundations.
PHIL330,PHIL101,Philosophy of religion follows the introductory philosophy survey.
PHIL401,PHIL201; PHIL310,Senior seminar should follow logic and upper-level philosophy preparation.
CMGT220,CMGT210,Estimating follows the introduction to construction materials and methods.
CMGT310,CMGT220,Construction scheduling is strongest after early estimating and project foundations.
CMGT410,CMGT310,Construction project management follows scheduling and control preparation.
INTD220,INTD210,Interior materials and finishes follows the first interior design studio.
INTD310,INTD210,The second interior design studio follows the first studio sequence.
INTD410,INTD310,Professional practice follows the upper-level studio sequence.
ENTR300,MGMT220; MKTG210,Venture creation is strongest after basic management and marketing preparation.
ENTR410,ENTR300,Small business strategy follows venture-creation coursework.
```

- [ ] **Step 3: Run a quick inspection for the new rows**

Run:
```bash
Import-Csv C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\courses.csv | Where-Object {$_.code -in @('PHYS201','PHIL201','CMGT210','INTD210','ENTR300')} | Format-Table code,title,department -AutoSize
```

Expected: each new course appears with the correct department.

- [ ] **Step 4: Commit the course and prerequisite additions**

```bash
git add backend/data/courses.csv backend/data/prerequisites.csv backend/data/course_aliases.csv
git commit -m "Add course coverage for the next Morgan advising majors"
```

### Task 4: Add Degree-Requirement Paths for the New Programs

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\degree_requirements.csv`
- Test: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py`

- [ ] **Step 1: Add advising-oriented requirement paths for the new majors**

```csv
Physics,Physics,"PHYS101; PHYS102; PHYS201; PHYS310; PHYS320; PHYS401; MATH141; MATH241; MATH243; CHEM101","Morgan's physics program emphasizes mathematical preparation, laboratory science, and advanced physical reasoning for research and technical careers.","Stay on pace through calculus and the introductory physics sequence so upper-level theory and seminar work remain accessible."
Philosophy,Philosophy,"PHIL101; PHIL201; PHIL220; PHIL310; PHIL330; PHIL401; ENGL101; ENGL102","Morgan's philosophy study emphasizes ethics, logic, religion, and advanced critical reasoning useful for law, public service, and graduate study.","Take logic and writing-intensive coursework early so upper-level theory and seminar work are easier to sequence."
Marketing,Business Administration,"ACCT201; ECON201; MGMT220; MKTG210; MKTG331; STAT302; ENGL101; ENGL102; COMM200","Morgan marketing students build on business fundamentals, communication, and data-informed market strategy.","Complete the business core early so upper-level marketing strategy and internship planning stay flexible."
Entrepreneurship,Business Administration,"ACCT201; ECON201; MGMT220; MKTG210; ENTR300; ENTR410; STAT302; ENGL101; ENGL102","Morgan entrepreneurship students combine business fundamentals, venture design, and practical strategy for new enterprise development.","Build the management, marketing, and accounting base early so venture-creation courses have enough context to be useful."
Construction Management,Construction Management,"CMGT210; CMGT220; CMGT310; CMGT410; MATH141; PHYS101; ENGL101; COMM200","Morgan construction management students progress through materials, estimating, scheduling, and project delivery preparation.","Treat the construction sequence as a chain and avoid delaying estimating or scheduling if you want smoother upper-level planning."
Interior Design,Interior Design,"INTD210; INTD220; INTD310; INTD410; ARCH101; ARCH220; ENGL101; COMM200","Morgan interior design students need steady studio progression plus materials, documentation, and professional-practice readiness.","Use studio courses as anchors each term and avoid delaying materials or professional-practice work."
```

- [ ] **Step 2: Run the degree-progress tests for the expanded major set**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py -q
```

Expected: PASS for the new degree-progress coverage assertions.

- [ ] **Step 3: Commit the new requirement paths**

```bash
git add backend/data/degree_requirements.csv backend/tests/test_rag.py
git commit -m "Add requirement paths for more Morgan undergraduate majors"
```

### Task 5: Verify Retrieval, Imports, and Catalog Surfaces End-to-End

**Files:**
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_auth.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py`
- Modify: `C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py`

- [ ] **Step 1: Add retrieval coverage for at least one of the new majors**

```python
def test_retrieve_relevant_documents_supports_construction_management_queries():
    docs = retrieve_relevant_documents(
        "What construction estimating and scheduling classes should I take next?",
        user_major="Construction Management",
        top_k=5,
    )

    assert docs
    assert any((doc.major or "") == "Construction Management" for doc in docs)
```

- [ ] **Step 2: Add import normalization coverage for any new alias or course-family behavior if needed**

```python
def test_import_preview_recognizes_new_political_science_codes(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={
            "import_source": "websis_export",
            "source_text": "Completed Courses: POSC 101, POSC 201",
        },
    )

    payload = response.json()
    assert {"POSC101", "POSC201"}.issubset(set(payload["completed_course_codes"]))
```

- [ ] **Step 3: Run the focused verification set**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_auth.py C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_catalog.py C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py -q
```

Expected: PASS.

- [ ] **Step 4: Commit the retrieval/import verification work**

```bash
git add backend/tests/test_auth.py backend/tests/test_catalog.py backend/tests/test_rag.py
git commit -m "Verify new Morgan advising coverage end to end"
```

### Task 6: Run Full Verification and Prepare Handoff

**Files:**
- No code changes expected unless verification reveals a real issue

- [ ] **Step 1: Run the full backend test suite**

Run:
```bash
C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\.venv312\Scripts\python.exe -m pytest C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests -q
```

Expected: all tests pass.

- [ ] **Step 2: Run the backend compile check**

Run:
```bash
py -3.12 -m compileall app
```

Expected: `Listing 'app'...` with no errors.

- [ ] **Step 3: Inspect the working tree before final handoff**

Run:
```bash
git -c safe.directory=C:/Users/great/Desktop/cosc-490-senior-project-team-9-project-3 -C C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3 status --short
```

Expected: only the files intentionally changed in this plan are listed.

- [ ] **Step 4: Final commit for the slice**

```bash
git add backend/app/auth.py backend/app/rag.py backend/data/courses.csv backend/data/degree_requirements.csv backend/data/departments.csv backend/data/prerequisites.csv backend/data/course_aliases.csv backend/scripts/build_program_catalog.py backend/tests/test_auth.py backend/tests/test_catalog.py backend/tests/test_rag.py
git commit -m "Expand advising coverage for more Morgan undergraduate majors"
```
