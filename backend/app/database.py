import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

# Load DATABASE_URL from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine using that URL
engine = create_engine(DATABASE_URL)

# Create session factory from engine
SessionLocal = sessionmaker(engine)

# Create a function that yields a session per request
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
    