import aiohttp
from typing import Optional, Dict, Any
from mcnexus.players.exceptions import PlayerAPIError

class WynncraftAPI:
    """
    Asynchronous client for the Wynncraft API (Public).
    """
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._owns_session = session is None
        self.base_url = "https://api.wynncraft.com/v2"

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def get_player(self, player_name: str) -> Dict[str, Any]:
        """
        Returns full stats for a Wynncraft player.
        """
        url = f"{self.base_url}/player/{player_name}/stats"
        async with self.session.get(url) as resp:
            if resp.status != 200:
                raise PlayerAPIError(f"Wynncraft API error: {resp.status}")
            
            data = await resp.json()
            if not data.get("data"):
                return {}
            
            return data["data"][0]

    async def list_guilds(self) -> list:
        """
        Returns a list of all guilds.
        """
        url = f"{self.base_url}/guild/list"
        async with self.session.get(url) as resp:
            data = await resp.json()
            return data.get("guilds", [])

    async def close(self):
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
