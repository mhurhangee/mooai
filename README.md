# MooAI Slack Bot

A simple, elegant Slack bot that integrates with OpenAI's Agent SDK to provide AI assistant functionality in Slack threads.

## Features

- Responds to messages in Slack threads
- Uses OpenAI's Agent SDK for intelligent responses
- Provides suggested prompts to help users get started
- Supports markdown formatting in responses

## Prerequisites

- Python 3.8+
- Slack App with appropriate permissions
- OpenAI API key

## Environment Variables

The following environment variables are required:

- `SLACK_BOT_TOKEN` - Your Slack Bot User OAuth Token
- `SLACK_APP_TOKEN` - Your Slack App-Level Token (starts with `xapp-`)
- `OPENAI_API_KEY` - Your OpenAI API key

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables (see above)
4. Run the app:

```bash
python app.py
```

## Project Structure

- `app.py` - Entry point that initializes the Bolt app and registers listeners
- `listeners/` - Contains Slack event handlers
  - `assistant.py` - Handles assistant events and user messages
- `lib/` - Contains utilities and agent logic
  - `agent.py` - OpenAI Agent implementation
  - `constants.py` - System messages and prompts
  - `slack_utils.py` - Slack-specific utilities

## Persistence

The application uses Slack as the source of truth for conversation history. Messages are fetched directly from Slack threads when needed, eliminating the need for a separate database.

## Customization

You can customize the assistant's behavior by modifying:

- `lib/constants.py` - Change system instructions, greeting messages, and suggested prompts
- `lib/agent.py` - Modify agent configuration

## License

MIT
