from typing import Any, AsyncGenerator, Dict, Union

from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse

from ..config import ResponseConfig
from ..models import (
    OpenAIChatRequest,
    OpenAIChatResponse,
    OpenAIDeltaMessage,
    OpenAIStreamChoice,
    OpenAIStreamResponse,
)
from ..utils import count_tokens
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, response_config: ResponseConfig):
        self.response_config = response_config

    def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        first_chunk = OpenAIStreamResponse(
            model=model,
            choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(role="assistant"))],
        )
        yield f"data: {first_chunk.model_dump_json()}\n\n"

        for chunk in self.response_config.get_streaming_response_with_lag(
            content
        ):
            chunk_response = OpenAIStreamResponse(
                model=model,
                choices=[OpenAIStreamChoice(delta=OpenAIDeltaMessage(content=chunk))],
            )
            yield f"data: {chunk_response.model_dump_json()}\n\n"

        final_chunk = OpenAIStreamResponse(
            model=model,
            choices=[
                OpenAIStreamChoice(delta=OpenAIDeltaMessage(), finish_reason="stop")
            ],
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    async def handle_chat_completion(
        self, request: OpenAIChatRequest
    ) -> Union[Response, Dict[Any, Any]]:
        last_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"), None
        )

        if not last_message:
            raise HTTPException(
                status_code=400, detail="No user message found in request"
            )

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
        ).model_dump()
