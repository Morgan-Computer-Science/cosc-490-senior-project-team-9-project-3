# Morgan Entities Depth Design

## Goal

Deepen the Morgan entities layer so the advisor can answer people, office, organization, team, and lab-adjacent questions with more specific Morgan grounding and stronger official contact paths.

## Why this pass matters

The app now has:

- entity-aware retrieval
- question-type routing
- better fallback behavior for leadership and office questions

The next product-level step is to make that layer broader and more useful. Right now the structure is there, but the underlying entity coverage is still too thin.

This pass is about adding depth so the system can answer more questions directly, or at least route the student to the nearest valid Morgan path with confidence.

## Scope

This pass focuses on three entity groups:

### 1. People

- chairs
- deans
- directors of undergraduate studies
- key faculty contacts tied to advising, undergraduate research, labs, or student-facing leadership

### 2. Offices and support paths

- tutoring / academic support
- transfer / registrar / records
- accessibility / wellness / counseling
- career / internship support
- financial aid / administrative support
- advising centers and department office paths

### 3. Organizations, labs, and team-adjacent paths

- robotics
- research or lab-adjacent contact paths where Morgan publishes clear support routes
- selected student organization or program-community paths where the nearest official contact is known

## Product goals

This pass should improve questions like:

- “Who runs the robotics team?”
- “Who should I contact about undergraduate research in Computer Science?”
- “What office helps with tutoring?”
- “Who helps with accessibility accommodations?”
- “What office handles internships or career preparation?”
- “Is there a lab or research contact for AI or cybersecurity?”

## Desired behavior

The quality bar should be:

- direct answer if we have a real supported answer
- nearest valid Morgan contact path if the exact owner is not publicly listed
- no vague generic advising dump when the question is clearly about a person, office, org, team, or lab

## Boundaries

This pass should:

- deepen official Morgan entity coverage
- improve answer specificity for people, offices, orgs, and lab-adjacent questions
- strengthen the existing routing layer with better grounded data

This pass should **not**:

- invent unofficial contacts
- guess team leadership if Morgan does not publish it
- blur the line between exact answers and nearest supported paths
- turn into a broad campus scrape
- run at the same time as another major catalog expansion

## Data strategy

Keep the data model lightweight and honest.

Use:

- `faculty.csv` for public people and leadership records
- `departments.csv` for department-level contact paths
- `support_resources.csv` and `offices.csv` for official support routes
- `organizations.csv` for selected organizations, teams, and lab-adjacent paths where the contact route is defensible

Prefer nearest official contact paths over invented specificity.

## Success criteria

This pass succeeds if:

- the app gives more specific Morgan answers for people and office questions
- the app gives more useful nearest-valid routes for robotics, lab, or org-adjacent questions
- fallback answers become more trustworthy and less generic
- the expanded entity layer makes the product feel more complete without reducing honesty
