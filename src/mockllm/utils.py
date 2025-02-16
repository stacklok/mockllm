import tiktoken

def count_tokens(text: str, model: str) -> int:
    """Get realistic token count for text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if model not supported
        return len(text.split()) 