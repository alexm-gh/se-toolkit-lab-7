"""Handler for plain text messages."""


async def handle_message(text: str) -> str:
    """Handle plain text messages (for Task 3 - LLM routing)."""
    return f"I received your message: {text} (placeholder)"
