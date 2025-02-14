# Mock LLM Server

[![CI](https://github.com/stacklok/mockllm/actions/workflows/ci.yml/badge.svg)](https://github.com/stacklok/mockllm/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/mockllm.svg)](https://badge.fury.io/py/mockllm)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A FastAPI-based mock LLM server that mimics OpenAI and Anthropic API formats. Instead of calling actual language models,
it uses predefined responses from a YAML configuration file. 

This is made for when you want a deterministic response for testing or development purposes.

Check out the [CodeGate](https://github.com/stacklok/codegate) project when you're done here!

## Features

- OpenAI and Anthropic compatible API endpoints
- Streaming support (character-by-character response streaming)
- Configurable responses via YAML file
- Hot-reloading of response configurations
- JSON logging
- Error handling
- Mock token counting

## Installation

### From PyPI

```bash
pip install mockllm
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/stacklok/mockllm.git
cd mockllm
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install  # Install with all dependencies
# or
poetry install --without dev  # Install without development dependencies
```

## Usage

1. Set up the responses.yml

```bash
cp example.responses.yml responses.yml
```

2. Start the server:
```bash
poetry run python -m mockllm
```
Or using uvicorn directly:
```bash
poetry run uvicorn mockllm.server:app --reload
```

The server will start on `http://localhost:8000`

3. Send requests to the API endpoints:

### OpenAI Format

Regular request:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-llm",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ]
  }'
```

Streaming request:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-llm",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ],
    "stream": true
  }'
```

### Anthropic Format

Regular request:
```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ]
  }'
```

Streaming request:
```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [
      {"role": "user", "content": "what colour is the sky?"}
    ],
    "stream": true
  }'
```

## Configuration

### Response Configuration

Responses are configured in `responses.yml`. The file has two main sections:

1. `responses`: Maps input prompts to predefined responses
2. `defaults`: Contains default configurations like the unknown response message

Example `responses.yml`:
```yaml
responses:
  "what colour is the sky?": "The sky is blue during a clear day due to a phenomenon called Rayleigh scattering."
  "what is 2+2?": "2+2 equals 9."

defaults:
  unknown_response: "I don't know the answer to that. This is a mock response."
```

### Hot Reloading

The server automatically detects changes to `responses.yml` and reloads the configuration without requiring a restart.

## Development

The project uses Poetry for dependency management and includes a Makefile to help with common development tasks:

```bash
# Set up development environment
make setup

# Run all checks (setup, lint, test)
make all

# Run tests
make test

# Format code
make format

# Run all linting and type checking
make lint

# Clean up build artifacts
make clean

# See all available commands
make help
```

### Development Commands

- `make setup`: Install all development dependencies with Poetry
- `make test`: Run the test suite
- `make format`: Format code with black and isort
- `make lint`: Run all code quality checks (format, lint, type)
- `make build`: Build the package with Poetry
- `make clean`: Remove build artifacts and cache files
- `make install-dev`: Install package with development dependencies

For more details on available commands, run `make help`.

## Error Handling

The server includes comprehensive error handling:

- Invalid requests return 400 status codes with descriptive messages
- Server errors return 500 status codes with error details
- All errors are logged using JSON format

## Logging

The server uses JSON-formatted logging for:

- Incoming request details
- Response configuration loading
- Error messages and stack traces

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.
