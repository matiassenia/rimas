"""Orchestration - run plan workflow and persist."""

import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.rimas.agents.graph import build_plan_graph
from src.rimas.agents.state import PlanState
from src.rimas.api.schemas import (
    CreatePlanRequest,
    PlanMetadata,
    PlanRecommendation,
    PlanStatus,
)
from src.rimas.services.plan_service import create_plan

logger = logging.getLogger(__name__)


def _generate_recommendations(req: CreatePlanRequest, agent_result: dict) -> list[dict]:
    """Produce deterministic recommendations from request items."""
    recs = []
    for item in req.items:
        qty = max(0, 50 - item.current_stock) if item.current_stock < 50 else 0
        discount = min(0.1, req.constraints.max_discount) if qty > 0 else 0.0
        recs.append({
            "item_id": item.item_id,
            "recommended_order_qty": qty,
            "recommended_discount": round(discount, 2),
            "confidence": 0.85,
            "rationale": f"Stub: stock={item.current_stock}, horizon={req.horizon_days}d",
        })
    return recs


async def run_plan_workflow(
    req: CreatePlanRequest,
    db: AsyncSession,
) -> dict:
    context = {
        "store_id": req.store_id,
        "horizon_days": req.horizon_days,
        "constraints": req.constraints.model_dump(),
        "items": [i.model_dump() for i in req.items],
    }
    graph = build_plan_graph()
    initial: PlanState = {"objective": "optimize inventory", "context": context}
    result = graph.invoke(initial)

    agent_outputs = {
        "data_analysis": result.get("data_analysis", {}),
        "inventory_analysis": result.get("inventory_analysis", {}),
        "marketing_analysis": result.get("marketing_analysis", {}),
        "supervisor_decision": result.get("supervisor_decision", {}),
    }

    recommendations = _generate_recommendations(req, result)
    trace_id = str(uuid4())
    now = datetime.utcnow()

    final_decision = {
        "recommendations": recommendations,
        "metadata": {
            "model_version": None,
            "generated_at": now.isoformat(),
            "trace_id": trace_id,
        },
    }

    plan_id = await create_plan(
        db=db,
        request_payload=req.model_dump(mode="json"),
        agent_outputs=agent_outputs,
        final_decision=final_decision,
        status=PlanStatus.created,
    )

    return {
        "plan_id": plan_id,
        "status": PlanStatus.created,
        "recommendations": recommendations,
        "metadata": PlanMetadata(
            model_version=None,
            generated_at=now,
            trace_id=trace_id,
        ),
    }
