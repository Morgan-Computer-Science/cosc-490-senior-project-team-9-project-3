# Morgan Workflow Entrypoints Plan

## Implementation Steps

1. Add or refine tests for workflow-entry questions about forms, pages, and official starting points.
2. Add official Morgan workflow-entry rows to a dedicated backend data layer.
3. Introduce a workflow-entry knowledge source in retrieval.
4. Tune routing and scoring so form/page/start-here questions prefer official entry points before generic office contacts.
5. Verify targeted behavior and run broader backend regression coverage.

## Verification

- targeted `rag + chat` tests for workflow-entry questions
- full backend suite
- backend compile check
