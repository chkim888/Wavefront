from sqlalchemy import select
from app.workers.celery_app import app
from app.services.youtube import ingest_youtube_data
from app.services.sentiment import sentiment_analysis
from app.database import SessionLocal
from app.models.buzz_monitor import Topic, Project_Platform, Keyword

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
            topic_id = topic.id
            project_id = topic.project_id
            if project_id not in platform_dict:
                platform_dict[project_id] = db_session.scalars(
                    select(Project_Platform.platform_id).where(Project_Platform.project_id == project_id)).first()
            platform_id = platform_dict[project_id]
            keywords = db_session.scalars(select(Keyword.keyword).where(Keyword.topic_id == topic_id)).all()
            if keywords: # Ingestion task only if there are keywords for the topic
                ingestion_task.delay(topic_id, project_id, platform_id, list(keywords))
        # Run sentiment analysis task
        for topic in active_topics:
            sentiment_analysis_task.delay(topic.id)
        # Run spike detection
    finally:
        db_session.close()

# Define task for ingestion
@app.task
def ingestion_task(topic_id: str, project_id: str, platform_id: str, keywords: list[str]):
    db_session = SessionLocal()
    try:
        ingest_youtube_data(topic_id, project_id, platform_id, keywords, db_session)
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
def spike_detection_task():
    pass