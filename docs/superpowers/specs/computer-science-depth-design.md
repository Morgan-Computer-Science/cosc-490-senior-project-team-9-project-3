# Computer Science Depth Design

## Goal
Deepen Morgan State Computer Science advising so the advisor gives more trustworthy sequencing, pathway-aware recommendations, and capstone readiness guidance for CS students.

## Why this slice first
Computer Science is the best first department for depth because it already has the strongest transcript overlap, the heaviest advising demand in the current app, and the most obvious prerequisite-sensitive planning questions.

## Phase 1 scope
This phase will improve:
- CS core sequencing guidance
- upper-level pathway-aware recommendations
- capstone readiness checks for COSC490
- CS-specific chat and degree-progress recommendation quality

This phase will not yet attempt:
- every CS elective in perfect detail
- a full official CS degree audit engine
- transcript-perfect handling of every edge case
- non-CS department depth

## Architecture
Keep the existing generic advising and RAG system for all majors, but add a Computer Science planning layer that activates when:
- the student major is Computer Science, or
- the advising question is clearly CS-focused

The CS planning layer should provide:

### 1. Core sequencing rules
Encode the Morgan CS progression more explicitly so the advisor does not rely only on prompt inference. The planning layer should reason about foundational progression such as:
- introductory programming
- data structures and algorithms
- architecture / systems / databases / software foundations
- upper-level CS electives
- capstone preparation

### 2. Pathway grouping
Create advising-friendly internal groupings for upper-level CS interests, such as:
- AI and data
- systems and cloud
- software engineering
- networking and security

These groups are internal advisor guidance structures, not official Morgan concentrations unless an official source explicitly supports them.

### 3. Capstone readiness check
Add rule-based guidance around whether COSC490 appears well-timed, premature, or nearly ready based on completed coursework and core gaps.

### 4. Recommendation formatter
Use the sequencing rules and pathway groupings to generate structured CS-specific planning output, including:
- recommended next courses
- courses that look premature or blocked
- pathway suggestions based on student interest
- capstone readiness notes

This output should feed both:
- degree-progress recommendation logic
- chat context for CS advising answers

## Data model direction
The first CS depth phase can stay lightweight and CSV-backed. Add a dedicated backend data source for CS planning metadata, for example:
- core sequencing anchors
- pathway group membership
- capstone readiness expectations

This should be explicit, testable, and separate from the generic catalog rows.

## Expected product behavior
After this phase, the app should answer CS questions more convincingly, including:
- What should I take after COSC241?
- Am I ready for COSC490?
- I want to focus on AI. What should I line up next?
- Should I take operating systems, software engineering, or databases next?
- Which CS electives fit best with what I have already completed?

## Testing expectations
Add backend tests for:
- CS next-course sequencing behavior
- CS pathway recommendation behavior
- COSC490 readiness checks
- CS-specific retrieval/context shaping where needed

Run:
- targeted backend tests for the new CS planning logic
- full backend test suite
- compile check

## Follow-on phases
After this phase:
1. deepen CS catalog coverage further
2. deepen CS degree-audit logic
3. then repeat the department-depth pattern for other Morgan departments
