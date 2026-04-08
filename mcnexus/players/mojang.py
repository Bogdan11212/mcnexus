import aiohttp
from typing import Optional, Dict, Any, List
from mcnexus.players.exceptions import PlayerNotFoundError, PlayerAPIError, PlayerRateLimitError

class MojangAPI:
    """
    Asynchronous client for the official Mojang API.
    Used for nickname-to-uuid resolution and profile data.
    """
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._owns_session = session is None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def get_uuid(self, username: str) -> str:
        """
        Resolves a Minecraft username to its UUID.
        """
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        async with self.session.get(url) as resp:
            if resp.status == 204: # No Content
                raise PlayerNotFoundError(f"Player '{username}' not found.")
            if resp.status == 429:
                raise PlayerRateLimitError("Mojang API rate limit exceeded.")
            if resp.status != 200:
                raise PlayerAPIError(f"Mojang API error: {resp.status}")
            
            data = await resp.json()
            return data["id"]

    async def get_profile(self, uuid: str) -> Dict[str, Any]:
        """
        Returns the full profile data for a given UUID (skins, capes, etc).
        """
        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        async with self.session.get(url) as resp:
            if resp.status == 204:
                raise PlayerNotFoundError(f"UUID '{uuid}' not found.")
            if resp.status == 429:
                raise PlayerRateLimitError("Mojang API rate limit exceeded.")
            if resp.status != 200:
                raise PlayerAPIError(f"Mojang API error: {resp.status}")
            
            return await resp.json()

    async def get_name_history(self, uuid: str) -> List[Dict[str, Any]]:
        """
        Returns the username history for a given UUID.
        Note: This is partially deprecated in some versions of Mojang API, 
        but still supported by some proxy endpoints.
        """
        # Official Mojang API removed this endpoint recently, 
        # using Ashcon or other reliable proxies is recommended for this specific task.
        url = f"https://api.ashcon.app/mojang/v2/user/{uuid}"
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("username_history", [])

    async def close(self):
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
