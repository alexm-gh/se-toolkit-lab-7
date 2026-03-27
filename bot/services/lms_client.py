"""LMS API client for the Telegram bot."""

import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)


class LMSClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self) -> None:
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def get(self, endpoint: str, params: dict | None = None) -> dict | list:
        """Make a GET request to the LMS API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"LMS GET: {url} params={params}")
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers, params=params)
            logger.debug(f"LMS response: {response.status_code}")
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict | None = None) -> dict:
        """Make a POST request to the LMS API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"LMS POST: {url} data={data}")
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=self.headers, json=data or {})
            logger.debug(f"LMS response: {response.status_code}")
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> dict:
        """Check if backend is healthy by fetching items."""
        items = await self.get("/items/")
        return {"healthy": True, "items_count": len(items) if isinstance(items, list) else 0}

    async def get_labs(self) -> list:
        """Get list of labs."""
        items = await self.get("/items/")
        if isinstance(items, list):
            return [item for item in items if item.get("type") == "lab"]
        return []

    async def get_pass_rates(self, lab: str) -> dict:
        """Get pass rates for a specific lab."""
        return await self.get("/analytics/pass-rates", params={"lab": lab})


lms_client = LMSClient()
