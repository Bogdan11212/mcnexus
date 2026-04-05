import asyncio
import socket
from typing import Tuple, Optional

try:
    import dns.asyncresolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

class MinecraftResolver:
    """
    Handles resolving Minecraft server addresses, including SRV records.
    """
    @staticmethod
    async def resolve(host: str, port: int = 25565) -> Tuple[str, int]:
        """
        Resolves the given host and port.
        Checks for SRV records (_minecraft._tcp.host) first.
        """
        if not HAS_DNS:
            # Fallback to standard resolution if dnspython is not installed
            return host, port

        try:
            srv_record = f"_minecraft._tcp.{host}"
            resolver = dns.asyncresolver.Resolver()
            # Set a small timeout for DNS resolution
            resolver.timeout = 2.0
            resolver.lifetime = 2.0
            
            answers = await resolver.resolve(srv_record, 'SRV')
            if answers:
                # Take the first record (usually highest priority)
                rdata = answers[0]
                target = str(rdata.target).rstrip('.')
                return target, rdata.port
        except Exception:
            # If SRV lookup fails or no record found, use original host/port
            pass

        return host, port

    @staticmethod
    async def get_ip(host: str) -> str:
        """Returns the IP address of a hostname."""
        loop = asyncio.get_event_loop()
        try:
            return (await loop.getaddrinfo(host, None))[0][4][0]
        except Exception:
            return host
