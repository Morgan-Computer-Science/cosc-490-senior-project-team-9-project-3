# Morgan State AI Faculty Advisor

Morgan State AI Faculty Advisor is a full-stack student advising system built for a university-wide advising experience. It combines authentication, degree-progress tracking, retrieval-augmented advising, student-state analysis, and multimodal chat features into one demo-ready application.

## Current capabilities

- Secure student signup and login
- Profile editing with major and class year
- Completed-course tracking and degree-progress summaries
- Recommended next courses based on remaining requirements and prerequisite checks
- University-wide advising retrieval across courses, departments, faculty, degree requirements, and support resources
- Advisor chat with session history
- Voice input through browser speech recognition
- Spoken advisor replies through browser text-to-speech
- Student-state analysis for planning, career, and wellness-support signals

## Tech stack

- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy
- AI model: Gemini
- Grounding: CSV-backed retrieval layer for Morgan State advising data

## Project structure

- `frontend/`: React client
- `backend/`: FastAPI API, retrieval logic, models, and data
- `docs/`: architecture and project documentation

## Run locally

### Backend

```bash
cd backend
source .venv312/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at `http://127.0.0.1:5173` and backend runs at `http://127.0.0.1:8000`.

## Key documentation

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Demo Walkthrough](docs/DEMO_WALKTHROUGH.md)
- [Data Connectors Plan](docs/DATA_CONNECTORS.md)

## Current focus

The project has moved beyond a Computer Science-only chatbot. The system now aims to support students across multiple Morgan State majors while remaining grounded in university-specific source material.
