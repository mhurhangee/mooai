from agents import Agent, Runner, WebSearchTool
from lib.constants import SYSTEM_INSTRUCTIONS
from lib.models import StructuredResponse
from typing import List, Dict, Optional, Union
import asyncio
import logging

logger = logging.getLogger(__name__)

# Define the expected message type for agent input
AgentMessage = Dict[str, str]


async def run_agent_with_messages(
    messages: List[AgentMessage], 
    system_instructions: Optional[str] = SYSTEM_INSTRUCTIONS,
    use_structured_output: bool = False
) -> Union[str, StructuredResponse]:
    """
    Run the OpenAI Agent asynchronously with the provided message history and system instructions.
    
    Args:
        messages: List of messages in the conversation history
        system_instructions: Custom system instructions (defaults to SYSTEM_INSTRUCTIONS)
        use_structured_output: Whether to use structured output format
        
    Returns:
        Either a string (plain text response) or a StructuredResponse object
    """
    agent = Agent(
        name="Assistant",
        instructions=system_instructions,
        tools=[WebSearchTool(user_location={"type": "approximate", "country": "GB"})],
        model="gpt-4.1-mini",
        output_type=StructuredResponse if use_structured_output else None,
    )
    # Ensure messages is the correct type for Runner.run
    # If Runner.run expects Sequence[TResponseInputItem], cast messages accordingly
    result = await Runner.run(agent, messages)  # type: ignore  # See Pyright lint: type invariance
    logger.debug(result)
    
    return result.final_output


def run_agent_with_messages_sync(
    messages: List[AgentMessage], 
    system_instructions: Optional[str] = None,
    use_structured_output: bool = False
) -> Union[str, StructuredResponse]:
    """
    Run the OpenAI Agent synchronously as a wrapper for the async function,
    because Bolt handlers are synchronous.
    
    Args:
        messages: List of messages in the conversation history
        system_instructions: Custom system instructions
        use_structured_output: Whether to use structured output format
        
    Returns:
        Either a string (plain text response) or a StructuredResponse object
    """
    try:
        return asyncio.run(run_agent_with_messages(
            messages, 
            system_instructions, 
            use_structured_output
        ))
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception(f"Agent execution failed: {e}")
        if use_structured_output:
            return StructuredResponse(
                thread_title=None,
                message_title="Error Encountered",
                response=f"I'm sorry, I encountered an error: {str(e)}",
                followups=None
            )
        else:
            return f"I'm sorry, I encountered an error: {str(e)}"
