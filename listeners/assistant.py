import logging
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient

from agent_core.agent_service import run_agent_with_messages_sync
from listeners.constants import ASSISTANT_GREETING, SUGGESTED_PROMPTS, GENERIC_ERROR, THREAD_START_ERROR_LOG, USER_MESSAGE_ERROR_LOG, THINKING_MESSAGE

from markdown_to_mrkdwn import SlackMarkdownConverter

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
        logger.exception(THREAD_START_ERROR_LOG.format(error=e), e)
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
):
    try:
        set_status(THINKING_MESSAGE)  # Show "is typing..." in Slack thread

        # Fetch the full thread from Slack
        thread_ts = context.thread_ts or payload.get("thread_ts") or payload.get("ts")
        channel_id = context.channel_id
        if channel_id is None or thread_ts is None:
            logger.error("Missing channel or thread timestamp for conversations_replies.")
            say(GENERIC_ERROR.format(error="Missing channel or thread timestamp."))
            return
        try:
            response = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=1000)
            slack_messages = response.get("messages", [])
        except Exception as e:
            logger.exception(f"Failed to fetch Slack thread: {e}")
            say(GENERIC_ERROR.format(error=e))
            return

        # Format Slack messages into OpenAI Message format
        formatted_messages = []
        if slack_messages is not None:
            for msg in slack_messages:
                role = "user" if not msg.get("bot_id") else "assistant"
                formatted_messages.append({
                    "role": role,
                    "content": msg.get("text", ""),
                    "type": "message"
                })
        else:
            logger.error("Slack thread messages are None.")
            say(GENERIC_ERROR.format(error="No messages found in thread."))
            return

        # Forward the full thread to the OpenAI Agent using our agent service
        returned_message = run_agent_with_messages_sync(formatted_messages)

        # Convert Markdown to Slack mrkdwn before sending
        try:
            converter = SlackMarkdownConverter()
            mrkdwn_message = converter.convert(returned_message)
        except Exception as e:
            logger.error(f"Markdown to mrkdwn conversion failed: {e}")
            mrkdwn_message = returned_message

        say(mrkdwn_message)
    except Exception as e:
        logger.exception(USER_MESSAGE_ERROR_LOG.format(error=e))
        say(GENERIC_ERROR.format(error=e))
