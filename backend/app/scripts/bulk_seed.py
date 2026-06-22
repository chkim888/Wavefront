'''
For bulk-seeding data necessary for Locust testing
It needs these:
    1) Fake posts
    2) Fake alerts
'''
from sqlalchemy import insert, select
from datetime import datetime
import uuid
import random
from app.models.user import Project
from app.models.buzz_monitor import Post, Platform, Alert, Topic
from app.database import SessionLocal

# Configure number of fake posts & alerts
NUM_POSTS = 1000
NUM_ALERTS = 1000
BK_PROJECTS = 50
BK_TOPICS = 5

# Fake posts
def generate_fake_posts(topic_id, project_id, db_session):
    fake_posts = list()
    platform_id = db_session.scalars(
        select(Platform.id).where(Platform.name=="youtube")
    ).first()
    posted_time=datetime.now()
    for i in range(NUM_POSTS):
        post = Post(
            external_id=uuid.uuid4(),
            topic_id=topic_id,
            project_id=project_id,
            platform_id=platform_id,
            original_poster="locust_test",
            posted_time=posted_time,
            content_type="video",
            content="locust_test",
            # Omitting optional fields
        )
        fake_posts.append(post)
    # insert all data
    db_session.add_all(fake_posts)
    db_session.commit()

# Fake alerts
def generate_fake_alerts(project_id, topic_id, db_session):
    fake_alerts = list()
    triggered_at = datetime.now()
    for i in range(NUM_ALERTS):
        alert = Alert(
            project_id=project_id,
            topic_id=topic_id,
            triggered_at=triggered_at,
            message="locust_test"
        )
        fake_alerts.append(alert)
    # insert all data
    db_session.add_all(fake_alerts)
    db_session.commit()

'''
Generate background data for bigger databases
'''
def generate_background_data(db_session):
    platform_id = db_session.scalars(
        select(Platform.id).where(Platform.name=="youtube")
    ).first()

    # Background projects
    for i in range(BK_PROJECTS):
        random_time = datetime.now()
        new_project = Project(
            name=f"background_{i}",
            description="background",
            created_at=random_time
        )
        db_session.add(new_project)
        db_session.flush()
        
        # Background topics
        for j in range(BK_TOPICS):
            new_topic = Topic(
                title=f"background_{i}_{j}",
                description="background",
                is_active=True,
                project_id=new_project.id
            )
            db_session.add(new_topic)
            db_session.flush()

            # alerts
            alerts = list()
            for _ in range(random.randint(50, 150)):
                new_alert = Alert(
                    project_id=new_project.id,
                    topic_id=new_topic.id,
                    triggered_at=random_time, 
                    message="background"
                )
                alerts.append(new_alert)
            db_session.add_all(alerts)

            # posts
            posts = list()
            for _ in range(random.randint(50, 300)):
                new_post = Post(
                    external_id=uuid.uuid4(),
                    topic_id=new_topic.id,
                    project_id=new_project.id,
                    platform_id=platform_id,
                    original_poster="background",
                    posted_time=random_time,
                    content_type="video",
                    content="background",
                    # Omitting optional fields
                )
                posts.append(new_post)
            db_session.add_all(posts)
    db_session.commit()    