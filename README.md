# Mock LLM Server

A FastAPI-based mock LLM server that mimics OpenAI's API format. Instead of calling an actual language model, it uses predefined responses from a YAML configuration file. Made for when you want a deterministic response for testing or development purposes.

I wrote this for the CodeGate project, to mock out certain responses to develop, test and validate certain features. Check it out [here](https://github.com/stacklok/codegate).

## Features

- OpenAI-compatible API endpoint
- Streaming support (character-by-character response streaming)
- Configurable responses via YAML file
- Hot-reloading of response configurations
- JSON logging
- Error handling
- Mock token counting


## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mockllm.git
cd mockllm
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn src.mockllm.server:app --reload
```

The server will start on `http://localhost:8000`

2. Send requests to the API endpoint:

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

## Configuration

### Response Configuration

Responses are configured in `responses.yml`. The file has two main sections:

1. `responses`: Maps input prompts to predefined responses
2. `defaults`: Contains default configurations like the unknown response message

Example `responses.yml`:
```yaml
responses:
  "what colour is the sky?": "The sky is blue during a clear day due to a phenomenon called Rayleigh scattering."
  "who is the president?": "This is a mock response. In a production environment, this would be replaced with accurate, up-to-date information."

defaults:
  unknown_response: "I don't know the answer to that. This is a mock response."
```

### Hot Reloading

The server automatically detects changes to `responses.yml` and reloads the configuration without requiring a restart. This makes it easy to add or modify responses while the server is running.

## API Format

### Request Format

```json
{
  "model": "mock-llm",
  "messages": [
    {"role": "user", "content": "what colour is the sky?"}
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false
}
```

### Response Format

Regular response:
```json
{
  "id": "mock-123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "mock-llm",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The sky is blue during a clear day due to a phenomenon called Rayleigh scattering."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

Streaming response (Server-Sent Events format):
```
data: {"id":"mock-123","object":"chat.completion.chunk","created":1700000000,"model":"mock-llm","choices":[{"delta":{"role":"assistant"},"index":0}]}

data: {"id":"mock-124","object":"chat.completion.chunk","created":1700000000,"model":"mock-llm","choices":[{"delta":{"content":"T"},"index":0}]}

data: {"id":"mock-125","object":"chat.completion.chunk","created":1700000000,"model":"mock-llm","choices":[{"delta":{"content":"h"},"index":0}]}

... (character by character)

data: {"id":"mock-999","object":"chat.completion.chunk","created":1700000000,"model":"mock-llm","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}

data: [DONE]
```

## Error Handling

The server includes comprehensive error handling:

- Invalid requests return 400 status codes with descriptive messages
- Server errors return 500 status codes with error details
- All errors are logged using JSON format

## Logging

The server uses JSON-formatted logging

- Incoming request details
- Response configuration loading
- Error messages and stack traces
