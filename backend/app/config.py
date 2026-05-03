import os


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


DEFAULT_FRONTEND_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

ALLOWED_CORS_ORIGINS = _split_csv(os.getenv("ALLOWED_CORS_ORIGINS")) or DEFAULT_FRONTEND_ORIGINS
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./morgan_ai.db")
MAX_ATTACHMENT_BYTES = int(os.getenv("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024)))
AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "5"))
AUTH_RATE_WINDOW_SECONDS = int(os.getenv("AUTH_RATE_WINDOW_SECONDS", "60"))
CHAT_RATE_LIMIT = int(os.getenv("CHAT_RATE_LIMIT", "12"))
CHAT_RATE_WINDOW_SECONDS = int(os.getenv("CHAT_RATE_WINDOW_SECONDS", "60"))
IMPORT_RATE_LIMIT = int(os.getenv("IMPORT_RATE_LIMIT", "6"))
IMPORT_RATE_WINDOW_SECONDS = int(os.getenv("IMPORT_RATE_WINDOW_SECONDS", "60"))
