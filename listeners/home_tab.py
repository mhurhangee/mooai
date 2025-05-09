import logging
from slack_sdk import WebClient
from slack_sdk.models.blocks import (
    HeaderBlock,
    DividerBlock,
    SectionBlock,
    ContextBlock,
    PlainTextObject,
    MarkdownTextObject,
)


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

        # Build blocks for the home tab using Block Kit builder classes
        blocks = [
            # Header
            HeaderBlock(text=PlainTextObject(text="🐮 Welcome to MooAI!", emoji=True)),
            DividerBlock(),
            # Chat with MooAI section
            SectionBlock(text=MarkdownTextObject(text="🐄 *Chat with MooAI...*")),
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=" 1️⃣ *... in side panel*: Add MooAI to top bar by clicking three dots in top right ↗️"
                    )
                ]
            ),
            ContextBlock(
                elements=[MarkdownTextObject(text=" 2️⃣ *... in full mode*: Open MooAI via the apps menu in the side bar ⬅️")]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(text=" 3️⃣ *... in threads*: While in a channel, mention `@MooAI` to start a thread 🧵")
                ]
            ),
            DividerBlock(),
            # Chat Features section
            SectionBlock(text=MarkdownTextObject(text="🐮 *Chat Features*")),
            ContextBlock(
                elements=[MarkdownTextObject(text=" 📎 *Attach files and images*: Add PDF and/or images to your message")]
            ),
            ContextBlock(
                elements=[MarkdownTextObject(text=" 📑 *Markdown formatting*: MooAI supports rich text responses")]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(text=" 🌐 *Web search*: MooAI can search the web to provide up-to-date information")
                ]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=" 📊 *Thread titles*: MooAI automatically updates thread titles based on conversation"
                    )
                ]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=" 🗣️ *Follow-up prompts*: generates follow-up prompts to help you continue the conversation"
                    )
                ]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(
                        text=" 💡 *Coming Soon*: Knowledge base integration, and image generation!"
                    )
                ]
            ),
            DividerBlock(),
            # Commands section
            SectionBlock(text=MarkdownTextObject(text="*Available Commands*")),
            SectionBlock(text=MarkdownTextObject(text="• `/echo [message]` - Echo back your message")),
        ]

        # Publish a Home tab view
        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [block.to_dict() for block in blocks],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
