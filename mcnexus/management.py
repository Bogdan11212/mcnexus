from typing import Dict, Any, Literal, Optional
from mcnexus.pterodactyl import PterodactylClientAPI
from mcnexus.pufferpanel import PufferPanelAPI

class ServerManager:
    """
    High-level manager to control servers across different panels (Pterodactyl, PufferPanel).
    """
    
    @staticmethod
    async def set_power_state(
        panel_type: Literal["pterodactyl", "pufferpanel"],
        panel_url: str,
        api_credentials: Dict[str, str],
        server_id: str,
        action: Literal["start", "stop", "restart", "kill"]
    ) -> None:
        """
        Universally sets the power state of a server.
        
        :param panel_type: Type of the panel ('pterodactyl' or 'pufferpanel')
        :param panel_url: Full URL to the panel (e.g. 'https://panel.example.com')
        :param api_credentials: Dictionary with auth data.
               For Pterodactyl: {'api_key': '...' }
               For PufferPanel: {'client_id': '...', 'client_secret': '...'}
        :param server_id: The unique identifier of the server in the panel.
        :param action: The action to perform ('start', 'stop', 'restart', 'kill').
        """
        
        if panel_type == "pterodactyl":
            api_key = api_credentials.get("api_key")
            if not api_key:
                raise ValueError("Pterodactyl requires 'api_key' in api_credentials")
            
            async with PterodactylClientAPI(panel_url, api_key) as client:
                await client.send_power_action(server_id, action)
                
        elif panel_type == "pufferpanel":
            client_id = api_credentials.get("client_id")
            client_secret = api_credentials.get("client_secret")
            if not client_id or not client_secret:
                raise ValueError("PufferPanel requires 'client_id' and 'client_secret' in api_credentials")
            
            async with PufferPanelAPI(panel_url, client_id, client_secret) as client:
                # PufferPanel uses 'restart' but Pterodactyl and our method use it too. 
                # Mapping is mostly 1:1.
                await client.send_server_power(server_id, action)
        else:
            raise ValueError(f"Unsupported panel type: {panel_type}")
