import asyncio
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from mcnexus.rcon.client import RCONClient
from mcnexus.rcon.response import RCONResponse

logger = logging.getLogger(__name__)

class RCONPool:
    """
    Manages multiple RCON connections simultaneously.
    Allows for broadcasting commands and managing multiple servers by alias.
    """
    def __init__(self, default_timeout: float = 10.0, auto_reconnect: bool = True):
        self._clients: Dict[str, RCONClient] = {}
        self._default_timeout = default_timeout
        self._auto_reconnect = auto_reconnect

    def add_server(
        self, 
        alias: str, 
        host: str, 
        port: int, 
        password: str, 
        timeout: Optional[float] = None,
        auto_reconnect: Optional[bool] = None
    ):
        """Adds a server configuration to the pool."""
        if alias in self._clients:
            logger.warning(f"Server with alias '{alias}' already exists. Overwriting.")
        
        self._clients[alias] = RCONClient(
            host=host, 
            port=port, 
            password=password, 
            timeout=timeout or self._default_timeout,
            auto_reconnect=auto_reconnect if auto_reconnect is not None else self._auto_reconnect
        )

    async def connect_all(self) -> Dict[str, bool]:
        """Connects to all servers in the pool. Returns a map of alias to success."""
        tasks = []
        aliases = list(self._clients.keys())
        
        for alias in aliases:
            tasks.append(self._clients[alias].connect())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        status = {}
        for alias, result in zip(aliases, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to connect to '{alias}': {result}")
                status[alias] = False
            else:
                status[alias] = True
        return status

    async def disconnect_all(self):
        """Disconnects from all servers."""
        tasks = [client.disconnect() for client in self._clients.values()]
        await asyncio.gather(*tasks)

    async def command(self, alias: str, cmd: str) -> RCONResponse:
        """Sends a command to a specific server by alias."""
        if alias not in self._clients:
            raise KeyError(f"Server alias '{alias}' not found in pool")
        
        return await self._clients[alias].command(cmd)

    async def broadcast(self, cmd: str) -> Dict[str, Union[RCONResponse, Exception]]:
        """Sends a command to all servers in the pool."""
        aliases = list(self._clients.keys())
        tasks = [self._clients[alias].command(cmd) for alias in aliases]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {alias: result for alias, result in zip(aliases, results)}

    def get_client(self, alias: str) -> RCONClient:
        """Returns the RCONClient instance for a given alias."""
        return self._clients[alias]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect_all()
