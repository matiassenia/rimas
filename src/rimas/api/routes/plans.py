"""Plans endpoint - multi-agent orchestration."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.rimas.api.deps import get_db
from src.rimas.services.orchestration import run_plan_workflow

logger = logging.getLogger(__name__)
router = APIRouter()


class PlanRequest(BaseModel):
    objective: str = "optimize inventory"
    context: dict | None = None


class PlanResponse(BaseModel):
    plan_id: str
    objective: str
    final_decision: dict
    agent_outputs: dict
    status: str


@router.post("/", response_model=PlanResponse)
async def create_plan(
    req: PlanRequest,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    result = await run_plan_workflow(
        objective=req.objective,
        context=req.context or {},
        db=db,
    )
    return PlanResponse(**result)
