from pathlib import Path

import pytest

from mockllm import server
from mockllm.config import ResponseConfig

MOCK_YAML_CONTENT = """
responses:
  default: "Hello, this is a mock response."
"""


@pytest.fixture(autouse=True)
def mock_responses():
    # Override the default responses path for testing
    ResponseConfig.DEFAULT_RESPONSES_PATH = "tests/test_responses.yml"
    return ResponseConfig()


@pytest.fixture(autouse=True)
def test_response_config(monkeypatch):
    """Use a test-specific responses.yml file."""
    test_dir = Path(__file__).parent
    test_responses_path = test_dir / "tests/responses.yml"

    # Ensure the test responses.yml file exists
    if not test_responses_path.exists():
        test_responses_path.write_text(MOCK_YAML_CONTENT)

    # Create a ResponseConfig instance with our test file
    test_config = ResponseConfig(yaml_path=str(test_responses_path))

    # Replace the module-level response_config with our test instance
    monkeypatch.setattr(server, "response_config", test_config)

    return test_config
