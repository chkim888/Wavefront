from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime, timezone
from app.database import get_db_session
from app.schemas.experiment import AssignmentResponse
from app.models.experiment import Assignment, Experiment
from app.services.assignments import get_variant
from app.constants import RUNNING

# Router initialization
router = APIRouter(prefix="/assignments")

# Assign variable (or return assignment if one exists)
@router.post("/{experiment_id}/{session_id}", response_model=AssignmentResponse)
def assign_variant(experiment_id: UUID, session_id: str, db_session=Depends(get_db_session)):
    # fetch experiment
    experiment = db_session.scalars(
        select(Experiment).where(Experiment.id == experiment_id)
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    # Check if the experiment is running -- raise error if not
    curr_status = experiment.curr_status
    if curr_status != RUNNING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experiment is not currently running, and assignment is not possible."
        )
    # see if assignment already exists for the session -- return if exists
    existing = db_session.scalars(
        select(Assignment).where(and_(
            Assignment.session_id == session_id,
            Assignment.experiment_id == experiment_id
    ))).first()
    if existing:
        return existing
    # determine which variant the session is being assigned to
    traffic_split = experiment.traffic_split
    variant = get_variant(session_id, str(experiment_id), traffic_split)
    # create a new assignment for the session
    new_assignment = Assignment(
        session_id=session_id,
        experiment_id=experiment_id,
        created_at=datetime.now(timezone.utc),
        variant=variant
    )
    # Push new assignment & return
    db_session.add(new_assignment)
    db_session.commit()
    db_session.refresh(new_assignment)
    return new_assignment