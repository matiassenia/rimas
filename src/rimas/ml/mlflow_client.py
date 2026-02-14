"""MLflow client - model loading and tracking."""

import logging
from typing import Any

from src.rimas.config import settings

logger = logging.getLogger(__name__)

_loaded_model = None


def get_model(model_name: str = "demand_model", stage: str = "Production") -> Any | None:
    global _loaded_model
    try:
        import mlflow
        import mlflow.pyfunc

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        model_uri = f"models:/{model_name}/{stage}"
        _loaded_model = mlflow.pyfunc.load_model(model_uri)
        logger.info("Model loaded from MLflow", extra={"model_uri": model_uri})
        return _loaded_model
    except Exception as e:
        logger.warning("No model in MLflow, using stub", extra={"error": str(e)})
        return None
