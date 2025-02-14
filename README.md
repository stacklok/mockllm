# Mock LLM Server

A FastAPI-based mock LLM server that mimics OpenAI and Anthropic API formats. Instead of calling actual language models,
it uses predefined responses from a YAML configuration file. 

This is made for when you want a deterministic response for testing or development purposes.

Check out the [CodeGate](https://github.com/stacklok/codegate) when you're done here!.

## Features

- OpenAI and Anthropic compatible API endpoints
- Streaming support (character-by-character response streaming)
- Configurable responses via YAML file
- Hot-reloading of response configurations
- JSON logging
- Error handling
- Mock token counting


## Installation

1. Clone the repository:
```bash
git clone https://github.com/lukehinds/mockllm.git
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

1. Set up the responses.yml

```bash
cp example.responses.yml responses.yml
```

2. Start the server:
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn src.mockllm.server:app --reload
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

## API Format

### OpenAI Format

#### Request Format

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

#### Response Format

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

### Anthropic Format

#### Request Format

```json
{
  "model": "claude-3-sonnet-20240229",
  "messages": [
    {"role": "user", "content": "what colour is the sky?"}
  ],
  "max_tokens": 1024,
  "stream": false
}
```

#### Response Format

Regular response:
```json
{
  "id": "mock-123",
  "type": "message",
  "role": "assistant",
  "model": "claude-3-sonnet-20240229",
  "content": [
    {
      "type": "text",
      "text": "The sky is blue during a clear day due to a phenomenon called Rayleigh scattering."
    }
  ],
  "usage": {
    "input_tokens": 10,
    "output_tokens": 5,
    "total_tokens": 15
  }
}
```

Streaming response (Server-Sent Events format):
```
data: {"type":"message_delta","id":"mock-123","delta":{"type":"content_block_delta","index":0,"delta":{"text":"T"}}}

data: {"type":"message_delta","id":"mock-123","delta":{"type":"content_block_delta","index":0,"delta":{"text":"h"}}}

... (character by character)

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
