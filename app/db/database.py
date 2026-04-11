import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


BASE_DIR = Path(__file__).resolve().parents[2]


def resolve_database_url(explicit_url: str | None = None) -> str:
    return explicit_url or f"sqlite:///{(BASE_DIR / 'compliance.db').as_posix()}"


def build_engine_kwargs(database_url: str) -> dict:
    kwargs = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        return kwargs

    kwargs.update(
        pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "40")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    )
    return kwargs


DATABASE_URL = resolve_database_url(settings.DATABASE_URL)
engine = create_engine(DATABASE_URL, **build_engine_kwargs(DATABASE_URL))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
