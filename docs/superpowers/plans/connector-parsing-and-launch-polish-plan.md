# Connector Parsing And Launch Polish Plan

## Goal

Implement source-specific Canvas and WebSIS import behavior, then polish the connector-facing product experience so it feels launch-ready while remaining honest about upload-based use today.

## Phase breakdown

### 1. Canvas parsing
- Add tests for Canvas-specific import preview behavior.
- Extend backend import interpretation so `canvas_export` favors:
  - planned/current courses
  - schedule context
  - workload-oriented summary/confidence text
- Keep Canvas from over-classifying current classes as completed.

### 2. WebSIS parsing
- Add tests for WebSIS-specific import preview behavior.
- Extend backend import interpretation so `websis_export` favors:
  - completed courses
  - remaining/needed courses
  - official-record-style summary/confidence text
- Allow WebSIS inputs to influence degree-progress style interpretation more strongly.

### 3. Shared import pipeline cleanup
- Refactor source-specific logic into focused helpers instead of burying it in one route.
- Make sure shared OCR extraction remains the base layer and source-specific interpretation only adjusts the final analysis.

### 4. Connector launch polish
- Improve connector card copy and source-selection guidance in the profile/import UI.
- Clarify what Canvas is best for versus WebSIS.
- Tighten import helper copy, preview messages, and empty states.

### 5. Documentation
- Update connector docs and README if needed so the product story matches the new behavior.

### 6. Verification
- Run focused parser/import tests first.
- Run the full backend test suite.
- Run backend compile check.
- Run frontend build.

## Implementation order

1. Add failing Canvas import tests
2. Implement Canvas-specific parsing behavior
3. Add failing WebSIS import tests
4. Implement WebSIS-specific parsing behavior
5. Refactor shared import interpretation helpers
6. Polish connector and import UI copy/presentation
7. Update docs
8. Run verification

## Guardrails

- Do not fake live sync
- Do not turn Canvas into an official transcript source
- Do not turn WebSIS into guaranteed perfect official data
- Do not break manual or OCR-based imports already working today
- Keep source-specific behavior transparent and confidence-aware

## Success criteria

- Canvas and WebSIS previews differ meaningfully
- Canvas emphasizes current/planned context
- WebSIS emphasizes completed/remaining context
- connector UI feels more informative and launch-ready
- backend and frontend verification remain green
