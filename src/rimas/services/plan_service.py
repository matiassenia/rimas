"""Plan persistence service."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rimas.api.schemas import PlanStatus
from rimas.db.models import Plan, PlanEvent


def _to_serializable(obj: dict) -> dict:
    """Ensure all values are JSON-serializable."""
    result = {}
    for k, v in obj.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, dict):
            result[k] = _to_serializable(v)
        elif isinstance(v, list):
            result[k] = [
                _to_serializable(x) if isinstance(x, dict) else x
                for x in v
            ]
        else:
            result[k] = v
    return result


async def create_plan(
    db: AsyncSession,
    request_payload: dict,
    agent_outputs: dict,
    final_decision: dict,
    status: str = PlanStatus.created,
) -> str:
    now = datetime.utcnow()
    payload = _to_serializable(request_payload)
    outputs = _to_serializable(agent_outputs)
    decision = _to_serializable(final_decision)

    plan = Plan(
        id=str(uuid4()),
        request_payload=payload,
        agent_outputs=outputs,
        final_decision=decision,
        status=status,
        created_at=now,
        updated_at=now,
    )
    db.add(plan)
    await db.flush()

    for event_type, payload_val in outputs.items():
        ev = PlanEvent(
            plan_id=plan.id,
            event_type=event_type,
            payload=payload_val if isinstance(payload_val, dict) else {"value": payload_val},
            created_at=now,
        )
        db.add(ev)
    ev = PlanEvent(
        plan_id=plan.id,
        event_type="final_decision",
        payload=decision,
        created_at=now,
    )
    db.add(ev)
    await db.flush()
    return plan.id


async def get_plan(db: AsyncSession, plan_id: str) -> Plan | None:
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalar_one_or_none()


async def approve_plan(db: AsyncSession, plan_id: str) -> Plan | None:
    plan = await get_plan(db, plan_id)
    if plan is None:
        return None
    plan.status = PlanStatus.approved
    plan.updated_at = datetime.utcnow()
    await db.flush()
    ev = PlanEvent(
        plan_id=plan.id,
        event_type="approved",
        payload={"status": PlanStatus.approved},
        created_at=datetime.utcnow(),
    )
    db.add(ev)
    await db.flush()
    return plan


async def reject_plan(db: AsyncSession, plan_id: str) -> Plan | None:
    plan = await get_plan(db, plan_id)
    if plan is None:
        return None
    plan.status = PlanStatus.rejected
    plan.updated_at = datetime.utcnow()
    await db.flush()
    ev = PlanEvent(
        plan_id=plan.id,
        event_type="rejected",
        payload={"status": PlanStatus.rejected},
        created_at=datetime.utcnow(),
    )
    db.add(ev)
    await db.flush()
    return plan
