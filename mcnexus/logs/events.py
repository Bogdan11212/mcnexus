from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class LogEvent:
    """Base class for all log events."""
    timestamp: datetime
    raw: str
    thread: str = "Server thread"
    level: str = "INFO"

@dataclass
class ChatEvent(LogEvent):
    """Triggered when a player sends a message in chat."""
    player: str = ""
    message: str = ""

@dataclass
class JoinEvent(LogEvent):
    """Triggered when a player joins the server."""
    player: str = ""
    ip: Optional[str] = None

@dataclass
class LeaveEvent(LogEvent):
    """Triggered when a player leaves the server."""
    player: str = ""
    reason: str = ""

@dataclass
class DeathEvent(LogEvent):
    """Triggered when a player dies."""
    player: str = ""
    cause: str = ""

@dataclass
class AdvancementEvent(LogEvent):
    """Triggered when a player completes an advancement."""
    player: str = ""
    advancement: str = ""

@dataclass
class CommandEvent(LogEvent):
    """Triggered when a command is executed (e.g. from console)."""
    issuer: str = ""
    command: str = ""

@dataclass
class GenericEvent(LogEvent):
    """Triggered for any other INFO/WARN/ERROR log lines."""
    content: str = ""
