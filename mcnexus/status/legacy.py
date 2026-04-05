import asyncio
import time
from mcnexus.status.models import StatusResponse

class LegacyPing:
    """
    Implements the Legacy Server List Ping protocol (pre-1.7).
    """
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    async def ping(self) -> StatusResponse:
        start_time = time.time()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )
        except Exception:
            return StatusResponse(host=self.host, port=self.port, online=False)

        try:
            # 1. Send 0xFE 0x01 (Legacy Ping)
            writer.write(b'\xfe\x01')
            await writer.drain()

            # 2. Read Response (0xFF followed by length and UCS-2 string)
            packet_id = await reader.readexactly(1)
            if packet_id != b'\xff':
                raise ValueError("Invalid legacy packet ID")

            length_bytes = await reader.readexactly(2)
            length = int.from_bytes(length_bytes, byteorder='big')
            
            data = await reader.readexactly(length * 2)
            decoded = data.decode('utf-16be')
            
            ping_ms = (time.time() - start_time) * 1000

            if decoded.startswith('\xa7\x31\x00'): # 1.4+ protocol
                parts = decoded.split('\x00')
                return StatusResponse(
                    host=self.host,
                    port=self.port,
                    online=True,
                    protocol_version=int(parts[1]),
                    version_name=parts[2],
                    motd=parts[3],
                    players_online=int(parts[4]),
                    players_max=int(parts[5]),
                    ping=ping_ms
                )
            else: # Older protocol
                parts = decoded.split('\xa7')
                return StatusResponse(
                    host=self.host,
                    port=self.port,
                    online=True,
                    motd=parts[0],
                    players_online=int(parts[1]),
                    players_max=int(parts[2]),
                    ping=ping_ms
                )

        except Exception:
            return StatusResponse(host=self.host, port=self.port, online=False)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass
