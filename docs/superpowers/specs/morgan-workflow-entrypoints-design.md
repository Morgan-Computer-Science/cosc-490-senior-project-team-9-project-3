# Morgan Workflow Entrypoints Design

## Goal
Make the advisor stronger at giving students the actual official Morgan starting page or workflow entry point for common student processes, instead of only naming the office that owns the process.

## Product Intent
This slice should improve answers to questions like:
- Where is the withdrawal form?
- What page do I use for transcript requests?
- Where do I start transfer credit evaluation?
- What page should I use to form a student organization?
- Where do I begin accommodations or undergraduate research involvement?

The product shift is:
- from “here’s who handles it”
- to “here’s where you actually start”

## Scope
This pass focuses on four workflow-entry families:
1. Registrar and records entry points
2. Academic process entry points
3. Student support entry points
4. Involvement and opportunity entry points

## Workflow-Entry Families

### 1. Registrar And Records Entry Points
Improve guidance for:
- transcript request pages
- enrollment verification workflow pages
- graduation / records-related starting pages

### 2. Academic Process Entry Points
Improve guidance for:
- transfer-credit workflow pages
- withdrawal / add-drop / registration-help pages
- advising or process pages that explain the next step

### 3. Student Support Entry Points
Improve guidance for:
- accommodations request pages
- tutoring / student-success starting pages
- counseling / wellness workflow pages when Morgan publishes them

### 4. Involvement And Opportunity Entry Points
Improve guidance for:
- student organization registration / formation pages
- undergraduate research getting-started pages
- internship / career-platform starting pages

## Data Strategy
Use official Morgan pages when available.
If Morgan does not publish a direct form or single workflow page, store the nearest official entry point page instead of guessing.

Likely source families for this slice:
- registrar / records pages
- transfer and advising process pages
- student support service pages
- student organizations pages
- undergraduate research pages
- career / internship platform entry pages

## Retrieval / Routing Expectations
Questions in this slice should route toward workflow entry points before generic office contacts.
Examples:
- transcript request -> transcript request page first, registrar contact second
- withdrawal -> withdrawal/process page first, registrar or advising contact second
- accommodations -> accommodations process page first, accessibility contact second
- form a student organization -> organization formation page first, student life contact second

## Answer Quality Bar
The app should:
- provide the official workflow entry point if one exists
- otherwise provide the nearest valid official Morgan page
- then provide the owning office or contact as the fallback next step
- avoid vague generic office-only responses when a better official starting page exists

## Deadlines And Timing
If Morgan publishes a clearly official page containing timing or deadline guidance, the app should prefer linking to that page.
It should avoid hardcoding dates unless they are clearly published and stable enough to trust.

## Boundaries
This pass should not:
- invent unpublished forms or workflow pages
- hardcode changing deadlines unsafely
- claim a page guarantees approval or resolution
- turn into a broad web scrape of everything on the university site

## Success Criteria
This pass is successful if:
- process answers become more actionable
- students are pointed to official starting pages more often
- office/process answers feel less generic and more usable
- the app reliably says “start here, then contact this office if needed”
