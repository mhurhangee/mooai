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
