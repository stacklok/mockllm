from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Union

from fastapi import Response


class LLMProvider(ABC):
    @abstractmethod
    async def handle_chat_completion(
        self, request: Any
    ) -> Union[Response, Dict[Any, Any]]:
        pass

    @abstractmethod
    def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Note: Removed async from method signature since AsyncGenerator is already async"""
        yield ""  # pragma: no cover
