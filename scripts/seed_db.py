"""Seed database with sample data."""

import asyncio
import logging
import sys

sys.path.insert(0, ".")
from src.rimas.db.session import init_db, get_async_session_maker
from src.rimas.db.models import Plan
from src.rimas.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def seed():
    await init_db()
    maker = get_async_session_maker()
    async with maker() as session:
        plan = Plan(
            request_payload={"objective": "seed"},
            agent_outputs={},
            final_decision={"approved": True},
            status="seed",
        )
        session.add(plan)
        await session.commit()
        logger.info("Database seeded")


if __name__ == "__main__":
    asyncio.run(seed())
