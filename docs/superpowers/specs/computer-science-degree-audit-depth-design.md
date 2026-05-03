# Computer Science Degree-Audit Depth Design

## Goal
Deepen the Morgan State Computer Science advising backend so uploaded transcripts and degree-audit documents can be interpreted like a real CS advising workflow instead of a generic remaining-course list. This phase should make the system substantially better at understanding CS audit structure, capstone readiness, pathway direction, and the difference between completed, in-progress, remaining, and unmapped coursework.

## Why This Phase Matters
The current backend already supports:
- OCR and audit-style document parsing
- CS pathway recommendations
- COSC490 readiness checks
- CS focus-area guidance

What is still missing is a CS-specific audit interpretation layer that can turn raw audit signals into a trustworthy, structured advising picture. Right now the system can recognize courses and produce degree progress, but it does not yet interpret a CS audit with enough nuance to feel like a department-aware degree review.

This phase closes that gap.

## Scope
This phase will focus on Computer Science only.

It will do two things deeply:
1. Improve CS audit accuracy to the greatest practical extent within the current public-data and OCR-based system.
2. Improve student-facing clarity by generating strong CS-specific audit summaries for import previews and richer CS context for chat.

This phase will not yet try to build a perfect registrar-grade audit engine for every edge case or extend the same level of audit depth to non-CS majors.

## Architecture
Add a dedicated Computer Science audit interpretation layer on top of the existing OCR/import and degree-progress stack.

This layer should:
- consume recognized course signals from transcript and degree-audit parsing
- classify CS-related coursework into advising buckets
- evaluate readiness for upper-level work and capstone timing
- infer likely CS pathway direction from completed and in-progress upper-level work
- expose a structured CS audit interpretation that can be reused by both import preview and chat

The generic advising engine remains in place for all majors. The CS audit layer activates when the user major is Computer Science or the uploaded record clearly reflects a CS audit path.

## CS Audit Interpretation Model
The CS audit layer should generate a structured interpretation with at least these categories:

- completed courses
- in-progress courses
- remaining courses
- unmapped or unknown courses
- foundation status
- core progression status
- capstone readiness status
- pathway/elective leaning
- strongest next-step recommendations

### Foundation Status
The system should explicitly evaluate the early backbone of the CS path, including:
- introductory programming progression
- systems/data-structure foundations
- math/stat support that upper-level CS depends on

This should let the advisor tell whether the student has truly built the base needed for deeper CS work.

### Core Progression Status
The system should identify:
- which core CS requirements appear complete
- which are still missing
- which in-progress items are already helping unlock later work
- which upper-level recommendations would be premature

The goal is to move from a flat checklist to a real progression view.

### Capstone Readiness
The system should evaluate COSC490 readiness more deeply than a simple required/missing check.

It should determine whether the student:
- is clearly ready
- is close but still missing key foundations
- is not ready because the core backbone is still too thin

This readiness view should be tied to actual CS sequencing rather than broad generic degree progress alone.

### Pathway and Elective Interpretation
The system should infer which CS directions the student’s existing coursework most strongly aligns with. These pathway signals should be grounded in the CS focus-area work already added to the backend.

Target internal pathway groupings include:
- AI and Data
- Cybersecurity
- Cloud and Systems
- Software Engineering

This phase should not pretend these are official transcript concentrations unless Morgan explicitly labels them that way. They are internal advising lenses used to improve planning quality.

### Mismatch and Unmapped Course Handling
The system should keep unknown or unmapped CS-related courses visible instead of discarding them.

If the parser recognizes CS-style codes or record entries that do not yet map cleanly into the dataset, the audit interpretation should surface that clearly so:
- the student-facing summary stays honest
- future dataset improvements remain easy to identify

## Student-Facing Output
This phase should improve clarity without cluttering the UI.

### Import Preview
The CS import/audit preview should gain a compact CS-specific interpretation section that explains:
- how far along the student appears in the CS path
- whether foundations are solid or still incomplete
- whether capstone timing looks reasonable
- which direction the student’s upper-level record is leaning toward
- whether any recognized CS items still need advisor confirmation

This should be concise and polished, not a dump of raw backend fields.

### Chat Context
When a CS student uploads an audit/transcript and asks a planning question, chat should receive richer CS interpretation context rather than only raw course buckets.

This should help the advisor answer questions like:
- What should I take after COSC241?
- Am I ready for COSC490?
- Which CS direction am I already leaning toward?
- What foundations am I still missing before advanced AI, cloud, or cybersecurity work?

The chat UI itself should remain clean. The improvement belongs in the backend context and the quality of the response, not in visible metadata under the assistant reply.

## Implementation Direction
Add a reusable CS audit interpretation function or module in the backend that:
- accepts major, completed codes, planned/in-progress codes, remaining codes, and course-signal context
- returns a structured CS audit interpretation object
- plugs into both degree-progress-style logic and import/chat flows

This interpretation should reuse existing CS pathway and capstone data where possible instead of duplicating those rules.

## Testing Strategy
Add targeted tests for:
- CS completed vs in-progress vs remaining extraction from realistic audit text
- CS foundation/core bucket classification
- capstone readiness in ready, not-ready, and near-ready cases
- pathway leaning inference across different upper-level course combinations
- preservation of unmapped/unknown CS codes
- import preview integration using the CS-specific interpretation
- chat integration where the richer CS interpretation feeds advising context

Run the full backend suite after implementation.

## Success Criteria
This phase is successful when the backend can do all of the following for Computer Science students:
- interpret a CS transcript or degree audit more like a real advising review
- distinguish foundations, core progress, upper-level direction, and capstone timing
- produce stronger CS-specific next-step guidance from audit context
- explain that guidance clearly in import summaries and chat responses
- surface unknown CS items honestly instead of hiding them

## Out of Scope
This phase does not include:
- full non-CS audit depth
- perfect handling for every transcript layout in the wild
- replacing the broader degree-progress engine for other majors
- major frontend redesign beyond the small import-summary improvements needed to reflect the deeper CS interpretation
