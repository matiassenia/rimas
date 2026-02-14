"""Shared state for multi-agent workflow."""

from typing import TypedDict


class PlanState(TypedDict, total=False):
    objective: str
    context: dict
    data_analysis: dict
    inventory_analysis: dict
    marketing_analysis: dict
    supervisor_decision: dict
    final_decision: dict
    errors: list[str]
