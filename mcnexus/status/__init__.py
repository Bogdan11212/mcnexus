import asyncio
from typing import Optional, List

from mcnexus.status.modern import ModernPing
from mcnexus.status.legacy import LegacyPing
from mcnexus.status.resolver import MinecraftResolver
from mcnexus.status.models import StatusResponse, Player

async def status(
    host: str, 
    port: int = 25565, 
    timeout: float = 5.0,
    try_legacy: bool = True
) -> StatusResponse:
    """
    Retrieves the status of a Minecraft server.
    
    1. Resolves SRV records.
    2. Attempts Modern SLP (1.7+).
    3. If Modern fails and try_legacy is True, attempts Legacy SLP (pre-1.7).
    """
    # 1. Resolve SRV records
    resolved_host, resolved_port = await MinecraftResolver.resolve(host, port)
    
    # 2. Try Modern Ping
    modern = ModernPing(resolved_host, resolved_port, timeout)
    response = await modern.ping()
    
    # 3. If offline, try Legacy Ping
    if not response.online and try_legacy:
        legacy = LegacyPing(resolved_host, resolved_port, timeout)
        response = await legacy.ping()
        
    # Ensure original input host/port are kept in response if needed for tracking
    # (Optional: the response currently uses resolved host/port)
    
    return response

async def status_bulk(
    servers: List[tuple], # List of (host, port)
    timeout: float = 5.0
) -> List[StatusResponse]:
    """
    Retrieves status for multiple servers concurrently.
    """
    tasks = []
    for s in servers:
        h, p = s if len(s) == 2 else (s[0], 25565)
        tasks.append(status(h, p, timeout))
    
    return await asyncio.gather(*tasks)

__all__ = [
    "status",
    "status_bulk",
    "StatusResponse",
    "Player",
    "MinecraftResolver"
]
