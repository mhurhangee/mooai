from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from db.models import Base

# Path to the SQLite DB file (default for local development)
DB_PATH = os.path.join(os.path.dirname(__file__), '../agent_responses.db')
# SQLAlchemy engine and session setup
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Create all tables in the database (if they don't exist).
    Should be called once at app startup.
    """
    Base.metadata.create_all(bind=engine)
