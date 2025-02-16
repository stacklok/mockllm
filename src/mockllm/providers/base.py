from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Union

from fastapi.responses import StreamingResponse


class LLMProvider(ABC):
    @abstractmethod
    async def handle_chat_completion(
        self, request: Any
    ) -> Union[Dict[str, Any], StreamingResponse]:
        pass

    @abstractmethod
    async def generate_stream_response(
        self, content: str, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        yield ""  # pragma: no cover
