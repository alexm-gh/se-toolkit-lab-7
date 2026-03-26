# LMS Telegram Bot — Development Plan

## Overview

This document describes the development plan for building a Telegram bot that integrates with the LMS backend. The bot allows users to check system health, browse labs and scores, and ask questions in plain language using an LLM for intent routing.

## Architecture

The bot follows a layered architecture:

1. **Entry point** (`bot.py`) — Handles Telegram startup and `--test` mode
2. **Handlers** (`handlers/`) — Command logic as plain functions, no Telegram dependency
3. **Services** (`services/`) — API client for LMS backend, LLM client for intent routing
4. **Configuration** (`config.py`) — Environment variable loading from `.env.bot.secret`

The key design principle is **separation of concerns**: handlers don't know about Telegram, making them testable via `--test` mode and reusable in unit tests.

## Task 1: Plan and Scaffold (Current)

**Goal:** Create project structure and testable handler architecture.

**Deliverables:**
- `bot/bot.py` with `--test` mode
- `bot/handlers/` with placeholder handlers
- `bot/config.py` for environment loading
- `bot/PLAN.md` (this file)
- `bot/pyproject.toml` with dependencies

**Testing:** Run `uv run bot.py --test "/command"` to verify handlers work without Telegram.

## Task 2: Backend Integration

**Goal:** Connect handlers to the real LMS backend API.

**Approach:**
1. Create `bot/services/lms_client.py` — HTTP client for backend API
2. Implement Bearer token authentication using `LMS_API_KEY`
3. Update handlers to call real endpoints:
   - `/health` → `GET /health`
   - `/labs` → `GET /items?category=lab`
   - `/scores <lab>` → `GET /analytics?lab=<lab>`
4. Add error handling for backend downtime

**Testing:** Verify each command returns real data from the backend.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Enable plain text queries interpreted by LLM.

**Approach:**
1. Create `bot/services/llm_client.py` — LLM API client
2. Define tool descriptions for each backend endpoint
3. Implement intent router:
   - User sends plain text → LLM decides which tool to call
   - LLM returns tool name + arguments → Call appropriate handler
4. Add inline keyboard buttons for common actions

**Key insight:** The LLM reads tool descriptions to decide which to call. Description quality matters more than prompt engineering.

**Testing:** Send plain text like "what labs are available" and verify correct response.

## Task 4: Containerize and Document

**Goal:** Deploy the bot alongside the existing backend.

**Approach:**
1. Create `bot/Dockerfile` — Multi-stage build for the bot
2. Update `docker-compose.yml` — Add bot service
3. Configure container networking — Use service names, not `localhost`
4. Document deployment in README

**Deployment:** Bot runs as a systemd service on the VM, managed by docker-compose.

## Environment Variables

Required in `.env.bot.secret`:

- `BOT_TOKEN` — Telegram bot token
- `LMS_API_BASE_URL` — Backend API URL
- `LMS_API_KEY` — Backend API key for Bearer auth
- `LLM_API_KEY` — LLM API key for intent routing

## Git Workflow

For each task:
1. Create issue describing the work
2. Create branch: `task-N-short-description`
3. Implement, test with `--test` mode
4. Create PR with "Closes #..." in description
5. Partner review, then merge to `main`
6. Pull on VM and deploy

## Success Criteria

By the end of this lab:
1. Bot responds to all slash commands in Telegram
2. Bot understands plain text queries via LLM
3. Bot handles backend errors gracefully
4. Bot is containerized and deployed on the VM
5. Documentation explains how to run and modify the bot
