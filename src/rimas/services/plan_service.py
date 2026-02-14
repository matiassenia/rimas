"""Plan persistence service."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.rimas.db.models import Plan, PlanEvent


async def create_plan(
    db: AsyncSession,
    request_payload: dict,
    agent_outputs: dict,
    final_decision: dict,
) -> str:
    plan = Plan(
        id=str(uuid4()),
        request_payload=request_payload,
        agent_outputs=agent_outputs,
        final_decision=final_decision,
        status="completed",
    )
    db.add(plan)
    await db.flush()

    event = PlanEvent(
        plan_id=plan.id,
        event_type="plan_created",
        payload={"status": "completed"},
    )
    db.add(event)
    await db.flush()
    return plan.id
