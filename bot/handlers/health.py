"""Handler for /health command."""

from services.lms_client import lms_client


async def handle_health() -> str:
    """Handle /health command by checking backend status."""
    try:
        result = await lms_client.health_check()
        return f"Backend is healthy. {result['items_count']} items available."
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "502" in error_msg or "bad gateway" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "401" in error_msg or "unauthorized" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY configuration."
        elif "404" in error_msg or "not found" in error_msg:
            return f"Backend error: HTTP 404 Not Found. The endpoint may not exist."
        else:
            return f"Backend error: {e}"
