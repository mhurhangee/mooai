import asyncio
from agents import Agent, Runner  # external OpenAI Agents package
from db.response_map import store_response_id, get_response_id
from db.session import init_db
import asyncio

# Ensure the agent response mapping table is created in the database
init_db()

async def call_agent(user_id: str, channel_id: str, thread_ts: str, user_message: str, system_instructions: str = None):
    """
    Run the OpenAI Agent for a given Slack user and thread.
    Uses previous response_id (if any) for context continuity.
    Stores the new response_id for future turns.
    """
    agent = Agent(
        name="Assistant",
        instructions=system_instructions or "You are a helpful assistant. Be VERY concise.",
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
    """
    Synchronous wrapper for call_agent, for use in synchronous Slack Bolt handlers.
    """
    return asyncio.run(call_agent(user_id, channel_id, thread_ts, user_message, system_instructions))
