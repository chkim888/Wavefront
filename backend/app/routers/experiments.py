from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user, permission_check
from app.database import get_db_session
from app.schemas.experiment import ExperimentBase, ExperimentResponse, ExperimentUpdate, ResultResponse
from app.models.experiment import Experiment, Result
from app.models.user import User_Project
from app.services.stats_engine import run_stats_engine
from app.constants import OWNER, VIEWER, CREATED, RUNNING, COMPLETE

# Router initialization
router = APIRouter(prefix="/experiments")

## Create
# create a new experiment (for a project)
@router.post("/", response_model=ExperimentResponse)
def create_experiment(experiment: ExperimentBase, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, experiment.project_id, db_session) == OWNER:
        existing = db_session.scalars(
            select(Experiment).where(
                and_(Experiment.title == experiment.title,
                     Experiment.project_id == experiment.project_id))
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already exists experiment with the same name"
            )
        new_experiment = Experiment(
            project_id=experiment.project_id,
            title=experiment.title,
            description=experiment.description,
            curr_status=CREATED,
            traffic_split=experiment.traffic_split,
            success_metric=experiment.success_metric,
            start_time=datetime.now(timezone.utc)
        )
        db_session.add(new_experiment)
        db_session.commit()
        db_session.refresh(new_experiment)
        return new_experiment
    
# Start an experiment (already created)
@router.post("/{experiment_id}/start", response_model=ExperimentResponse)
def start_experiment(experiment_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Fetch experiment details
    experiment = db_session.scalars(
        select(Experiment).where(Experiment.id == experiment_id)
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    # Check user permission for project (ownership)
    if permission_check(user.id, experiment.project_id, db_session) == OWNER:
        # Check if the experiment hasn't been started yet
        if experiment.curr_status != CREATED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Experiment already started"
            )
        # Start experiment
        experiment.curr_status = RUNNING
        experiment.start_time = datetime.now(timezone.utc)
        # Push changes
        db_session.add(experiment)
        db_session.commit()
        db_session.refresh(experiment)
        return experiment
    
# Stop experiment
@router.post("/{experiment_id}/stop", response_model=ResultResponse)
def stop_experiment(experiment_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Fetch experiment details
    experiment = db_session.scalars(
        select(Experiment).where(Experiment.id == experiment_id)
    ).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    # Check user permission for project (ownership)
    if permission_check(user.id, experiment.project_id, db_session) == OWNER:
        # Check if the experiment hasn't been started yet
        if experiment.curr_status != RUNNING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Experiment is not running"
            )
        # Check if result already exists
        check_duplicate = db_session.scalars(
            select(Result).where(Result.experiment_id==experiment_id)
        ).first()
        if check_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="result already exists for the experiment"
            )
        # Update experiment status
        experiment.curr_status = COMPLETE
        experiment.end_time = datetime.now(timezone.utc)
        # Calculate results
        result = run_stats_engine(experiment_id, db_session)
        # Create new Result & insert into db
        new_result = Result(**result)
        # Push changes
        db_session.add(new_result)
        db_session.commit()
        db_session.refresh(new_result)
        return new_result

## Read
# Read experiments info
@router.get("/project/{project_id}", response_model=list[ExperimentResponse])
def get_all_experiments(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    if permission_check(user.id, project_id, db_session) in [OWNER, VIEWER]:
        experiments = db_session.scalars(
            select(Experiment).where(Experiment.project_id == project_id)
        ).all()
        if not experiments:
            experiments = [] # return an empty list if no experiments found for the project
        return experiments

# Read one experiment info
@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    experiment = db_session.scalars(select(Experiment).where(Experiment.id == experiment_id)).first()
    if experiment and permission_check(user.id, experiment.project_id, db_session) in [OWNER, VIEWER]:
        return experiment
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

# Read result
@router.get("/{experiment_id}/result", response_model=ResultResponse)
def get_result(experiment_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    experiment = db_session.scalars(select(Experiment).where(Experiment.id == experiment_id)).first()
    if experiment and permission_check(user.id, experiment.project_id, db_session) in [OWNER, VIEWER]:
        result = db_session.scalars(
            select(Result).where(Result.experiment_id == experiment_id)
        ).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found"
            )
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

## Update
# update experiments
@router.patch("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(experiment_id: UUID, updates: ExperimentUpdate, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    experiment = db_session.scalars(select(Experiment).where(Experiment.id == experiment_id)).first()
    if experiment and permission_check(user.id, experiment.project_id, db_session) == OWNER:
        if updates.title:
            existing = db_session.scalars(
                select(Experiment).where(
                    and_(Experiment.title == updates.title,
                         Experiment.project_id == experiment.project_id)
            )).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="There already exists the title for an experiment under the project"
                )
            experiment.title = updates.title
        if updates.description:
            experiment.description = updates.description
        if updates.traffic_split:
            experiment.traffic_split = updates.traffic_split
        if updates.success_metric:
            experiment.success_metric = updates.success_metric
        if updates.end_time:
            experiment.end_time = updates.end_time
        db_session.commit()
        db_session.refresh(experiment)
        return experiment
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )

## Delete
# Delete experiment
@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(experiment_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    experiment = db_session.scalars(select(Experiment).where(Experiment.id == experiment_id)).first()
    if experiment and permission_check(user.id, experiment.project_id, db_session) == OWNER:
        db_session.delete(experiment)
        db_session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )