import logging
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_sdk import WebClient

from lib.agent import run_agent_with_messages_sync
from lib.constants import ASSISTANT_GREETING, SUGGESTED_PROMPTS, GENERIC_ERROR, THREAD_START_ERROR_LOG, USER_MESSAGE_ERROR_LOG, THINKING_MESSAGE

from lib.slack_utils import (
    fetch_slack_thread,
    format_slack_messages_for_openai,
    markdown_to_mrkdwn
)

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

        # Fetch the full thread from Slack using utility
        slack_messages = fetch_slack_thread(client, context, payload, say)
        if not slack_messages:
            return

        # Format Slack messages into OpenAI Message format using utility
        formatted_messages = format_slack_messages_for_openai(slack_messages)
        if not formatted_messages:
            say(GENERIC_ERROR.format(error="No messages found in thread."))
            return

        # Forward the full thread to the OpenAI Agent using our agent service
        returned_message = run_agent_with_messages_sync(formatted_messages)

        # Convert Markdown to Slack mrkdwn before sending using utility
        mrkdwn_message = markdown_to_mrkdwn(returned_message)
        say(mrkdwn_message)

    except Exception as e:
        logger.exception(USER_MESSAGE_ERROR_LOG.format(error=e))
        say(GENERIC_ERROR.format(error=e))
