"""
Tests for the agent module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from lib.agent import run_agent_with_messages, run_agent_with_messages_sync
from lib.models import StructuredResponse


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
        
        
@pytest.mark.asyncio
async def test_run_agent_with_messages_structured_output():
    """Test the async agent function with structured output."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello", "type": "message"},
        {"role": "assistant", "content": "Hi there", "type": "message"},
    ]
    
    # Create a structured response
    structured_response = StructuredResponse(
        thread_title="Test Thread",
        message_title="Test Response",
        response="This is the agent's structured response",
        followups=["Follow-up 1", "Follow-up 2"]
    )

    # Mock the Agent and Runner
    with patch("lib.agent.Agent") as MockAgent, patch("lib.agent.Runner") as MockRunner:

        # Setup mock agent instance
        mock_agent_instance = MockAgent.return_value

        # Setup mock runner
        mock_result = AsyncMock()
        mock_result.final_output = structured_response
        MockRunner.run = AsyncMock(return_value=mock_result)

        # Act
        result = await run_agent_with_messages(messages, use_structured_output=True)

        # Assert
        MockAgent.assert_called_once()
        assert MockAgent.call_args[1]["output_type"] is not None  # Should have output_type set
        MockRunner.run.assert_called_once_with(mock_agent_instance, messages)
        assert isinstance(result, StructuredResponse)
        assert result.thread_title == "Test Thread"
        assert result.message_title == "Test Response"
        assert result.response == "This is the agent's structured response"
        assert result.followups == ["Follow-up 1", "Follow-up 2"]


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
        mock_async_run.assert_called_once_with(messages, None, False)
        assert result == "This is the agent's response"
        
        
def test_run_agent_with_messages_sync_structured():
    """Test the sync agent function with structured output."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello", "type": "message"},
        {"role": "assistant", "content": "Hi there", "type": "message"},
    ]
    
    # Create a structured response
    structured_response = StructuredResponse(
        thread_title="Test Thread",
        message_title="Test Response",
        response="This is the agent's structured response",
        followups=["Follow-up 1", "Follow-up 2"]
    )

    # Mock the async function
    with patch("lib.agent.run_agent_with_messages") as mock_async_run:
        mock_async_run.return_value = structured_response

        # Act
        result = run_agent_with_messages_sync(messages, use_structured_output=True)

        # Assert
        mock_async_run.assert_called_once_with(messages, None, True)
        assert isinstance(result, StructuredResponse)
        assert result.thread_title == "Test Thread"
        assert result.message_title == "Test Response"
        assert result.response == "This is the agent's structured response"
        assert result.followups == ["Follow-up 1", "Follow-up 2"]


def test_run_agent_with_messages_sync_error_handling():
    """Test error handling in the sync agent function."""
    # Arrange
    messages = [{"role": "user", "content": "Hello", "type": "message"}]

    # Mock the async function to raise an exception and logging
    with patch("lib.agent.run_agent_with_messages") as mock_async_run:
        mock_async_run.side_effect = Exception("Test error")

        # Act
        result = run_agent_with_messages_sync(messages)

        # Assert - result should be a string with the error message
        assert isinstance(result, str)
        assert "I'm sorry, I encountered an error" in result
        
        
def test_run_agent_with_messages_sync_error_handling_structured():
    """Test error handling in the sync agent function with structured output."""
    # Arrange
    messages = [{"role": "user", "content": "Hello", "type": "message"}]

    # Mock the async function to raise an exception and logging
    with patch("lib.agent.run_agent_with_messages") as mock_async_run:
        mock_async_run.side_effect = Exception("Test error")

        # Act
        result = run_agent_with_messages_sync(messages, use_structured_output=True)

        # Assert
        assert isinstance(result, StructuredResponse)
        assert result.message_title == "Error Encountered"
        assert "I'm sorry, I encountered an error" in result.response
