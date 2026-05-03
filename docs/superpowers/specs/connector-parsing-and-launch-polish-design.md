# Connector Parsing And Launch Polish Design

## Goal

Make Canvas and WebSIS imports behave like real source-specific product flows instead of generic uploads, then polish the connector experience so it feels launch-ready.

This phase builds on the existing OCR pipeline and connector registry. It should improve how the advisor understands source-specific files while keeping the product honest about what is upload-based today and what will require direct sync later.

## Why this phase exists

The app now has:

- shared OCR and document interpretation
- source-aware import labels
- a real connector registry
- a real connector surface in the profile/import workflow

What is still missing is source-specific intelligence.

Right now, Canvas and WebSIS uploads mostly pass through the same generic parsing pipeline. That is not enough for a launch-oriented product. Students need the system to understand that Canvas exports usually represent current-course context, while WebSIS exports are closer to official transcript and degree data.

## Recommended approach

Implement specialized parsing and interpretation layers for:

- Canvas exports
- WebSIS exports

Then polish the connector-facing UI and copy so the workflow feels product-ready.

This should be done in three steps:

1. Canvas export parsing
2. WebSIS export parsing
3. launch polish around connectors

## Scope

### In scope

- Source-specific parsing rules for Canvas-style uploads
- Source-specific parsing rules for WebSIS-style uploads
- Import preview behavior that differs intelligently by source
- Chat/upload behavior that uses source-specific context where appropriate
- Connector UI/copy polish in the existing profile/import workflow
- Tests for parsing behavior and import preview outputs

### Out of scope

- Real Canvas OAuth
- Real WebSIS authentication
- Background sync jobs
- Fake sync-history dashboards
- Full SIS integration

## Product behavior

### Canvas imports

Canvas-style imports should be treated as current academic context.

The system should prioritize extracting:

- current or planned courses
- schedule-like context
- assignment or workload signals when present

Canvas imports should lean toward helping the advisor answer questions like:

- What am I taking now?
- Is my schedule balanced?
- How heavy does this term look?
- What should I plan next semester based on current enrollment?

In the import preview, Canvas uploads should favor:

- planned/current courses
- schedule interpretation
- course-load context

They should not overconfidently mark everything as completed.

### WebSIS imports

WebSIS-style imports should be treated as the closest thing to official academic record data available in this project.

The system should prioritize extracting:

- completed courses
- major or program hints
- remaining or required courses
- degree-audit-like context

WebSIS imports should lean toward helping the advisor answer questions like:

- What have I already completed?
- What is still left for my degree?
- Does this look like an official program record or audit?

In the import preview, WebSIS uploads should favor:

- completed courses
- remaining/needed courses
- degree-audit interpretation

### Launch polish

The connector UI should make the product feel intentional and launch-ready.

That means:

- Canvas is described as current-course context
- WebSIS is described as official-record-style export support
- upload-based use today is clear
- direct sync later is clear
- no fake connection state or misleading actions

The existing profile/import experience should feel sharper, more trustworthy, and easier to understand.

## Architecture

### 1. Source-specific import interpretation

Extend the backend import pipeline so `canvas_export` and `websis_export` use source-specific interpretation rules on top of shared OCR extraction.

This should happen after text extraction and before the final preview payload is built.

The parser layer should be able to influence:

- detected document type
- summary
- confidence note
- completed course bucket
- planned/current bucket
- remaining/needed bucket

### 2. Canvas parser behavior

The Canvas path should look for cues such as:

- current enrollment wording
- assignment or course dashboard language
- schedule terminology
- course list patterns that imply active classes

It should produce a preview that emphasizes:

- planned/current courses
- schedule context
- workload-style interpretation

### 3. WebSIS parser behavior

The WebSIS path should look for cues such as:

- transcript wording
- audit wording
- official academic record language
- program/major mentions
- completed history and requirement sections

It should produce a preview that emphasizes:

- completed courses
- remaining requirements
- official-record-style interpretation

### 4. Connector-aware UI refinement

In the frontend profile/import area:

- connector cards should better explain what each source is best for
- source selection should feel more guided
- preview messaging should reflect connector intent more clearly
- helper copy should reduce ambiguity around what Canvas vs WebSIS means in practice

## Data flow

### Canvas import flow

1. Student chooses Canvas export import.
2. Student uploads or pastes export content.
3. OCR/text extraction runs.
4. Canvas-specific interpretation adjusts the preview.
5. Preview highlights current/planned courses and schedule context.
6. Student applies only the relevant completed-course data when appropriate.

### WebSIS import flow

1. Student chooses WebSIS export import.
2. Student uploads or pastes export content.
3. OCR/text extraction runs.
4. WebSIS-specific interpretation adjusts the preview.
5. Preview highlights completed courses and remaining/needed coursework.
6. Student applies completed-course data with stronger confidence.

## Error handling

The system should clearly handle:

- weak source-specific confidence
- exports that do not match the selected connector well
- files that look generic even after source selection
- partial extraction success

If confidence is weak, the app should say so clearly and avoid overstating certainty.

## Testing

This phase should include:

- backend parser tests for Canvas source behavior
- backend parser tests for WebSIS source behavior
- import preview tests showing different bucket behavior by source
- connector-aware preview tests for summary and confidence notes
- chat-related tests where source-specific interpretation affects advising context when relevant
- frontend build verification
- full backend test suite verification

## Success criteria

This phase is successful if:

- Canvas imports feel different from generic transcript uploads
- WebSIS imports feel different from generic transcript uploads
- import previews reflect source-specific meaning
- connector copy and UI feel more launch-ready
- the product remains honest about upload-based behavior versus direct-sync future plans

## Notes

This phase should improve real behavior, not just wording. The goal is for students and evaluators to feel that Canvas and WebSIS are meaningful product concepts already, even though live authenticated sync is still a future phase.
