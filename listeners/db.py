from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../agent_responses.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(Base):
    Base.metadata.create_all(bind=engine)
