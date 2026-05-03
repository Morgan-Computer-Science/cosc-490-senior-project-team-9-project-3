# Computer Science Catalog Depth Design

## Goal
Deepen the Morgan State Computer Science backend so advising reflects Morgan's public Computer Science focus areas more authentically, with stronger elective mapping, pathway guidance, and faculty-context alignment.

## Why this phase now
The first CS depth slice already improved sequencing and COSC490 readiness. The next best step is to deepen the CS catalog itself so those recommendations are supported by richer, more authentic Morgan-specific pathway data.

## Morgan grounding
This phase should use Morgan's public Computer Science framing, especially the focus areas surfaced through department and degree pages, including:
- Software Engineering
- Cybersecurity
- Artificial Intelligence
- Quantum Security
- Data Science
- Game / Robotics
- Quantum Computing
- Cloud Computing

These focus areas should guide advising organization, but they should still be treated carefully unless Morgan explicitly describes them as formal undergraduate tracks.

## Scope
This phase will improve:
- CS elective and upper-level course coverage
- CS pathway/course mapping grounded in Morgan focus areas
- faculty and advising context for CS interests where officially supported
- better chat and planning context for questions like 'which upper-level CS classes fit my interests?'

This phase will not yet attempt:
- a perfect official CS elective catalog
- full transcript-perfect audit behavior
- other department depth at the same time

## Architecture
Keep the CS pathway layer added in the previous phase, but deepen it with additional Morgan-specific metadata.

### 1. Focus-area mapping
Add a dedicated CS catalog-depth data source that maps Morgan's CS focus areas to:
- relevant CS courses
- prerequisite expectations
- faculty or contact context when publicly supported
- pathway notes that explain what the area is good for

### 2. Course-depth expansion
Add missing upper-level or pathway-relevant CS courses that materially improve advising quality, especially around:
- AI / data
- systems / cloud
- software engineering
- networking / security
- robotics / game / quantum-related interest areas if official support is available

### 3. Faculty-context alignment
Where Morgan publicly supports it, connect CS pathway areas to faculty or department contact context so the advisor can point students toward the most relevant people or research directions.

### 4. Recommendation quality improvement
Use the richer CS pathway data to improve:
- pathway recommendations
n- interest-sensitive course suggestions
- 'what should I line up next?' answers
- course and faculty context returned in chat retrieval

## Data model direction
Stay CSV-backed and explicit. Add a dedicated CS focus-area dataset, for example:
- focus area name
- related courses
- foundational courses
- faculty/contact context
- notes/source URL if helpful

Keep this separate from the generic catalog rows so the logic remains easy to test and easy to expand.

## Expected product behavior
After this phase, the advisor should do better on questions like:
- I want to focus on cybersecurity. What should I take after the core sequence?
- Which courses line up with AI and data science at Morgan?
- If I am interested in software engineering, what upper-level classes should I prioritize?
- Who in Morgan CS is most relevant to cloud, AI, or systems interests?

## Testing expectations
Add backend tests for:
- official CS focus-area mapping presence
- richer CS pathway recommendation quality
- faculty/contact context retrieval for CS interests where supported
- regression coverage for generic CS advising behavior

Run:
- targeted backend tests for CS planning and retrieval
- full backend suite
- compile check

## Follow-on phase
After this phase:
1. deepen CS degree-audit logic
2. then repeat the same department-depth pattern for the next Morgan department
