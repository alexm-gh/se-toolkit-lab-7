"""Handler for plain text messages."""

from services.intent_router import route_message


async def handle_message(text: str) -> str:
    """Handle plain text messages using LLM intent routing."""
    try:
        response = await route_message(text)
        return response
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"LLM service error: connection refused. Check that the LLM is running."
        elif "401" in error_msg or "unauthorized" in error_msg:
            return f"LLM service error: HTTP 401 Unauthorized. Token may have expired."
        elif "502" in error_msg or "bad gateway" in error_msg:
            return f"LLM service error: HTTP 502 Bad Gateway. The service may be down."
        else:
            return f"LLM error: {e}"
