# Computer Science Audit Frontend Design

## Goal
Surface the new Computer Science audit depth that already exists in the backend so students can actually benefit from it in the product. This phase should make the CS-specific audit interpretation visible in the current profile and degree-progress flow without cluttering the UI.

## Why This Phase Matters
The backend now provides a richer `cs_audit_summary` for Computer Science students, including:
- capstone readiness
- CS foundation and core progress
- math-support progress
- upper-level progress
- pathway direction
- unmapped CS courses
- concise summary lines

Right now that value is mostly invisible unless it indirectly changes chat quality. The frontend needs to expose it directly so students can understand their CS standing without guessing.

## Scope
This phase focuses only on surfacing the new CS audit depth in the existing frontend.

It will:
- show a CS audit summary inside the import preview when relevant
- show a persistent CS audit summary inside the degree-progress/profile area when relevant
- preserve the existing product layout and premium visual system

It will not:
- redesign the full profile experience from scratch
- add a new top-level route just for CS audit
- expose raw backend internals or debug-style output
- duplicate the CS audit summary in chat replies

## Placement
The CS audit summary should appear in two places.

### 1. Import Preview
When a user imports transcript, degree-audit, or WebSIS-style data and the backend returns `cs_audit_summary`, the preview should include a compact Computer Science interpretation section.

This is the most natural place to show the new backend work because it directly answers: “What did the system understand from my audit?”

### 2. Degree Progress Area
If the logged-in student major is Computer Science and the backend returns `cs_audit_summary` as part of degree progress, the profile page should show a persistent CS audit summary within the degree-progress area.

This ensures the student does not lose the interpretation after the preview is cleared.

## Content
The CS audit UI should show only the most useful student-facing information.

### Capstone Readiness
Display a clear status pill for capstone readiness:
- ready
- nearly ready
- not ready

If missing foundations exist, show them directly under the status.

### Audit Summary Lines
Display the backend-generated `summary_lines` as the human-friendly explanation block.
These should act like the short advising interpretation for the student.

### Bucketed Progress
Show grouped course chips or compact lists for:
- foundations
- core progression
- math support
- upper-level progress

Each group should visually separate:
- completed
- in progress
- remaining

Only show sections that actually contain data.

### Pathway Direction
If present, show:
- primary pathway direction
- aligned courses
- pathway notes when available

This should read like a planning signal, not like a declared concentration.

### Unmapped Courses
If present, show unmapped CS-coded courses in a separate “Needs advisor confirmation” block.
This should be visually subordinate to the main progress sections so it informs without alarming.

## Interaction Rules
- Show the CS audit block only when `cs_audit_summary` exists.
- Keep the import-preview version attached to the preview card.
- Keep the persistent version attached to the degree-progress card or the nearby profile progress area.
- Do not show the same large block multiple times on the same screen.
- Do not reintroduce visible chat metadata under assistant messages.

## Visual Direction
The new UI should match the current product styling:
- premium, clean, Morgan-branded interface
- compact cards and chips
- clear hierarchy
- no raw JSON or admin/debug styling

Suggested hierarchy:
1. capstone readiness
2. summary lines
3. grouped audit buckets
4. pathway direction
5. unmapped courses if needed

## Data Flow
The frontend should treat `cs_audit_summary` as optional data that may appear in:
- import preview payloads
- degree progress payloads

This phase should:
- extend the frontend data typing expectations informally through component logic
- render safely when the field is absent
- avoid breaking other majors

## Success Criteria
This phase is successful when:
- a CS student importing an audit/transcript sees a meaningful CS interpretation immediately
- a CS student viewing profile/degree progress sees a persistent summary of CS standing
- capstone readiness is clearly visible
- pathway direction is visible when available
- unmapped CS courses are shown honestly but unobtrusively
- the UI still feels like a launchable product, not a debugging panel

## Out of Scope
This phase does not include:
- Business or other department depth
- full transcript/audit visualization for every major
- new chat UI for audit details
- a separate page dedicated only to Computer Science audit review
