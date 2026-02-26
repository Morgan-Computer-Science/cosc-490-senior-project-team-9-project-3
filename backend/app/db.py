from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL. The file will be created in the backend/ folder.
DATABASE_URL = "sqlite:///./morgan_ai.db"

# connect_args is needed for SQLite when used in multi-threaded apps like FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each request to the API will get its own database session object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our ORM models will inherit from
Base = declarative_base()


def init_db() -> None:
    """
    Create all tables in the database.
    Called once on application startup.
    """
    from . import models  # import models so Base knows them
    Base.metadata.create_all(bind=engine)