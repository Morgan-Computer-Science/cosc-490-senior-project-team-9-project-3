import csv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSES_CSV_PATH = DATA_DIR / "courses.csv"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _normalize_course_row(row: dict[str, str]) -> dict[str, object]:
    credits = (row.get("credits") or "").strip()
    return {
        "code": (row.get("code") or "").strip(),
        "title": (row.get("title") or "").strip(),
        "description": (row.get("description") or "").strip() or None,
        "credits": int(credits) if credits.isdigit() else None,
        "department": (row.get("department") or "").strip() or None,
        "level": (row.get("level") or "").strip() or None,
        "semester_offered": (row.get("semester_offered") or "").strip() or None,
        "instructor": (row.get("instructor") or "").strip() or None,
    }


def _sync_courses_from_csv() -> None:
    from . import models

    if not COURSES_CSV_PATH.exists():
        return

    with SessionLocal() as db:
        existing_by_code = {
            course.code: course
            for course in db.query(models.Course).all()
            if course.code
        }

        with COURSES_CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            for raw_row in csv.DictReader(csv_file):
                payload = _normalize_course_row(raw_row)
                code = payload["code"]
                if not code:
                    continue

                existing = existing_by_code.get(code)
                if existing:
                    existing.title = payload["title"]
                    existing.description = payload["description"]
                    existing.credits = payload["credits"]
                    existing.department = payload["department"]
                    existing.level = payload["level"]
                    existing.semester_offered = payload["semester_offered"]
                    existing.instructor = payload["instructor"]
                    continue

                db.add(models.Course(**payload))

        db.commit()


def init_db():
    Base.metadata.create_all(bind=engine)
    _sync_courses_from_csv()
