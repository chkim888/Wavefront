from sqlalchemy import select
from app.database import SessionLocal
from app.models.buzz_monitor import Platform

# Get db session
db_session = SessionLocal()

# Check if a row for YouTube already exists in db & insert if not
youtube_exists = db_session.scalars(select(Platform).where(Platform.name == "youtube")).first()
if not youtube_exists:
    youtube = Platform(
        name="youtube"
    )
    db_session.add(youtube)
    db_session.commit()