import asyncio
import logging
import os
import random
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, Optional

import yaml
from fastapi import HTTPException
from pythonjsonlogger import jsonlogger

log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
logger = logging.getLogger(__name__)


class ResponseConfig:
    """Handles loading and managing response configurations from YAML."""

    def __init__(self, yaml_path: str = None):
        self.yaml_path = yaml_path or os.getenv(
            "MOCKLLM_RESPONSES_FILE", "responses.yml"
        )
        self.last_modified = 0
        self.responses: Dict[str, str] = {}
        self.default_response = "I don't know the answer to that."
        self.lag_enabled = False
        self.lag_factor = 10
        self.load_responses()

    def load_responses(self) -> None:
        """Load or reload responses from YAML file if modified."""
        try:
            current_mtime = Path(self.yaml_path).stat().st_mtime
            if current_mtime > self.last_modified:
                with open(self.yaml_path, "r") as f:
                    data = yaml.safe_load(f)
                    self.responses = data.get("responses", {})
                    self.default_response = data.get("defaults", {}).get(
                        "unknown_response", self.default_response
                    )
                    settings = data.get("settings", {})
                    self.lag_enabled = settings.get("lag_enabled", False)
                    self.lag_factor = settings.get("lag_factor", 10)
                self.last_modified = int(current_mtime)
                logger.info(
                    f"Loaded {len(self.responses)} responses from {self.yaml_path}"
                )
        except Exception as e:
            logger.error(f"Error loading responses: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to load response configuration"
            ) from e

    def get_response(self, prompt: str) -> str:
        """Get response for a given prompt."""
        self.load_responses()  # Check for updates
        return self.responses.get(prompt, self.default_response)

    def get_streaming_response(
        self, prompt: str, chunk_size: Optional[int] = None
    ) -> Generator[str, None, None]:
        """Generator that yields response content
        character by character or in chunks."""
        response = self.get_response(prompt)
        if chunk_size:
            # Yield response in chunks
            for i in range(0, len(response), chunk_size):
                yield response[i : i + chunk_size]
        else:
            # Yield response character by character
            for char in response:
                yield char

    async def get_response_with_lag(self, prompt: str) -> str:
        """Get response with artificial lag for non-streaming responses."""
        response = self.get_response(prompt)
        if self.lag_enabled:
            # Base delay on response length and lag factor
            delay = len(response) / (self.lag_factor * 10)
            await asyncio.sleep(delay)
        return response

    async def get_streaming_response_with_lag(
        self, prompt: str, chunk_size: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Generator that yields response content with artificial lag."""
        response = self.get_response(prompt)

        if chunk_size:
            for i in range(0, len(response), chunk_size):
                chunk = response[i : i + chunk_size]
                if self.lag_enabled:
                    delay = len(chunk) / (self.lag_factor * 10)
                    await asyncio.sleep(delay)
                yield chunk
        else:
            for char in response:
                if self.lag_enabled:
                    # Add random variation to character delay
                    base_delay = 1 / (self.lag_factor * 10)
                    variation = random.uniform(-0.5, 0.5) * base_delay
                    delay = max(0, base_delay + variation)
                    await asyncio.sleep(delay)
                yield char
