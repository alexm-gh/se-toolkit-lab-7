"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              — Start Telegram bot
    uv run bot.py --test "/command" — Test command without Telegram
"""

import argparse
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_message,
    handle_scores,
    handle_start,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_command(command: str) -> str:
    """Run a command and return the result."""
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

    return response


async def cmd_start(message: types.Message) -> None:
    """Handle /start command."""
    response = await handle_start()
    await message.answer(response)


async def cmd_help(message: types.Message) -> None:
    """Handle /help command."""
    response = await handle_help()
    await message.answer(response)


async def cmd_health(message: types.Message) -> None:
    """Handle /health command."""
    response = await handle_health()
    await message.answer(response)


async def cmd_labs(message: types.Message) -> None:
    """Handle /labs command."""
    response = await handle_labs()
    await message.answer(response)


async def cmd_scores(message: types.Message) -> None:
    """Handle /scores command."""
    args = message.text.split(maxsplit=1)
    lab_name = args[1] if len(args) > 1 else ""
    response = await handle_scores(lab_name)
    await message.answer(response)


async def handle_text(message: types.Message) -> None:
    """Handle plain text messages."""
    response = await handle_message(message.text)
    await message.answer(response)


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
        result = asyncio.run(run_command(args.test))
        print(result)
        sys.exit(0)
    else:
        # Telegram mode: start the bot
        if not settings.bot_token:
            logger.error("BOT_TOKEN not set. Please set BOT_TOKEN in .env.bot.secret")
            logger.info("Starting in test mode only. Use --test to test commands.")
            # Keep running for container health
            asyncio.run(run_forever_without_token())
            return
        
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher()

        # Register handlers
        dp.message.register(cmd_start, CommandStart())
        dp.message.register(cmd_help, Command("help"))
        dp.message.register(cmd_health, Command("health"))
        dp.message.register(cmd_labs, Command("labs"))
        dp.message.register(cmd_scores, Command("scores"))
        dp.message.register(handle_text)

        logger.info("Starting Telegram bot...")
        dp.run_polling(bot)


async def run_forever_without_token() -> None:
    """Keep the container running even without BOT_TOKEN."""
    logger.info("Container running in health-check mode (no BOT_TOKEN)")
    logger.info("Set BOT_TOKEN in .env.bot.secret to enable Telegram")
    # Sleep forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    main()
