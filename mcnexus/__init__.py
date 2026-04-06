"""
mcnexus - A Python library for Minecraft server tools.
"""

from mcnexus.rcon import (
    RCONClient,
    RCONPool,
    RCONWatcher,
    RCONResponse,
    strip_colors,
    RCONError,
    RCONAuthError,
    RCONConnectionError,
    RCONTimeoutError
)
from mcnexus.status import status, status_bulk, StatusResponse
from mcnexus.logs import (
    LogWatcher,
    LogEvent,
    ChatEvent,
    JoinEvent,
    LeaveEvent,
    DeathEvent,
    AdvancementEvent,
    GenericEvent
)
from mcnexus.pterodactyl import (
    PterodactylClientAPI,
    PterodactylApplicationAPI,
    PterodactylError,
    PterodactylAuthError,
    PterodactylNotFoundError,
    PterodactylRateLimitError,
    PterodactylServerError,
    PterodactylValidationError
)

__version__ = "0.1.0"

__all__ = [
    "RCONClient",
    "RCONPool",
    "RCONWatcher",
    "RCONResponse",
    "status",
    "status_bulk",
    "StatusResponse",
    "LogWatcher",
    "LogEvent",
    "ChatEvent",
    "JoinEvent",
    "LeaveEvent",
    "DeathEvent",
    "AdvancementEvent",
    "GenericEvent",
    "PterodactylClientAPI",
    "PterodactylApplicationAPI",
    "PterodactylError",
    "PterodactylAuthError",
    "PterodactylNotFoundError",
    "PterodactylRateLimitError",
    "PterodactylServerError",
    "PterodactylValidationError",
    "strip_colors",
    "RCONError",
    "RCONAuthError",
    "RCONConnectionError",
    "RCONTimeoutError"
]
