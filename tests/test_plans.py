"""Plan REST contract tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.rimas.api.main import app
from src.rimas.api.deps import get_db
from src.rimas.db.models import Base


@pytest.fixture
async def db_client():
    """Client with in-memory SQLite."""
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
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_plan_returns_plan_id_and_recommendations(db_client):
    r = await db_client.post(
        "/plans/",
        json={
            "store_id": 1,
            "horizon_days": 7,
            "constraints": {"lead_time_days": 5, "budget_limit": 5000.0, "max_discount": 0.15},
            "items": [
                {"item_id": 101, "current_stock": 10},
                {"item_id": 102, "current_stock": 60},
            ],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "plan_id" in data
    assert data["plan_id"]
    assert data["status"] == "created"
    assert "recommendations" in data
    assert len(data["recommendations"]) == 2
    rec = data["recommendations"][0]
    assert "item_id" in rec
    assert "recommended_order_qty" in rec
    assert "recommended_discount" in rec
    assert "confidence" in rec
    assert "rationale" in rec
    assert "metadata" in data
    assert "trace_id" in data["metadata"]
    assert "generated_at" in data["metadata"]


@pytest.mark.asyncio
async def test_get_plan_by_id(db_client):
    create_r = await db_client.post(
        "/plans/",
        json={"store_id": 1, "horizon_days": 7, "items": [{"item_id": 1, "current_stock": 5}]},
    )
    assert create_r.status_code == 200
    plan_id = create_r.json()["plan_id"]

    get_r = await db_client.get(f"/plans/{plan_id}")
    assert get_r.status_code == 200
    data = get_r.json()
    assert data["plan_id"] == plan_id
    assert data["status"] == "created"
    assert len(data["recommendations"]) == 1


@pytest.mark.asyncio
async def test_get_plan_not_found(db_client):
    r = await db_client.get("/plans/nonexistent-id")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_approve_plan_changes_status(db_client):
    create_r = await db_client.post(
        "/plans/",
        json={"store_id": 1, "items": []},
    )
    assert create_r.status_code == 200
    plan_id = create_r.json()["plan_id"]

    approve_r = await db_client.post(f"/plans/{plan_id}/approve")
    assert approve_r.status_code == 200
    assert approve_r.json()["status"] == "approved"

    get_r = await db_client.get(f"/plans/{plan_id}")
    assert get_r.status_code == 200
    assert get_r.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_reject_plan_changes_status(db_client):
    create_r = await db_client.post(
        "/plans/",
        json={"store_id": 1, "items": []},
    )
    assert create_r.status_code == 200
    plan_id = create_r.json()["plan_id"]

    reject_r = await db_client.post(f"/plans/{plan_id}/reject")
    assert reject_r.status_code == 200
    assert reject_r.json()["status"] == "rejected"
