"""
Tests for the slack_utils module.
"""

from unittest.mock import MagicMock, patch
from lib.slack_utils import format_slack_messages_for_openai, fetch_slack_thread, markdown_to_mrkdwn


def test_format_slack_messages_for_openai_with_valid_data():
    """Test formatting Slack messages to OpenAI format with valid data."""
    # Arrange
    slack_messages = [
        {"text": "Hello", "bot_id": None},
        {"text": "Hi there", "bot_id": "B123"},
    ]

    # Act
    result = format_slack_messages_for_openai(slack_messages)

    # Assert
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "Hello"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Hi there"


def test_format_slack_messages_for_openai_with_empty_data():
    """Test formatting Slack messages to OpenAI format with empty data."""
    # Arrange
    slack_messages = []

    # Act
    result = format_slack_messages_for_openai(slack_messages)

    # Assert
    assert result == []


def test_format_slack_messages_for_openai_with_none_data():
    """Test formatting Slack messages to OpenAI format with None data."""
    # Arrange
    slack_messages = None

    # Act
    result = format_slack_messages_for_openai(slack_messages)

    # Assert
    assert result == []


@patch("lib.slack_utils.logger")
def test_fetch_slack_thread_success(mock_logger):
    """Test fetching a Slack thread successfully."""
    # Arrange
    mock_client = MagicMock()
    mock_client.conversations_replies.return_value = {"messages": ["message1", "message2"]}

    mock_context = MagicMock()
    mock_context.thread_ts = "123.456"
    mock_context.channel_id = "C123"

    mock_payload = {}
    mock_say = MagicMock()

    # Act
    result = fetch_slack_thread(mock_client, mock_context, mock_payload, mock_say)

    # Assert
    assert result == ["message1", "message2"]
    mock_client.conversations_replies.assert_called_once_with(channel="C123", ts="123.456", limit=1000, inclusive=True)


@patch("lib.slack_utils.logger")
def test_fetch_slack_thread_missing_data(mock_logger):
    """Test fetching a Slack thread with missing data."""
    # Arrange
    mock_client = MagicMock()
    mock_context = MagicMock()
    mock_context.thread_ts = None
    mock_context.channel_id = None

    mock_payload = {}
    mock_say = MagicMock()

    # Act
    result = fetch_slack_thread(mock_client, mock_context, mock_payload, mock_say)

    # Assert
    assert result is None
    mock_logger.error.assert_called_once()
    mock_say.assert_called_once()


def test_markdown_to_mrkdwn_conversion():
    """Test converting markdown to Slack mrkdwn format."""
    # Arrange
    markdown_text = "**Bold** and *italic*"

    # Act
    with patch("lib.slack_utils.SlackMarkdownConverter") as MockConverter:
        mock_instance = MockConverter.return_value
        mock_instance.convert.return_value = "*Bold* and _italic_"

        result = markdown_to_mrkdwn(markdown_text)

    # Assert
    assert result == "*Bold* and _italic_"
    mock_instance.convert.assert_called_once_with(markdown_text)


def test_markdown_to_mrkdwn_empty_string():
    """Test converting empty string to mrkdwn."""
    # Act
    result = markdown_to_mrkdwn("")

    # Assert
    assert result == ""
