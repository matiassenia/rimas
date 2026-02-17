"""Anomaly detection endpoint."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from rimas.ml.inference import detect_anomaly

logger = logging.getLogger(__name__)
router = APIRouter()


class AnomalyRequest(BaseModel):
    metric: str | None = "sales"
    value: float | None = 0.0


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    score: float
    metric: str | None
    is_mock: bool


@router.post("/", response_model=AnomalyResponse)
async def anomaly_endpoint(req: AnomalyRequest) -> AnomalyResponse:
    result = detect_anomaly(
        metric=req.metric or "sales",
        value=req.value or 0.0,
    )
    return AnomalyResponse(**result)
