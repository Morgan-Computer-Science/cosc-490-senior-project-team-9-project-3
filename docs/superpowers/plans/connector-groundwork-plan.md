# Connector Groundwork Plan

## Goal

Implement the first real connector foundation for the Morgan State AI Advisor so Canvas and WebSIS become explicit product concepts and backend objects without introducing fake live integrations.

## Phase breakdown

### 1. Backend connector registry
- Add a dedicated backend module for connector definitions.
- Define connectors for:
  - manual
  - canvas
  - websis
- Each connector should include:
  - id
  - display name
  - status
  - description
  - capabilities
  - supported record types
  - authentication requirement
  - upload support

### 2. Integration schemas and routes
- Add schemas for:
  - connector summary
  - connector detail
- Add routes for:
  - `GET /integrations/connectors`
  - `GET /integrations/connectors/{connector_id}`
- Keep route behavior metadata-only in this phase.

### 3. Backend tests
- Add tests for connector list/detail responses.
- Verify:
  - expected connector ids are present
  - statuses are stable
  - unknown connector ids return 404

### 4. Frontend API support
- Add frontend API helpers for integration metadata.
- Keep these isolated from the current import preview API so existing behavior is unchanged.

### 5. Frontend connector surface
- Extend the existing profile/import experience to show connector options.
- Present:
  - available now
  - upload-assisted today
  - planned direct sync
- Make the UI supportive of the existing import wizard, not a replacement for it.

### 6. Documentation
- Update connector documentation so the product behavior matches the new implementation.
- Keep the docs honest about what is upload-based today versus direct-sync later.

### 7. Verification
- Run backend tests including the new connector tests.
- Run backend compile check.
- Run frontend build.

## Implementation order

1. Add backend connector registry module
2. Add schemas and integration routes
3. Add backend tests and get them green
4. Add frontend API helpers
5. Add frontend connector UI in the profile/import flow
6. Update docs
7. Run verification

## Guardrails

- Do not implement fake OAuth flows
- Do not add broken buttons that imply real sync exists today
- Do not break the existing OCR/import workflow
- Keep connector states explicit and honest in both backend and frontend

## Success criteria

- Connectors are available from real backend endpoints
- Frontend shows them as part of the product
- Existing import workflow still works
- Canvas and WebSIS are now represented as real planned integrations with clean future extension points
