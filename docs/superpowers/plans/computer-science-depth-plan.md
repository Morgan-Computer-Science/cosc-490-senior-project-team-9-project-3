# Computer Science Depth Implementation Plan

## Goal
Add a Morgan-specific Computer Science planning layer that improves sequencing, pathway-aware advising, and COSC490 readiness guidance.

## Task 1: Write red tests for CS sequencing and capstone readiness
Files:
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py

Steps:
- Add failing tests for CS next-course recommendations after core milestones like COSC241.
- Add failing tests for COSC490 readiness when core courses are missing.
- Add failing tests for pathway-aware guidance when a CS student asks about AI or systems directions.
- Run targeted pytest and verify failures are for the expected missing planning logic.

## Task 2: Add a dedicated CS planning data source
Files:
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\cs_pathways.csv
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\data\cs_capstone_rules.csv

Steps:
- Create a lightweight CSV-backed planning source for CS pathway groups.
- Create a lightweight CSV-backed source for COSC490 readiness expectations.
- Keep these structures explicit and testable instead of hiding them in prompt text.

## Task 3: Implement the CS planning layer
Files:
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\rag.py
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\schemas.py

Steps:
- Add helper functions to load CS pathway and capstone-rule data.
- Add CS-specific sequencing logic that activates when the student major is Computer Science.
- Add capstone readiness evaluation for COSC490.
- Add pathway-aware recommendation outputs to the degree-progress summary.

## Task 4: Feed CS planning into chat context
Files:
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\app\chat.py

Steps:
- Inject CS-specific planning context into chat when the user is a CS major or the question is clearly CS-focused.
- Make pathway suggestions available to the live AI and fallback advising paths.
- Keep the student-facing output natural and concise.

## Task 5: Verify and refine
Files:
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_rag.py
- C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\backend\tests\test_chat.py

Steps:
- Run targeted backend tests for the new CS planning logic.
- Run the full backend suite.
- Run compile check.
- Adjust any brittle recommendation logic until results are stable and believable.
