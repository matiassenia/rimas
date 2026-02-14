"""SQLAlchemy models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_default() -> str:
    return str(uuid4())


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=uuid_default
    )
    request_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    agent_outputs: Mapped[dict] = mapped_column(JSON, nullable=False)
    final_decision: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    events: Mapped[list["PlanEvent"]] = relationship(
        "PlanEvent", back_populates="plan", cascade="all, delete-orphan"
    )


class PlanEvent(Base):
    __tablename__ = "plan_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=uuid_default
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="events")
