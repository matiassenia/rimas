"""Plans endpoint - REST contract."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rimas.api.deps import get_db
from rimas.api.schemas import CreatePlanRequest, PlanMetadata, PlanResponse
from rimas.services.orchestration import run_plan_workflow
from rimas.services.plan_service import get_plan, approve_plan, reject_plan

logger = logging.getLogger(__name__)
router = APIRouter()


def _plan_to_response(plan) -> PlanResponse:
    """Map Plan model to PlanResponse."""
    fd = plan.final_decision or {}
    recs = fd.get("recommendations", [])
    meta = fd.get("metadata", {})
    return PlanResponse(
        plan_id=plan.id,
        status=plan.status,
        recommendations=recs,
        metadata=PlanMetadata(
            model_version=meta.get("model_version"),
            generated_at=meta.get("generated_at"),
            trace_id=meta.get("trace_id") or str(uuid.uuid4()),
        ),
    )


@router.post("/", response_model=PlanResponse)
async def create_plan_endpoint(
    req: CreatePlanRequest,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    result = await run_plan_workflow(req=req, db=db)
    return PlanResponse(
        plan_id=result["plan_id"],
        status=result["status"],
        recommendations=result["recommendations"],
        metadata=result["metadata"],
    )


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan_endpoint(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    plan = await get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _plan_to_response(plan)


@router.post("/{plan_id}/approve", response_model=PlanResponse)
async def approve_plan_endpoint(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    plan = await approve_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _plan_to_response(plan)


@router.post("/{plan_id}/reject", response_model=PlanResponse)
async def reject_plan_endpoint(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    plan = await reject_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _plan_to_response(plan)
