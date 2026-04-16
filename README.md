# Morgan State AI Faculty Advisor

**Interface**
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React%20Router-7-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white)

**Backend**
![Python](https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.133-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**AI and Document Understanding**
![Gemini](https://img.shields.io/badge/Gemini-Live%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![PDF Parsing](https://img.shields.io/badge/PDF-Parsing-B30B00?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
![OCR](https://img.shields.io/badge/OCR-Images%20%26%20Scans-5C6BC0?style=for-the-badge)
![Morgan State](https://img.shields.io/badge/Morgan%20State-University%20Advising-002D62?style=for-the-badge)

Morgan State AI Faculty Advisor is a full-stack student advising system built for a university-wide advising experience. It combines authentication, degree-progress tracking, retrieval-augmented advising, student-state analysis, and multimodal chat features into one launch-oriented application.

## Current capabilities

- Secure student signup and login
- Profile editing with major and class year
- Completed-course tracking and degree-progress summaries
- Recommended next courses based on remaining requirements and prerequisite checks
- University-wide advising retrieval across courses, departments, faculty, degree requirements, and support resources
- Advisor chat with session history
- Voice input through browser speech recognition
- Spoken advisor replies through browser text-to-speech
- Image, PDF, and text-file attachment support in chat
- Student-state analysis for planning, career, and wellness-support signals
- Connector-ready import flow for manual, Canvas-style, and WebSIS-style student data
- Source-specific connector parsing for Canvas current-course context and WebSIS academic-record context

## Tech stack

### Frontend

- React
- Vite
- Axios
- React Router

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

### AI and document understanding

- Gemini for live advisor responses and multimodal reasoning
- PDF extraction for transcript, degree-audit, and document parsing
- OCR-assisted image and scanned-document handling

### Grounding and advising data

- CSV-backed Morgan State course, program, faculty, department, and prerequisite data
- Degree-progress and prerequisite-aware planning logic
- Canvas-style and WebSIS-style import support through a connector-ready ingestion flow

## Project structure

- `frontend/`: React client
- `backend/`: FastAPI API, retrieval logic, models, and data
- `docs/`: architecture and project documentation

## Run locally

### 1. Clone the project

#### Git Bash

```bash
git clone https://github.com/Morgan-Computer-Science/cosc-490-senior-project-team-9-project-3.git
cd cosc-490-senior-project-team-9-project-3
```

#### PowerShell

```powershell
git clone https://github.com/Morgan-Computer-Science/cosc-490-senior-project-team-9-project-3.git
cd .\cosc-490-senior-project-team-9-project-3
```

### 2. Set up the backend

#### Git Bash

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

#### PowerShell

```powershell
cd .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` and add your Gemini key:

```env
GEMINI_API_KEY=your_api_key_here
```

Then start the backend:

#### Git Bash

```bash
cd backend
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### PowerShell

```powershell
cd .\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 3. Set up the frontend

#### Git Bash

```bash
cd frontend
npm install
npm run dev
```

#### PowerShell

```powershell
cd .\frontend
npm install
npm run dev
```

### 4. Open the app

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`

## Environment notes

- The backend expects a Gemini key in `backend/.env`.
- If the live advisor falls back to grounded-only responses, restart the backend after checking the API key.
- If an older local virtual environment like `.venv312` causes issues, create a fresh `backend/.venv` and reinstall from `requirements.txt`.
- If PowerShell blocks local script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Key documentation

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Data Connectors Plan](docs/DATA_CONNECTORS.md)
- [Computer Science Audit Frontend Design](docs/superpowers/specs/computer-science-audit-frontend-design.md)
- [Business Administration, Marketing, and Entrepreneurship Depth Design](docs/superpowers/specs/business-administration-marketing-entrepreneurship-depth-design.md)

## Current focus

The project has moved beyond a Computer Science-only chatbot. The system now supports multiple Morgan State majors while remaining grounded in university-specific source material, OCR-assisted document understanding, connector-ready student data ingestion, and deeper department-specific advising logic.
