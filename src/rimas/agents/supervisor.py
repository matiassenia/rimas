"""Supervisor Agent - aggregates and decides."""

import logging

from rimas.agents.state import PlanState

logger = logging.getLogger(__name__)


def supervisor_agent(state: PlanState) -> PlanState:
    state["supervisor_decision"] = {
        "action": "proceed",
        "rationale": "All agents aligned. Stub decision.",
    }
    state["final_decision"] = {
        "approved": True,
        "summary": "Plan approved based on stub analysis",
        "next_steps": ["execute", "monitor"],
    }
    return state
