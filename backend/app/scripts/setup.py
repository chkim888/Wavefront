'''
For setting up testing environment for Locust
It needs these:
    1) User
    2) Project/topic
    3) Running experiment
'''
from sqlalchemy import insert
from datetime import datetime
from app.database import SessionLocal
from app.models.user import Project, User_Project
from app.models.buzz_monitor import Topic
from app.models.experiment import Experiment
from app.schemas.user import UserRegister
from app.routers.auth import register
from app.scripts.bulk_seed import generate_fake_posts, generate_fake_alerts, generate_background_data
from app.constants import RUNNING

# Getting database session
db_session = SessionLocal()

try:
    '''
    Generate "real" users, etc. for testing
    '''
    # Setting up one analyst user
    new_user = UserRegister(
        username="locust_test",
        email="locust@test.com",
        password="locust_test"
    ) 
    new_user = register(new_user, db_session) # calling the router directly

    # Setting up a project & topic
    new_project = db_session.scalars(
        insert(Project).values(
            name="locust_test",
            description="locust_test",
            created_at=datetime.now()
        ).returning(Project)
    ).first()
    db_session.add(new_project)
    db_session.commit()
    db_session.refresh(new_project)

    new_ownership = db_session.scalars(
        insert(User_Project).values(
            user_id=new_user.id,
            project_id=new_project.id,
            role="owner"
        ).returning(User_Project)
    ).first()
    db_session.add(new_ownership)
    db_session.commit()
    db_session.refresh(new_ownership)

    new_topic = db_session.scalars(
        insert(Topic).values(
            title="locust_test",
            description="locust_test",
            is_active=True,
            project_id=new_project.id
        ).returning(Topic)
    ).first()
    db_session.add(new_topic)
    db_session.commit()
    db_session.refresh(new_topic)

    # Setting up a running experiment
    new_experiment = db_session.scalars(
        insert(Experiment).values(
            project_id=new_project.id,
            title="locust_test",
            description="locust_test",
            curr_status=RUNNING,
            traffic_split=50,
            success_metric="button_click",
            start_time=datetime.now()
        ).returning(Experiment)
    ).first()
    db_session.add(new_experiment)
    db_session.commit()
    db_session.refresh(new_experiment)

    # Call functions in bulk_seed.py
    generate_fake_posts(
        topic_id=new_topic.id,
        project_id=new_project.id,
        db_session=db_session
    )
    generate_fake_alerts(
        topic_id=new_topic.id,
        project_id=new_project.id,
        db_session=db_session
    )
    # generate_background_data(db_session)

    print("New user ID:", new_user.id)
    print("New project ID:", new_project.id)
    print("New topic ID:", new_topic.id)
    print("New experiment ID:", new_experiment.id)

finally:
    db_session.close()