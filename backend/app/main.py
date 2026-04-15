from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from .config import ALLOWED_CORS_ORIGINS
from .db import init_db
from .auth import router as auth_router
from .catalog import router as catalog_router
from .chat import router as chat_router

app = FastAPI(title="Morgan State AI Advisor Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "morgan-ai-backend-web"}


app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(chat_router)
