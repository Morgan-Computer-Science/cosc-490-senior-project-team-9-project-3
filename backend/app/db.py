from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

# SQLite database URL. The file will be created in the backend/ folder.
DATABASE_URL = "sqlite:///./morgan_ai.db"

# connect_args is needed for SQLite when used in multi-threaded apps like FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each request to the API will get its own database session object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def init_db():
    # Import models so metadata knows about them
    from . import models

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed initial data if tables are empty
    db = SessionLocal()
    try:
        # --- Seed Courses ---
        if db.query(models.Course).count() == 0:
            sample_courses = [
                models.Course(
                    code="COSC 111",
                    title="Computer Science I",
                    description="Introduction to problem solving, algorithms, and programming in a high-level language.",
                    credits=4,
                    department="Computer Science",
                    level="Undergraduate",
                    semester_offered="Fall,Spring",
                ),
                models.Course(
                    code="COSC 112",
                    title="Computer Science II",
                    description="Continuation of COSC 111 with emphasis on data structures and software design.",
                    credits=4,
                    department="Computer Science",
                    level="Undergraduate",
                    semester_offered="Spring",
                ),
                models.Course(
                    code="COSC 457",
                    title="Artificial Intelligence",
                    description="Introduction to artificial intelligence concepts including search, reasoning, and learning.",
                    credits=3,
                    department="Computer Science",
                    level="Undergraduate",
                    semester_offered="Fall",
                ),
                models.Course(
                    code="COSC 458",
                    title="Machine Learning",
                    description="Study of machine learning algorithms and applications.",
                    credits=3,
                    department="Computer Science",
                    level="Undergraduate",
                    semester_offered="Spring",
                ),
            ]
            db.add_all(sample_courses)

        # --- Seed Faculty ---
        if db.query(models.Faculty).count() == 0:
            sample_faculty = [
                models.Faculty(
                    name="Dr. Morgan Advisor",
                    title="Associate Professor of Computer Science",
                    email="morgan.advisor@morgan.edu",
                    office="Dwight Hall 101",
                    phone="(410) 555-1001",
                    department="Computer Science",
                    office_hours="Mon/Wed 2:00–4:00 PM",
                ),
                models.Faculty(
                    name="Dr. AI Mentor",
                    title="Assistant Professor of Computer Science",
                    email="ai.mentor@morgan.edu",
                    office="Dwight Hall 202",
                    phone="(410) 555-1002",
                    department="Computer Science",
                    office_hours="Tue/Thu 11:00 AM–1:00 PM",
                ),
            ]
            db.add_all(sample_faculty)

        db.commit()
    finally:
        db.close()


# FastAPI dependency that gives a DB session to each request
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()