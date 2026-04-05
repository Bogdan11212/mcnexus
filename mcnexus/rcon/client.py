import asyncio
import struct
import logging
import time
from typing import Optional, Union

from mcnexus.rcon.packet import RCONPacket, PacketType
from mcnexus.rcon.response import RCONResponse
from mcnexus.rcon.exceptions import (
    RCONAuthError, 
    RCONConnectionError, 
    RCONTimeoutError, 
    RCONProtocolError,
    RCONDisconnectedError,
    RCONCommandError
)

logger = logging.getLogger(__name__)

class RCONClient:
    def __init__(
        self, 
        host: str, 
        port: int, 
        password: str, 
        timeout: float = 10.0,
        encoding: str = "utf-8",
        auto_reconnect: bool = True
    ):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.encoding = encoding
        self.auto_reconnect = auto_reconnect
        
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._request_id = 0
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def connect(self):
        """Connects to the RCON server and authenticates."""
        async with self._lock:
            if self._is_connected:
                return

            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                raise RCONTimeoutError("Connection timed out", self.host, self.port)
            except Exception as e:
                raise RCONConnectionError(f"Could not connect: {e}", self.host, self.port)

            try:
                # Login (Type 3)
                login_id = self._next_id()
                await self._send_packet(RCONPacket(id=login_id, type=PacketType.LOGIN, payload=self.password))
                
                response = await self._read_packet()
                # If auth fails, server responds with ID -1
                if response.id == -1:
                    await self.disconnect()
                    raise RCONAuthError("Authentication failed: invalid password", self.host, self.port)
                
                self._is_connected = True
                logger.info(f"Successfully connected to RCON at {self.host}:{self.port}")
                
            except RCONAuthError:
                raise
            except Exception as e:
                await self.disconnect()
                raise RCONConnectionError(f"Protocol error during login: {e}", self.host, self.port)

    async def disconnect(self):
        """Closes the connection to the RCON server."""
        self._is_connected = False
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def _ensure_connection(self):
        """Ensures the client is connected if auto_reconnect is enabled."""
        if not self._is_connected:
            if self.auto_reconnect:
                logger.debug(f"[{self.host}:{self.port}] Auto-reconnecting...")
                await self.connect()
            else:
                raise RCONDisconnectedError("Client is not connected", self.host, self.port)

    async def command(self, cmd: str) -> RCONResponse:
        """
        Sends a command and returns a structured response object.
        """
        await self._ensure_connection()

        start_time = time.time()
        async with self._lock:
            try:
                # 1. Send the actual command
                cmd_id = self._next_id()
                await self._send_packet(RCONPacket(id=cmd_id, type=PacketType.COMMAND, payload=cmd))

                # 2. Send a dummy packet to mark the end of the response
                dummy_id = self._next_id()
                await self._send_packet(RCONPacket(id=dummy_id, type=PacketType.COMMAND, payload=""))

                full_response = []
                while True:
                    packet = await asyncio.wait_for(self._read_packet(), timeout=self.timeout)
                    
                    if packet.id == dummy_id:
                        # We reached our marker; the command output is finished.
                        break
                    
                    if packet.id == cmd_id:
                        full_response.append(packet.payload)
                    else:
                        logger.warning(f"[{self.host}:{self.port}] Received unexpected packet ID {packet.id}")
                
                elapsed_time = time.time() - start_time
                return RCONResponse(raw="".join(full_response), time_taken=elapsed_time)

            except asyncio.TimeoutError:
                await self.disconnect()
                raise RCONTimeoutError("Command execution timed out", self.host, self.port)
            except asyncio.IncompleteReadError:
                # Connection dropped by server
                await self.disconnect()
                raise RCONConnectionError("Connection closed by server", self.host, self.port)
            except Exception as e:
                await self.disconnect()
                raise RCONCommandError(str(e), self.host, self.port, cmd)

    def _next_id(self) -> int:
        self._request_id = (self._request_id + 1) & 0x7FFFFFFF
        return self._request_id

    async def _send_packet(self, packet: RCONPacket):
        if not self._writer:
            raise RCONDisconnectedError("Writer is not available", self.host, self.port)
        
        self._writer.write(packet.encode(self.encoding))
        await self._writer.drain()

    async def _read_packet(self) -> RCONPacket:
        if not self._reader:
            raise RCONDisconnectedError("Reader is not available", self.host, self.port)
        
        header = await self._reader.readexactly(4)
        length = struct.unpack("<i", header)[0]
        
        data = await self._reader.readexactly(length)
        return RCONPacket.decode(data, self.encoding)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
