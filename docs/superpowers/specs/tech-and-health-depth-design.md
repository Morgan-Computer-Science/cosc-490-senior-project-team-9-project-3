# Tech and Health Depth Design

## Goal
Deepen the backend advising logic for five undergraduate Morgan State majors that are useful for both the immediate project presentation and the longer-term product roadmap:
- Information Science
- Cloud Computing
- Nursing
- Biology
- Psychology

This pass builds on the existing Morgan catalog and program dataset that is already in place. The purpose is not to do another broad catalog-ingestion sweep. The purpose is to make degree progress, recommendation logic, and chat advising feel more major-aware and more trustworthy for these five programs.

## Why This Slice
These majors are a strong next step because:
- Information Science and Cloud Computing are close enough to the current Computer Science depth work that we can create more believable technical advising quickly.
- Nursing, Biology, and Psychology provide broader academic coverage for tomorrow's presentation and make the product feel more university-wide.
- The backend already has baseline rows for these programs, so the highest-value work now is reasoning depth rather than raw catalog presence.

## Approach
Use one shared advising pass with two major families:
- Technology family:
  - Information Science
  - Cloud Computing
- Health and science family:
  - Nursing
  - Biology
  - Psychology

Each family gets stronger shared sequencing and readiness logic, then each individual major gets its own program-specific guidance layer.

## Technology Family Design

### Shared technology foundations
The advising engine should recognize that Information Science and Cloud Computing both depend on lower-division technical preparation before upper-level specialization becomes useful. That shared layer should account for:
- early technical and programming preparation
- enough systems or quantitative context before advanced courses
- the idea that upper-level technical work should not be recommended too early

### Information Science guidance
Information Science should feel more oriented toward:
- information systems
- enterprise and data flows
- platform and systems usage in organizational settings

The advisor should better understand when a student is still building the early INSS sequence versus when they are ready to move toward more advanced Information Science planning.

### Cloud Computing guidance
Cloud Computing should feel more oriented toward:
- infrastructure
- cloud platforms
- automation
- operational or security-aware platform work

The advisor should distinguish students still finishing the lower-division setup from those who are ready for upper-level cloud progression.

### Technology-family outcomes
This family should answer questions like:
- What should I take next in Information Science?
- Am I ready for upper-level cloud courses?
- How do Information Science and Cloud Computing differ in progression?

## Health and Science Family Design

### Shared health/science foundations
The advising engine should recognize that Nursing, Biology, and Psychology all depend on lower-division preparation and should not be handled like free-form elective-heavy paths. The shared logic should emphasize:
- foundational sequencing
- avoiding premature upper-level recommendations
- the importance of finishing enough of the lower-division base first

### Nursing guidance
Nursing should be the most structured of the three.
The advisor should:
- treat nursing progression as orderly and prerequisite-sensitive
- give clearer readiness language for moving beyond the lower-division base
- avoid overclaiming anything that sounds like official clearance or licensure approval

### Biology guidance
Biology should feel like a science progression path.
The advisor should:
- distinguish intro biology from more advanced biology progression
- avoid recommending upper-level biology too early
- help students line up the next science steps more coherently

### Psychology guidance
Psychology should feel different from Biology and different from generic advising.
The advisor should:
- recognize intro/statistics/research preparation as the real setup for more advanced psychology work
- better distinguish lower-division psychology from more advanced planning
- avoid flattening Psychology into a generic science major

### Health/science-family outcomes
This family should answer questions like:
- What should I take next in Nursing?
- Am I ready for upper-level Biology?
- What should a Psychology student finish before more advanced psych planning?

## Backend Changes
This pass should primarily deepen reasoning and recommendation logic on top of the current dataset.
Likely areas of change:
- `backend/app/rag.py`
  - add family-aware planning rules and major-specific guidance
  - improve next-course recommendation ordering and blocked-course behavior
- `backend/data/degree_requirements.csv`
  - small adjustments only if the current requirement rows need support for stronger logic
- `backend/data/courses.csv`
  - fill only the specific gaps discovered while deepening these majors
- `backend/data/prerequisites.csv`
  - add or correct prerequisite links only where necessary for better sequencing
- tests
  - add new regression tests for degree progress and chat context across all five majors

## Chat and Degree Progress Expectations
This pass should improve:
- degree progress recommendations
- blocked-course logic
- major-aware advising language in chat
- consistency between what the profile/degree progress surfaces and what chat says

This pass should not introduce a new frontend redesign. The value here is stronger backend behavior that the current UI can already surface.

## Boundaries
This pass does not try to do:
- full transcript-perfect audit depth for all five majors
- a new broad catalog expansion phase
- professional or licensure approval logic beyond what the current backend can honestly support
- another major UI refactor

## Verification Plan
The implementation should be considered complete only when it has:
- targeted regression tests for Information Science and Cloud Computing
- targeted regression tests for Nursing, Biology, and Psychology
- chat-context tests where useful
- a full backend test pass after the changes
- a compile check on the backend app

## Success Criteria
When this pass is complete:
- Information Science and Cloud Computing should feel distinct and technically grounded
- Nursing, Biology, and Psychology should feel more structured and major-aware
- the project should demo more convincingly across a broader range of Morgan State majors tomorrow
- the backend should still be in a strong place for deeper post-presentation work
