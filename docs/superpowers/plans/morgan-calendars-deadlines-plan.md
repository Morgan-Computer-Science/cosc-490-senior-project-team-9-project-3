# Morgan Calendars And Deadlines Plan

## Implementation Steps

1. Add or refine tests for academic calendar and deadline questions.
2. Add official Morgan calendar and timing rows to a dedicated backend data layer.
3. Introduce a calendar/deadline knowledge source in retrieval.
4. Tune routing and scoring so deadline-style questions prefer official timing pages before generic office contacts.
5. Verify targeted behavior and run broader backend regression coverage.

## Verification

- targeted `rag + chat` tests for calendar/deadline questions
- full backend suite
- backend compile check
