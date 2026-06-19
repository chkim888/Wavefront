from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from app.database import get_db_session
from app.auth.dependencies import get_current_user
from app.models.buzz_monitor import Alert
from app.models.user import User_Project
from app.schemas.buzz_monitor import AlertResponse

# Initialize router
router = APIRouter(prefix="/alerts")

# Get alerts
@router.get("/{project_id}", response_model=list[AlertResponse])
def get_alerts_by_project(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    user_check = db_session.scalars(
        select(User_Project).where(and_(User_Project.user_id == user.id,
                                        User_Project.project_id == project_id))
    ).first()
    if not user_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have access to project"
        )
    alerts = db_session.scalars(
        select(Alert).where(Alert.project_id==project_id)
        .order_by(Alert.triggered_at.desc())
    ).all()
    if not alerts:
        alerts = []
    return alerts