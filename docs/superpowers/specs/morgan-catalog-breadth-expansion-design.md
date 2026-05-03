# Morgan Catalog Breadth Expansion Design

## Goal

Expand the backend dataset toward broad, authentic Morgan State University advising coverage using official public source pages and downloadable documents.

This phase is breadth-first. The focus is to make the advisor useful across far more majors, departments, and courses without yet trying to achieve department-by-department perfection.

## Chosen approach

Use a catalog-first breadth strategy with light curation:

1. ingest broad academic coverage from official Morgan public sources
2. normalize that data into the backend's internal CSV-backed advising records
3. hand-curate the fields that matter most for advising quality

This is intentionally not a pure manual-edit pass and not a fragile runtime scraper. It is a repeatable backend ingestion workflow that produces committed data artifacts for the app to use at runtime.

## Official source targets

Primary Morgan public sources:

- central academic catalog
- undergraduate programs index
- departments A to Z
- school and department undergraduate program pages
- selected registrar and academic pages where they clarify official program structure or advising contacts

Typical source content we expect to extract:

- program names
- schools and departments
- course references
- degree requirement summaries
- faculty or advising contacts
- contact details and source URLs

## Data model

The current CSV-backed data model stays in place, but we enrich and normalize it more carefully.

Core record types:

- courses
n  - code, title, credits, department, level, semester or offering, description, source URL
- programs or majors
  - program name, degree type, school, department, public page URL, contact info
- degree requirements
  - major, requirement bucket, required course, notes, source URL
- departments
  - department name, school, office location, advising contact, public page URL
- faculty or advising contacts
  - name, title, department, email, phone, profile URL
- support resources
  - broader advising and student-support paths where they relate to academic guidance

Important normalization rule:

Program names and department names must be treated as separate concepts. A major can belong to a department whose public name is different from the major label shown to students.

## Ingestion workflow

1. discover official Morgan public pages
2. extract raw structured content from those pages and documents
3. normalize the extracted content into internal record shapes
4. lightly curate the advising-critical fields
5. regenerate committed backend datasets
6. validate the new coverage with tests

We will implement this as a script-driven ingestion workflow under `backend/scripts/` rather than as runtime scraping inside the app.

## Runtime behavior

The live app will continue to use committed CSV-backed datasets.

That means:

- the advisor remains fast and deterministic at runtime
- there is no dependency on Morgan site availability during normal app use
- dataset refreshes happen through controlled ingestion runs, not user-facing requests

## Coverage goals for this phase

This phase should move the system toward a university-wide advising baseline.

Each visible undergraduate major in the product should aim to have:

- a program or major record
- department alignment
- at least one contact or advising path
- degree requirement coverage for core classes
- some course coverage through the official-source ingestion pass

We are not promising perfect depth for every department in this phase. The goal is breadth and authenticity first.

## Testing and validation

Add verification that:

- newly ingested majors appear in normalized datasets
- program-to-department mapping is valid
- sample advising questions retrieve the right Morgan context for multiple majors
- ingestion output does not silently drop major records or obvious contact fields

Where practical, add parser tests around representative official page shapes so the ingestion workflow is less brittle.

## Out of scope for this phase

- full department-by-department deep curation
- perfect degree-audit logic for every major
- live authenticated Canvas or WebSIS sync
- runtime scraping in the product

Those remain future phases after the breadth pass is stable.
