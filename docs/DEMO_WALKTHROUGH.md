# Demo Walkthrough

## Goal

This walkthrough is designed for class demos, check-ins, and presentations. It shows the project as a multimodal Morgan State advising system rather than only a chatbot.

## Before the demo

1. Start the backend
```bash
cd backend
source .venv312/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

2. Start the frontend
```bash
cd frontend
npm run dev
```

3. Open the app at `http://127.0.0.1:5173`

## Demo flow

### 1. Authentication and profile grounding

- Sign up or log in
- Open the profile panel
- Set a major and year
- Mark a few completed courses

What to say:
- The advisor is personalized by major, year, and completed coursework
- This lets the system make more grounded planning decisions

### 2. Degree progress and next-course recommendations

- Show the progress summary
- Point out:
  - completion percentage
  - recommended next courses
  - blocked courses that still depend on prerequisites

What to say:
- The system does not just chat
- It performs degree-planning logic and prerequisite-aware sequencing

### 3. RAG-backed advising

- Ask: `Who should I contact for Information Systems advising?`
- Ask: `What are the degree requirements for Business Administration?`

What to say:
- The advisor retrieves university-specific context from courses, departments, faculty, degree requirements, and support resources
- This is retrieval-augmented generation, not a generic AI response

### 4. Multimodal input and output

- Use the microphone button to ask a question by voice
- Use the `Read aloud` button on the advisor response

What to say:
- The app supports speech input and speech output
- That helps satisfy the multimodal system requirement

### 5. Student-state / support-aware behavior

- Ask: `I feel overwhelmed and need help finding the right campus support.`

What to say:
- The system detects support-related language
- It can shift from planning mode into a more careful support-aware advising mode

### 6. File-assisted advising

- Upload a screenshot, image, text file, CSV, or PDF with a question
- Example prompt:
  - `Can you summarize the important points from this document for my advising plan?`
  - `Can you review this schedule screenshot and tell me what matters for advising?`
  - `Can you look at this degree audit PDF and tell me what seems incomplete?`
  - `Can you use this transcript-style file to help me think about what comes next?`

What to say:
- The project now supports attachment-assisted advising
- PDFs and text-based files can be brought into the chat context
- Images and screenshots can now go through Gemini-backed multimodal analysis in the advisor chat
- The backend now distinguishes likely document types such as schedules, transcripts, degree audits, and forms so the advisor can reason more appropriately about the uploaded material

## Good demo questions

- `What classes should I take after COSC 111?`
- `Help me plan a strong sophomore schedule.`
- `What are the degree requirements for Business Administration?`
- `Who should I contact for Information Systems advising?`
- `I feel overwhelmed and need help finding the right campus support.`
- `How should I prepare for internships in my major?`

## Talking points for the assignment

- Multimodal:
  - speech input
  - spoken output
  - attachment-assisted input for screenshots, images, PDFs, and text files
- Multi-stage / multi-model style system:
  - retrieval
  - degree-planning logic
  - student-state analysis
  - generative response layer
- University grounding:
  - Morgan State-specific data
  - department and faculty information
  - requirement-aware advising
