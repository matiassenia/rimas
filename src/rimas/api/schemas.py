"""Pydantic schemas for REST contract."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    created = "created"
    approved = "approved"
    rejected = "rejected"


class PlanConstraints(BaseModel):
    lead_time_days: int = 7
    budget_limit: float = 10000.0
    max_discount: float = 0.2


class PlanItemInput(BaseModel):
    item_id: int
    current_stock: int


class CreatePlanRequest(BaseModel):
    store_id: int
    horizon_days: int = 7
    constraints: PlanConstraints = Field(default_factory=PlanConstraints)
    items: list[PlanItemInput] = Field(default_factory=list, min_length=1)


class PlanRecommendation(BaseModel):
    item_id: int
    recommended_order_qty: int
    recommended_discount: float
    confidence: float
    rationale: str


class PlanMetadata(BaseModel):
    model_version: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class PlanResponse(BaseModel):
    plan_id: str
    status: PlanStatus
    recommendations: list[PlanRecommendation] = Field(default_factory=list)
    metadata: PlanMetadata
