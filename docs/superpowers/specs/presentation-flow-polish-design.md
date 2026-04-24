# Presentation Flow Polish Design

## Goal
Polish the product surfaces that matter most for tomorrow's presentation:
- Course Catalog
- Departments
- Degree Progress
- PDF-backed chat and degree-progress import behavior
- live AI and fallback reliability presentation

This pass is not a broad redesign. It is a targeted product polish pass focused on reducing clutter, improving clarity, fixing obvious broken flows, and making uploaded PDF workflows feel more trustworthy.

## Why This Pass
The backend is now strong enough for the presentation, but several visible product issues still create risk:
- the Course Catalog reads like a wall of cards
- course level filtering appears broken
- Departments cards overflow and feel messy
- Degree Progress feels static instead of workflow-oriented
- transcript and Degree Works PDFs are useful in the backend but not surfaced cleanly on the Degree Progress page
- live AI fallback messaging is too prominent and GPA extraction from PDFs is too weak for transcript-style questions

The goal is to reduce demo friction and make the app feel more intentional in the exact flows that are most likely to be shown.

## Course Catalog Design

### Problems
- the catalog is visually dense and reads like a giant list
- too much metadata is shown at the same weight
- the level filter does not appear to work

### Direction
Rework the catalog into a more controlled browsing surface.

The page should:
- keep the top search and filter controls
- make the filter bar feel more deliberate and compact
- reduce metadata shown by default on each course card
- make the card hierarchy clearer:
  - course code
  - title
  - one-line summary
  - credits
  - secondary details in a lighter footer row

### Functional fixes
- fix level filtering so selecting 100 / 200 / 300 / 400 actually returns the right courses
- keep search working in combination with level filters

### Presentation outcome
The catalog should feel searchable and curated, not like a raw data dump.

## Departments Design

### Problems
- the current card grid is too dense
- long major/program labels overflow and break the layout
- contact details are not visually prioritized well

### Direction
Keep the department grid, but make the cards more disciplined.

The page should:
- clamp or wrap long department/major labels safely
- reduce header collisions between the department title and the meta pill
- make office, email, and phone easier to scan
- keep overview text readable without letting cards become visually messy

### Presentation outcome
Departments should feel like clean institutional cards, not like overflowing database records.

## Degree Progress Design

### Problems
- the page feels passive and static
- there is no direct upload workflow on the page itself
- the app already has import logic, but the user has to rely on Profile or chat instead of a purpose-built degree-progress action

### Direction
Turn Degree Progress into a light workflow surface.

### Upload workflow
Add a visible import panel directly on the Degree Progress page.
The flow should be:
1. choose or drag a Degree Works/transcript PDF
2. preview what the app found
3. review completed / planned / remaining buckets
4. apply recognized completed courses into tracked progress only after review

### Preview contents
The page should show:
- detected document type
- extraction summary
- confidence note if the file is unclear
- completed courses found
- planned/in-progress courses found
- remaining/needed courses found
- Computer Science audit summary when relevant

### Application behavior
- only completed courses are applied to tracked degree progress
- planned/current/remaining stay informational for now
- the upload panel should not replace chat upload support; it should provide a cleaner direct workflow for degree progress

### Presentation outcome
Degree Progress should feel like a real advising utility instead of just a display page.

## PDF and GPA Extraction Design

### Problems
- transcript-style questions like “what is my GPA?” are not being answered from the uploaded PDF context
- current extraction is heavily course-signal oriented
- summary fields like GPA are not being surfaced strongly enough to the answer path

### Direction
Improve document extraction and attachment-aware answer grounding for summary fields.

The backend should try to recognize and surface, when available:
- GPA
- earned credits
- standing / summary academic fields if clearly present

This does not require a full student-record model. It requires better extraction and better attachment context shaping for questions that target summary fields.

### Presentation outcome
If a transcript or audit PDF visibly includes GPA, the system should have a much better chance of answering from that upload instead of defaulting to generic catalog retrieval.

## Live AI and Fallback Design

### Problems
- the product still visibly falls back with a distracting message
- live AI availability is environment-sensitive
- if Gemini is unavailable, the answer should stay usable and less jarring

### Direction
Treat this as both a runtime check and a presentation polish issue.

### Live AI runtime work
- verify the backend environment used for the presentation is the Gemini-compatible one if possible
- if the current runtime cannot support Gemini cleanly, preserve the safe fallback path

### Fallback presentation work
- make the fallback message calmer and shorter
- prioritize the grounded answer itself over the warning
- avoid letting the warning dominate the whole reply block

### Attachment-aware fallback behavior
When a PDF is uploaded and the question is specifically about a summary field like GPA, the fallback path should use extracted attachment context first rather than jumping straight to generic catalog/course retrieval.

### Presentation outcome
Live AI should be used when available, but fallback should still feel intentional and product-quality if the runtime does not support Gemini cleanly during the demo.

## Backend and Frontend Scope

### Frontend files likely involved
- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/components/DegreeProgressView.jsx`
- `frontend/src/components/DepartmentsView.jsx`
- `frontend/src/components/ProfilePanel.jsx`
- `frontend/src/components/Chatbot.jsx`
- `frontend/src/api.js`

### Backend files likely involved
- `backend/app/catalog.py`
- `backend/app/auth.py`
- `backend/app/chat.py`
- `backend/app/attachments.py`
- `backend/app/ai_client.py`
- `backend/app/schemas.py`
- tests across chat/auth/catalog where needed

## Boundaries
This pass should not try to do:
- another full UI redesign
- another broad major-expansion phase
- a full academic-record system
- complicated connector or deployment work unrelated to tomorrow's presentation

## Success Criteria
This pass is successful when:
- the Course Catalog feels less cluttered and the level filter works
- Departments cards no longer overflow or look broken
- Degree Progress includes a preview-first PDF import workflow
- PDF uploads provide better answers for summary questions like GPA when the value is present
- fallback behavior is less jarring if live AI is unavailable
- the app feels cleaner and more presentation-ready without introducing risky last-minute complexity
