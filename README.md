# MooAI Slack Bot

A Slack bot that integrates with OpenAI's Agent SDK to provide AI assistant functionality in Slack.

## Features

- Responds to app mentions in channels
- Ability to start assistant threads and have conversations
- Uses OpenAI's Agent SDK for intelligent responses
- Provides suggested prompts to help users get started
- Supports markdown formatting in responses
- Web search is enabled for the agent
- Supports image and PDF file attachments
- Home tab
- AI generated suggested prompts, message title and thread title

## Roadmap

- Add knowledge base functionality
- Add image generation functionality for the agent
- Add (switchable) personas for the agent
- Add slash commands
- Token limits

## Prerequisites

- Python 3.8+
- Slack App with appropriate permissions
- OpenAI API key

## Environment Variables

This app connects to Slack via socket mode for ease.

The following environment variables are required:

- `SLACK_BOT_TOKEN` - Your Slack Bot User OAuth Token (starts with `xoxb-`)
- `SLACK_APP_TOKEN` - Your Slack App-Level Token (starts with `xapp-`)
- `OPENAI_API_KEY` - Your OpenAI API key

## Slack App Configuration

### Required Scopes

Your Slack app needs the following OAuth scopes:

- `app_mentions:read` - Allow the app to read app mentions
- `assistant:write` - Allow the app to act as an App agent
- `channels:history` - View messages in public channels
- `channels:join` - Join public channels
- `chat:write` - Send messages
- `commands` - Allow the app to register commands
- `files:read` - Access files (for PDF support)
- `groups:history` - View messages in private channels
- `im:history` - View messages in direct messages
- `users:read` - Read user information

### Event subscriptions

Your app needs to subscribe to the following events:

- `app_home_opened` - When a user opens their home tab
- `app_mention` - When the app is mentioned in a channel
- `assistant_thread_started` - When a user starts a new assistant thread
- `assistant_thread_context_changed` - When a user sends a message in an assistant thread
- `message:im` - When a message is sent in a channel

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Slack app in [Slack API Console](https://api.slack.com/apps)
4. Set up your environment variables (see above)
5. Run the app:

```bash
python3 app.py
```

## Code Quality

This project uses Black for code formatting and Flake8 for linting to maintain code quality.

### Formatting with Black

To format your code with Black:

```bash
# Format all Python files
black .

# Format a specific file
black path/to/file.py
```

### Linting with Flake8

To check your code with Flake8:

```bash
# Check all Python files
flake8 .

# Check a specific file
flake8 path/to/file.py
```

## Testing

This project uses pytest for testing. The test files are located in the `tests/` directory.

### Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_slack_utils.py
```

To run a specific test function:

```bash
pytest tests/test_slack_utils.py::test_function_name
```

To run tests with coverage report:

```bash
pytest --cov=lib tests/
```

### Writing Tests

Test files should be named `test_*.py` and placed in the `tests/` directory. Test functions should be named `test_*`.

Example test structure:

```python
def test_function_name():
    # Arrange - set up test data
    test_data = {...}
    
    # Act - call the function being tested
    result = function_to_test(test_data)
    
    # Assert - check the result
    assert result == expected_result
```

## Project Structure

- `app.py` - Entry point that initializes the Bolt app and registers listeners
- `listeners/` - Contains Slack event handlers
  - `assistant.py` - Handles assistant events and user messages
  - `command.py` - Handles slash commands
  - `home_tab.py` - Handles home tab events
- `lib/` - Contains utilities and agent logic
  - `agent.py` - OpenAI Agent implementation
  - `constants.py` - System messages and prompts
  - `slack_utils.py` - Slack-specific utilities
  - `file_utils.py` - File (PDF and image) handling utilities

## Persistence

The application uses Slack as the source of truth for conversation history. Messages are fetched directly from Slack threads when needed, eliminating the need for a separate database.

## Customization

You can easily customize the assistant's behavior by modifying:

- `lib/constants.py` - Change system instructions, greeting messages, and suggested prompts
- `lib/agent.py` - Modify agent configuration
- `listeners/home_tab.py` - Modify home tab content

## License

MIT

:)