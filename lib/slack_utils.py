"""
slack_utils.py
Reusable utilities for Slack message formatting, thread fetching, and markdown conversion.
"""
from typing import List, Dict, Any, Optional
import logging
from markdown_to_mrkdwn import SlackMarkdownConverter
from lib.constants import GENERIC_ERROR

logger = logging.getLogger(__name__)

def format_slack_messages_for_openai(slack_messages: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    """
    Format Slack messages into OpenAI Message format.
    Args:
        slack_messages: List of Slack message dicts.
    Returns:
        List of OpenAI-formatted message dicts.
    """
    formatted_messages = []
    
    if not slack_messages:
        logger.error("Slack thread messages are empty or None.")
        return formatted_messages
        
    for msg in slack_messages:
        role = "user" if not msg.get("bot_id") else "assistant"
        formatted_messages.append({
            "role": role,
            "content": msg.get("text", ""),
            "type": "message"
        })
    
    return formatted_messages

def fetch_slack_thread(client: Any, context: Any, payload: Dict[str, Any], say: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch the full thread from Slack using conversations_replies.
    Args:
        client: Slack WebClient instance.
        context: Slack context object (should have thread_ts and channel_id).
        payload: Event payload dict.
        say: Slack say function for error reporting.
    Returns:
        List of messages in the thread, or None if error.
    """
    thread_ts = getattr(context, 'thread_ts', None) or payload.get("thread_ts") or payload.get("ts")
    channel_id = getattr(context, 'channel_id', None)
    
    if not channel_id or not thread_ts:
        error_msg = "Missing channel or thread timestamp for conversations_replies."
        logger.error(error_msg)
        say(GENERIC_ERROR.format(error=error_msg))
        return None
        
    try:
        response = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=1000)
        return response.get("messages", [])
    except Exception as e:
        error_msg = f"Failed to fetch Slack thread: {e}"
        logger.exception(error_msg)
        say(GENERIC_ERROR.format(error=e))
        return None

def markdown_to_mrkdwn(returned_message: str) -> str:
    """
    Convert Markdown to Slack mrkdwn format.
    Args:
        returned_message: Markdown string.
    Returns:
        mrkdwn-formatted string.
    """
    if not returned_message:
        return ""
        
    try:
        converter = SlackMarkdownConverter()
        return converter.convert(returned_message)
    except Exception as e:
        error_msg = f"Markdown to mrkdwn conversion failed: {e}"
        logger.error(error_msg)
        return returned_message
