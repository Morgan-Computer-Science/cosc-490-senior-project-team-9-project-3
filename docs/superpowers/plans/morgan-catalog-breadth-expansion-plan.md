# Morgan Catalog Breadth Expansion Plan

1. Audit the current dataset and identify the highest-value coverage gaps in majors, departments, and course records.
2. Add a script-driven ingestion foundation under `backend/scripts/` for collecting and normalizing official Morgan program and department data.
3. Expand the dataset from official public sources into normalized CSV-backed records, starting with broad undergraduate program and department coverage.
4. Update backend retrieval and advising logic where needed so the expanded data is actually used well.
5. Add tests that verify broader major coverage, normalized program-to-department mapping, and multi-major retrieval behavior.
6. Run backend tests and compile checks, then review the working tree before any commit.
