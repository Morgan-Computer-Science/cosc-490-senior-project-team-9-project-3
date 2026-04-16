# Business Administration + Marketing + Entrepreneurship Depth Design

## Goal
Deepen Morgan State advising for the Department of Business Administration by improving backend planning logic for the three closely related undergraduate programs most likely to share advising flows:
- Business Administration
- Marketing
- Entrepreneurship

This phase should make advising feel more authentic to Morgan State University by modeling the shared lower-division business core and then layering program-specific guidance on top of it.

## Why This Slice
These three programs sit under the same department and overlap heavily in real advising flows. Students often build the same foundation before specializing, and advising questions naturally cross program lines.

This makes them a better first business-depth slice than trying to deepen each program independently or broadening the entire Graves School at once.

## Scope
This phase covers:
- shared business-core sequencing and readiness logic
- stronger next-course recommendations for Business Administration, Marketing, and Entrepreneurship
- clearer blocked-course logic when foundational work is missing
- richer chat advising context for those three programs

This phase does not yet cover:
- Accounting and Finance depth
- full school-wide Graves depth
- transcript-perfect degree-audit specialization for all business programs
- major frontend redesign

## Official Morgan Grounding
The slice should remain grounded in Morgan’s public undergraduate structure:
- Business Administration, Marketing, Entrepreneurship, Hospitality Management, and Human Resource Management are associated with the Department of Business Administration
- Accounting and Finance are associated with the Department of Accounting & Finance
- Undergraduate program presence should continue to trace back to Morgan’s official undergraduate program and business pages

## Architecture
Add a dedicated business-planning layer on top of the existing degree-progress and RAG system.

The planning model should have two tiers:

1. Shared Business Core
A common readiness layer for:
- accounting fundamentals
- economics fundamentals
- statistics / quantitative preparation
- management foundations
- marketing foundations

2. Program-Specific Layers
Program-aware planning logic for:
- Business Administration
- Marketing
- Entrepreneurship

The shared core should drive sequencing, while the program-specific layers determine the strongest next moves and the best advising language for each major.

## Shared Business Core Logic
The system should recognize a shared lower-division business foundation that supports upper-level work.

Core readiness should evaluate whether students have enough of the following to move responsibly into upper-level business courses:
- ACCT201 / ACCT202
- ECON201 / ECON202
- STAT302 or equivalent business/statistical preparation
- MGMT220
- MKTG210 where relevant

This layer should answer questions such as:
- is the student still building the business foundation?
- are upper-level management/marketing/venture courses premature?
- which lower-division courses should be prioritized next?

## Program-Specific Advising Logic
### Business Administration
The advisor should understand that Business Administration students often move from a broad lower-division core into upper-level management and strategy work.

The system should:
- prioritize business-core completion first
- then recommend courses such as organizational behavior / strategy once the foundation is present
- avoid recommending advanced management work too early

### Marketing
The advisor should understand the path from business fundamentals into marketing-specific strategy work.

The system should:
- treat MKTG210 as an important transition point
- avoid pushing upper-level marketing strategy before enough core business context exists
- recommend communication- and strategy-supportive next steps when marketing direction is clear

### Entrepreneurship
The advisor should understand that venture courses are more useful after a student has enough management, marketing, and accounting context.

The system should:
- avoid recommending venture-heavy work before the business base is present
- identify when students are ready for entrepreneurship-specific coursework such as venture creation and small business strategy
- use stronger language around practical sequencing for students interested in launching or managing ventures

## Recommendation Outcomes
For these three majors, degree progress should become more intentional.

The backend should produce stronger:
- recommended next courses
- blocked courses
- program-specific guidance notes
- pathway or direction hints where appropriate

Examples of better outcomes:
- Business Administration students should be guided toward the remaining shared core before strategic management-style work
- Marketing students should see recommendations that move from principles into marketing management only when foundational work is in place
- Entrepreneurship students should see venture coursework as a later step built on business fundamentals

## Chat Context Improvements
The chat layer should receive richer program-aware business planning context so the live advisor can answer more like a department advisor.

It should support questions such as:
- What should I take next for Business Administration?
- Am I ready for upper-level marketing classes?
- Should I take entrepreneurship courses yet?
- What should I finish before strategy-focused courses?

Responses should feel grounded and practical without exposing internal planning metadata directly to the student.

## Data Model Strategy
This phase should reuse the current CSV-backed system and extend it where useful.

Likely changes:
- enrich degree requirement structure for the three programs where needed
- enrich prerequisite links that materially affect sequencing
- optionally add a dedicated business-planning data file if that is the cleanest way to model shared-core and program-specific rules

The main goal is not just more rows, but better planning behavior.

## Testing Strategy
Verification should include:
- unit/regression tests for shared business-core sequencing
- tests that Business Administration does not jump too early to upper-level management/strategy recommendations
- tests that Marketing treats MKTG210 as a meaningful step toward upper-level marketing work
- tests that Entrepreneurship waits for enough business foundation before recommending venture-heavy coursework
- chat-context tests where useful
- full backend suite after implementation

## Success Criteria
This slice is successful when:
- Business Administration recommendations feel grounded in a real shared business core
- Marketing recommendations feel more sequential and discipline-specific
- Entrepreneurship recommendations feel practical and appropriately staged
- chat answers for these majors feel like Morgan business advising rather than generic remaining-course dumps

## Follow-On Work
After this slice, the next business-depth phase should expand to the broader Graves undergraduate business ecosystem, especially:
- Accounting
- Finance

That later phase can build on the shared-core work created here.
