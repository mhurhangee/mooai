import logging
from slack_bolt import Ack, Respond
from typing import Dict, Any


def echo_command(command: Dict[str, Any], ack: Ack, respond: Respond, logger: logging.Logger) -> None:
    """
    Handle the /echo slash command to echo back the user's message.

    Args:
        command: The command data from Slack
        ack: Function to acknowledge the command request
        respond: Function to respond to the command
        logger: The logger instance
    """
    try:
        # Acknowledge the command request immediately
        ack()

        # Get the text from the command
        text = command.get("text", "").strip()

        if text:
            # Respond with the echoed message
            respond(f"MooAI: {text}")
        else:
            # Respond with a helpful message if no text was provided
            respond("Please provide a message to echo. Usage: `/echo [message]`")

    except Exception as e:
        logger.error(f"Error handling echo command: {e}")
        respond("Sorry, something went wrong while processing your command.")
