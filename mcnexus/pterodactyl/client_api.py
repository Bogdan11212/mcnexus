from typing import Dict, Any, List, Optional
from mcnexus.pterodactyl.http import PterodactylHTTPClient

class PterodactylClientAPI:
    """
    Wrapper for the Pterodactyl Client API (User-facing panel).
    """
    def __init__(self, panel_url: str, api_key: str):
        self.http = PterodactylHTTPClient(panel_url, api_key)
        self.base_url = "/api/client"

    async def close(self):
        await self.http.close()

    # --- Account ---
    async def get_account_details(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/account")

    async def get_account_two_factor(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/account/two-factor")

    async def update_email(self, email: str, password: str) -> None:
        await self.http.put(f"{self.base_url}/account/email", {"email": email, "password": password})

    async def update_password(self, current_password: str, new_password: str) -> None:
        await self.http.put(f"{self.base_url}/account/password", {
            "current_password": current_password,
            "password": new_password,
            "password_confirmation": new_password
        })

    async def get_api_keys(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/account/api-keys")

    async def create_api_key(self, description: str, allowed_ips: Optional[List[str]] = None) -> Dict[str, Any]:
        data = {"description": description, "allowed_ips": allowed_ips or []}
        return await self.http.post(f"{self.base_url}/account/api-keys", data)

    async def delete_api_key(self, identifier: str) -> None:
        await self.http.delete(f"{self.base_url}/account/api-keys/{identifier}")

    # --- Servers ---
    async def list_servers(self) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}")

    async def get_server(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}")

    async def get_server_resources(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/resources")

    async def send_command(self, server_id: str, command: str) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/command", {"command": command})

    async def send_power_action(self, server_id: str, action: str) -> None:
        """action can be: 'start', 'stop', 'restart', 'kill'"""
        await self.http.post(f"{self.base_url}/servers/{server_id}/power", {"signal": action})

    # --- Databases ---
    async def get_databases(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/databases")

    async def create_database(self, server_id: str, database: str, remote: str = "%") -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/databases", {"database": database, "remote": remote})

    async def rotate_database_password(self, server_id: str, database_id: str) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/databases/{database_id}/rotate-password")

    async def delete_database(self, server_id: str, database_id: str) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/databases/{database_id}")

    # --- Files ---
    async def list_files(self, server_id: str, directory: str = "/") -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/files/list", params={"directory": directory})

    async def read_file(self, server_id: str, file_path: str) -> str:
        # Pterodactyl returns file contents as plain text, not json
        url = f"{self.http.panel_url}{self.base_url}/servers/{server_id}/files/contents?file={file_path}"
        async with self.http.session.get(url) as response:
            return await response.text()

    async def get_download_url(self, server_id: str, file_path: str) -> str:
        res = await self.http.get(f"{self.base_url}/servers/{server_id}/files/download?file={file_path}")
        return res["attributes"]["url"]

    async def rename_file(self, server_id: str, root: str, files: List[Dict[str, str]]) -> None:
        """files is a list of dicts: [{'from': 'old.txt', 'to': 'new.txt'}]"""
        await self.http.put(f"{self.base_url}/servers/{server_id}/files/rename", {"root": root, "files": files})

    async def copy_file(self, server_id: str, location: str) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/files/copy", {"location": location})

    async def write_file(self, server_id: str, file_path: str, content: str) -> None:
        url = f"{self.http.panel_url}{self.base_url}/servers/{server_id}/files/write?file={file_path}"
        async with self.http.session.post(url, data=content) as response:
            await self.http._handle_response(response)

    async def compress_files(self, server_id: str, root: str, files: List[str]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/files/compress", {"root": root, "files": files})

    async def decompress_file(self, server_id: str, root: str, file: str) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/files/decompress", {"root": root, "file": file})

    async def delete_files(self, server_id: str, root: str, files: List[str]) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/files/delete", {"root": root, "files": files})

    async def create_folder(self, server_id: str, root: str, name: str) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/files/create-folder", {"root": root, "name": name})

    async def chmod_files(self, server_id: str, root: str, files: List[Dict[str, str]]) -> None:
        """files is a list of dicts: [{'file': 'script.sh', 'mode': '0777'}]"""
        await self.http.post(f"{self.base_url}/servers/{server_id}/files/chmod", {"root": root, "files": files})

    # --- Schedules ---
    async def list_schedules(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/schedules")

    async def create_schedule(self, server_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/schedules", data)

    async def get_schedule(self, server_id: str, schedule_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}")

    async def update_schedule(self, server_id: str, schedule_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}", data)

    async def delete_schedule(self, server_id: str, schedule_id: str) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}")

    async def create_schedule_task(self, server_id: str, schedule_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}/tasks", data)

    async def update_schedule_task(self, server_id: str, schedule_id: str, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}/tasks/{task_id}", data)

    async def delete_schedule_task(self, server_id: str, schedule_id: str, task_id: str) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/schedules/{schedule_id}/tasks/{task_id}")

    # --- Network ---
    async def list_allocations(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/network/allocations")

    async def set_primary_allocation(self, server_id: str, allocation_id: int) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/network/allocations/{allocation_id}/primary")

    async def set_allocation_note(self, server_id: str, allocation_id: int, notes: str) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/network/allocations/{allocation_id}", {"notes": notes})

    # --- Users (Subusers) ---
    async def list_users(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/users")

    async def create_user(self, server_id: str, email: str, permissions: List[str]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/users", {"email": email, "permissions": permissions})

    async def get_user(self, server_id: str, uuid: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/users/{uuid}")

    async def update_user(self, server_id: str, uuid: str, permissions: List[str]) -> Dict[str, Any]:
        return await self.http.post(f"{self.base_url}/servers/{server_id}/users/{uuid}", {"permissions": permissions})

    async def delete_user(self, server_id: str, uuid: str) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/users/{uuid}")

    # --- Backups ---
    async def list_backups(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/backups")

    async def create_backup(self, server_id: str, name: str = "", is_locked: bool = False, ignored_files: Optional[List[str]] = None) -> Dict[str, Any]:
        data = {"name": name, "is_locked": is_locked}
        if ignored_files:
            data["ignored"] = "\n".join(ignored_files)
        return await self.http.post(f"{self.base_url}/servers/{server_id}/backups", data)

    async def get_backup(self, server_id: str, backup_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/backups/{backup_id}")

    async def get_backup_download_url(self, server_id: str, backup_id: str) -> str:
        res = await self.http.get(f"{self.base_url}/servers/{server_id}/backups/{backup_id}/download")
        return res["attributes"]["url"]

    async def delete_backup(self, server_id: str, backup_id: str) -> None:
        await self.http.delete(f"{self.base_url}/servers/{server_id}/backups/{backup_id}")

    # --- Startup ---
    async def get_startup_variables(self, server_id: str) -> Dict[str, Any]:
        return await self.http.get(f"{self.base_url}/servers/{server_id}/startup")

    async def update_startup_variable(self, server_id: str, key: str, value: str) -> Dict[str, Any]:
        return await self.http.put(f"{self.base_url}/servers/{server_id}/startup/variable", {"key": key, "value": value})

    # --- Settings ---
    async def rename_server(self, server_id: str, name: str, description: str = "") -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/settings/rename", {"name": name, "description": description})

    async def reinstall_server(self, server_id: str) -> None:
        await self.http.post(f"{self.base_url}/servers/{server_id}/settings/reinstall")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
