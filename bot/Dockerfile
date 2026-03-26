FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY . .

# Sync dependencies
RUN uv sync --frozen

# Run the bot
CMD ["uv", "run", "bot.py"]
