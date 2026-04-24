from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BACKEND_ENV_PATH)

from .config import ALLOWED_CORS_ORIGINS
from .db import init_db
from .auth import router as auth_router
from .catalog import router as catalog_router
from .chat import router as chat_router
from .integrations import router as integrations_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Morgan State AI Advisor Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "morgan-ai-backend-web"}


app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(chat_router)
app.include_router(integrations_router)
