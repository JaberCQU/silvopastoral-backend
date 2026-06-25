# ============================================================
# Database engine and session management
# ============================================================
# Works with both SQLite (local dev, zero setup) and PostgreSQL
# (production on Render/Railway) without any code changes --
# SQLAlchemy abstracts the difference. Which one is used is
# controlled entirely by the DATABASE_URL environment variable.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# SQLite needs this extra flag to allow use across threads
# (FastAPI/uvicorn handles each request on a worker thread).
# Postgres does not need or accept this flag.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and guarantees it is closed afterwards, even if an error occurs.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
