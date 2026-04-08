import aiohttp
from typing import Optional, Dict, Any
from mcnexus.players.exceptions import PlayerAPIError, PlayerRateLimitError

class HypixelAPI:
    """
    Asynchronous client for the Hypixel API.
    Requires an API key from /api inside the game.
    """
    def __init__(self, api_key: str, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self._session = session
        self._owns_session = session is None
        self.base_url = "https://api.hypixel.net"

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers={"API-Key": self.api_key})
            self._owns_session = True
        return self._session

    async def get_player(self, uuid: str) -> Dict[str, Any]:
        """
        Returns full player statistics.
        """
        url = f"{self.base_url}/player?uuid={uuid}"
        async with self.session.get(url) as resp:
            if resp.status == 429:
                raise PlayerRateLimitError("Hypixel API rate limit exceeded.")
            if resp.status != 200:
                raise PlayerAPIError(f"Hypixel API error: {resp.status}")
            
            data = await resp.json()
            if not data.get("success"):
                raise PlayerAPIError(f"Hypixel API request failed: {data.get('cause')}")
            
            return data.get("player") or {}

    async def get_status(self, uuid: str) -> Dict[str, Any]:
        """
        Returns the current online status of a player.
        """
        url = f"{self.base_url}/status?uuid={uuid}"
        async with self.session.get(url) as resp:
            data = await resp.json()
            return data.get("session", {})

    async def get_recent_games(self, uuid: str) -> list:
        """
        Returns a list of recently played games.
        """
        url = f"{self.base_url}/recentgames?uuid={uuid}"
        async with self.session.get(url) as resp:
            data = await resp.json()
            return data.get("games", [])

    async def close(self):
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
