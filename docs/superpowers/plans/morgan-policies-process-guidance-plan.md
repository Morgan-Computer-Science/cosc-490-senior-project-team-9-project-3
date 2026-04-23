# Morgan Policies And Student Process Guidance Plan

## Implementation Steps

1. Add or refine tests for registrar, transfer, withdrawal, override, and support-procedure questions.
2. Add official Morgan process-guidance rows to a dedicated backend data layer.
3. Introduce a process-guidance knowledge source in retrieval.
4. Tune routing and scoring for registrar, transfer, course-change, and support-procedure queries.
5. Verify targeted behavior and run broader backend regression coverage.

## Verification

- targeted `rag + chat` tests for process-guidance questions
- full backend suite
- backend compile check
