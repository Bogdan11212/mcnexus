import aiohttp
from typing import Dict, Any, Optional
import json

from mcnexus.pterodactyl.exceptions import (
    PterodactylError,
    PterodactylAuthError,
    PterodactylNotFoundError,
    PterodactylRateLimitError,
    PterodactylServerError,
    PterodactylValidationError
)

class PterodactylHTTPClient:
    def __init__(self, panel_url: str, api_key: str):
        self.panel_url = panel_url.rstrip("/")
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        if response.status == 204:
            return None
            
        try:
            data = await response.json()
        except Exception:
            data = {"errors": [{"detail": "Unable to parse JSON response."}]}

        if 200 <= response.status < 300:
            return data

        # Handle errors
        if response.status == 401 or response.status == 403:
            raise PterodactylAuthError("Authentication failed: Invalid API key or missing permissions.")
        elif response.status == 404:
            raise PterodactylNotFoundError("Requested resource was not found.")
        elif response.status == 429:
            raise PterodactylRateLimitError("Rate limit exceeded.")
        elif response.status == 422:
            errors = data.get("errors", [])
            msg = errors[0].get("detail", "Validation Error") if errors else "Validation Error"
            raise PterodactylValidationError(msg, errors)
        elif response.status >= 500:
            raise PterodactylServerError(f"Panel server error ({response.status})")
        else:
            errors = data.get("errors", [])
            msg = errors[0].get("detail", f"Unknown error ({response.status})") if errors else f"Unknown error ({response.status})"
            raise PterodactylError(msg)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.panel_url}{endpoint}"
        async with self.session.get(url, params=params) as response:
            return await self._handle_response(response)

    async def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.panel_url}{endpoint}"
        async with self.session.post(url, json=json_data) as response:
            return await self._handle_response(response)

    async def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.panel_url}{endpoint}"
        async with self.session.put(url, json=json_data) as response:
            return await self._handle_response(response)

    async def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.panel_url}{endpoint}"
        async with self.session.patch(url, json=json_data) as response:
            return await self._handle_response(response)

    async def delete(self, endpoint: str) -> Any:
        url = f"{self.panel_url}{endpoint}"
        async with self.session.delete(url) as response:
            return await self._handle_response(response)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
