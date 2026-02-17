"""Inference - demand prediction and anomaly detection."""

import logging
from typing import Any

from rimas.ml.mlflow_client import get_model

logger = logging.getLogger(__name__)


def predict_demand(product_id: str, quantity: float) -> dict[str, Any]:
    model = get_model("demand_model")
    if model is not None:
        pred = model.predict([{"product_id": product_id, "quantity": quantity}])
        return {"prediction": float(pred[0]), "product_id": product_id, "is_mock": False}
    return {
        "prediction": 100.0 * quantity,
        "product_id": product_id,
        "is_mock": True,
    }


def detect_anomaly(metric: str, value: float) -> dict[str, Any]:
    model = get_model("anomaly_model")
    if model is not None:
        pred = model.predict([{"metric": metric, "value": value}])
        return {"is_anomaly": bool(pred[0]), "score": 0.0, "metric": metric, "is_mock": False}
    is_anomaly = value > 1000 or value < 0
    return {
        "is_anomaly": is_anomaly,
        "score": 0.5 if is_anomaly else 0.1,
        "metric": metric,
        "is_mock": True,
    }
