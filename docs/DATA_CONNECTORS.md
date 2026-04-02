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

The app now supports a source-aware import wizard with these import labels:

- `transcript_text`
- `manual`
- `canvas_export`
- `websis_export`

At the moment, all of them still flow through the same parsing pipeline, but the source labels prepare the project for real integrations later.

## Connector roadmap

### Phase 1
- Manual import preview
- File-assisted transcript parsing
- Student confirmation before saving matched courses

### Phase 2
- Canvas export ingestion
- Student can upload or authorize a current-course export
- Advisor uses current-course context in planning and wellness checks

### Phase 3
- SIS or WebSIS integration
- Pull official completed courses and major
- Reduce manual data entry
- Improve degree-audit reliability

## Architecture implication

All imports should normalize into the same internal completed-course format:

- course code
- source type
- confidence
- raw import summary

That keeps the rest of the advising system stable no matter where student data comes from.
