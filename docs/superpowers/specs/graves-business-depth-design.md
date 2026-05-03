# Graves Business Depth Design

## Goal
Deepen Morgan State advising for the broader Earl G. Graves School of Business and Management undergraduate ecosystem by extending the current business-planning layer beyond Business Administration, Marketing, and Entrepreneurship.

This phase should add stronger advising depth for:
- Accounting
- Finance
- Hospitality Management
- Human Resource Management

while preserving a coherent shared business-core model across the Graves undergraduate programs.

## Why This Slice
The project already has a stronger advising layer for Business Administration, Marketing, and Entrepreneurship. The next gap is that other Graves undergraduate majors still feel thinner and less consistent.

Accounting and Finance need the most sequencing depth because they rely on tighter prerequisite progression and are common advising targets. Hospitality Management and Human Resource Management should also become more coherent, but they do not need the same level of sequencing detail in this phase.

## Scope
This phase covers:
- a shared Graves undergraduate business core across the business-school majors
- deeper program-specific sequencing for Accounting and Finance
- lighter but real program-specific sequencing for Hospitality Management and Human Resource Management
- stronger next-course recommendations and blocked-course logic for those majors
- richer business-school advising context in chat for those majors

This phase does not yet cover:
- transcript-perfect audit specialization for all Graves programs
- graduate business programs
- major frontend redesign
- non-business department depth

## Official Morgan Grounding
This slice should remain grounded in Morgan’s public undergraduate business structure:
- Accounting and Finance are associated with the Department of Accounting & Finance
- Hospitality Management and Human Resource Management are associated with the Department of Business Administration
- The broader business-school identity remains the Earl G. Graves School of Business and Management
- Program presence and mapping should continue to trace back to Morgan’s official undergraduate program and business pages

## Architecture
Extend the current business-planning layer into a broader `Graves undergraduate business core` with weighted program-specific depth.

The planning model should have three tiers:

1. Shared Graves Core
A common readiness layer across the business-school ecosystem for:
- accounting foundations
- economics foundations
- statistics / quantitative preparation
- management / organizational foundations
- marketing foundations where relevant

2. High-Depth Tracks
Richer sequencing and readiness logic for:
- Accounting
- Finance

3. Lighter Program Layers
Cleaner and more coherent sequencing for:
- Hospitality Management
- Human Resource Management

The shared core should keep the school coherent, while the program layers determine which requirements and recommendations should be emphasized next.

## Shared Graves Core Logic
The planner should recognize a shared lower-division business foundation that supports upper-level work across Graves majors.

Core readiness should evaluate whether students have enough of the following to move responsibly into more advanced business coursework:
- ACCT201 / ACCT202 where appropriate
- ECON201 / ECON202 where appropriate
- STAT302 or other quantitative preparation where the major depends on it
- MGMT220 and related management foundations where appropriate
- MKTG210 where the program benefits from a marketing foundation

The core layer should answer questions such as:
- is the student still building the business foundation?
- are upper-level accounting, finance, hospitality, or HR courses premature?
- which lower-division business requirements should be prioritized next?

## Program-Specific Advising Logic
### Accounting
The advisor should understand that Accounting requires a more sensitive sequence than the lighter management-oriented business majors.

The system should:
- strongly respect the accounting progression from ACCT201 to ACCT202 to ACCT301 to ACCT302
- avoid recommending upper accounting too early
- support practical language around internship readiness, public accounting, and CPA-oriented planning where appropriate

### Finance
The advisor should understand that Finance builds on accounting and economics, not just generic business interest.

The system should:
- treat ACCT201 and ECON201 / ECON202 as real foundations for stronger finance guidance
- avoid pushing finance-heavy work too early
- make next-step recommendations feel more grounded in finance preparation rather than generic business progression

### Hospitality Management
The advisor should understand Hospitality Management as a business-school path that builds from a shared core into service, operations, and management direction.

The system should:
- use the shared business foundation where it matters
- then guide students toward hospitality-specific progression once that foundation exists
- remain lighter than Accounting and Finance in this phase, but still coherent and grounded

### Human Resource Management
The advisor should understand HRM as a business-school path that benefits from management and organizational foundations.

The system should:
- use the shared business foundation where it matters
- then guide students toward management, organizational behavior, and HR-relevant progression
- remain lighter than Accounting and Finance in this phase, but still coherent and grounded

## Recommendation Outcomes
For these Graves majors, degree progress should become more intentional.

The backend should produce stronger:
- recommended next courses
- blocked courses
- program-specific guidance notes
- cleaner sequencing around shared business foundations

Examples of better outcomes:
- Accounting students should not be pushed into ACCT301 or ACCT302 prematurely
- Finance students should build accounting and economics before deeper finance planning
- Hospitality Management students should move through a recognizable business-to-hospitality path
- Human Resource Management students should move through a recognizable business-to-management/HR path

## Chat Context Improvements
The chat layer should receive richer Graves-program-specific planning context so the live advisor can answer more like a business-school advisor.

It should support questions such as:
- Am I ready for upper-level accounting?
- What should I finish before finance courses?
- What should I take next in Hospitality Management?
- What should an HRM student do after the shared business core?

Responses should feel more realistic and practical without exposing internal planning metadata directly to the student.

## Data Model Strategy
This phase should continue to use the current CSV-backed model and extend it where useful.

Likely changes:
- expand the shared business-planning data so it supports the broader Graves ecosystem
- tighten degree-requirement rows for Accounting, Finance, Hospitality Management, and Human Resource Management where needed
- add prerequisite relationships that materially affect sequencing and advising quality

The goal is again not just more rows, but stronger program-aware planning behavior.

## Testing Strategy
Verification should include:
- unit/regression tests for Graves shared-core sequencing
- tests that Accounting respects the accounting sequence and does not jump too early
- tests that Finance respects accounting/economics foundations before stronger finance recommendations
- tests that Hospitality Management becomes more coherent after the shared business core
- tests that Human Resource Management becomes more coherent after the shared business core
- chat-context tests where useful
- full backend suite after implementation

## Success Criteria
This slice is successful when:
- Accounting recommendations feel more sequence-aware and professionally grounded
- Finance recommendations feel tied to real accounting/economics preparation
- Hospitality Management recommendations feel like a coherent Morgan business-school path
- Human Resource Management recommendations feel like a coherent Morgan business-school path
- the Graves undergraduate business ecosystem feels more consistent overall

## Follow-On Work
After this slice, the next natural business-school phase would be deeper audit interpretation for the Graves majors, especially:
- Accounting
- Finance

That later phase can build on the shared-core and weighted-depth logic created here.
