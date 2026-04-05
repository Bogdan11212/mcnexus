from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from mcnexus.rcon.response import strip_colors

@dataclass
class Player:
    name: str
    id: str

@dataclass
class StatusResponse:
    host: str
    port: int
    online: bool
    version_name: Optional[str] = None
    protocol_version: Optional[int] = None
    players_max: int = 0
    players_online: int = 0
    players_sample: List[Player] = field(default_factory=list)
    motd: str = ""
    ping: float = 0.0  # In milliseconds
    favicon: Optional[str] = None  # Base64 string
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def motd_clean(self) -> str:
        """Returns the MOTD without Minecraft formatting codes."""
        return strip_colors(self.motd)

    def __str__(self) -> str:
        status = "Online" if self.online else "Offline"
        return f"[{self.host}:{self.port}] {status} - {self.players_online}/{self.players_max} players"
