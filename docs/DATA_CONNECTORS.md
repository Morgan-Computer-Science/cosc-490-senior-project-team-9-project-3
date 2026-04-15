# Data Connectors Plan

## Goal

Define how student information should enter the advising system over time without tying the project too early to one campus platform.

## Recommended connector strategy

Use a hybrid model:

1. Manual import
- Best for development, demos, and early testing
- Students can paste transcript text or upload transcript-style files
- Already supported in the profile import flow

2. Canvas connector
- Best for current-course context
- Useful for:
  - enrolled courses
  - assignment load
  - current-semester activity
  - class-level context
- Not the best source of truth for official degree progress

3. WebSIS or SIS connector
- Best long-term source for:
  - official major
  - full transcript
  - academic standing
  - degree audit data
- Likely the correct source of truth for production-grade advising

## Why Canvas should not be the only source

Canvas is useful, but it is usually downstream from the student information system. That means it may reflect course activity well without representing the official academic record completely.

For this project, Canvas is a strong future connector for present-tense academic context, while WebSIS or the SIS should remain the better target for official program and transcript data.

## Current system state

The app now has a real connector registry in the backend and a connector surface in the profile import workflow.

Supported connectors:

- `manual`
- `canvas`
- `websis`

Each connector now exposes metadata about:

- status
- supported record types
- capabilities
- whether file upload is supported now
- whether authentication is required yet

The current product behavior is intentionally honest:

- `Manual` is available now
- `Canvas` supports export-style uploads today for current-course and schedule context, with direct sync planned later
- `WebSIS` supports export-style uploads today for official-record-style history and degree-audit context, with direct sync planned later

The import wizard still remains the active ingestion path, but connectors are now a first-class part of the product instead of just labels on a form.

## Connector roadmap

### Phase 1
- Manual import preview
- File-assisted transcript parsing
- Student confirmation before saving matched courses

### Phase 2
- OCR-backed transcript, schedule, and degree-audit ingestion
- Shared document workflow for profile imports and chat uploads
- Stronger confidence and source-awareness in import previews

### Phase 3
- Connector registry and integration metadata endpoints
- Frontend connector surface inside the import workflow
- Upload-assisted Canvas and WebSIS paths represented as real product connectors

### Future phase
- Real Canvas authenticated sync
- Real WebSIS or SIS authenticated sync
- Official course history and major sync into the normalized advising data layer

## Source-specific behavior today

### Canvas

Canvas-style imports are interpreted as present-tense academic context.

That means the system now prefers:

- planned or current courses
- schedule-style interpretation
- workload and enrollment cues when available

Canvas uploads are intentionally not treated as the primary source of completed-course history unless the content clearly shows that.

### WebSIS

WebSIS-style imports are interpreted as academic-record-style context.

That means the system now prefers:

- completed courses
- remaining or needed coursework
- degree-audit or official-record style summaries when the text supports that

WebSIS uploads are the stronger path for degree-progress style interpretation until real direct sync exists.

## Architecture implication

All imports and future syncs should normalize into the same internal academic-record shape:

- connector id
- course code
- source type
- confidence
- raw import summary
- record type
- detected document type when relevant

That keeps the rest of the advising system stable no matter where student data comes from.
