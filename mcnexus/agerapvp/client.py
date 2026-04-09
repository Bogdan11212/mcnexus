import aiohttp
from typing import Optional, Dict, Any, List
from mcnexus.agerapvp.exceptions import AgeraAuthError, AgeraNotFoundError, AgeraAPIError

class AgeraPVPAPI:
    """
    Asynchronous client for the AgeraPVP API.
    """
    def __init__(self, api_key: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self._session = session
        self._owns_session = session is None
        self.api_base = "https://api.agerapvp.club/v1"
        self.skin_base = "https://skin.agerapvp.club/v1"

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["X-Api-Key"] = self.api_key
            self._session = aiohttp.ClientSession(headers=headers)
            self._owns_session = True
        return self._session

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        async with self.session.request(method, url, **kwargs) as resp:
            if resp.status == 401 or resp.status == 403:
                raise AgeraAuthError("Invalid or missing API key.")
            if resp.status == 404:
                raise AgeraNotFoundError("The requested player or resource was not found.")
            if resp.status != 200:
                raise AgeraAPIError(f"AgeraPVP API error: {resp.status}")
            
            return await resp.json()

    # --- Player Data ---
    async def get_profile(self, name_or_uuid: str) -> Dict[str, Any]:
        """Returns the general profile data for a player."""
        return await self._request("GET", f"{self.api_base}/player/profile/{name_or_uuid}")

    async def get_stats(self, name_or_uuid: str) -> Dict[str, Any]:
        """Returns detailed game statistics for a player."""
        return await self._request("GET", f"{self.api_base}/player/stats/{name_or_uuid}")

    # --- Skin Service (Static URL Generators) ---
    def get_head_url(self, username: str) -> str:
        """Returns the URL for the player's head avatar."""
        return f"{self.skin_base}/head/{username}/"

    def get_body_url(self, username: str) -> str:
        """Returns the URL for the player's 3D body render."""
        return f"{self.skin_base}/body/{username}/"

    def get_skin_url(self, username: str) -> str:
        """Returns the URL for the raw .png skin file."""
        return f"{self.skin_base}/skin/{username}/"

    def get_cape_url(self, username: str) -> str:
        """Returns the URL for the player's cape file."""
        return f"{self.skin_base}/cape/{username}/"

    async def close(self):
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
