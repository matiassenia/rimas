"""LangGraph workflow for multi-agent plans."""

from langgraph.graph import StateGraph, END

from src.rimas.agents.state import PlanState
from src.rimas.agents.data_analyst import data_analyst_agent
from src.rimas.agents.inventory import inventory_agent
from src.rimas.agents.marketing import marketing_agent
from src.rimas.agents.supervisor import supervisor_agent


def build_plan_graph():
    graph = StateGraph(PlanState)

    graph.add_node("data_analyst", data_analyst_agent)
    graph.add_node("inventory", inventory_agent)
    graph.add_node("marketing", marketing_agent)
    graph.add_node("supervisor", supervisor_agent)

    graph.set_entry_point("data_analyst")
    graph.add_edge("data_analyst", "inventory")
    graph.add_edge("inventory", "marketing")
    graph.add_edge("marketing", "supervisor")
    graph.add_edge("supervisor", END)

    return graph.compile()
