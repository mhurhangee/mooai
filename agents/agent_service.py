import asyncio
from agents import Agent, Runner
from db.response_map import store_response_id, get_response_id
from db.session import init_db
from agents import Agent, Runner
import asyncio

init_db()

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
