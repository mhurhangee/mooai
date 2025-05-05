from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AgentResponseMap(Base):
    __tablename__ = 'agent_response_map'
    user_id = Column(String, primary_key=True)
    channel_id = Column(String, primary_key=True)
    thread_ts = Column(String, primary_key=True)
    response_id = Column(String)
    expires_at = Column(String)
