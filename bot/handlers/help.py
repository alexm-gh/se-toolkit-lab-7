"""Handler for /help command."""


async def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start — Welcome message
/help — This help message
/health — Check backend status
/labs — List available labs
/scores <lab> — Get scores for a lab"""
