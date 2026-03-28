FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Sync dependencies (frozen to use exact versions from lock file)
RUN uv sync --frozen

# Copy the rest of the bot code
COPY . .

# Run the bot
CMD ["uv", "run", "bot.py"]
