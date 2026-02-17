"""Seed database with sample data."""

import asyncio
import logging
import sys

sys.path.insert(0, ".")
from rimas.db.session import init_db, get_async_session_maker
from rimas.db.models import Plan
from rimas.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def seed():
    await init_db()
    maker = get_async_session_maker()
    async with maker() as session:
        plan = Plan(
            request_payload={"store_id": 1, "horizon_days": 7, "items": []},
            agent_outputs={},
            final_decision={
                "recommendations": [],
                "metadata": {"model_version": None, "generated_at": "2024-01-01T00:00:00", "trace_id": "seed"},
            },
            status="created",
        )
        session.add(plan)
        await session.commit()
        logger.info("Database seeded")


if __name__ == "__main__":
    asyncio.run(seed())
