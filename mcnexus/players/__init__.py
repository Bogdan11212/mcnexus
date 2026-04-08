from typing import Optional, Dict, Any, List
from mcnexus.players.mojang import MojangAPI
from mcnexus.players.hypixel import HypixelAPI
from mcnexus.players.wynncraft import WynncraftAPI
from mcnexus.players.exceptions import (
    PlayerError, 
    PlayerNotFoundError, 
    PlayerAPIError, 
    PlayerRateLimitError
)

class PlayerIntelligence:
    """
    Unified entry point for player intelligence.
    Gathers data from Mojang, Hypixel, and Wynncraft.
    """
    def __init__(self, hypixel_api_key: Optional[str] = None):
        self.mojang = MojangAPI()
        self.hypixel = HypixelAPI(hypixel_api_key) if hypixel_api_key else None
        self.wynncraft = WynncraftAPI()

    async def get_full_report(self, username: str) -> Dict[str, Any]:
        """
        Gathers all available information for a player.
        """
        # 1. Resolve UUID (Fundamental step)
        uuid = await self.mojang.get_uuid(username)
        
        # 2. Parallel data gathering
        import asyncio
        tasks = [
            self.mojang.get_profile(uuid),
            self.mojang.get_name_history(uuid),
            self.wynncraft.get_player(username)
        ]
        
        if self.hypixel:
            tasks.append(self.hypixel.get_player(uuid))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "username": username,
            "uuid": uuid,
            "profile": results[0] if not isinstance(results[0], Exception) else {},
            "history": results[1] if not isinstance(results[1], Exception) else [],
            "wynncraft": results[2] if not isinstance(results[2], Exception) else {},
            "hypixel": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
        }

    async def close(self):
        await self.mojang.close()
        if self.hypixel:
            await self.hypixel.close()
        await self.wynncraft.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

__all__ = [
    "PlayerIntelligence",
    "MojangAPI",
    "HypixelAPI",
    "WynncraftAPI",
    "PlayerError",
    "PlayerNotFoundError",
    "PlayerAPIError",
    "PlayerRateLimitError"
]
