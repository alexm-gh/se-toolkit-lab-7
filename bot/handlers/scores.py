"""Handler for /scores command."""

from services.lms_client import lms_client


async def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command by fetching pass rates from backend."""
    if not lab_name:
        return "Please specify a lab name, e.g., /scores lab-01"
    
    try:
        data = await lms_client.get_pass_rates(lab_name)
        if not data:
            return f"No scores found for {lab_name}. The lab may not exist or has no submissions."
        
        result = f"Pass rates for {lab_name}:\n"
        
        # Handle different response formats
        if isinstance(data, dict):
            # Format: {"task_name": percentage, ...} or {"scores": [...]}
            if "scores" in data and isinstance(data["scores"], list):
                for item in data["scores"]:
                    task_name = item.get("task", item.get("name", "Unknown"))
                    rate = item.get("rate", item.get("percentage", item.get("pass_rate", 0)))
                    attempts = item.get("attempts", "")
                    attempts_str = f" ({attempts} attempts)" if attempts else ""
                    result += f"- {task_name}: {rate:.1f}%{attempts_str}\n"
            else:
                # Direct dict: {task_name: percentage}
                for task_name, rate in data.items():
                    if isinstance(rate, (int, float)):
                        result += f"- {task_name}: {rate:.1f}%\n"
        
        elif isinstance(data, list):
            # Format: [{"task": "...", "rate": ...}, ...]
            for item in data:
                task_name = item.get("task", item.get("name", "Unknown"))
                rate = item.get("rate", item.get("percentage", item.get("pass_rate", 0)))
                attempts = item.get("attempts", "")
                attempts_str = f" ({attempts} attempts)" if attempts else ""
                result += f"- {task_name}: {rate:.1f}%{attempts_str}\n"
        
        return result.strip()
    
    except Exception as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg or "connect" in error_msg:
            return f"Backend error: connection refused. Check that the services are running."
        elif "502" in error_msg or "bad gateway" in error_msg:
            return f"Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "401" in error_msg or "unauthorized" in error_msg:
            return f"Backend error: HTTP 401 Unauthorized. Check LMS_API_KEY configuration."
        elif "404" in error_msg or "not found" in error_msg:
            return f"Backend error: HTTP 404 Not Found. Lab '{lab_name}' may not exist."
        else:
            return f"Backend error: {e}"
