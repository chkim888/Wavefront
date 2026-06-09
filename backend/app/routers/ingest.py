from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from uuid import UUID
from app.models.buzz_monitor import Platform, Keyword
from app.models.user import User_Project
from app.database import get_db_session
from app.auth.dependencies import get_current_user
from app.services.youtube import ingest_youtube_data

# Constant initialization
YOUTUBE = "youtube"
router = APIRouter(prefix="/ingest")

# Ingest youtube data by calling ingest_youtube_data() services.youtube
@router.post("/youtube/{topic_id}/{project_id}", status_code=status.HTTP_200_OK) # does this account for no 
def ingest_youtube_endpoint(topic_id: UUID, project_id: UUID, user=Depends(get_current_user), db_session=Depends(get_db_session)):
    # Check if the user is authorized for the project
    authorized = db_session.scalars(
        select(User_Project).where(
            and_(User_Project.user_id == user.id,
                 User_Project.project_id == project_id))).first()
    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access for project")
    # Fetch YouTube platform ID
    platform_id = db_session.scalars(
        select(Platform.id).where(Platform.name == YOUTUBE)).first()
    if not platform_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform ID not found for YouTube")
    # Run the ingestion function
    keywords = db_session.scalars( # handle keyword number limit somehow later 
        select(Keyword.keyword).where(Keyword.topic_id == topic_id)).all()
    if not keywords:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keywords not found for the specified topic")
    ingest_youtube_data(topic_id, project_id, platform_id, keywords, db_session)
    return {"message": "Youtube ingestion complete", "topic_id": topic_id, "project_id": project_id}