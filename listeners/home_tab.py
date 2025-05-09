import logging
from slack_sdk import WebClient


def home_opened(client: WebClient, event: dict, logger: logging.Logger):
    """
    Handle the app_home_opened event to display a custom home tab.

    Args:
        client: The Slack WebClient instance
        event: The event data from Slack
        logger: The logger instance
    """
    try:
        # Get the user ID from the event
        user_id = event["user"]

        # Publish a Home tab view
        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": "Welcome to MooAI! 🐮", "emoji": True}},
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "🐮 *Chat with MooAI...*"}},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 1️⃣ *... in side panel*: Add MooAI to top bar by clicking three dots in top right ↗️",
                            }
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 2️⃣ *... in full mode*: Open MooAI via the apps menu in the side bar ⬅️",
                            }
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 3️⃣ *... in threads*: _(coming soon)_ While in a channel, mention `@MooAI` to start a thread 🧵",
                            }
                        ],
                    },
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "🧀 *Chat Features*"}},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 📎 *Attach files and images*: Add PDF and/or images to your message",
                            }
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {"type": "mrkdwn", "text": " 📑 *Markdown formatting*: MooAI supports rich text responses"}
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 🌐 *Web search*: MooAI can search the web to provide up-to-date information",
                            }
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": " 💡 *Coming Soon*: Knowledge base integration, image generation, and switchable personas!",
                            }
                        ],
                    },
                    {"type": "divider"},
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "*Available Commands*"}},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "• `/echo [message]` - Echo back your message"}},
                ],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
