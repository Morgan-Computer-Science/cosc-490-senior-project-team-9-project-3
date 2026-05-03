# Connector Groundwork Design

## Goal

Add a real connector foundation for Canvas and WebSIS-style data without pretending live campus integrations already exist.

This phase should make connectors a first-class part of the product and the backend architecture while keeping the current manual/OCR import workflow as the active path today.

## Why this phase exists

The app already supports source-aware imports through labels like `manual`, `canvas_export`, and `websis_export`, but those are still just labels on the same import endpoint.

To move closer to a launchable product, the system needs an explicit connector layer that can answer:

- what integrations exist
- what each integration can provide
- whether it is available now or planned
- how imported records normalize into the advising system

This creates a clean seam for future real integrations without requiring live OAuth or campus credentials in this phase.

## Recommended approach

Build a connector registry plus a normalized import contract.

That means:

1. The backend exposes integration metadata for supported connectors.
2. The frontend can render connectors as part of the student data/import experience.
3. All imported or synced academic records normalize into a shared internal shape, regardless of whether they come from manual text, OCR, Canvas export, or a future WebSIS connection.

This keeps the rest of the advising system stable while connector implementations evolve later.

## Scope

### In scope

- Backend connector registry
- Integration metadata API endpoints
- Shared schemas for connectors and normalized import records
- Frontend connector display inside the existing profile/import workflow
- Clear statuses such as available now, upload-based, or planned
- Documentation updates for connector behavior and future sync strategy

### Out of scope

- Real Canvas OAuth
- Real WebSIS authentication
- Live SIS sync jobs
- Background worker infrastructure
- Full account-linking flows

## Product behavior

### Student experience

Inside the existing profile/import flow, students should be able to see that the app supports multiple ways of bringing data in:

- Manual text import
- Transcript or degree-audit upload
- Canvas-style export upload
- WebSIS-style export upload
- Future authenticated connectors

The UI should clearly distinguish between:

- available today
- upload-assisted today
- planned for future sync

The experience should feel honest and product-ready, not like a fake integration.

### Backend behavior

The backend should expose connector definitions describing:

- connector id
- display name
- status
- description
- capabilities
- supported record types
- whether authentication is required
- whether file upload is supported now

This lets the frontend and future backend logic reason about connectors explicitly instead of inferring behavior from source labels.

## Architecture

### 1. Connector registry

Create a small backend module that defines supported connectors such as:

- `manual`
- `canvas`
- `websis`

Each connector should declare:

- user-facing name
- current availability status
- whether it supports uploads now
- whether it is a planned authenticated sync
- what data domains it can provide, such as:
  - completed courses
  - current schedule
  - degree audit
  - official major

### 2. Integration API

Add backend endpoints such as:

- `GET /integrations/connectors`
- `GET /integrations/connectors/{connector_id}`

These endpoints should return connector metadata only in this phase.

They should not start live syncs yet.

### 3. Normalized import record contract

Define a shared backend schema for imported academic data so all connectors eventually normalize into one shape.

The normalized record model should support fields like:

- `source_type`
- `record_type`
- `confidence`
- `raw_summary`
- `course_codes`
- `detected_document_type`
- `connector_id`

This does not require replacing the existing import preview payload immediately, but it should become the architectural direction for connector-backed imports.

### 4. Frontend connector presentation

Extend the existing profile/import flow so students can see available connectors and what they do.

This should be a compact, launch-friendly surface that communicates:

- upload from Canvas export today
- upload from WebSIS export today
- future direct sync is planned

The connector surface should support the existing import wizard rather than compete with it.

## Data flow

### Current phase

1. Student opens the profile/import area.
2. Frontend loads connector definitions from the backend.
3. Student sees which data sources are available and what each source can provide.
4. Student continues using the current import wizard for upload/paste-based ingestion.

### Future phase

1. Student selects a connector.
2. Connector-specific auth or export flow begins.
3. Data is fetched and normalized into the shared import format.
4. Degree progress, chat, and planning logic consume the normalized data.

## Error handling

The system should clearly handle:

- unknown connector ids
- unsupported connector actions
- connector metadata not loading
- planned connectors being shown but not yet linkable

Responses should remain honest:

- available now
- upload-based today
- direct sync planned

No fake success states.

## Testing

This phase should include:

- backend tests for connector list/detail endpoints
- tests that verify supported connector ids and statuses
- frontend verification that connector metadata can render without breaking the existing import flow

## Success criteria

This phase is successful if:

- connectors are represented explicitly in the backend
- the frontend shows connector options clearly
- manual and OCR imports still work unchanged
- the app now has a clean architecture seam for real Canvas/WebSIS integration later
- the product feels more launch-ready because integrations are visible, honest, and structured

## Notes

This phase should stay lightweight and truthful. The goal is not to simulate a campus integration that does not exist yet. The goal is to build the product and backend foundation that a real integration would attach to later.
