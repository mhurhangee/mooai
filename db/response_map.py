from datetime import datetime, timedelta
from db.models import AgentResponseMap
from db.session import SessionLocal

def store_response_id(user_id: str, channel_id: str, thread_ts: str, response_id: str, expires_in_days: int = 30):
    """
    Store or update the OpenAI response_id for a given (user, channel, thread) tuple.
    Used to enable context continuity for agent conversations in Slack.
    """
    expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
    session = SessionLocal()
    obj = session.query(AgentResponseMap).filter_by(
        user_id=user_id, channel_id=channel_id, thread_ts=thread_ts
    ).first()
    if obj:
        obj.response_id = response_id
        obj.expires_at = expires_at
    else:
        obj = AgentResponseMap(
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
            response_id=response_id,
            expires_at=expires_at,
        )
        session.add(obj)
    session.commit()
    session.close()

def get_response_id(user_id: str, channel_id: str, thread_ts: str):
    """
    Retrieve the most recent response_id for a given (user, channel, thread) tuple, if not expired.
    Returns None if no valid mapping is found.
    """
    session = SessionLocal()
    obj = session.query(AgentResponseMap).filter_by(
        user_id=user_id, channel_id=channel_id, thread_ts=thread_ts
    ).first()
    session.close()
    if obj and obj.expires_at > datetime.utcnow().isoformat():
        return obj.response_id
    return None
