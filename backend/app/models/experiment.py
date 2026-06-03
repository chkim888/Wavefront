from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint, UUID
from typing import Optional
from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from app.database import Base

class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    curr_status: Mapped[str] = mapped_column(
        CheckConstraint(
            "curr_status IN ('created', 'running', 'complete', 'archived')", 
            name="check_valid_status"
        )
    )
    traffic_split: Mapped[int] = mapped_column()
    success_metric: Mapped[str] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[Optional[datetime]] = mapped_column()

class Assignment(Base):
    __tablename__ = "assignments"

    session_id: Mapped[str] = mapped_column(primary_key=True)
    experiment_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("experiments.id"), 
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column()
    variant: Mapped[str] = mapped_column(
        CheckConstraint(
            "variant IN ('control', 'treatment')", 
            name="check_valid_variant"
        )
    )

class Event(Base):
    __tablename__ = "events"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    session_id: Mapped[str] = mapped_column()
    experiment_id: Mapped[PyUUID] = mapped_column(ForeignKey("experiments.id"))
    happened_at: Mapped[datetime] = mapped_column()
    event_type: Mapped[str] = mapped_column()

class Results(Base):
    __tablename__ = "results"

    experiment_id: Mapped[PyUUID] = mapped_column(ForeignKey("experiments.id"), primary_key=True)
    control_conversions: Mapped[int] = mapped_column()
    treatment_conversions: Mapped[int] = mapped_column()
    control_rate: Mapped[float] = mapped_column()
    treatment_rate: Mapped[float] = mapped_column()
    lift: Mapped[float] = mapped_column()
    confidence: Mapped[float] = mapped_column()
    winner: Mapped[Optional[str]] = mapped_column()