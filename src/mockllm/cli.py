from pathlib import Path

import click
import uvicorn
import yaml

from . import __version__
from .config import ResponseConfig


def validate_responses_file(ctx, param, value):
    """Validate the responses YAML file."""
    if not value:
        return None
    try:
        path = Path(value)
        if not path.exists():
            raise click.BadParameter(f"File {value} does not exist")
        with open(path) as f:
            data = yaml.safe_load(f)
            # Validate structure
            if not isinstance(data, dict):
                raise click.BadParameter("YAML file must contain a dictionary")
            if "responses" not in data:
                raise click.BadParameter("YAML file must contain 'responses' key")
            if not isinstance(data["responses"], dict):
                raise click.BadParameter("'responses' must be a dictionary")
        return value
    except yaml.YAMLError as e:
        raise click.BadParameter(f"Invalid YAML file: {e}")  # noqa: B904


@click.group()
@click.version_option(version=__version__)
def cli():
    """MockLLM - A mock server that mimics OpenAI and Anthropic API formats."""
    pass


@cli.command()
@click.option(
    "--responses",
    "-r",
    type=str,
    callback=validate_responses_file,
    help="Path to responses YAML file",
    default="responses.yml",
)
@click.option("--host", "-h", type=str, help="Host to bind to", default="0.0.0.0")
@click.option("--port", "-p", type=int, help="Port to bind to", default=8000)
@click.option(
    "--reload", is_flag=True, help="Enable auto-reload on file changes", default=True
)
def start(responses, host, port, reload):
    """Start the MockLLM server."""
    if responses:
        click.echo(f"Using responses file: {responses}")

    # Set the responses file path in the environment
    import os

    os.environ["MOCKLLM_RESPONSES_FILE"] = responses

    click.echo(f"Starting server on {host}:{port}")
    uvicorn.run("mockllm.server:app", host=host, port=port, reload=reload)


@cli.command()
@click.argument("responses_file", type=click.Path(exists=True))
def validate(responses_file):
    """Validate a responses YAML file."""
    try:
        config = ResponseConfig(responses_file)
        config.load_responses()
        click.echo(click.style("✓ Valid responses file", fg="green"))
        click.echo(f"Found {len(config.responses)} responses")
    except Exception as e:
        click.echo(click.style("✗ Invalid responses file", fg="red"))
        click.echo(str(e))
        exit(1)


def main():
    """Entry point for the CLI."""
    cli()
