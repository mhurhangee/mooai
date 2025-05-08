import logging
from typing import List, Dict
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from agents.agent_service import call_agent_sync
from listeners.constants import ASSISTANT_GREETING, SUGGESTED_PROMPTS, GENERIC_ERROR, THREAD_START_ERROR_LOG, USER_MESSAGE_ERROR_LOG, THINKING_MESSAGE

# Initialize the Slack Assistant middleware instance
# This handles AI-powered threads in Slack using the Bolt framework
assistant = Assistant()

# Handler for when a user starts a new assistant thread in Slack.
# Presents the user with a set of suggested prompts to help them get started.
@assistant.thread_started
def start_assistant_thread(
    say: Say,
    get_thread_context: GetThreadContext,
    set_suggested_prompts: SetSuggestedPrompts,
    logger: logging.Logger,
):
    try:
        say(ASSISTANT_GREETING)

        # Optionally, you could use thread_context to customize prompts per channel/thread
        thread_context = get_thread_context()
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
    get_thread_context: GetThreadContext,
    client: WebClient,
    say: Say,
):
    try:
        # Get the latest user message from the Slack event payload
        user_message = payload["text"]
        set_status(THINKING_MESSAGE)  # Show "is typing..." in Slack thread

        # TODO: Add custom logic for special prompts (e.g. summarization)

        # Forward the user's message to the OpenAI Agent.
        # The agent uses response_id mapping for context, so only the latest message is needed.
        returned_message = call_agent_sync(
            payload.get("user"),
            context.channel_id,
            context.thread_ts,
            user_message
        )
        say(returned_message)
    except Exception as e:
        logger.exception(USER_MESSAGE_ERROR_LOG.format(error=e))
        say(GENERIC_ERROR.format(error=e))
