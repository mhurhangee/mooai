import logging
from .assistant import assistant
from .commands import echo_command
from .home_tab import home_opened

# Get logger
logger = logging.getLogger("mooai.listeners")


def register_listeners(app):
    logger.debug("Registering listeners...")

    # Register the home tab event listener
    logger.debug("Registering app_home_opened event handler")
    app.event("app_home_opened")(home_opened)

    # Register slash commands
    logger.debug("Registering /echo command handler")
    app.command("/echo")(echo_command)

    # Register the assistant middleware
    logger.debug("Registering assistant middleware")
    app.assistant(assistant)

    logger.debug("All listeners registered successfully")
