from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .auth import router as auth_router

app = FastAPI(title="Morgan State CS AI Advisor Backend")

# CORS for your website frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create tables if they don't exist
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "morgan-ai-backend-web"}


# Register auth routes under /auth
app.include_router(auth_router)