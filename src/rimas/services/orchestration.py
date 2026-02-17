"""Orchestration - run plan workflow (stub or LangGraph)."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from rimas.api.schemas import CreatePlanRequest
from rimas.config import settings

logger = logging.getLogger(__name__)


async def run_plan_workflow(
    req: CreatePlanRequest,
    db: AsyncSession,
) -> dict:
    if settings.orchestrator == "langgraph":
        from rimas.services.orchestration_langgraph import run_plan_workflow_langgraph

        return await run_plan_workflow_langgraph(req=req, db=db)

    from rimas.services._orchestration_stub import run_plan_workflow_stub

    return await run_plan_workflow_stub(req=req, db=db)
