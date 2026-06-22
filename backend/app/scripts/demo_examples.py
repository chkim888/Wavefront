'''
For setting up example projects, users, etc. for demo
'''
from sqlalchemy import insert, select
from datetime import datetime
from app.database import SessionLocal
from app.models.user import Project, User_Project
from app.models.buzz_monitor import Topic, Keyword, Project_Platform, Platform
from app.schemas.user import UserRegister
from app.routers.auth import register

db_session = SessionLocal()

try:
    # Create a demo user
    demo_user = UserRegister(
        username="demo",
        email="demo@demo.com",
        password="demo"
    )
    demo_user = register(demo_user, db_session)
    print(f"Demo user ID: {demo_user.id}")

    # Create a demo project 
    demo_project = db_session.scalars(
        insert(Project).values(
            name="Banner test",
            description="For determining which movie banner to show on the homepage",
            created_at=datetime.now()
        ).returning(Project)
    ).first()
    db_session.add(demo_project)
    db_session.flush()
    print(f"Demo project ID: {demo_project.id}")

    ownership = db_session.scalars(
        insert(User_Project).values(
            user_id=demo_user.id,
            project_id=demo_project.id,
            role="owner"
        ).returning(User_Project)
    ).first()
    db_session.add(ownership)
    db_session.flush()

    platform_id = db_session.scalars(
        select(Platform).where(Platform.name == "youtube")
    ).first()
    platform = db_session.scalars(
        insert(Project_Platform).values(
            project_id=demo_project.id,
            platform_id=platform_id
        ).returning(Project_Platform)
    ).first()
    db_session.add(platform)
    db_session.flush()

    # Populate demo topics (different movies)
    for topic in ["Obsession", "Disclosure Day", "Toy Story 5"]:
        demo_topic = db_session.scalars(
            insert(Topic).values(
                title=topic,
                description="Testing different movies",
                is_active=True,
                project_id=demo_project.id
            ).returning(Topic)
        ).first()
        db_session.add(demo_topic)
        db_session.flush()
        print(f"Demo topic ID for {topic}: {demo_topic.id}")

        # For each topic, add keywords
        if topic == "Obsession":
            keywords = ["Obsession 2026 movie", "Obsession horror review 2026"]
        elif topic == "Disclosure Day":
            keywords = ["Disclosure Day movie", "Disclosure Day Spielberg review"]
        else:
            keywords = ["Toy Story 5", "Toy Story review"]
        for keyword in keywords:
            demo_keyword = db_session.scalars(
                insert(Keyword).values(
                    topic_id=demo_topic.id,
                    project_id=demo_project.id,
                    keyword=keyword
                ).returning(Keyword)
            ).first()
            db_session.add(demo_keyword)
            db_session.flush()
            print(f"Demo keyword ID for {keyword}: {demo_keyword.id}")
    # Push the changes to the db
    db_session.commit()

finally:
    db_session.close()