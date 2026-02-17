"""LangGraph nodes for plan orchestration."""

import logging

from rimas.agents.state import PlanState

logger = logging.getLogger(__name__)


def data_analysis_node(state: PlanState) -> dict:
    """Analyze data patterns from request."""
    request = state.get("request") or {}
    items = request.get("items", [])
    horizon = request.get("horizon_days", 7)

    low_stock = sum(1 for i in items if i.get("current_stock", 0) < 30)
    summary = f"Stub: {len(items)} items, {low_stock} low-stock, horizon={horizon}d"
    trends = ["stable", "seasonal"] if low_stock <= len(items) / 2 else ["declining", "restock_needed"]

    return {
        "agent_outputs": {
            "data_analysis": {
                "summary": summary,
                "trends": trends,
                "low_stock_count": low_stock,
                "confidence": 0.85,
            }
        }
    }


def inventory_analysis_node(state: PlanState) -> dict:
    """Analyze inventory levels and reorder needs."""
    request = state.get("request") or {}
    items = request.get("items", [])
    constraints = request.get("constraints", {})

    if not items:
        return {
            "agent_outputs": {
                "inventory_analysis": {
                    "stock_level": "unknown",
                    "recommendation": "no items provided",
                    "risk_score": 0.0,
                }
            }
        }

    total_stock = sum(i.get("current_stock", 0) for i in items)
    avg_stock = total_stock / len(items)
    stock_level = "adequate" if avg_stock >= 30 else "low" if avg_stock >= 10 else "critical"
    risk_score = max(0.0, 1.0 - avg_stock / 50)

    return {
        "agent_outputs": {
            "inventory_analysis": {
                "stock_level": stock_level,
                "recommendation": "restock" if stock_level != "adequate" else "maintain",
                "risk_score": round(risk_score, 2),
                "avg_stock": round(avg_stock, 1),
            }
        }
    }


def marketing_analysis_node(state: PlanState) -> dict:
    """Analyze marketing / promotion potential."""
    inv = (state.get("agent_outputs") or {}).get("inventory_analysis", {})
    stock_level = inv.get("stock_level", "adequate")

    if stock_level == "critical":
        campaign = "high"
        action = "urgent promotion"
        lift = 0.2
    elif stock_level == "low":
        campaign = "medium"
        action = "targeted promotion"
        lift = 0.1
    else:
        campaign = "low"
        action = "maintain visibility"
        lift = 0.05

    return {
        "agent_outputs": {
            "marketing_analysis": {
                "campaign_potential": campaign,
                "suggested_action": action,
                "estimated_lift": lift,
            }
        }
    }


def supervisor_node(state: PlanState) -> dict:
    """Aggregate agent outputs and produce final recommendations."""
    request = state.get("request") or {}
    items = request.get("items", [])
    constraints = request.get("constraints", {})
    max_discount = constraints.get("max_discount", 0.2)
    agent_outputs = state.get("agent_outputs") or {}

    inv = agent_outputs.get("inventory_analysis", {})
    mkt = agent_outputs.get("marketing_analysis", {})

    recommendations = []
    for item in items:
        item_id = item.get("item_id", 0)
        stock = item.get("current_stock", 0)
        qty = max(0, 50 - stock) if stock < 50 else 0
        discount = min(0.1, max_discount) if qty > 0 else 0.0
        rationale = f"stock={stock}, {inv.get('recommendation', 'maintain')}, {mkt.get('suggested_action', '')}"
        recommendations.append({
            "item_id": item_id,
            "recommended_order_qty": qty,
            "recommended_discount": round(discount, 2),
            "confidence": 0.85,
            "rationale": rationale,
        })

    sup_decision = {
        "action": "proceed",
        "rationale": "All agents aligned",
        "item_count": len(recommendations),
    }
    final_decision = {
        "approved": True,
        "summary": f"Plan for {len(items)} items",
        "recommendations": recommendations,
    }
    return {
        "agent_outputs": {"supervisor_decision": sup_decision},
        "final_decision": final_decision,
        "recommendations": recommendations,
    }
