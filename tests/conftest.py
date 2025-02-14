import pytest
from unittest.mock import MagicMock

from mockllm.config import ResponseConfig
from mockllm import server

@pytest.fixture(autouse=True)
def mock_response_config(monkeypatch):
    """Mock ResponseConfig to avoid file system dependencies in tests."""
    mock_config = MagicMock(spec=ResponseConfig)
    
    # Set up mock responses
    mock_config.get_response.return_value = "This is a mock response"
    mock_config.get_streaming_response.return_value = iter("This is a mock response")
    mock_config.responses = {
        "test message": "This is a mock response"
    }
    mock_config.default_response = "This is a default mock response"
    
    # Replace the module-level response_config with our mock
    monkeypatch.setattr(server, "response_config", mock_config)
    
    return mock_config