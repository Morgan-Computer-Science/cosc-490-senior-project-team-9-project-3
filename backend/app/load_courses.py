import csv
from pathlib import Path

from .db import SessionLocal, init_db
from . import models

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "courses.csv"


def load_courses_from_csv(csv_path: Path = DATA_PATH) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    init_db()

    db = SessionLocal()
    try:
        db.query(models.Course).delete()
        db.commit()

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                course = models.Course(
                    code=(row.get("code") or "").strip(),
                    title=(row.get("title") or "").strip(),
                    description=(row.get("description") or "").strip() or None,
                    credits=int(row["credits"]) if row.get("credits") else None,
                    department=(row.get("department") or "").strip() or None,
                    level=(row.get("level") or "").strip() or None,
                    semester_offered=(row.get("semester_offered") or "").strip() or None,
                    instructor=(row.get("instructor") or "").strip() or None,
                )
                db.add(course)
                count += 1

        db.commit()
        print(f"Loaded {count} courses from {csv_path}")
    finally:
        db.close()


if __name__ == "__main__":
    load_courses_from_csv()