from sqlalchemy import select
# from googleapiclient.errors import HttpError
from celery import chain
from app.workers.celery_app import app
from app.services.youtube import ingest_youtube_data
from app.services.sentiment import sentiment_analysis
from app.services.spike_detection import spike_detection
from app.database import SessionLocal
from app.models.buzz_monitor import Topic, Project_Platform, Keyword
from app.models.user import Project, User_Project

# Fan-out pattern
@app.task
def schedule_ingestion():
    # Fetch all active topics
    db_session = SessionLocal()
    try:
        active_topics = db_session.scalars(
            select(Topic).where(Topic.is_active == True)).all()
        platform_dict = dict() # Save platform
        # Run ingestion task
        for topic in active_topics:
            # Initialize all values for the ingestion task function
            project_id = topic.project_id
            if project_id not in platform_dict:
                platform_dict[project_id] = db_session.scalars(
                    select(Project_Platform.platform_id).where(Project_Platform.project_id == project_id)).first()
            platform_id = platform_dict[project_id]
            if not platform_id:
                continue # skip if no platform
            keywords = db_session.scalars(select(Keyword.keyword).where(Keyword.topic_id == topic.id)).all()
            if keywords: # Ingestion task only if there are keywords for the topic
                chain(
                    ingestion_task.si(str(topic.id), str(project_id), str(platform_id), list(keywords)), # adding to queue
                    sentiment_analysis_task.si(str(topic.id)), # run sentiment analysis
                    spike_detection_task.si(str(topic.id), str(topic.project_id)) # run spike detection
                ).delay()
    finally:
        db_session.close()

# Define task for ingestion
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingestion_task(self, topic_id: str, project_id: str, platform_id: str, keywords: list[str]):
    from googleapiclient.errors import HttpError
    db_session = SessionLocal()
    try:
        ingest_youtube_data(topic_id, project_id, platform_id, keywords, db_session)
    except HttpError as e:
        raise self.retry(exc=e)
    finally:
        db_session.close()

# Task for sentiment analysis
@app.task
def sentiment_analysis_task(topic_id: str):
    db_session = SessionLocal()
    try:
        sentiment_analysis(topic_id, db_session)
    finally:
        db_session.close()

# Task for spike detection
@app.task
def spike_detection_task(topic_id: str, project_id: str):
    db_session = SessionLocal()
    try:
        spike_detection(topic_id, project_id, db_session)
    finally:
        db_session.close()