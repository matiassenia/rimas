"""Database session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from rimas.config import settings
from rimas.db.models import Base

_engine = None
_session_maker = None


def get_async_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url_async,
            echo=False,
        )
    return _engine


def get_async_session_maker():
    global _session_maker
    if _session_maker is None:
        engine = get_async_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_maker


async def init_db() -> None:
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
