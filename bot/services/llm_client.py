"""LLM client for intent routing."""

import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with the LLM API."""

    def __init__(self) -> None:
        self.base_url = settings.llm_api_base_url or "http://10.93.24.208:42005/v1"
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model or "coder-model"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        system_prompt: str | None = None,
    ) -> dict:
        """Send a chat request to the LLM with optional tool definitions."""
        # Build messages with system prompt
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": all_messages,
        }
        if tools:
            payload["tools"] = tools

        # Build URL - avoid double /v1 if base_url already contains it
        if self.base_url.endswith("/v1"):
            url = f"{self.base_url}/chat/completions"
        else:
            url = f"{self.base_url}/v1/chat/completions"

        # Disable SSL verification for HTTP (localhost) connections
        # For HTTPS, keep verification enabled
        verify_ssl = self.base_url.startswith("https")

        logger.debug(f"LLM request: POST {url}")
        logger.debug(f"Headers: {self.headers}")
        logger.debug(f"Payload: {payload}")

        try:
            async with httpx.AsyncClient(verify=verify_ssl) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                logger.debug(f"LLM response status: {response.status_code}")
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            logger.error(f"LLM connection error: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM HTTP error: {e.response.status_code} - {e.response.text}")
            raise

    def get_tool_definitions(self) -> list[dict]:
        """Return tool definitions for all backend endpoints."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get list of all labs and tasks. Use this to discover what labs are available.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get list of enrolled students and their groups.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average pass rates and attempt counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submissions per day for a specific lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group scores and student counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a specific lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                            "limit": {"type": "integer", "description": "Number of top learners to return, e.g. 5"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a specific lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL sync to refresh data from autochecker.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]


llm_client = LLMClient()
