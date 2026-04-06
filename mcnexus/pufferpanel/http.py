import aiohttp
from typing import Dict, Any, Optional
import json

from mcnexus.pufferpanel.exceptions import (
    PufferPanelError,
    PufferPanelAuthError,
    PufferPanelNotFoundError,
    PufferPanelPermissionError,
    PufferPanelServerError
)

class PufferPanelHTTPClient:
    def __init__(self, panel_url: str, client_id: str, client_secret: str):
        self.panel_url = panel_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def authenticate(self):
        """Exchange client credentials for an OAuth2 token."""
        url = f"{self.panel_url}/oauth2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        # Temporary session for auth
        async with aiohttp.ClientSession() as auth_session:
            async with auth_session.post(url, data=data) as resp:
                if resp.status != 200:
                    raise PufferPanelAuthError(f"Failed to authenticate with PufferPanel: {resp.status}")
                res_data = await resp.json()
                self._token = res_data.get("access_token")
                # Reset main session to include new token
                if self._session:
                    await self._session.close()
                    self._session = None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        if response.status == 204:
            return None
            
        try:
            data = await response.json()
        except Exception:
            data = {}

        if 200 <= response.status < 300:
            return data

        if response.status == 401:
            raise PufferPanelAuthError("Unauthorized: Token expired or invalid.")
        elif response.status == 403:
            raise PufferPanelPermissionError("Forbidden: Lacking permissions.")
        elif response.status == 404:
            raise PufferPanelNotFoundError("Resource not found.")
        elif response.status >= 500:
            raise PufferPanelServerError(f"PufferPanel internal server error ({response.status})")
        else:
            msg = data.get("error", {}).get("message", f"Unknown error ({response.status})")
            raise PufferPanelError(msg)

    async def request(self, method: str, endpoint: str, **kwargs) -> Any:
        if not self._token:
            await self.authenticate()

        url = f"{self.panel_url}{endpoint}"
        async with self.session.request(method, url, **kwargs) as response:
            if response.status == 401: # Token might have expired
                await self.authenticate()
                # Retry once
                async with self.session.request(method, url, **kwargs) as retry_resp:
                    return await self._handle_response(retry_resp)
            return await self._handle_response(response)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("POST", endpoint, json=json_data)

    async def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("PUT", endpoint, json=json_data)

    async def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self.request("PATCH", endpoint, json=json_data)

    async def delete(self, endpoint: str) -> Any:
        return await self.request("DELETE", endpoint)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
