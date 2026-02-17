"""Demand prediction endpoint."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from rimas.ml.inference import predict_demand

logger = logging.getLogger(__name__)
router = APIRouter()


class PredictRequest(BaseModel):
    product_id: str | None = None
    quantity: float | None = 1.0


class PredictResponse(BaseModel):
    prediction: float
    product_id: str | None
    is_mock: bool


@router.post("/", response_model=PredictResponse)
async def predict_endpoint(req: PredictRequest) -> PredictResponse:
    result = predict_demand(
        product_id=req.product_id or "default",
        quantity=req.quantity or 1.0,
    )
    return PredictResponse(**result)
