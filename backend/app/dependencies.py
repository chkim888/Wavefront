from fastapi import HTTPException, status
from sqlalchemy import select
from uuid import UUID
from app.models.experiment import Experiment

def get_experiment_by_id(experiment_id: UUID, db_session):
    # fetch experiment
    experiment = db_session.scalars(
        select(Experiment).where(Experiment.id == experiment_id)
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    return experiment