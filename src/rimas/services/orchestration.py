"""Orchestration - run plan workflow and persist."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.rimas.agents.graph import build_plan_graph
from src.rimas.agents.state import PlanState
from src.rimas.services.plan_service import create_plan

logger = logging.getLogger(__name__)


async def run_plan_workflow(
    objective: str,
    context: dict,
    db: AsyncSession,
) -> dict:
    graph = build_plan_graph()
    initial: PlanState = {"objective": objective, "context": context}
    result = graph.invoke(initial)

    agent_outputs = {
        "data_analysis": result.get("data_analysis", {}),
        "inventory_analysis": result.get("inventory_analysis", {}),
        "marketing_analysis": result.get("marketing_analysis", {}),
        "supervisor_decision": result.get("supervisor_decision", {}),
    }
    final_decision = result.get("final_decision", {"approved": False})

    plan_id = await create_plan(
        db=db,
        request_payload={"objective": objective, "context": context},
        agent_outputs=agent_outputs,
        final_decision=final_decision,
    )
    return {
        "plan_id": plan_id,
        "objective": objective,
        "final_decision": final_decision,
        "agent_outputs": agent_outputs,
        "status": "completed",
    }
