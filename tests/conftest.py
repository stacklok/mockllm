from pathlib import Path

import pytest

from mockllm import server
from mockllm.config import ResponseConfig


@pytest.fixture(autouse=True)
def test_response_config(monkeypatch):
    """Use a test-specific responses.yml file."""
    # Get the path to responses.yml in the tests directory
    test_dir = Path(__file__).parent
    test_responses_path = test_dir / "responses.yml"

    # Create a ResponseConfig instance with our test file
    test_config = ResponseConfig(yaml_path=str(test_responses_path))

    # Replace the module-level response_config with our test instance
    monkeypatch.setattr(server, "response_config", test_config)

    return test_config
