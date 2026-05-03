# Presentation Major Enrichment Design

## Goal

Tighten the demo experience for tomorrow by improving three visible product behaviors without opening a risky full-catalog expansion pass:

1. Make six priority majors feel intentionally browseable in the Course Catalog.
2. Reduce the large `Needs confirmation` block that appears when importing the user's real Morgan PDF.
3. Make casual chat prompts behave like normal conversation instead of immediately dumping advising context.

## Priority Majors

This pass focuses only on these majors:

- Computer Science
- Information Science
- Cloud Computing
- Nursing
- Biology
- Psychology

These were chosen because they give the strongest presentation coverage across technical and health/science advising while overlapping with the majors already deepened in the backend.

## Scope

### In scope

- Targeted course-data enrichment for the six priority majors
- Catalog filtering improvements for those six majors so browsing feels major-specific
- Transcript import cleanup driven by the user's real PDF and the specific unknown course codes it surfaces
- Casual small-talk detection and lightweight friendly replies in chat
- Tests for new catalog filtering behavior and small-talk handling

### Out of scope

- Full Morgan catalog completion
- Every elective for every major
- Another broad public-source ingestion sweep across the university
- Major frontend redesign beyond the existing catalog and chat polish already in flight

## Product Behavior

### 1. Course Catalog for the six majors

The Course Catalog major filter should feel like a major browser, not a degree-audit dump and not a broad department browser.

For the six priority majors:

- Selecting the major should show the dominant course family for that major.
- Combining the major with a level should only show courses that are clearly part of that major family and level.
- The result set should not include unrelated support courses, general education, or adjacent-department rows simply because those classes appear on a degree requirements sheet.

Examples:

- `Computer Science + 300 level` should return only CS 300-level courses.
- `Information Science + All levels` should stay on the INSS family.
- `Biology + 100 level` should stay in the BIOL family.

For majors that are currently sparse, the backend dataset should be enriched enough that the filter does not look empty or obviously unfinished in the demo.

## 2. Transcript import cleanup

The real Morgan PDF should be treated as the target sample for this pass.

The import preview should:

- Recognize as many course codes from that document as we can verify today.
- Move those codes out of `Needs confirmation` and into the correct bucket where possible.
- Leave only a very small remainder in `Needs confirmation`, ideally none for the major courses relevant to the demo.

The cleanup should prioritize:

- priority-major course codes
- codes visible in the user's actual PDF
- codes that influence the degree progress and CS demo story

We should not guess at codes we cannot verify. If something remains unresolved, it should stay visible rather than be silently misclassified.

## 3. Casual chat behavior

The advisor should recognize small-talk prompts before applying the major-aware advising stack.

Triggers include common greetings and casual questions such as:

- hello
- hi
- how are you
- what's up
- good morning

For those prompts, the response should:

- be brief
- be friendly
- avoid dumping degree progress, recommendations, or department-specific context unless the user actually asks for advising help

Example behavior:

- `Hello how are you?` -> short conversational reply plus a gentle invitation to ask an advising question

This should improve the demo feel without weakening the advising logic for real academic questions.

## Backend Design

### Catalog filtering

The existing major filter should be tightened so it operates on a major's dominant course family rather than broad department labels or every support course in the degree requirements table.

Expected behavior:

- Resolve aliases such as `Information Science` -> `Information Systems`.
- Determine the dominant course prefix family for the selected major.
- Filter the catalog to those course families, then apply the selected level.

This keeps the major filter aligned with what a student expects when browsing by major.

### Dataset enrichment

For the six priority majors, add missing verified course rows needed to make browsing and import recognition feel complete enough for the demo.

Priority order:

1. Computer Science
2. Information Science
3. Cloud Computing
4. Nursing
5. Biology
6. Psychology

Each new course row should include at minimum:

- code
- title
- department
- level
- credits when known
- semester/instructor only when reasonably supported by current data

Accuracy matters more than filling every optional field.

### Transcript import

Use the real PDF unknown list as the working checklist.

For each code:

- verify whether it belongs in the catalog data
- add or map it if it is a real Morgan course we can support
- allow the import preview to classify it correctly on the next pass

### Chat small-talk path

Add a lightweight pre-check before the normal advising flow:

- detect common greeting/small-talk prompts
- return a short conversational response
- do not attach degree-progress summaries or retrieved course dumps

This logic should stay narrow so it does not steal real advising questions away from the normal flow.

## Testing

Add or update tests for:

- major-filter behavior for the six priority majors, especially Computer Science and Information Science
- level + major combinations returning only major-family rows
- small-talk prompts producing conversational replies instead of advising dumps
- transcript import recognition for newly added codes where feasible

Run:

- targeted backend tests for catalog, chat, and import behavior
- full backend suite
- frontend build

## Success Criteria

This pass is successful if:

- the six priority majors no longer look empty or obviously wrong in the Course Catalog
- the user's real PDF import shows a dramatically smaller `Needs confirmation` list
- casual greetings in chat feel natural instead of overly academic
- existing advising behavior for the already-deepened majors remains stable
