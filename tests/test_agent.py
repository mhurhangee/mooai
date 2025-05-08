"""
Tests for the agent module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from lib.agent import run_agent_with_messages, run_agent_with_messages_sync


@pytest.mark.asyncio
async def test_run_agent_with_messages():
    """Test the async agent function with messages."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello", "type": "message"},
        {"role": "assistant", "content": "Hi there", "type": "message"},
    ]

    # Mock the Agent and Runner
    with patch("lib.agent.Agent") as MockAgent, patch("lib.agent.Runner") as MockRunner:

        # Setup mock agent instance
        mock_agent_instance = MockAgent.return_value

        # Setup mock runner
        mock_result = AsyncMock()
        mock_result.final_output = "This is the agent's response"
        MockRunner.run = AsyncMock(return_value=mock_result)

        # Act
        result = await run_agent_with_messages(messages)

        # Assert
        MockAgent.assert_called_once()
        MockRunner.run.assert_called_once_with(mock_agent_instance, messages)
        assert result == "This is the agent's response"


def test_run_agent_with_messages_sync():
    """Test the sync agent function with messages."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello", "type": "message"},
        {"role": "assistant", "content": "Hi there", "type": "message"},
    ]

    # Mock the async function
    with patch("lib.agent.run_agent_with_messages") as mock_async_run:
        mock_async_run.return_value = "This is the agent's response"

        # Act
        result = run_agent_with_messages_sync(messages)

        # Assert
        assert result == "This is the agent's response"


def test_run_agent_with_messages_sync_error_handling():
    """Test error handling in the sync agent function."""
    # Arrange
    messages = [{"role": "user", "content": "Hello", "type": "message"}]

    # Mock the async function to raise an exception and logging
    with patch("lib.agent.run_agent_with_messages") as mock_async_run:
        mock_async_run.side_effect = Exception("Test error")

        # Act
        result = run_agent_with_messages_sync(messages)

        # Assert
        assert "I'm sorry, I encountered an error" in result
