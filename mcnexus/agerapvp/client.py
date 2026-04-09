import aiohttp
from typing import Optional, Dict, Any, List
from mcnexus.agerapvp.exceptions import AgeraAuthError, AgeraNotFoundError, AgeraAPIError

class AgeraPVPAPI:
    """
    Asynchronous client for the AgeraPVP API.
    Provides 100% coverage of the Public API endpoints.
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

    async def _request(self, method: str, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.api_base}{path}"
        async with self.session.request(method, url, params=params) as resp:
            if resp.status == 401 or resp.status == 403:
                raise AgeraAuthError("Invalid or missing API key.")
            if resp.status == 404:
                raise AgeraNotFoundError(f"Resource not found: {path}")
            if resp.status != 200:
                data = await resp.json()
                raise AgeraAPIError(f"AgeraPVP API error: {data.get('detail', resp.status)}")
            
            return await resp.json()

    # --- Test ---
    async def test_connection(self) -> bool:
        """Checks if the API key and connection are working."""
        data = await self._request("GET", "/test")
        return data.get("success", False)

    # --- Player API ---
    async def get_profile(self, name: str) -> Dict[str, Any]:
        """Returns the player profile (ranks, skin, server, last login)."""
        return await self._request("GET", f"/player/profile/{name}")

    async def get_stats(self, name: str, mode: str) -> Dict[str, Any]:
        """Returns player statistics for a specific mode (e.g. BW, DUELS)."""
        return await self._request("GET", f"/player/stats/{name}/{mode}")

    async def get_friends(self, name: str) -> List[Dict[str, Any]]:
        """Returns the list of player friends profiles."""
        data = await self._request("GET", f"/player/friends/{name}")
        return data.get("profiles", [])

    # --- Staff API ---
    async def get_staff_stats(self) -> Dict[str, Any]:
        """Returns various staff statistics (total bans, mutes, active ones)."""
        return await self._request("GET", "/staff/stats")

    async def get_online_staff(self) -> List[Dict[str, Any]]:
        """Returns a list of currently online staff members."""
        data = await self._request("GET", "/staff/online")
        return data.get("players", [])

    # --- Server API ---
    async def get_running_servers(self, mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns a list of all running servers, optionally filtered by mode."""
        path = "/server/running"
        if mode:
            path += f"/{mode}"
        data = await self._request("GET", path)
        return data.get("servers", [])

    async def get_mode_online(self, mode: str) -> int:
        """Returns the number of players currently in a specific mode."""
        data = await self._request("GET", f"/server/online/by-mode/{mode}")
        return data.get("online", 0)

    async def get_available_modes(self) -> Dict[str, List[str]]:
        """Returns a list of all available game modes (master and mini)."""
        return await self._request("GET", "/server/modes/available")

    async def get_mode_maps(self, mode: str) -> List[str]:
        """Returns a list of maps available for the specified mode."""
        data = await self._request("GET", f"/server/maps/by-mode/{mode}")
        return data.get("maps", [])

    # --- Core API ---
    async def get_total_online(self) -> int:
        """Returns the current total online player count on the network."""
        data = await self._request("GET", "/core/online/total")
        return data.get("online", 0)

    async def get_uptime(self) -> int:
        """Returns the current server uptime in seconds."""
        data = await self._request("GET", "/core/uptime")
        return data.get("uptime", 0)

    async def get_streams(self) -> List[Dict[str, Any]]:
        """Returns a list of currently running streams (streamer, url, platform)."""
        data = await self._request("GET", "/core/streams")
        return data.get("streams", [])

    async def get_leaderboard(self, mode: str, field: str) -> Dict[str, int]:
        """Returns top players based on a specific stats field and mode."""
        data = await self._request("GET", f"/core/top/{mode}/{field}")
        return data.get("top", {})

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
