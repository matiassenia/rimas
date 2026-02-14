"""Plan creation tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.rimas.api.main import app
from src.rimas.api.deps import get_db
from src.rimas.db.models import Base


@pytest.fixture
async def db_client():
    """Client with real async DB - requires DATABASE_URL_ASYNC to use test DB."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from src.rimas.db.models import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async def override_get_db():
        async with maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_plans_returns_structured_response(db_client):
    r = await db_client.post("/plans/", json={"objective": "test", "context": {}})
    assert r.status_code == 200
    data = r.json()
    assert "plan_id" in data
    assert "objective" in data
    assert data["objective"] == "test"
    assert "final_decision" in data
    assert "agent_outputs" in data
    assert "status" in data
    assert data["status"] == "completed"
