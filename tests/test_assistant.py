"""
Tests for the assistant listeners.
"""

from unittest.mock import MagicMock, patch
from listeners.assistant import start_assistant_thread, respond_in_assistant_thread
from lib.constants import ASSISTANT_GREETING, SUGGESTED_PROMPTS, THINKING_MESSAGE


def test_start_assistant_thread_success():
    """Test starting an assistant thread successfully."""
    # Arrange
    mock_say = MagicMock()
    mock_set_suggested_prompts = MagicMock()
    mock_logger = MagicMock()

    # Act
    start_assistant_thread(say=mock_say, set_suggested_prompts=mock_set_suggested_prompts, logger=mock_logger)

    # Assert
    mock_say.assert_called_once_with(ASSISTANT_GREETING)
    mock_set_suggested_prompts.assert_called_once_with(prompts=SUGGESTED_PROMPTS)
    mock_logger.exception.assert_not_called()


def test_start_assistant_thread_error():
    """Test error handling when starting an assistant thread."""
    # Arrange
    mock_say = MagicMock()
    mock_set_suggested_prompts = MagicMock()
    mock_logger = MagicMock()

    # We need to patch the GENERIC_ERROR to avoid errors in the except block
    with patch("listeners.assistant.GENERIC_ERROR", "{error}"):
        # Make the first call to say work, but have set_suggested_prompts raise an exception
        mock_set_suggested_prompts.side_effect = Exception("Test error")

        # Act
        start_assistant_thread(say=mock_say, set_suggested_prompts=mock_set_suggested_prompts, logger=mock_logger)

    # Assert
    mock_logger.exception.assert_called_once()
    # First call is the greeting, second call is the error message
    assert mock_say.call_count == 2


@patch("listeners.assistant.fetch_slack_thread")
@patch("listeners.assistant.format_slack_messages_for_openai")
@patch("listeners.assistant.run_agent_with_messages_sync")
@patch("listeners.assistant.markdown_to_mrkdwn")
def test_respond_in_assistant_thread_success(
    mock_markdown_to_mrkdwn, mock_run_agent, mock_format_messages, mock_fetch_thread
):
    """Test responding in an assistant thread successfully."""
    # Arrange
    mock_payload = {}
    mock_logger = MagicMock()
    mock_context = MagicMock()
    mock_set_status = MagicMock()
    mock_client = MagicMock()
    mock_say = MagicMock()

    # Setup mocks
    mock_fetch_thread.return_value = ["message1", "message2"]
    mock_format_messages.return_value = [{"role": "user", "content": "Hello"}]
    mock_run_agent.return_value = "Agent response"
    mock_markdown_to_mrkdwn.return_value = "Formatted agent response"

    # Act
    respond_in_assistant_thread(
        payload=mock_payload,
        logger=mock_logger,
        context=mock_context,
        set_status=mock_set_status,
        client=mock_client,
        say=mock_say,
    )

    # Assert
    mock_set_status.assert_called_once_with(THINKING_MESSAGE)
    mock_fetch_thread.assert_called_once()
    mock_format_messages.assert_called_once_with(["message1", "message2"])
    mock_run_agent.assert_called_once_with([{"role": "user", "content": "Hello"}])
    mock_markdown_to_mrkdwn.assert_called_once_with("Agent response")
    mock_say.assert_called_once_with("Formatted agent response")


@patch("listeners.assistant.fetch_slack_thread")
def test_respond_in_assistant_thread_no_messages(mock_fetch_thread):
    """Test responding when no messages are found in the thread."""
    # Arrange
    mock_payload = {}
    mock_logger = MagicMock()
    mock_context = MagicMock()
    mock_set_status = MagicMock()
    mock_client = MagicMock()
    mock_say = MagicMock()

    # Setup mocks
    mock_fetch_thread.return_value = None

    # Act
    respond_in_assistant_thread(
        payload=mock_payload,
        logger=mock_logger,
        context=mock_context,
        set_status=mock_set_status,
        client=mock_client,
        say=mock_say,
    )

    # Assert
    mock_set_status.assert_called_once_with(THINKING_MESSAGE)
    mock_fetch_thread.assert_called_once()
    # Should return early without calling say
    mock_say.assert_not_called()


@patch("listeners.assistant.fetch_slack_thread")
@patch("listeners.assistant.format_slack_messages_for_openai")
def test_respond_in_assistant_thread_empty_formatted_messages(mock_format_messages, mock_fetch_thread):
    """Test responding when formatted messages are empty."""
    # Arrange
    mock_payload = {}
    mock_logger = MagicMock()
    mock_context = MagicMock()
    mock_set_status = MagicMock()
    mock_client = MagicMock()
    mock_say = MagicMock()

    # Setup mocks
    mock_fetch_thread.return_value = ["message1", "message2"]
    mock_format_messages.return_value = []

    # Act
    respond_in_assistant_thread(
        payload=mock_payload,
        logger=mock_logger,
        context=mock_context,
        set_status=mock_set_status,
        client=mock_client,
        say=mock_say,
    )

    # Assert
    mock_set_status.assert_called_once_with(THINKING_MESSAGE)
    mock_fetch_thread.assert_called_once()
    mock_format_messages.assert_called_once_with(["message1", "message2"])
    # Should call say with error message
    mock_say.assert_called_once()
    mock_logger.error.assert_called_once()
