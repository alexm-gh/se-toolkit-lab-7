"""Handler for /start command."""

# Inline keyboard buttons for common actions
# Format: list of lists of tuples (label, callback_data)
START_KEYBOARD = [
    [("📚 Available Labs", "/labs"), ("📊 My Scores", "/scores")],
    [("❤️ Health Check", "/health"), ("❓ Help", "/help")],
]


async def handle_start() -> str:
    """Handle /start command."""
    return """Welcome to LMS Bot! 🎓

I can help you explore labs, check scores, and answer questions about your progress.

Try these commands:
- /labs — List available labs
- /scores <lab> — Get scores for a lab
- /health — Check backend status
- /help — Show all commands

Or just ask me a question like:
"What labs are available?"
"Show me scores for lab 4"
"Which lab has the lowest pass rate?"
"""
