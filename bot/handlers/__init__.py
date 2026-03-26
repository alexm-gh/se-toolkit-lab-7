"""Command handlers for the LMS Telegram bot.

Handlers are plain functions that take input and return text.
They don't depend on Telegram — same logic works from --test mode,
unit tests, or Telegram.
"""


async def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start — Welcome message
/help — This help message
/health — Check backend status
/labs — List available labs
/scores <lab> — Get scores for a lab"""


async def handle_health() -> str:
    """Handle /health command."""
    # TODO: Call backend API in Task 2
    return "Backend status: OK (placeholder)"


async def handle_labs() -> str:
    """Handle /labs command."""
    # TODO: Call backend API in Task 2
    return "Available labs: lab-01, lab-02, lab-03 (placeholder)"


async def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command."""
    # TODO: Call backend API in Task 2
    if not lab_name:
        return "Please specify a lab name, e.g., /scores lab-01"
    return f"Scores for {lab_name}: Task 1: 80%, Task 2: 75% (placeholder)"


async def handle_message(text: str) -> str:
    """Handle plain text messages (for Task 3 - LLM routing)."""
    # TODO: Implement LLM intent routing in Task 3
    return f"I received your message: {text} (placeholder)"
