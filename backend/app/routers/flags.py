from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from uuid import UUID
from app.database import get_db_session
from app.models.experiment import Experiment
from app.services.assignments import get_or_assign_variant
from app.constants import RUNNING, TREATMENT
from app.dependencies import get_experiment_by_id

router = APIRouter(prefix="/flags")

@router.post("/{experiment_id}/{session_id}")
def check_flag(experiment_id: UUID, session_id: str, db_session=Depends(get_db_session)):
    experiment = get_experiment_by_id(experiment_id, db_session)
    # experiment is currently not running
    if experiment.curr_status != RUNNING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Experiment is not currently running"
        )
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The session ID was not fetched correctly"
        )
    assignment = get_or_assign_variant(session_id, experiment, db_session)
    return {"enabled": assignment.variant == TREATMENT}