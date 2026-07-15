from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings

# Celery tasks are plain sync functions, so they get their own sync engine
# (psycopg2) rather than sharing the async engine used by FastAPI.
_sync_url = settings.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")

sync_engine = create_engine(_sync_url, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


def get_sync_db() -> Session:
    """Call from Celery tasks: `with get_sync_db() as db:`"""
    return SyncSessionLocal()