"""FastAPI application entry point."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rimas.logging import setup_logging
from rimas.db.session import init_db
from rimas.api.routes import health, predict, anomaly, plans

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="RIMAS",
    description="Retail Intelligence Multi-Agent System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, prefix="/predict-demand", tags=["ML"])
app.include_router(anomaly.router, prefix="/detect-anomaly", tags=["ML"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"])
