# Morgan High-Impact Undergraduate Expansion Design

## Goal
Expand the backend Morgan State advising dataset using official public undergraduate sources, prioritizing the programs most likely to appear in real advising questions, transcript imports, and degree-progress workflows.

This pass is strictly limited to undergraduate programs and courses. It does not attempt graduate coverage.

## Scope
Target the next highest-impact undergraduate programs first:
- Physics
- Philosophy
- Marketing
- Entrepreneurship
- Construction Management
- Interior Design

Tighten coverage where needed if official source material supports it:
- Finance
- Chemistry
- Economics
- Political Science

## Product Intent
This project is a Morgan State advising system, not a generic university chatbot. New data in this pass should improve the actual student experience in these existing product flows:
- advisor chat retrieval
- degree progress
- next-course recommendations
- transcript/import recognition
- source-aware connector imports

## Data Strategy
For each target program, add or improve four layers of data.

### 1. Program-level coverage
Capture:
- official undergraduate program name
- canonical major name used internally by the app
- department mapping
- school mapping when available
- official source URL

### 2. Department and advising coverage
Add or tighten:
- advising office or department contact path
- contact details when publicly available
- a concise overview grounded in the official Morgan framing
- source URL for traceability

### 3. Degree-requirement coverage
Add a realistic advising-oriented core requirement path that is sufficient for:
- progress tracking
- remaining-course identification
- next-course recommendation logic
- transcript and import matching

This pass should not pretend to reproduce a registrar-grade full audit when the public source does not support that level of detail.

### 4. Course and prerequisite coverage
Add the course rows and prerequisite relationships needed so the supported majors can be advised coherently.

This includes:
- missing course codes required by the new majors
- prerequisite links that materially affect sequencing quality
- course prefix normalization when older internal seed codes drift from official Morgan naming

## Architecture
Keep the same runtime model already established in the backend.

### Ingestion model
- continue using committed CSV-backed data at runtime
- continue using script-driven generation and normalization under `backend/scripts/`
- avoid live runtime scraping in the product

### Data model
Continue building on the existing normalized dataset shapes:
- `programs.csv`
- `departments.csv`
- `degree_requirements.csv`
- `courses.csv`
- `prerequisites.csv`
- `course_aliases.csv` when normalization drift needs explicit mapping

### Advising model
The new data must flow through the existing advising stack:
- `catalog` endpoints
- `rag` retrieval
- degree progress and recommendation logic
- transcript/import matching

## Source Policy
Use official Morgan public undergraduate sources only for this slice.

Priority sources include:
- undergraduate program pages
- department undergraduate pages
- academic catalog pages and official course detail pages
- official advising or department contact pages

Do not broaden this pass to unofficial mirrors or generic third-party school-summary sites.

## Testing and Verification
Add or update backend tests for:
- new programs appearing in catalog and retrieval surfaces
- degree progress working for the new majors
- any new course-code normalization rules
- any major-specific requirement paths introduced in this pass

Required verification before completion:
- targeted backend tests for new majors
- full backend test suite
- backend compile check

## Out of Scope
This slice does not include:
- graduate programs
- real Canvas or WebSIS sync
- department-by-department deep modeling across the whole university
- live AI reliability work
- frontend redesign

Those are separate next steps after this breadth slice.

## Expected Outcome
After this pass, more real Morgan undergraduate majors will be backed by:
- official program mapping
- department contact paths
- requirement coverage
- course and prerequisite data strong enough for meaningful advising

The advisor should feel more like a real Morgan State planning tool for a broader set of undergraduate paths, while staying grounded in official public source material.
