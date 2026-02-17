"""Shared state for multi-agent workflow."""

from datetime import datetime
from typing import Annotated, TypedDict


def _merge_agent_outputs(left: dict, right: dict) -> dict:
    """Merge agent output updates (right into left)."""
    out = dict(left) if left else {}
    if right:
        out.update(right)
    return out


class PlanState(TypedDict, total=False):
    """Workflow state for plan orchestration."""

    request: dict
    trace_id: str
    generated_at: datetime
    agent_outputs: Annotated[dict, _merge_agent_outputs]
    final_decision: dict
    recommendations: list
    # Legacy keys (stub graph)
    objective: str
    context: dict
    data_analysis: dict
    inventory_analysis: dict
    marketing_analysis: dict
    supervisor_decision: dict
    errors: list[str]
