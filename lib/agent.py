from agents import Agent, Runner, WebSearchTool
from lib.constants import SYSTEM_INSTRUCTIONS
from typing import List, Dict, Optional
import asyncio

# Define the expected message type for agent input
AgentMessage = Dict[str, str]


async def run_agent_with_messages(
    messages: List[AgentMessage], system_instructions: Optional[str] = SYSTEM_INSTRUCTIONS
) -> str:
    """
    Run the OpenAI Agent asynchronously with the provided message history and system instructions.
    Returns the agent's final output as a string.
    Note: system_instructions will default to SYSTEM_INSTRUCTIONS if not provided.
    """
    agent = Agent(
        name="Assistant",
        instructions=system_instructions if system_instructions is not None else SYSTEM_INSTRUCTIONS,
        tools=[WebSearchTool(user_location={"type": "approximate", "country": "GB"})],
    )
    # Ensure messages is the correct type for Runner.run
    # If Runner.run expects Sequence[TResponseInputItem], cast messages accordingly
    result = await Runner.run(agent, messages)  # type: ignore  # See Pyright lint: type invariance
    return result.final_output


def run_agent_with_messages_sync(messages: List[AgentMessage], system_instructions: Optional[str] = None) -> str:
    """
    Run the OpenAI Agent synchronously as a wrapper for the async function,
    because Bolt handlers are synchronous.
    """
    try:
        return asyncio.run(run_agent_with_messages(messages, system_instructions))
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception(f"Agent execution failed: {e}")
        return f"I'm sorry, I encountered an error: {str(e)}"
