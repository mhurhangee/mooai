import logging
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus, SetTitle
from slack_sdk import WebClient
from slack_sdk.models.blocks import HeaderBlock, SectionBlock, DividerBlock

from lib.agent import run_agent_with_messages_sync
from lib.constants import (
    ASSISTANT_GREETING,
    SUGGESTED_PROMPTS,
    GENERIC_ERROR,
    THREAD_START_ERROR_LOG,
    USER_MESSAGE_ERROR_LOG,
    THINKING_MESSAGE,
    MENTION_GREETING,
    FOLLOWUP_PROMPTS_TITLE,
)

from lib.slack_utils import fetch_slack_thread, format_slack_messages_for_openai, markdown_to_mrkdwn
from lib.file_utils import extract_files_from_slack_messages

# Initialize the Slack Assistant middleware instance
# This handles AI-powered threads in Slack using the Bolt framework
assistant = Assistant()


# Handler for when a user starts a new assistant thread in Slack.
# Presents the user with a set of suggested prompts to help them get started.
@assistant.thread_started
def start_assistant_thread(
    say: Say,
    set_suggested_prompts: SetSuggestedPrompts,
    logger: logging.Logger,
):
    try:
        say(ASSISTANT_GREETING)

        # Optionally, you could use thread_context to customize prompts per channel/thread
        set_suggested_prompts(prompts=SUGGESTED_PROMPTS)
    except Exception as e:
        error_msg = THREAD_START_ERROR_LOG.format(error=e)
        logger.exception(error_msg)
        say(GENERIC_ERROR.format(error=e))


# Handler for when a user sends a message in an assistant thread.
# Passes the user's latest message to the OpenAI agent (with context maintained by response_id mapping).
@assistant.user_message
def respond_in_assistant_thread(
    payload: dict,
    logger: logging.Logger,
    context: BoltContext,
    set_status: SetStatus,
    client: WebClient,
    say: Say,
    set_title: SetTitle,
    set_suggested_prompts: SetSuggestedPrompts,
):
    try:
        set_status(THINKING_MESSAGE)  # Show "is typing..." in Slack thread

        # Fetch the full thread from Slack using utility
        slack_messages = fetch_slack_thread(client, context, payload, say)
        if not slack_messages:
            # Error already logged and displayed by fetch_slack_thread
            return

        # Process any file attachments in the thread
        files_by_ts = extract_files_from_slack_messages(client, slack_messages)

        # Format Slack messages into OpenAI Message format using utility
        formatted_messages = format_slack_messages_for_openai(slack_messages, files_by_ts)
        if not formatted_messages:
            error_msg = "No messages found in thread."
            logger.error(error_msg)
            say(GENERIC_ERROR.format(error=error_msg))
            return

        # Forward the full thread to the OpenAI Agent using our agent service with structured output
        response = run_agent_with_messages_sync(formatted_messages, use_structured_output=True)

        # Handle structured response
        from lib.models import StructuredResponse

        if isinstance(response, StructuredResponse):
            # Update thread title if provided
            if response.thread_title:
                set_title(response.thread_title)

            # Build blocks for the message
            blocks = []

            # Add message title if provided
            if response.message_title:
                blocks.append(HeaderBlock(text=response.message_title))

            # Add main response content
            mrkdwn_response = markdown_to_mrkdwn(response.response)
            blocks.append(SectionBlock(text=mrkdwn_response))

            # Send the message with blocks
            say(text=mrkdwn_response, blocks=blocks)

            # Set follow-up prompts if provided
            if response.followups and len(response.followups) > 0:
                # Use the helper method to get properly formatted prompts
                from typing import cast, List, Dict, Union

                formatted_prompts = cast(List[Union[str, Dict[str, str]]], response.get_formatted_prompts())
                set_suggested_prompts(prompts=formatted_prompts, title=FOLLOWUP_PROMPTS_TITLE)

        else:
            # Fallback to plain text response if not structured
            mrkdwn_message = markdown_to_mrkdwn(response)
            say(mrkdwn_message)

    except Exception as e:
        error_msg = USER_MESSAGE_ERROR_LOG.format(error=e)
        logger.exception(error_msg)
        say(GENERIC_ERROR.format(error=e))


# Handler for when the bot is mentioned in a channel.
# Creates a new thread with the bot's response.
def respond_to_mention(
    body: dict,
    logger: logging.Logger,
    client: WebClient,
):
    """Handle mentions in channels by creating a thread with the bot's response.

    Args:
        body: The event body containing the mention details
        logger: Logger instance for error reporting
        client: Slack WebClient instance
    """
    try:
        # Extract event data from the body
        event = body.get("event", {})
        message_text = event.get("text", "")
        # user_id = event.get("user")
        channel_id = event.get("channel")
        ts = event.get("ts")
        thread_ts = event.get("thread_ts", ts)  # Use message ts as thread_ts if not in a thread

        if not message_text or not channel_id or not ts:
            logger.error("Missing required fields in mention payload")
            return

        # If this is a new message (not in a thread), create a thread by responding
        if thread_ts == ts:  # This is a new message, not in a thread
            thread_response = client.chat_postMessage(channel=channel_id, thread_ts=ts, text=MENTION_GREETING)

            if not thread_response or not thread_response.get("ok", False):
                logger.error(f"Failed to create thread: {thread_response.get('error', 'Unknown error')}")
                return

        # Process the thread and generate a response
        process_thread_and_respond(channel_id, thread_ts, client, logger)

    except Exception as e:
        error_msg = f"Failed to handle mention: {e}"
        logger.exception(error_msg)
        # We can't reliably send an error message here as we might not have channel_id and ts


# Handler for messages in threads where the bot has been mentioned
def respond_to_thread_message(
    body: dict,
    logger: logging.Logger,
    client: WebClient,
):
    """Handle messages in threads where the bot has been previously mentioned.
    Only responds if the message contains a direct mention to the bot.

    Args:
        body: The event body containing the message details
        logger: Logger instance for error reporting
        client: Slack WebClient instance
    """
    try:
        # Extract event data from the body
        event = body.get("event", {})
        message_text = event.get("text", "")
        # user_id = event.get("user")
        channel_id = event.get("channel")
        ts = event.get("ts")
        thread_ts = event.get("thread_ts")
        bot_id = body.get("authorizations", [{}])[0].get("user_id")

        # Skip if not in a thread or missing required fields
        if not thread_ts or not message_text or not channel_id or not ts or not bot_id:
            return

        # Skip if this is a bot message (to avoid loops)
        if event.get("bot_id") or event.get("user") == bot_id:
            return

        # Check if the message mentions the bot
        if f"<@{bot_id}>" not in message_text:
            return

        # Process the thread and respond
        process_thread_and_respond(channel_id, thread_ts, client, logger)

    except Exception as e:
        error_msg = f"Failed to handle thread message: {e}"
        logger.exception(error_msg)


# Helper function to process a thread and generate a response
def process_thread_and_respond(channel_id: str, thread_ts: str, client: WebClient, logger: logging.Logger):
    """Process all messages in a thread and generate a response.

    Args:
        channel_id: The Slack channel ID
        thread_ts: The thread timestamp
        client: Slack WebClient instance
        logger: Logger instance for error reporting
    """
    try:
        # Use conversations_replies to get the thread messages
        response = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=1000, inclusive=True)
        slack_messages = response.get("messages", [])

        if not slack_messages:
            logger.error("No messages found in thread")
            return

        # Process any file attachments in the thread
        files_by_ts = extract_files_from_slack_messages(client, slack_messages)

        # Format Slack messages into OpenAI Message format
        formatted_messages = format_slack_messages_for_openai(slack_messages, files_by_ts)
        if not formatted_messages:
            error_msg = "No messages found in thread."
            logger.error(error_msg)
            client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=GENERIC_ERROR.format(error=error_msg))
            return

        # Forward the thread to the OpenAI Agent with structured output
        response = run_agent_with_messages_sync(formatted_messages, use_structured_output=True)

        # Handle structured response
        from lib.models import StructuredResponse

        if isinstance(response, StructuredResponse):
            # Build blocks for the message
            blocks = []

            # Add message title if provided
            if response.message_title:
                blocks.append(HeaderBlock(text=response.message_title))
                blocks.append(DividerBlock())

            # Add main response content
            mrkdwn_response = markdown_to_mrkdwn(response.response)
            blocks.append(SectionBlock(text=mrkdwn_response))

            # Send the response in the thread with blocks if available
            if blocks:
                client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=mrkdwn_response, blocks=blocks)
            else:
                client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=mrkdwn_response)

            # Note: We can't update thread title or set suggested prompts in regular threads
            # as those are specific to Assistant threads
        else:
            # Fallback to plain text response if not structured
            mrkdwn_message = markdown_to_mrkdwn(response)
            client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=mrkdwn_message)

    except Exception as thread_error:
        logger.exception(f"Error processing thread: {thread_error}")
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=GENERIC_ERROR.format(error=thread_error))
