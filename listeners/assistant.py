import logging
from typing import List, Dict
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from agents.agent_service import call_agent_sync

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
        say("How can I help you?")

        # Suggested prompts to help users interact with the assistant
        prompts: List[Dict[str, str]] = [
            {
                "title": "What does Slack stand for?",
                "message": "Slack, a business communication service, was named after an acronym. Can you guess what it stands for?",
            },
            {
                "title": "Write a draft announcement",
                "message": "Can you write a draft announcement about a new feature my team just released? It must include how impactful it is.",
            },
            {
                "title": "Suggest names for my Slack app",
                "message": "Can you suggest a few names for my Slack app? The app helps my teammates better organize information and plan priorities and action items.",
            },
        ]

        # Optionally, you could use thread_context to customize prompts per channel/thread
        thread_context = get_thread_context()
        set_suggested_prompts(prompts=prompts)
    except Exception as e:
        logger.exception(f"Failed to handle an assistant_thread_started event: {e}", e)
        say(f":warning: Something went wrong! ({e})")


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
        set_status("is typing...")  # Show "is typing..." in Slack thread

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
        logger.exception(f"Failed to handle a user message event: {e}")
        say(f":warning: Something went wrong! ({e})")
