from typing import Dict, Any, List, Optional
from mcnexus.pterodactyl.http import PterodactylHTTPClient

class PterodactylApplicationAPI:
    """
    Wrapper for the Pterodactyl Application API (Admin panel).
    """
    def __init__(self, panel_url: str, api_key: str):
        self.http = PterodactylHTTPClient(panel_url, api_key)
        self.base_url = "/api/application"

    async def close(self):
        await self.http.close()

    # --- Users ---
    async def list_users(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/users")

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/users/{user_id}")

    async def get_user_by_external_id(self, external_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/users/external/{external_id}")

    async def create_user(self, email: str, username: str, first_name: str, last_name: str, password: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        if password:
            data["password"] = password
        return await self.http.post(f"{self.base_url}/users", data)

    async def update_user(self, user_id: int, email: str, username: str, first_name: str, last_name: str, password: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        if password:
            data["password"] = password
        return await self.http.patch(f"{self.base_url}/users/{user_id}", data)

    async def delete_user(self, user_id: int) -> None:
        await self.http.delete(f"{self.base_url}/users/{user_id}")

    # --- Nodes ---
    async def list_nodes(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nodes")

    async def get_node(self, node_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nodes/{node_id}")

    async def get_node_configuration(self, node_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nodes/{node_id}/configuration")

    async def create_node(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/nodes", data)

    async def update_node(self, node_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.patch(f"{self.base_url}/nodes/{node_id}", data)

    async def delete_node(self, node_id: int) -> None:
        await self.http.delete(f"{self.base_url}/nodes/{node_id}")

    # --- Allocations ---
    async def list_node_allocations(self, node_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nodes/{node_id}/allocations")

    async def create_node_allocations(self, node_id: int, ip: str, ports: List[str]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/nodes/{node_id}/allocations", {"ip": ip, "ports": ports})

    async def delete_node_allocation(self, node_id: int, allocation_id: int) -> None:
        await self.http.delete(f"{self.base_url}/nodes/{node_id}/allocations/{allocation_id}")

    # --- Locations ---
    async def list_locations(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/locations")

    async def get_location(self, location_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/locations/{location_id}")

    async def create_location(self, short: str, long: str) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/locations", {"short": short, "long": long})

    async def update_location(self, location_id: int, short: str, long: str) -> Dict[str, Any]:
        return await self.http.patch(f"{self.base_url}/locations/{location_id}", {"short": short, "long": long})

    async def delete_location(self, location_id: int) -> None:
        await self.http.delete(f"{self.base_url}/locations/{location_id}")

    # --- Servers ---
    async def list_servers(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers")

    async def get_server(self, server_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}")

    async def get_server_by_external_id(self, external_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/external/{external_id}")

    async def update_server_details(self, server_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.patch(f"{self.base_url}/servers/{server_id}/details", data)

    async def update_server_build(self, server_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.patch(f"{self.base_url}/servers/{server_id}/build", data)

    async def update_server_startup(self, server_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.patch(f"{self.base_url}/servers/{server_id}/startup", data)

    async def create_server(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers", data)

    async def suspend_server(self, server_id: int) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/suspend")

    async def unsuspend_server(self, server_id: int) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/unsuspend")

    async def reinstall_server(self, server_id: int) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/reinstall")

    async def delete_server(self, server_id: int) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}")

    async def force_delete_server(self, server_id: int) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/force")

    # --- Nests & Eggs ---
    async def list_nests(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nests")

    async def get_nest(self, nest_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nests/{nest_id}")

    async def list_eggs(self, nest_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nests/{nest_id}/eggs")

    async def get_egg(self, nest_id: int, egg_id: int) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/nests/{nest_id}/eggs/{egg_id}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
