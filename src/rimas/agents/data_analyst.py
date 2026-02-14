"""Data Analyst Agent."""

import logging

from src.rimas.agents.state import PlanState

logger = logging.getLogger(__name__)


def data_analyst_agent(state: PlanState) -> PlanState:
    state["data_analysis"] = {
        "summary": "Stub: Data patterns analyzed",
        "trends": ["stable", "seasonal"],
        "confidence": 0.85,
    }
    return state
