from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime, timezone
from app.database import get_db_session
from app.models.experiment import Assignment, Event, Experiment
from app.schemas.experiment import EventResponse, EventCreate
from app.constants import RUNNING

# Router initialization
router = APIRouter(prefix="/events")

# Create event after trigger
@router.post("/{experiment_id}/{session_id}", response_model=EventResponse | None)
def create_event(experiment_id: UUID, session_id: str, event_data: EventCreate, db_session=Depends(get_db_session)):
    # fetch experiment
    experiment = db_session.scalars(
        select(Experiment).where(Experiment.id == experiment_id)
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    # Check if the experiment is running
    curr_status = experiment.curr_status
    if curr_status != RUNNING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experiment not running"
        )
    # Check which variant the session is assigned to for the experiment
    assignment = db_session.scalars(
        select(Assignment).where(and_(
            Assignment.experiment_id == experiment_id,
            Assignment.session_id == session_id
    ))).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    # Check if event type is appropriate for saving
    event_type = event_data.event_type
    if event_type != experiment.success_metric:
        return None
    # Create event
    new_event = Event (
        session_id=session_id,
        experiment_id=experiment_id,
        happened_at=datetime.now(timezone.utc),
        event_type=event_type
    )
    db_session.add(new_event)
    db_session.commit()
    db_session.refresh(new_event)
    return new_event
