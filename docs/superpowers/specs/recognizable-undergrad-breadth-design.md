# Recognizable Undergrad Breadth Design

## Goal

Expand the Morgan State advising product across a broader set of high-traffic, recognizable undergraduate majors so the app feels more university-wide, more credible, and less thin outside the majors we have already deepened.

This pass is focused on breadth, not full perfect audit depth. The purpose is to make the catalog, advising, and degree-progress experience feel intentionally supported across a wider undergraduate footprint.

## Scope

### In scope

- Undergraduate majors only
- High-traffic and recognizable Morgan majors first
- Program and department mapping cleanup where needed
- Course-family coverage improvements for browsing and retrieval
- Degree-requirement usefulness improvements for progress and advising
- Contact grounding improvements for department/program questions

### Out of scope

- Graduate programs
- Full transcript-perfect audit parity for every new major
- A full university-wide people/organizations layer in this pass
- Major frontend redesign
- Full Morgan catalog completion in one round

## Priority Major Set

This pass focuses on these recognizable undergraduate programs and supported paths:

- Criminal Justice (supported track / certificate path)
- Elementary Education
- Accounting
- Finance
- Business Administration
- Marketing
- Biology
- Psychology
- Nursing
- Computer Science
- Information Science
- Cloud Computing

This set was chosen because it gives the strongest product payoff across business, health, education, social science, and technical undergraduate advising while overlapping with programs students are likely to ask about first.

## Product Objectives

The outcome of this pass should be a product that feels broader and more grounded across undergraduate advising.

For each selected program or supported path, the app should improve in four ways:

1. Program presence
- The major should be represented cleanly in the program and department layer.
- Names, aliases, and school mappings should be correct enough that the app does not feel inconsistent.

2. Course-family coverage
- The catalog should have enough real course rows that browsing by major and level feels intentional.
- The major filter should not look empty or obviously unfinished.

3. Requirement usefulness
- Degree progress and chat should have enough requirement structure to support useful next-step guidance.
- The system does not need perfect registrar parity, but it should support believable advising.
- For `Criminal Justice`, this means a supported undergraduate path or certificate/minor-style advising presence rather than a false standalone degree model.

4. Contact grounding
- If a student asks who to contact or where to go next, the app should have a reasonable department or program contact path.

## Backend Data Strategy

This pass extends the existing Morgan dataset rather than rebuilding the data layer from scratch.

The main targets are:

- `backend/data/courses.csv`
- `backend/data/degree_requirements.csv`
- `backend/data/departments.csv`
- `backend/data/programs.csv`
- `backend/data/faculty.csv`
- `backend/data/prerequisites.csv` where needed

We should continue to rely on official Morgan undergraduate public source material where available, but we do not need another giant source-ingestion round for this pass.

Instead, this is a targeted expansion that strengthens the majors students and faculty are most likely to notice first.

## Catalog Behavior

The Course Catalog should feel broader but still major-specific.

For the selected programs and supported paths:

- Browsing by major should surface the dominant course family or families for that major.
- Browsing by major plus level should stay within that major's course family, not pull in unrelated support classes or general education rows.
- Sparse majors should be enriched enough that the filter does not feel broken.

Examples of expected behavior:

- `Accounting + 300 level` should browse like accounting, not mixed business support.
- `Biology + 100 level` should show biology-family intro science rows.
- `Elementary Education + 300 level` should feel education-specific.
- `Criminal Justice + All levels` should look like a real supported criminal justice path, not a blank or random list.

## Degree Progress and Advising Behavior

The goal is not full audit perfection for every supported area in this pass. The goal is that these majors and supported paths stop feeling generic.

For the selected majors and supported paths, the backend should have enough structure to support:

- cleaner remaining-course lists
- more believable next-course suggestions
- less generic advising replies
- better major-aware context in chat

This means:

- degree requirements need to be present and usable
- major aliases and mappings need to resolve correctly
- course and prerequisite rows need to be strong enough to support planning logic

## Contact and Department Grounding

For each selected major, the app should be able to ground the student in the correct department or program context.

That includes:

- department name
- school/college association
- advising or department contact route where available
- cleaner retrieval when a student asks where to go next

This is especially important for recognizable majors such as Nursing, Biology, Criminal Justice, and Elementary Education, where students may ask practical departmental questions.

## Implementation Shape

This should be treated as a targeted breadth pass, not a giant rewrite.

Expected work categories:

1. Program and alias cleanup
- fix or strengthen major naming and mapping

2. Course-family enrichment
- add missing course rows for the selected majors
- make browsing and retrieval feel fuller

3. Requirement enrichment
- add or tighten requirement rows so degree progress is more useful

4. Contact enrichment
- improve department grounding where it is thin or obviously missing

5. Retrieval verification
- make sure the advisor surfaces the correct major context for common questions

## Testing

Add or update tests for:

- selected major presence in the program/departments layer
- major-specific catalog filtering behavior where appropriate
- degree-progress usefulness for the selected majors
- retrieval quality for common major-aware questions

Run:

- targeted backend tests for catalog, degree progress, and retrieval
- full backend suite
- frontend build if any frontend touch is required in the process

## Success Criteria

This pass is successful if:

- the product feels broader across recognizable Morgan undergraduate majors
- the catalog is less likely to look empty or random for those majors
- degree progress is less generic for those majors
- contact and department grounding are stronger
- the app feels more like a Morgan-wide undergraduate advising product rather than a handful of strong majors surrounded by thin ones

## Boundaries

This pass should not drift into:

- full graduate support
- a giant organizations/leadership retrieval project
- full audit perfection for every major
- broad UI redesign work unrelated to the data foundation

The right outcome is a stronger undergraduate base that makes future retrieval, routing, and people/organization work easier and more trustworthy.
