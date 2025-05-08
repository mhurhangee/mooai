"""
constants.py
-------------
Central location for all user-facing prompts, system messages, and error templates for Slack listeners.
"""

# System prompt for initial assistant greeting
ASSISTANT_GREETING = "How can I help you?"

# Suggested prompts for new assistant threads
SUGGESTED_PROMPTS = [
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

THINKING_MESSAGE = "is typing..."

# Error message templates
GENERIC_ERROR = ":warning: Something went wrong! ({error})"

# Logging templates
THREAD_START_ERROR_LOG = "Failed to handle an assistant_thread_started event: {error}"
USER_MESSAGE_ERROR_LOG = "Failed to handle a user message event: {error}"
