# Morgan Entities and Routing Design

## Goal

Strengthen the Morgan advisor so it can answer people, office, leadership, and organization questions with more specific Morgan grounding instead of falling back to generic advising responses.

This pass is inspired by the stronger knowledge-source organization seen in the reference repo, but it stays grounded in our current product architecture rather than copying that stack.

## Scope

### In scope

- Add a clearer Morgan entities knowledge layer
- Improve question-type routing before retrieval scoring
- Strengthen responses for:
  - leadership questions
  - contact questions
  - support-office questions
  - organization and team questions
- Keep degree-planning, transcript, and small-talk routing from being mixed into the wrong question type
- Continue using the existing backend retrieval pipeline and data-backed architecture

### Out of scope

- Docker and deployment work in this pass
- Pinecone or external vector-database migration
- Full campus-wide organization coverage in one round
- Another giant course-ingestion pass at the same time
- Major frontend redesign

## Product Problem

The app is now stronger on major-aware advising, degree progress, transcript import, and recognizable undergraduate breadth. However, it still becomes too generic when a user asks highly specific Morgan questions about:

- who is in charge of something
- who to contact
- what office handles an issue
- which dean, chair, or director is responsible for a program
- which team or organization is associated with a topic

This makes the product feel less complete than it should, even when we have nearby Morgan context that could support a better answer.

## Product Objectives

This pass should make the advisor feel more like a real Morgan information system, not just a degree-planning assistant.

The outcome should be:

1. Better Morgan-specific entity answers
- The advisor should answer questions about chairs, deans, directors, offices, and supported organizations with clearer specificity.

2. Better contact routing
- If the user asks who to contact, the app should surface the strongest valid Morgan contact path it has.

3. Better question-type handling
- A question about a robotics team, dean, or office should not be treated like a degree-progress prompt.

4. Less generic fallback behavior
- When the exact answer is missing, the app should still return the closest valid Morgan contact, office, or page instead of a vague generic response.

## Knowledge-Source Layering

We should organize the backend knowledge more clearly into source families.

Recommended source families:

- `academics`
  - courses
  - degree requirements
  - programs
  - departments
- `people`
  - chairs
  - deans
  - directors
  - advisors
  - faculty contacts
- `offices`
  - advising offices
  - registrar-style offices
  - tutoring/support offices
  - transfer support where available
- `organizations`
  - selected student organizations
  - competition teams
  - robotics or related public-facing teams where officially documented
- `resources`
  - support pages
  - help pages
  - policy or process pages that matter for advising questions

This pass does not require a brand-new database system. It can extend the current CSV-backed, retrieval-driven backend if we keep the data structured and source-aware.

## Question-Type Routing

Before retrieval scoring, the backend should classify the question into a lightweight intent family.

Minimum routing families:

1. `degree_planning`
- examples:
  - What should I take next?
  - Am I ready for capstone?

2. `course_prerequisite`
- examples:
  - What is COSC242?
  - What do I need before MKTG331?

3. `people_contact_leadership`
- examples:
  - Who is the dean of Computer Science?
  - Who runs the robotics team?
  - Who should I contact about Nursing?

4. `office_resource`
- examples:
  - What office handles transfer advising?
  - Where can I get tutoring?

5. `organization_team`
- examples:
  - Is there a robotics team at Morgan?
  - What student organizations are related to Computer Science?

6. `transcript_import`
- examples:
  - What is my GPA?
  - What do you think of my degree works?
  - How many earned credits do I have?

7. `small_talk`
- examples:
  - Hello
  - How are you?
  - Thanks

This routing does not need to be overly complex. It just needs to stop obviously wrong retrieval priorities.

## Retrieval Behavior

The retrieval layer should use the routed intent to change source preference.

Examples:

- `people_contact_leadership`
  - search people, departments, offices first
  - do not over-weight the user's own major if the query clearly names another department or program

- `organization_team`
  - search organizations and related support pages first
  - then fall back to department/faculty context if the exact team entry is missing

- `office_resource`
  - search offices and support resources first
  - not degree requirements

- `degree_planning`
  - keep current major-aware and import-aware advising behavior

- `transcript_import`
  - prefer saved import snapshot and transcript summary context first

This should produce more specific answers while keeping the rest of the advising system intact.

## Data Targets

Likely files to add or extend:

- `backend/data/faculty.csv`
- `backend/data/departments.csv`
- `backend/data/support_resources.csv`
- possible new files such as:
  - `backend/data/offices.csv`
  - `backend/data/organizations.csv`
  - `backend/data/leadership.csv`

The exact shape can follow the current CSV approach so the app stays simple and fast at runtime.

## Success Criteria

This pass is successful if:

- leadership and contact questions stop sounding generic
- the advisor can answer more specific Morgan entity questions directly
- explicit cross-major entity questions override student-major bias appropriately
- office/resource questions search the right source family first
- missing exact answers still return the closest valid Morgan contact or page

## Next Steps After This Pass

After Morgan entities and routing are stronger, the best next product-level step is:

1. Docker and deployment portability
2. broader organizations/resources coverage
3. continued catalog and advising depth where needed

That keeps the project moving toward a more complete and portable product without overreaching in one iteration.
