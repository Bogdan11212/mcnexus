import struct
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional

class PacketType(IntEnum):
    RESPONSE = 0
    COMMAND = 2
    LOGIN = 3

@dataclass(frozen=True)
class RCONPacket:
    id: int
    type: PacketType
    payload: str

    def encode(self, encoding: str = "utf-8") -> bytes:
        """
        Encodes the packet into the Minecraft RCON binary format.
        Format: [Length (4b)][ID (4b)][Type (4b)][Payload (nb)][Null (1b)][Null (1b)]
        """
        encoded_payload = self.payload.encode(encoding)
        # Length includes ID (4), Type (4), Payload (n), and two null terminators (2).
        # It does NOT include the length field itself.
        length = 10 + len(encoded_payload)
        
        return struct.pack(
            f"<iii{len(encoded_payload)}sxx",
            length,
            self.id,
            int(self.type),
            encoded_payload
        )

    @classmethod
    def decode(cls, data: bytes, encoding: str = "utf-8") -> "RCONPacket":
        """
        Decodes raw bytes into an RCONPacket.
        Assumes the first 4 bytes (length) have already been stripped.
        """
        if len(data) < 10:
            raise ValueError("Packet data too short")
        
        req_id, type_int = struct.unpack("<ii", data[:8])
        # Payload starts at 8, ends before the two null terminators (\x00\x00)
        payload = data[8:-2].decode(encoding)
        
        return cls(id=req_id, type=PacketType(type_int), payload=payload)
