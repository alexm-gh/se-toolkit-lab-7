"""Handler for /labs command."""

from services.lms_client import lms_client


async def handle_labs() -> str:
    """Handle /labs command by fetching labs from backend."""
    try:
        labs = await lms_client.get_labs()
        if not labs:
            return "No labs available. The backend may be empty or not synced."
        
        result = "Available labs:\n"
        for lab in labs:
            lab_name = lab.get("name", lab.get("id", "Unknown"))
            result += f"- {lab_name}\n"
        return result.strip()
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "502" in error_msg or "bad gateway" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "401" in error_msg or "unauthorized" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY configuration."
        else:
            return f"Backend error: {e}"
