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
from mcnexus.management import ServerManager
from mcnexus.scheduling import ScheduleManager
from mcnexus.stats import StatsManager, ResourceStats
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
from mcnexus.pufferpanel import (
    PufferPanelAPI,
    PufferPanelError,
    PufferPanelAuthError,
    PufferPanelNotFoundError,
    PufferPanelPermissionError,
    PufferPanelServerError
)
from mcnexus.spark import (
    SparkAnalyzer,
    SparkClient,
    SparkProfile,
    SparkMetadata,
    SparkPluginAnalysis,
    SparkError,
    SparkFetchError,
    SparkParseError,
    SparkInvalidURLError
)
from mcnexus.players import (
    PlayerIntelligence,
    MojangAPI,
    HypixelAPI,
    WynncraftAPI,
    PlayerError,
    PlayerNotFoundError,
    PlayerAPIError,
    PlayerRateLimitError
)
from mcnexus.skins import (
    SkinsAPI,
    SkinError,
    SkinFetchError,
    InvalidSizeError
)
from mcnexus.version import VersionManager
from mcnexus.validator import (
    YAMLValidator,
    YAMLValidationResult,
    YAMLValidationError
)
from mcnexus.database import (
    SQLiteMigrator,
    MigrationError,
    DatabaseConnectionError,
    MigrationDataError,
    MigrationUnsupportedError
)
from mcnexus.agerapvp import (
    AgeraPVPAPI,
    AgeraError,
    AgeraAuthError,
    AgeraNotFoundError,
    AgeraAPIError
)

__version__ = "1.3.0"

# Automatic background check for updates
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(VersionManager.check_for_updates())
except Exception:
    pass

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
    "ServerManager",
    "ScheduleManager",
    "StatsManager",
    "ResourceStats",
    "PterodactylClientAPI",
    "PterodactylApplicationAPI",
    "PterodactylError",
    "PterodactylAuthError",
    "PterodactylNotFoundError",
    "PterodactylRateLimitError",
    "PterodactylServerError",
    "PterodactylValidationError",
    "PufferPanelAPI",
    "PufferPanelError",
    "PufferPanelAuthError",
    "PufferPanelNotFoundError",
    "PufferPanelPermissionError",
    "PufferPanelServerError",
    "SparkAnalyzer",
    "SparkClient",
    "SparkProfile",
    "SparkMetadata",
    "SparkPluginAnalysis",
    "SparkError",
    "SparkFetchError",
    "SparkParseError",
    "SparkInvalidURLError",
    "PlayerIntelligence",
    "MojangAPI",
    "HypixelAPI",
    "WynncraftAPI",
    "PlayerError",
    "PlayerNotFoundError",
    "PlayerAPIError",
    "PlayerRateLimitError",
    "SkinsAPI",
    "SkinError",
    "SkinFetchError",
    "InvalidSizeError",
    "VersionManager",
    "YAMLValidator",
    "YAMLValidationResult",
    "YAMLValidationError",
    "SQLiteMigrator",
    "MigrationError",
    "DatabaseConnectionError",
    "MigrationDataError",
    "MigrationUnsupportedError",
    "AgeraPVPAPI",
    "AgeraError",
    "AgeraAuthError",
    "AgeraNotFoundError",
    "AgeraAPIError",
    "strip_colors",
    "RCONError",
    "RCONAuthError",
    "RCONConnectionError",
    "RCONTimeoutError"
]
