# Morgan Calendars And Deadlines Design

## Goal
Make the advisor stronger on time-sensitive student questions by grounding answers in official Morgan calendar and deadline pages instead of guessing dates.

## Product Intent
This slice should improve answers to questions like:
- Where is the academic calendar?
- When is add/drop?
- When is the withdrawal deadline?
- When should I apply for graduation?
- Where do I find financial aid or scholarship timing?

The product shift is:
- from “here’s the office or workflow page”
- to “here’s the official calendar or deadline page you should use to confirm timing”

## Scope
This pass focuses on four time-sensitive families:
1. Academic calendar and registration timing
2. Graduation and records timing
3. Financial aid and scholarship timing
4. Student process timing

## Time-Sensitive Families

### 1. Academic Calendar And Registration Timing
Improve guidance for:
- academic calendar pages
- registration windows
- add/drop timing
- withdrawal timing

### 2. Graduation And Records Timing
Improve guidance for:
- graduation application timing
- transcript or records timelines when officially published
- clearance-related timing pages

### 3. Financial Aid And Scholarship Timing
Improve guidance for:
- financial aid timeline pages
- scholarship or opportunity timing pages where Morgan publishes them clearly

### 4. Student Process Timing
Improve guidance for:
- accommodations timelines if published
- student organization registration windows if published
- undergraduate research or opportunity timing pages if published

## Data Strategy
Use official Morgan calendar and deadline pages when available.
If Morgan does not publish a clear exact date in a stable official page, store the official page that students should use to confirm timing instead of guessing.

Likely source families for this slice:
- academic calendar pages
- registrar deadline pages
- graduation timing pages
- financial aid timeline pages
- scholarship timing pages
- student process pages with published timing guidance

## Retrieval / Routing Expectations
Questions in this slice should route toward official timing sources first.
Examples:
- withdrawal deadline -> academic calendar or registrar timing page first
- graduation deadline -> graduation timing page first
- financial aid deadline -> official aid timing page first
- calendar question -> academic calendar page first

## Answer Quality Bar
The app should:
- provide the official calendar or deadline page if available
- prefer the official page over hardcoded dates unless the date is clearly published and stable enough to trust
- provide the owning office or contact as a fallback if the timing is still unclear
- avoid unsafe exact-date claims when Morgan's published timing may change

## Boundaries
This pass should not:
- guess dates
- hardcode changing deadlines without trustworthy official grounding
- act like the app is the final authority over shifting academic calendars
- drift into generic time-management advice instead of Morgan-specific timing guidance

## Success Criteria
This pass is successful if:
- time-sensitive questions get safer and more actionable answers
- the app points students to official Morgan timing pages more often
- deadline answers become less generic without becoming risky
