from abc import ABC, abstractmethod
from typing import AsyncGenerator, Union
from fastapi import Response

class LLMProvider(ABC):
    @abstractmethod
    async def handle_chat_completion(self, request) -> Union[Response, dict]:
        pass

    @abstractmethod
    async def generate_stream_response(self, content: str, model: str) -> AsyncGenerator[str, None]:
        pass 