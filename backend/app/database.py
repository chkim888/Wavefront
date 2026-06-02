import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This is the base class all SQLAlchemy models inherit from (wrap everything together)
class Base(DeclarativeBase):
    pass # No logic needs to exist -- class is just to be inherited from

# Load DATABASE_URL from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine using that URL
engine = create_engine(DATABASE_URL) # This manages connections to PostgreSQL
                                     # Stays alive for the lifetime of the app

# Create session factory from engine
SessionLocal = sessionmaker(engine)

# Create a function that yields a session per request
def get_db_session():
    session = SessionLocal() # creates a new session per API request
    try:
        yield session   # pass session to endpoint
    finally:
        session.close() # close once request completed
    