from typing import AsyncGenerator, Union
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ..config import ResponseConfig
from ..models import (
    AnthropicChatRequest,
    AnthropicChatResponse,
    AnthropicStreamResponse,
    AnthropicStreamDelta,
)
from .base import LLMProvider
from ..utils import count_tokens

class AnthropicProvider(LLMProvider):
    def __init__(self, response_config: ResponseConfig):
        self.response_config = response_config

    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.response_config.get_streaming_response_with_lag(content):
            stream_response = AnthropicStreamResponse(
                delta=AnthropicStreamDelta(delta={"text": chunk})
            )
            yield f"data: {stream_response.model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    async def handle_chat_completion(
        self, request: AnthropicChatRequest
    ) -> Union[AnthropicChatResponse, StreamingResponse]:
        last_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"), None
        )

        if not last_message:
            raise HTTPException(status_code=400, detail="No user message found in request")

        if request.stream:
            return StreamingResponse(
                self.generate_stream_response(last_message.content, request.model),
                media_type="text/event-stream",
            )

        response_content = await self.response_config.get_response_with_lag(
            last_message.content
        )

        prompt_tokens = count_tokens(str(request.messages), request.model)
        completion_tokens = count_tokens(response_content, request.model)
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