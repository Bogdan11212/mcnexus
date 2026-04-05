import asyncio
import json
import struct
import time
from typing import Dict, Any, Optional

from mcnexus.status.models import StatusResponse, Player

class ModernPing:
    """
    Implements the Modern Server List Ping protocol (1.7+).
    """
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    @staticmethod
    def _encode_varint(val: int) -> bytes:
        total = b""
        while True:
            byte = val & 0x7F
            val >>= 7
            if val:
                total += struct.pack("B", byte | 0x80)
            else:
                total += struct.pack("B", byte)
                return total

    async def _read_varint(self, reader: asyncio.StreamReader) -> int:
        total = 0
        shift = 0
        while True:
            byte = await reader.readexactly(1)
            b = byte[0]
            total |= (b & 0x7F) << shift
            if not (b & 0x80):
                return total
            shift += 7
            if shift > 35:
                raise ValueError("VarInt too big")

    def _create_packet(self, packet_id: int, data: bytes) -> bytes:
        id_bytes = self._encode_varint(packet_id)
        length = self._encode_varint(len(id_bytes) + len(data))
        return length + id_bytes + data

    def _encode_string(self, s: str) -> bytes:
        encoded = s.encode("utf-8")
        return self._encode_varint(len(encoded)) + encoded

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
            # 1. Handshake (Packet ID 0x00, State 1)
            # Protocol -1, Host, Port, Next State 1
            handshake = (
                self._encode_varint(-1) + 
                self._encode_string(self.host) + 
                struct.pack(">H", self.port) + 
                self._encode_varint(1)
            )
            writer.write(self._create_packet(0x00, handshake))

            # 2. Request (Packet ID 0x00)
            writer.write(self._create_packet(0x00, b""))
            await writer.drain()

            # 3. Response (Packet ID 0x00)
            packet_len = await self._read_varint(reader)
            packet_id = await self._read_varint(reader)
            
            if packet_id != 0x00:
                raise ValueError(f"Unexpected packet ID {packet_id}")

            json_len = await self._read_varint(reader)
            json_data = await reader.readexactly(json_len)
            data = json.loads(json_data.decode("utf-8"))
            
            ping_ms = (time.time() - start_time) * 1000
            
            return self._parse_response(data, ping_ms)

        except Exception:
            return StatusResponse(host=self.host, port=self.port, online=False)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass

    def _parse_response(self, data: Dict[str, Any], ping_ms: float) -> StatusResponse:
        # Extract MOTD (can be string or dict)
        description = data.get("description", "")
        if isinstance(description, dict):
            # Modern versions use 'text' and 'extra'
            motd = description.get("text", "")
            for extra in description.get("extra", []):
                motd += extra.get("text", "")
        else:
            motd = str(description)

        players_data = data.get("players", {})
        players_sample = []
        for p in players_data.get("sample", []):
            players_sample.append(Player(name=p.get("name", ""), id=p.get("id", "")))

        version_data = data.get("version", {})

        return StatusResponse(
            host=self.host,
            port=self.port,
            online=True,
            version_name=version_data.get("name"),
            protocol_version=version_data.get("protocol"),
            players_max=players_data.get("max", 0),
            players_online=players_data.get("online", 0),
            players_sample=players_sample,
            motd=motd,
            ping=ping_ms,
            favicon=data.get("favicon"),
            raw=data
        )
