"""Plan REST contract tests.

These tests validate the FastAPI REST contract for the Plans API using an
in-memory SQLite database (aiosqlite) and dependency overrides so we don't
touch the real Postgres container during unit tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.rimas.api.deps import get_db
from src.rimas.api.main import app
from src.rimas.db.models import Base


@pytest.fixture
async def db_client():
    """Yield an AsyncClient wired to the FastAPI app + an in-memory SQLite DB.

    Why:
    - We want fast, isolated tests (no Docker required).
    - We override `get_db` so routes use this in-memory DB session.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Create all tables for this ephemeral DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Session factory for the in-memory database
    maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db():
        """Dependency override for `get_db` used by the FastAPI routes."""
        async with maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # Apply dependency override for the duration of this fixture
    app.dependency_overrides[get_db] = override_get_db

    # Use ASGITransport so HTTPX calls the app in-process (no network)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup overrides so they don't leak to other test modules
    app.dependency_overrides.clear()

    # Optional: dispose the engine (good practice)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_plan_returns_plan_id_and_recommendations(db_client):
    """POST /plans returns PlanResponse with recommendations + metadata."""
    r = await db_client.post(
        "/plans/",
        json={
            "store_id": 1,
            "horizon_days": 7,
            "constraints": {
                "lead_time_days": 5,
                "budget_limit": 5000.0,
                "max_discount": 0.15,
            },
            "items": [
                {"item_id": 101, "current_stock": 10},
                {"item_id": 102, "current_stock": 60},
            ],
        },
    )
    assert r.status_code == 200

    data = r.json()
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
    """GET /plans/{plan_id} returns persisted plan."""
    create_r = await db_client.post(
        "/plans/",
        json={
            "store_id": 1,
            # horizon_days omitted intentionally: schema has default=7
            "items": [{"item_id": 1, "current_stock": 10}],
        },
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
    """Unknown plan_id returns 404."""
    r = await db_client.get("/plans/nonexistent-id")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_approve_plan_changes_status(db_client):
    """POST /plans/{plan_id}/approve updates status and is reflected on GET."""
    create_r = await db_client.post(
        "/plans/",
        json={"store_id": 1, "items": [{"item_id": 1, "current_stock": 10}]},
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
    """POST /plans/{plan_id}/reject updates status and is reflected on GET."""
    create_r = await db_client.post(
        "/plans/",
        json={"store_id": 1, "items": [{"item_id": 1, "current_stock": 10}]},
    )
    assert create_r.status_code == 200
    plan_id = create_r.json()["plan_id"]

    reject_r = await db_client.post(f"/plans/{plan_id}/reject")
    assert reject_r.status_code == 200
    assert reject_r.json()["status"] == "rejected"

    get_r = await db_client.get(f"/plans/{plan_id}")
    assert get_r.status_code == 200
    assert get_r.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_create_plan_with_langgraph_orchestrator(db_client, monkeypatch):
    """POST /plans works with ORCHESTRATOR=langgraph.

    We patch settings at runtime so the orchestration layer uses the
    LangGraph-backed implementation (or stub).
    """
    import rimas.config as config_mod

    monkeypatch.setattr(config_mod.settings, "orchestrator", "langgraph")

    r = await db_client.post(
        "/plans/",
        json={
            "store_id": 1,
            "horizon_days": 7,
            "items": [{"item_id": 101, "current_stock": 10}],
        },
    )
    assert r.status_code == 200

    data = r.json()
    assert data["plan_id"]
    assert data["status"] == "created"
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
    assert "metadata" in data
    assert "trace_id" in data["metadata"]
