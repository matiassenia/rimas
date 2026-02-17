"""
LangGraph-based plan orchestration.

This module defines the LangGraph workflow used to execute
the multi-agent retail planning pipeline.

Compatibility notes:
- LangGraph versions differ in how they represent the "start" node:
  * Some expose START in langgraph.graph
  * Others require using `graph.set_entry_point(<node_name>)`
- To avoid version lock issues, we implement a small compatibility layer.

Design notes:
- State fields (channels) must NOT share names with graph node identifiers.
  PlanState often contains keys like "data_analysis", etc., so node names are
  prefixed with "node_" to avoid collisions.
"""

import logging
from datetime import datetime
from uuid import uuid4

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from rimas.agents.state import PlanState
from rimas.agents.nodes import (
    data_analysis_node,
    inventory_analysis_node,
    marketing_analysis_node,
    supervisor_node,
)
from rimas.api.schemas import CreatePlanRequest, PlanMetadata, PlanStatus
from rimas.services.plan_service import create_plan

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def _build_graph():
    """
    Build and compile a LangGraph StateGraph for the plan workflow.

    IMPORTANT:
    Node names must not collide with PlanState channels.
    So we name nodes with a `node_` prefix.
    """
    graph = StateGraph(PlanState)

    # Node identifiers (avoid collision with PlanState keys)
    node_data = "node_data_analysis"
    node_inv = "node_inventory_analysis"
    node_mkt = "node_marketing_analysis"
    node_sup = "node_supervisor"

    # Register nodes
    graph.add_node(node_data, data_analysis_node)
    graph.add_node(node_inv, inventory_analysis_node)
    graph.add_node(node_mkt, marketing_analysis_node)
    graph.add_node(node_sup, supervisor_node)

    # Wire edges
    graph.add_edge(node_data, node_inv)
    graph.add_edge(node_inv, node_mkt)
    graph.add_edge(node_mkt, node_sup)
    graph.add_edge(node_sup, END)

    # -----------------------------------------------------------------------
    # LangGraph "start" compatibility:
    # - Newer versions may expose START constant
    # - Older versions require set_entry_point()
    # -----------------------------------------------------------------------
    try:
        # Some versions expose START from langgraph.graph
        from langgraph.graph import START  # type: ignore
        graph.add_edge(START, node_data)
    except Exception:
        # Fallback for versions without START
        graph.set_entry_point(node_data)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public Orchestration Entry Point
# ---------------------------------------------------------------------------

async def run_plan_workflow_langgraph(
    req: CreatePlanRequest,
    db: AsyncSession,
) -> dict:
    """
    Execute the plan workflow using LangGraph.

    Steps:
    1) Build initial workflow state
    2) Execute graph asynchronously
    3) Extract agent outputs and recommendations
    4) Persist plan + audit-ready fields in DB
    5) Return REST-friendly response
    """
    trace_id = str(uuid4())
    now = datetime.utcnow()

    initial: PlanState = {
        "request": req.model_dump(mode="json"),
        "trace_id": trace_id,
        "generated_at": now,
        "agent_outputs": {},
    }

    graph = _build_graph()
    result = await graph.ainvoke(initial)

    agent_outputs = result.get("agent_outputs") or {}
    final_decision_raw = result.get("final_decision") or {}

    # Some node implementations may return recommendations directly in state,
    # others inside final_decision.
    recommendations = (
        result.get("recommendations")
        or final_decision_raw.get("recommendations", [])
    )

    # Persisted consolidated decision
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
