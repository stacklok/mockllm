import logging
from typing import AsyncGenerator, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pythonjsonlogger import jsonlogger

from .config import ResponseConfig
from .models import (
    AnthropicChatRequest,
    AnthropicChatResponse,
    AnthropicStreamDelta,
    AnthropicStreamResponse,
    OpenAIChatRequest,
    OpenAIChatResponse,
    OpenAIDeltaMessage,
    OpenAIStreamChoice,
    OpenAIStreamResponse,
)

log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock LLM Server")

response_config = ResponseConfig()


async def openai_stream_response(content: str, model: str) -> AsyncGenerator[str, None]:
    """Generate OpenAI-style streaming response in SSE format."""
    # Send the first message with role
    first_chunk = OpenAIStreamResponse(
        model=model,
        choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(role="assistant"))],
    )
    yield f"data: {first_chunk.model_dump_json()}\n\n"

    # Stream the content character by character
    for chunk in response_config.get_streaming_response(content):
        chunk_response = OpenAIStreamResponse(
            model=model,
            choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(content=chunk))],
        )
        yield f"data: {chunk_response.model_dump_json()}\n\n"

    # Send the final message
    final_chunk = OpenAIStreamResponse(
        model=model,
        choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(), finish_reason="stop")],
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


async def anthropic_stream_response(
    content: str, model: str
) -> AsyncGenerator[str, None]:
    """Generate Anthropic-style streaming response in SSE format."""
    for chunk in response_config.get_streaming_response(content):
        stream_response = AnthropicStreamResponse(
            delta=AnthropicStreamDelta(delta={"text": chunk})
        )
        yield f"data: {stream_response.model_dump_json()}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions", response_model=None)
async def openai_chat_completion(
    request: OpenAIChatRequest,
) -> Union[OpenAIChatResponse, StreamingResponse]:
    """Handle chat completion requests, supporting both regular and streaming responses."""
    try:
        logger.info(
            "Received chat completion request",
            extra={
                "model": request.model,
                "message_count": len(request.messages),
                "stream": request.stream,
            },
        )

        last_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"), None
        )

        if not last_message:
            raise HTTPException(
                status_code=400, detail="No user message found in request"
            )

        if request.stream:
            return StreamingResponse(
                openai_stream_response(last_message.content, request.model),
                media_type="text/event-stream",
            )

        response_content = response_config.get_response(last_message.content)

        # Calculate mock token counts
        prompt_tokens = len(str(request.messages).split())
        completion_tokens = len(response_content.split())
        total_tokens = prompt_tokens + completion_tokens

        return OpenAIChatResponse(
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_content},
                    "finish_reason": "stop",
                }
            ],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/v1/messages", response_model=None)
async def anthropic_chat_completion(
    request: AnthropicChatRequest,
) -> Union[AnthropicChatResponse, StreamingResponse]:
    """Handle Anthropic chat completion requests, supporting both regular and streaming responses."""
    try:
        logger.info(
            "Received Anthropic chat completion request",
            extra={
                "model": request.model,
                "message_count": len(request.messages),
                "stream": request.stream,
            },
        )

        last_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"), None
        )

        if not last_message:
            raise HTTPException(
                status_code=400, detail="No user message found in request"
            )

        if request.stream:
            return StreamingResponse(
                anthropic_stream_response(last_message.content, request.model),
                media_type="text/event-stream",
            )

        response_content = response_config.get_response(last_message.content)

        # Calculate mock token counts
        prompt_tokens = len(str(request.messages).split())
        completion_tokens = len(response_content.split())
        total_tokens = prompt_tokens + completion_tokens

        return AnthropicChatResponse(
            model=request.model,
            content=[{"type": "text", "text": response_content}],
            usage={
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
