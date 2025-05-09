"""
Tests for the assistant listeners.
"""

from unittest.mock import MagicMock, patch
from listeners.assistant import (
    start_assistant_thread,
    respond_in_assistant_thread,
    respond_to_mention,
    respond_to_thread_message,
    process_thread_and_respond,
)
from lib.constants import ASSISTANT_GREETING, SUGGESTED_PROMPTS, THINKING_MESSAGE, MENTION_GREETING


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
@patch("listeners.assistant.extract_files_from_slack_messages")
@patch("listeners.assistant.format_slack_messages_for_openai")
@patch("listeners.assistant.run_agent_with_messages_sync")
@patch("listeners.assistant.markdown_to_mrkdwn")
def test_respond_in_assistant_thread_success(
    mock_markdown_to_mrkdwn, mock_run_agent, mock_format_messages, mock_extract_files, mock_fetch_thread
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
    mock_extract_files.return_value = {"123.456": [{"type": "input_image", "image_url": "data:image/png;base64,abc"}]}
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
    mock_extract_files.assert_called_once_with(mock_client, ["message1", "message2"])
    mock_format_messages.assert_called_once_with(["message1", "message2"], mock_extract_files.return_value)
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
@patch("listeners.assistant.extract_files_from_slack_messages")
@patch("listeners.assistant.format_slack_messages_for_openai")
def test_respond_in_assistant_thread_empty_formatted_messages(mock_format_messages, mock_extract_files, mock_fetch_thread):
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
    mock_extract_files.return_value = {}
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
    mock_extract_files.assert_called_once_with(mock_client, ["message1", "message2"])
    mock_format_messages.assert_called_once_with(["message1", "message2"], {})
    # Should call say with error message
    mock_say.assert_called_once()
    mock_logger.error.assert_called_once()


@patch("listeners.assistant.process_thread_and_respond")
def test_respond_to_mention_new_thread(mock_process_thread):
    """Test responding to a new mention in a channel (creating a new thread)."""
    # Arrange
    mock_body = {"event": {"text": "<@U123> Hello", "user": "U456", "channel": "C789", "ts": "123.456"}}
    mock_logger = MagicMock()
    mock_client = MagicMock()

    # Setup mocks
    mock_client.chat_postMessage.return_value = {"ok": True}

    # Act
    respond_to_mention(body=mock_body, logger=mock_logger, client=mock_client)

    # Assert
    mock_client.chat_postMessage.assert_called_once_with(channel="C789", thread_ts="123.456", text=MENTION_GREETING)
    mock_process_thread.assert_called_once_with("C789", "123.456", mock_client, mock_logger)


@patch("listeners.assistant.process_thread_and_respond")
def test_respond_to_mention_missing_data(mock_process_thread):
    """Test responding to a mention with missing data."""
    # Arrange
    mock_body = {"event": {}}
    mock_logger = MagicMock()
    mock_client = MagicMock()

    # Act
    respond_to_mention(body=mock_body, logger=mock_logger, client=mock_client)

    # Assert
    mock_logger.error.assert_called_once()
    mock_client.chat_postMessage.assert_not_called()
    mock_process_thread.assert_not_called()


@patch("listeners.assistant.process_thread_and_respond")
def test_respond_to_thread_message_with_mention(mock_process_thread):
    """Test responding to a message in a thread that mentions the bot."""
    # Arrange
    mock_body = {
        "event": {
            "text": "<@B123> Tell me more",
            "user": "U456",
            "channel": "C789",
            "ts": "123.789",
            "thread_ts": "123.456",
        },
        "authorizations": [{"user_id": "B123"}],
    }
    mock_logger = MagicMock()
    mock_client = MagicMock()

    # Act
    respond_to_thread_message(body=mock_body, logger=mock_logger, client=mock_client)

    # Assert
    mock_process_thread.assert_called_once_with("C789", "123.456", mock_client, mock_logger)


@patch("listeners.assistant.process_thread_and_respond")
def test_respond_to_thread_message_without_mention(mock_process_thread):
    """Test that the bot doesn't respond to a thread message without a mention."""
    # Arrange
    mock_body = {
        "event": {
            "text": "Tell me more",  # No mention here
            "user": "U456",
            "channel": "C789",
            "ts": "123.789",
            "thread_ts": "123.456",
        },
        "authorizations": [{"user_id": "B123"}],
    }
    mock_logger = MagicMock()
    mock_client = MagicMock()

    # Act
    respond_to_thread_message(body=mock_body, logger=mock_logger, client=mock_client)

    # Assert
    mock_process_thread.assert_not_called()


@patch("listeners.assistant.extract_files_from_slack_messages")
@patch("listeners.assistant.format_slack_messages_for_openai")
@patch("listeners.assistant.run_agent_with_messages_sync")
@patch("listeners.assistant.markdown_to_mrkdwn")
def test_process_thread_and_respond_success(
    mock_markdown_to_mrkdwn, mock_run_agent, mock_format_messages, mock_extract_files
):
    """Test processing a thread and generating a response successfully."""
    # Arrange
    channel_id = "C789"
    thread_ts = "123.456"
    mock_client = MagicMock()
    mock_logger = MagicMock()

    # Setup mocks
    mock_client.conversations_replies.return_value = {"messages": ["message1", "message2"]}
    mock_extract_files.return_value = {}
    mock_format_messages.return_value = [{"role": "user", "content": "Hello"}]
    mock_run_agent.return_value = "Agent response"
    mock_markdown_to_mrkdwn.return_value = "Formatted agent response"

    # Act
    process_thread_and_respond(channel_id, thread_ts, mock_client, mock_logger)

    # Assert
    mock_client.conversations_replies.assert_called_once_with(channel=channel_id, ts=thread_ts, limit=1000, inclusive=True)
    mock_extract_files.assert_called_once_with(mock_client, ["message1", "message2"])
    mock_format_messages.assert_called_once_with(["message1", "message2"], {})
    mock_run_agent.assert_called_once_with([{"role": "user", "content": "Hello"}])
    mock_markdown_to_mrkdwn.assert_called_once_with("Agent response")
    mock_client.chat_postMessage.assert_called_once_with(
        channel=channel_id, thread_ts=thread_ts, text="Formatted agent response"
    )
