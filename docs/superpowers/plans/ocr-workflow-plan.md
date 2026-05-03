# OCR Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared OCR and document-analysis workflow that powers both profile import preview and advisor chat with stronger, structured document understanding.

**Architecture:** Keep one shared backend document pipeline inside the attachment layer, returning a structured analysis result instead of only raw extracted text. Use that shared result in both the import preview route and the chat route, then surface a cleaner OCR preview in the profile flow while keeping chat visually uncluttered.

**Tech Stack:** FastAPI, SQLAlchemy, Gemini file/vision extraction, React, existing upload endpoints, pytest, FastAPI TestClient.

---

## File Structure

**Create**
- `backend/tests/test_ocr_workflow.py`
  - dedicated OCR/document-analysis tests for the shared pipeline

**Modify**
- `backend/app/attachments.py`
  - replace the current attachment-only context with a richer shared document analysis result
- `backend/app/schemas.py`
  - extend import preview and chat response contracts to carry OCR-specific metadata cleanly
- `backend/app/auth.py`
  - update import preview to return the structured OCR analysis fields
- `backend/app/chat.py`
  - update chat attachment handling to consume the same structured OCR analysis result
- `frontend/src/api.js`
  - keep the API helpers aligned with any expanded OCR preview fields
- `frontend/src/components/ProfilePanel.jsx`
  - present detected type, extraction summary, and OCR confidence/ambiguity notes in the import preview
- `frontend/src/components/Chatbot.jsx`
  - improve attachment pre-send messaging using the richer OCR preview concepts without cluttering assistant messages
- `frontend/src/App.css`
  - style the new OCR preview states in the profile/import workflow and attachment review area

---

### Task 1: Introduce a shared backend OCR analysis model

**Files:**
- Modify: `backend/app/attachments.py`
- Test: `backend/tests/test_ocr_workflow.py`

- [ ] **Step 1: Add structured OCR result dataclasses**

```python
# backend/app/attachments.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DocumentCourseSignals:
    completed_codes: tuple[str, ...] = ()
    planned_codes: tuple[str, ...] = ()
    remaining_codes: tuple[str, ...] = ()
    matched_course_codes: tuple[str, ...] = ()
    unknown_course_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocumentAnalysis:
    filename: str
    content_type: str
    detected_document_type: str
    extraction_method: str
    extracted_text: Optional[str]
    context_text: str
    summary: str
    confidence_note: Optional[str] = None
    temp_path: Optional[str] = None
    signals: DocumentCourseSignals = DocumentCourseSignals()
```

- [ ] **Step 2: Add a helper that computes structured course signals from extracted text**

```python
# backend/app/attachments.py
from .rag import extract_attachment_course_signals, extract_known_course_codes, load_course_rows


def build_document_course_signals(extracted_text: str | None, document_type: str) -> DocumentCourseSignals:
    if not extracted_text:
        return DocumentCourseSignals()

    known_codes = {
        row.get("code", "").strip().upper()
        for row in load_course_rows()
        if row.get("code")
    }
    interpreted = extract_attachment_course_signals(extracted_text, document_type, limit=30)
    mentioned = extract_known_course_codes(extracted_text, limit=30)
    matched = tuple(sorted(code for code in mentioned if code in known_codes))
    unknown = tuple(sorted(code for code in mentioned if code not in known_codes))
    return DocumentCourseSignals(
        completed_codes=tuple(sorted(interpreted.completed_codes)),
        planned_codes=tuple(sorted(interpreted.planned_codes)),
        remaining_codes=tuple(sorted(interpreted.remaining_codes)),
        matched_course_codes=matched,
        unknown_course_codes=unknown,
    )
```

- [ ] **Step 3: Make the extraction pipeline return `DocumentAnalysis` with extraction metadata**

```python
# backend/app/attachments.py
analysis = DocumentAnalysis(
    filename=filename,
    content_type=content_type,
    detected_document_type=document_type,
    extraction_method="pdf_local" if extracted_text else "pdf_gemini",
    extracted_text=extracted_text,
    context_text=...,
    summary=...,
    confidence_note=None if extracted_text else "Readable text was limited; review carefully.",
    temp_path=temp_path,
    signals=build_document_course_signals(extracted_text, document_type),
)
```

Use the same idea for:
- text documents (`text_local`)
- images/screenshots (`image_gemini`)
- generic fallback (`none`)

- [ ] **Step 4: Write a failing OCR unit test**

```python
# backend/tests/test_ocr_workflow.py
from app.attachments import build_document_course_signals


def test_document_course_signals_extracts_known_codes():
    result = build_document_course_signals(
        "Completed: COSC 111. Planned next semester: MATH 141.",
        "transcript",
    )
    assert "COSC111" in result.matched_course_codes
```

- [ ] **Step 5: Run the single OCR test to verify red/green**

Run: `.
\.venv312\Scripts\python.exe -m pytest tests/test_ocr_workflow.py -q`
Expected: first red if signatures or imports are incomplete, then green after implementation.

- [ ] **Step 6: Commit**

```bash
git add backend/app/attachments.py backend/tests/test_ocr_workflow.py
git commit -m "Add a shared OCR document analysis model"
```

### Task 2: Wire the shared OCR result into import preview

**Files:**
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/auth.py`
- Modify: `frontend/src/api.js`
- Modify: `frontend/src/components/ProfilePanel.jsx`
- Modify: `frontend/src/App.css`
- Test: `backend/tests/test_auth.py`
- Test: `backend/tests/test_ocr_workflow.py`

- [ ] **Step 1: Extend the import preview schema to include OCR metadata**

```python
# backend/app/schemas.py
class CompletedCoursesImportPreview(BaseModel):
    import_source: str = "manual"
    detected_document_type: str = "text_document"
    extraction_method: str = "none"
    confidence_note: Optional[str] = None
    summary: Optional[str] = None
    matched_course_codes: list[str] = Field(default_factory=list)
    completed_course_codes: list[str] = Field(default_factory=list)
    planned_course_codes: list[str] = Field(default_factory=list)
    remaining_course_codes: list[str] = Field(default_factory=list)
    unknown_course_codes: list[str] = Field(default_factory=list)
    matched_count: int = 0
    source_summary: Optional[str] = None
```

- [ ] **Step 2: Return the OCR metadata from the import preview route**

```python
# backend/app/auth.py
attachment_analysis = await extract_attachment_context(attachment) if attachment else None
...
return schemas.CompletedCoursesImportPreview(
    import_source=normalized_import_source,
    detected_document_type=detected_document_type,
    extraction_method=attachment_analysis.extraction_method if attachment_analysis else "text_only",
    confidence_note=attachment_analysis.confidence_note if attachment_analysis else None,
    summary=attachment_analysis.summary if attachment_analysis else source_summary,
    matched_course_codes=list(attachment_analysis.signals.matched_course_codes) if attachment_analysis else matched,
    ...
)
```

- [ ] **Step 3: Add a failing route test for OCR metadata**

```python
# backend/tests/test_auth.py

def test_import_preview_returns_ocr_metadata(client, auth_headers):
    response = client.post(
        "/auth/me/completed-courses/import",
        headers=auth_headers,
        data={"import_source": "transcript_text", "source_text": "Completed: COSC 111"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "detected_document_type" in payload
    assert "extraction_method" in payload
```

- [ ] **Step 4: Show OCR summary and confidence in the profile import UI**

```jsx
// frontend/src/components/ProfilePanel.jsx
{importPreview ? (
  <div className="import-preview">
    <p className="panel-subtext">
      {importPreview.summary || importPreview.source_summary}
    </p>
    <div className="ocr-summary-row">
      <span className="meta-pill">{importDocumentLabels[importPreview.detected_document_type] || "Document"}</span>
      <span className="meta-pill">{importPreview.extraction_method}</span>
    </div>
    {importPreview.confidence_note ? (
      <p className="ocr-note">{importPreview.confidence_note}</p>
    ) : null}
    ...
  </div>
) : null}
```

- [ ] **Step 5: Add CSS for OCR preview summary states**

```css
/* frontend/src/App.css */
.ocr-summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ocr-note {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 237, 213, 0.7);
  border: 1px solid rgba(232, 119, 34, 0.2);
  color: #9a3412;
}
```

- [ ] **Step 6: Run auth and OCR tests**

Run: `.
\.venv312\Scripts\python.exe -m pytest tests/test_auth.py tests/test_ocr_workflow.py -q`
Expected: both suites pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas.py backend/app/auth.py backend/tests/test_auth.py backend/tests/test_ocr_workflow.py frontend/src/api.js frontend/src/components/ProfilePanel.jsx frontend/src/App.css
git commit -m "Surface OCR preview details in the import workflow"
```

### Task 3: Use the shared OCR result in chat

**Files:**
- Modify: `backend/app/chat.py`
- Modify: `backend/app/schemas.py`
- Modify: `frontend/src/components/Chatbot.jsx`
- Modify: `frontend/src/App.css`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Replace direct attachment-text assumptions with the shared analysis result**

```python
# backend/app/chat.py
attachment_analysis = await extract_attachment_context(attachment) if attachment else None
attachment_context = attachment_analysis
attachment_signals = attachment_analysis.signals if attachment_analysis else AttachmentCourseSignals(None, None, None)
```

Use the shared fields instead of re-deriving document signals from raw text wherever possible.

- [ ] **Step 2: Add chat response fields for OCR ambiguity when needed**

```python
# backend/app/schemas.py
class AdvisorInsights(BaseModel):
    ...
    attachment_summary: Optional[str] = None
    attachment_confidence_note: Optional[str] = None
```

```python
# backend/app/chat.py
advisor_insights = schemas.AdvisorInsights(
    ...,
    attachment_summary=attachment_analysis.summary if attachment_analysis else None,
    attachment_confidence_note=attachment_analysis.confidence_note if attachment_analysis else None,
)
```

- [ ] **Step 3: Add a failing chat test for OCR-backed attachment metadata**

```python
# backend/tests/test_chat.py

def test_chat_response_includes_attachment_summary(client, auth_headers):
    session_id = client.post("/chat/sessions", headers=auth_headers, json={"title": "OCR"}).json()["id"]
    response = client.post(
        f"/chat/sessions/{session_id}/messages",
        headers=auth_headers,
        data={"content": "Review this transcript"},
        files={"attachment": ("transcript.txt", BytesIO(b"Completed: COSC 111"), "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["advisor_insights"]["attachment_summary"]
```

- [ ] **Step 4: Improve the pre-send attachment UI in chat**

```jsx
// frontend/src/components/Chatbot.jsx
<div className="composer-footnote">
  {selectedAttachment ? (
    <span>
      {attachmentPreview}: {selectedAttachment.name}. The advisor will analyze the document before replying.
    </span>
  ) : ...}
</div>
```

Keep the chat message area clean. Do not add OCR debug blocks under assistant replies.

- [ ] **Step 5: Add any needed CSS support for attachment guidance text**

```css
/* frontend/src/App.css */
.composer-footnote {
  max-width: 768px;
  margin: 12px auto 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  text-align: center;
}
```

- [ ] **Step 6: Run chat and OCR tests**

Run: `.
\.venv312\Scripts\python.exe -m pytest tests/test_chat.py tests/test_ocr_workflow.py -q`
Expected: both suites pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/chat.py backend/app/schemas.py backend/tests/test_chat.py backend/tests/test_ocr_workflow.py frontend/src/components/Chatbot.jsx frontend/src/App.css
git commit -m "Ground chat uploads in the shared OCR workflow"
```

### Task 4: Strengthen extraction behavior and fallback notes

**Files:**
- Modify: `backend/app/attachments.py`
- Modify: `backend/tests/test_ocr_workflow.py`

- [ ] **Step 1: Add explicit extraction method and confidence rules for each path**

```python
# backend/app/attachments.py
if content_type == PDF_MIME_TYPE or filename.lower().endswith(".pdf"):
    extraction_method = "pdf_local"
    if not extracted_text:
        extraction_method = "pdf_gemini"
...
confidence_note = (
    None
    if extracted_text and len(extracted_text.strip()) > 80
    else "Extraction was limited. Review the original document before making important academic decisions."
)
```

- [ ] **Step 2: Add OCR workflow tests for low-confidence paths**

```python
# backend/tests/test_ocr_workflow.py
from io import BytesIO
import asyncio

from app.attachments import extract_attachment_context


class DummyUpload:
    def __init__(self, filename, content_type, payload):
        self.filename = filename
        self.content_type = content_type
        self._payload = payload

    async def read(self):
        return self._payload

    async def close(self):
        return None


def test_text_attachment_returns_structured_analysis():
    upload = DummyUpload("transcript.txt", "text/plain", b"Completed: COSC 111")
    analysis = asyncio.run(extract_attachment_context(upload))
    assert analysis.detected_document_type in {"transcript", "text_document"}
    assert analysis.extraction_method == "text_local"
    assert "COSC111" in analysis.signals.matched_course_codes


def test_unsupported_attachment_is_rejected():
    upload = DummyUpload("bad.exe", "application/octet-stream", b"fake")
    with pytest.raises(Exception):
        asyncio.run(extract_attachment_context(upload))
```

- [ ] **Step 3: Run the OCR-only test suite**

Run: `.
\.venv312\Scripts\python.exe -m pytest tests/test_ocr_workflow.py -q`
Expected: OCR tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/attachments.py backend/tests/test_ocr_workflow.py
git commit -m "Clarify OCR extraction methods and confidence notes"
```

### Task 5: Run the full verification pass

**Files:**
- Verify only

- [ ] **Step 1: Run the full backend test suite**

Run: `.
\.venv312\Scripts\python.exe -m pytest tests -q`
Expected: all backend tests pass.

- [ ] **Step 2: Run the frontend build**

Run: `npm.cmd run build`
Expected: Vite build succeeds.

- [ ] **Step 3: Run backend compile verification**

Run: `py -3.12 -m compileall app`
Expected: no compile errors.

- [ ] **Step 4: Check git status for only expected OCR workflow changes**

Run: `git status --short`
Expected: only the OCR-related backend/frontend files are modified.

- [ ] **Step 5: Commit the OCR workflow sweep**

```bash
git add backend/app backend/tests frontend/src docs/superpowers/specs/ocr-workflow-design.md docs/superpowers/plans/ocr-workflow-plan.md
git commit -m "Build a shared OCR workflow for imports and chat"
```
