import logging
from pathlib import Path
from typing import Dict, Optional

import yaml
from fastapi import HTTPException
from pythonjsonlogger import jsonlogger

log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler])
logger = logging.getLogger(__name__)

class ResponseConfig:
    """Handles loading and managing response configurations from YAML."""

    def __init__(self, yaml_path: str = "responses.yml"):
        self.yaml_path = yaml_path
        self.last_modified = 0
        self.responses: Dict[str, str] = {}
        self.default_response = "I don't know the answer to that."
        self.load_responses()

    def load_responses(self) -> None:
        """Load or reload responses from YAML file if modified."""
        try:
            current_mtime = Path(self.yaml_path).stat().st_mtime
            if current_mtime > self.last_modified:
                with open(self.yaml_path, 'r') as f:
                    data = yaml.safe_load(f)
                    self.responses = data.get('responses', {})
                    self.default_response = data.get('defaults', {}).get(
                        'unknown_response', self.default_response
                    )
                self.last_modified = current_mtime
                logger.info(f"Loaded {len(self.responses)} responses from {self.yaml_path}")
        except Exception as e:
            logger.error(f"Error loading responses: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to load response configuration"
            )

    def get_response(self, prompt: str) -> str:
        """Get response for a given prompt."""
        self.load_responses()  # Check for updates
        return self.responses.get(prompt.lower().strip(), self.default_response)

    def get_streaming_response(self, prompt: str, chunk_size: Optional[int] = None) -> str:
        """Generator that yields response content character by character or in chunks."""
        response = self.get_response(prompt)
        if chunk_size:
            # Yield response in chunks
            for i in range(0, len(response), chunk_size):
                yield response[i:i + chunk_size]
        else:
            # Yield response character by character
            for char in response:
                yield char