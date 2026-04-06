from dataclasses import dataclass
from typing import Dict, Any, Literal, Optional
from mcnexus.pterodactyl import PterodactylClientAPI
from mcnexus.pufferpanel import PufferPanelAPI

@dataclass
class ResourceStats:
    """Unified model for server resource usage."""
    panel_type: str
    server_id: str
    state: str  # e.g. "running", "off"
    cpu_usage: float  # Percentage
    memory_bytes: int
    memory_limit_bytes: int
    disk_bytes: int
    network_rx_bytes: int  # Received
    network_tx_bytes: int  # Transmitted

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024 * 1024)

    @property
    def disk_mb(self) -> float:
        return self.disk_bytes / (1024 * 1024)

class StatsManager:
    """
    Manager to retrieve real-time resource statistics from control panels.
    """

    @staticmethod
    async def get_server_stats(
        panel_type: Literal["pterodactyl", "pufferpanel"],
        panel_url: str,
        api_credentials: Dict[str, str],
        server_id: str
    ) -> ResourceStats:
        """
        Retrieves real-time CPU, Memory, and Network stats.
        """
        if panel_type == "pterodactyl":
            api_key = api_credentials.get("api_key")
            async with PterodactylClientAPI(panel_url, api_key) as client:
                data = await client.get_server_resources(server_id)
                attrs = data["attributes"]["resources"]
                return ResourceStats(
                    panel_type="pterodactyl",
                    server_id=server_id,
                    state=data["attributes"]["current_state"],
                    cpu_usage=attrs["cpu_absolute"],
                    memory_bytes=attrs["memory_bytes"],
                    memory_limit_bytes=0, # Pterodactyl doesn't always return limit in resources
                    disk_bytes=attrs["disk_bytes"],
                    network_rx_bytes=attrs["network_rx_bytes"],
                    network_tx_bytes=attrs["network_tx_bytes"]
                )

        elif panel_type == "pufferpanel":
            c_id = api_credentials.get("client_id")
            c_sec = api_credentials.get("client_secret")
            async with PufferPanelAPI(panel_url, c_id, c_sec) as api:
                data = await api.get_server_stats(server_id)
                # PufferPanel format: {"cpu": 0.5, "memory": 12345, ...}
                return ResourceStats(
                    panel_type="pufferpanel",
                    server_id=server_id,
                    state="running" if data.get("cpu", 0) > 0 else "unknown",
                    cpu_usage=data.get("cpu", 0.0),
                    memory_bytes=data.get("memory", 0),
                    memory_limit_bytes=0,
                    disk_bytes=0, # PufferPanel stats API might not include disk
                    network_rx_bytes=0,
                    network_tx_bytes=0
                )
        else:
            raise ValueError(f"Unsupported panel: {panel_type}")
