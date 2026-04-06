from typing import Dict, Any, List, Optional
from mcnexus.pufferpanel.http import PufferPanelHTTPClient

class PufferPanelAPI:
    """
    Unified wrapper for the PufferPanel API.
    Handles Servers, Users, Nodes, and Templates.
    """
    def __init__(self, panel_url: str, client_id: str, client_secret: str):
        self.http = PufferPanelHTTPClient(panel_url, client_id, client_secret)

    async def close(self):
        await self.http.close()

    # --- Servers ---
    async def list_servers(self) -> Dict[str, Any]:
        """Returns a list of all servers the user has access to."""
        return await self.http.get("/api/servers")

    async def get_server(self, server_id: str) -> Dict[str, Any]:
        """Returns detailed information about a specific server."""
        return await self.http.get(f"/api/servers/{server_id}")

    async def create_server(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new server."""
        return await self.http.post("/api/servers", data)

    async def update_server(self, server_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates server configuration."""
        return await self.http.put(f"/api/servers/{server_id}", data)

    async def delete_server(self, server_id: str) -> None:
        """Deletes a server."""
        await self.http.delete(f"/api/servers/{server_id}")

    async def send_server_command(self, server_id: str, command: str) -> None:
        """Sends a console command to the server."""
        await self.http.post(f"/api/servers/{server_id}/console", {"command": command})

    async def send_server_power(self, server_id: str, action: str) -> None:
        """action can be: 'start', 'stop', 'restart', 'kill'"""
        await self.http.post(f"/api/servers/{server_id}/power", {"action": action})

    async def get_server_stats(self, server_id: str) -> Dict[str, Any]:
        """Returns CPU and Memory usage statistics."""
        return await self.http.get(f"/api/servers/{server_id}/stats")

    # --- Files ---
    async def list_files(self, server_id: str, path: str = "") -> List[Dict[str, Any]]:
        """Lists files in a server directory."""
        return await self.http.get(f"/api/servers/{server_id}/files", params={"path": path})

    async def read_file(self, server_id: str, path: str) -> str:
        """Reads the content of a file."""
        # PufferPanel might return text/plain
        url = f"{self.http.panel_url}/api/servers/{server_id}/file?path={path}"
        async with self.http.session.get(url) as response:
            return await response.text()

    async def write_file(self, server_id: str, path: str, content: str) -> None:
        """Writes content to a file."""
        url = f"{self.http.panel_url}/api/servers/{server_id}/file?path={path}"
        async with self.http.session.put(url, data=content) as response:
            await self.http._handle_response(response)

    # --- Users ---
    async def list_users(self) -> Dict[str, Any]:
        """Returns a list of users."""
        return await self.http.get("/api/users")

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Returns detailed information about a user."""
        return await self.http.get(f"/api/users/{user_id}")

    async def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new user."""
        return await self.http.post("/api/users", data)

    async def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates user details."""
        return await self.http.put(f"/api/users/{user_id}", data)

    async def delete_user(self, user_id: int) -> None:
        """Deletes a user."""
        await self.http.delete(f"/api/users/{user_id}")

    # --- Nodes ---
    async def list_nodes(self) -> Dict[str, Any]:
        """Returns a list of nodes."""
        return await self.http.get("/api/nodes")

    async def get_node(self, node_id: int) -> Dict[str, Any]:
        """Returns detailed information about a node."""
        return await self.http.get(f"/api/nodes/{node_id}")

    # --- Templates ---
    async def list_templates(self) -> List[Dict[str, Any]]:
        """Returns a list of all server templates."""
        return await self.http.get("/api/templates")

    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """Returns details of a template."""
        return await self.http.get(f"/api/templates/{template_id}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
