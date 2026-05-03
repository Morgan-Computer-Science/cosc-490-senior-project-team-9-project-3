# Presentation Flow Polish Plan

## Goal
Implement a tightly scoped polish pass for tomorrow's presentation by cleaning up the Course Catalog, Departments, and Degree Progress pages while fixing the most visible PDF/chat reliability gaps.

## Execution Order
1. Fix backend data and answer-path issues that are causing clearly broken behavior.
2. Improve the Degree Progress workflow so the new upload/preview/apply path exists where students expect it.
3. Clean the Course Catalog and Departments surfaces so the pages look intentional during the demo.
4. Run targeted verification and only then decide whether the README needs any small clarification updates.

## Step 1: Backend fixes
### 1.1 Course level filtering
- Update `backend/app/catalog.py` so level filtering uses the actual course level field instead of `code.startswith(level)`.
- Add or update catalog API tests for level-filter behavior.

### 1.2 Transcript summary extraction
- Inspect the existing attachment extraction path and add lightweight summary extraction for transcript-like documents.
- Recognize fields such as GPA and earned credits when clearly present.
- Extend schemas if the preview response needs to expose summary fields.

### 1.3 Better attachment-aware answering
- Improve the chat answer path so GPA-style questions prioritize extracted transcript summary fields before generic catalog retrieval.
- Keep the fallback path, but make the user-facing wording calmer and shorter.
- Preserve the existing grounded fallback if Gemini is unavailable.

## Step 2: Degree Progress workflow
### 2.1 Add an import surface
- Add a preview-first upload panel directly to `frontend/src/components/DegreeProgressView.jsx`.
- Reuse as much of the existing profile import logic as practical instead of duplicating the parsing contract.

### 2.2 Apply behavior
- Keep the flow as preview first, then apply recognized completed courses.
- Update parent wiring in `frontend/src/App.jsx` as needed so the Degree Progress page can trigger import preview and save completed courses.

### 2.3 Surface richer results
- Show detected document type, extraction summary, confidence note, and the completed/planned/remaining buckets.
- Show the CS audit summary when relevant.
- Show transcript summary fields such as GPA when present.

## Step 3: Catalog and Departments cleanup
### 3.1 Course Catalog
- Reduce visual clutter in the catalog card grid.
- Improve hierarchy so code/title/summary/credits are primary and secondary metadata is lighter.
- Keep search and level filtering visible and working together.

### 3.2 Departments
- Make department headers more stable with long labels.
- Wrap or clamp the major/program pill safely.
- Improve contact readability and reduce the sense of overflow.

## Step 4: Verification
### Backend
- Run targeted tests for catalog/chat/auth/attachment behavior.
- Run the full backend suite if the targeted tests pass.
- Run compile check.

### Frontend
- Run `npm run build`.
- Confirm the new Degree Progress upload flow compiles and receives the expected preview shape.

## Risks and boundaries
- Do not attempt Docker before the presentation.
- Do not do another large redesign.
- Keep fallback behavior honest even if live Gemini is still environment-limited.
- If the README already covers local run steps clearly, avoid unnecessary churn there.
