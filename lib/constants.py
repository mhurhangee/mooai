"""
constants.py
-------------
Central location for all user-facing prompts, system messages, and error templates for Slack listeners.
"""

# Suggested prompts for new assistant threads
from typing import List, Dict, Union

# System prompt for initial assistant greeting
ASSISTANT_GREETING = "🐄🐮 You called, I herd you! Let's get started!"

# Greeting when the bot is mentioned in a channel
MENTION_GREETING = "🐮 Thanks for the moo-mention! Give me a second, and I'll help you with that. If you want me to reply to any later messages in this thread, just mention me again."

SUGGESTED_PROMPTS: List[Union[str, Dict[str, str]]] = [
    {
        "title": "😊 What are some positive news stories from today?",
        "message": "😊 What are some positive news stories from today?",
    },
    {
        "title": "📧 Help me write an email",
        "message": "📧 Help me write an email",
    },
    {
        "title": "🧠 Brainstorm ideas for my next project",
        "message": "🧠 Brainstorm ideas for my next project",
    },
    {
        "title": "🌍 Give me ideas for reducing my carbon footprint",
        "message": "🌍 Give me ideas for reducing my carbon footprint",
    }
]

THINKING_MESSAGE = "is thinking 🐮💭 ..."

FOLLOWUP_PROMPTS_TITLE = "💭✍️ Suggested follow-ups or write your own "

# Error message templates
GENERIC_ERROR = ":warning: Something went wrong! ({error})"

# Logging templates
THREAD_START_ERROR_LOG = "Failed to handle an assistant_thread_started event: {error}"
USER_MESSAGE_ERROR_LOG = "Failed to handle a user message event: {error}"

SYSTEM_INSTRUCTIONS = """
- You are a very friendly and helpful assistant.
- Be concise and to the point.
- Format your responses with markdown and emojis.
- Your responses will be structured with the following components:
  1. Thread Title: A concise title that summarizes the conversation thread (3-5 words) and starts with emojis.
  2. Message Title: A brief header for your current response (optional) and starts with emojis.
  3. Response: Your main response content formatted with markdown and emojis.
  4. Followups: 2-3 suggested follow-up questions the user might want to ask formatted with emojis.
- For thread titles, focus on the overall topic of conversation, not just the current message.
- For message titles, use a short phrase that captures the essence of your response.
- Keep your main response clear, helpful, and well-formatted.
- Suggest followups that are natural extensions of the conversation.
"""
