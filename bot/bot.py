"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              — Start Telegram bot
    uv run bot.py --test "/command" — Test command without Telegram
"""

import argparse
import asyncio
import sys

from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_message,
    handle_scores,
    handle_start,
)


async def run_command(command: str) -> None:
    """Run a command and print the result to stdout."""
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Route to appropriate handler
    if cmd == "/start":
        response = await handle_start()
    elif cmd == "/help":
        response = await handle_help()
    elif cmd == "/health":
        response = await handle_health()
    elif cmd == "/labs":
        response = await handle_labs()
    elif cmd == "/scores":
        response = await handle_scores(args.strip())
    else:
        # Treat as plain text message
        response = await handle_message(command)

    print(response)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        metavar="TEXT",
        help="Test mode: run a command and print response to stdout",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: run command and exit
        asyncio.run(run_command(args.test))
        sys.exit(0)
    else:
        # Telegram mode: start the bot
        print("Telegram bot mode not implemented yet — Task 2")
        print("For now, use --test mode to verify handlers")


if __name__ == "__main__":
    main()
