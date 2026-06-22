import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

# Imported env variable
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

# Create a Celery instance using Redis as broker
app = Celery("wavefront", broker=REDIS_URL)

# Initializing beat (periodic task scheduler)
app.conf.beat_schedule = {
    'ingest-every-hour': {
        'task': 'app.workers.tasks.schedule_ingestion',
        'schedule': crontab(minute=0),
    },
}
app.conf.timezone = 'UTC'