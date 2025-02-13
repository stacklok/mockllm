import time
import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message model."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat completion request model."""
    model: str
    messages: List[Message]
    temperature: Optional[float] = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=150)
    stream: Optional[bool] = Field(default=False)

class DeltaMessage(BaseModel):
    """Streaming delta message model."""
    role: Optional[str] = None
    content: Optional[str] = None

class StreamChoice(BaseModel):
    """Streaming choice model."""
    delta: DeltaMessage
    index: int = 0
    finish_reason: Optional[str] = None

class ChatChoice(BaseModel):
    """Regular chat choice model."""
    message: Message
    index: int = 0
    finish_reason: str = "stop"

class ChatResponse(BaseModel):
    """Chat completion response model."""
    id: str = Field(default_factory=lambda: f"mock-{uuid.uuid4()}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Dict]
    usage: Dict[str, int]

class StreamResponse(BaseModel):
    """Streaming response model."""
    id: str = Field(default_factory=lambda: f"mock-{uuid.uuid4()}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[StreamChoice]