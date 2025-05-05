import asyncio
from datetime import datetime, timedelta
from agents import Agent, Runner
from .models import AgentResponseMap, Base
from .db import SessionLocal, init_db

# Initialize DB (once)
init_db(Base)

def store_response_id(user_id: str, channel_id: str, thread_ts: str, response_id: str, expires_in_days: int = 30):
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
    session = SessionLocal()
    obj = session.query(AgentResponseMap).filter_by(
        user_id=user_id, channel_id=channel_id, thread_ts=thread_ts
    ).first()
    session.close()
    if obj and obj.expires_at > datetime.utcnow().isoformat():
        return obj.response_id
    return None

async def call_agent(user_id: str, channel_id: str, thread_ts: str, user_message: str, system_instructions: str = None):
    agent = Agent(
        name="Assistant",
        instructions=system_instructions or "You are a helpful assistant. Be VERY concise. Speak like a pirate.",
    )
    previous_response_id = get_response_id(user_id, channel_id, thread_ts)
    result = await Runner.run(
        agent,
        user_message,
        previous_response_id=previous_response_id,
    )
    store_response_id(user_id, channel_id, thread_ts, result.last_response_id)
    return result.final_output

def call_agent_sync(user_id: str, channel_id: str, thread_ts: str, user_message: str, system_instructions: str = None):
    return asyncio.run(call_agent(user_id, channel_id, thread_ts, user_message, system_instructions))
