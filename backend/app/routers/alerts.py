from fastapi import APIRouter, Depends
from sqlalchemy import select
from uuid import UUID
from app.dependencies import get_db_session
from app.auth.dependencies import get_current_user
from app.models.buzz_monitor import Alert
from app.schemas.buzz_monitor import AlertResponse

# Initialize router
router = APIRouter(prefix="/alerts")

# Get alerts
@router.get("/{project_id}", response_model=list[AlertResponse])
def get_alerts_by_project(project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    alerts = db_session.scalars(
        select(Alert).where(Alert.project_id==project_id)
        .order_by(Alert.triggered_at.desc())
    ).all()
    if not alerts:
        alerts = []
    return alerts