import uvicorn


def main() -> None:
    """Run the mock LLM server."""
    uvicorn.run("mockllm.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
