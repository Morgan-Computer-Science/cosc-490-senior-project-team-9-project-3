from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db

app = FastAPI(title="Morgan State CS AI Advisor Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create tables if they don't exist yet
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "morgan-ai-backend-web"}