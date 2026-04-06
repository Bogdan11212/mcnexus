from typing import Dict, Any, List, Optional, Literal
from mcnexus.pterodactyl import PterodactylClientAPI
from mcnexus.pufferpanel import PufferPanelAPI

class ScheduleManager:
    """
    Advanced manager to handle server schedules and automated tasks on control panels.
    """

    @staticmethod
    async def create_pterodactyl_schedule(
        panel_url: str,
        api_key: str,
        server_id: str,
        name: str,
        minute: str = "*",
        hour: str = "*",
        day_of_month: str = "*",
        month: str = "*",
        day_of_week: str = "*",
        is_active: bool = True,
        only_when_online: bool = False
    ) -> Dict[str, Any]:
        """
        Creates a native schedule on Pterodactyl.
        
        :param minute: Cron minute (0-59 or *)
        :param hour: Cron hour (0-23 or *)
        :param only_when_online: Only run tasks if the server is running.
        """
        async with PterodactylClientAPI(panel_url, api_key) as client:
            data = {
                "name": name,
                "is_active": is_active,
                "minute": minute,
                "hour": hour,
                "day_of_month": day_of_month,
                "month": month,
                "day_of_week": day_of_week,
                "only_when_online": only_when_online
            }
            return await client.create_schedule(server_id, data)

    @staticmethod
    async def add_pterodactyl_task(
        panel_url: str,
        api_key: str,
        server_id: str,
        schedule_id: int,
        action: Literal["command", "power", "backup"],
        payload: str,
        time_offset: int = 0,
        continue_on_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Adds a specific task to an existing Pterodactyl schedule.
        
        :param action: 'command' (payload is command string), 
                       'power' (payload is start/stop/restart/kill),
                       'backup' (payload is ignored files string).
        :param time_offset: Seconds to wait after the previous task.
        """
        async with PterodactylClientAPI(panel_url, api_key) as client:
            data = {
                "action": action,
                "payload": payload,
                "time_offset": time_offset,
                "continue_on_failure": continue_on_failure
            }
            return await client.create_schedule_task(server_id, str(schedule_id), data)

    @staticmethod
    async def create_pufferpanel_task(
        panel_url: str,
        client_id: str,
        client_secret: str,
        server_id: str,
        name: str,
        cron: str,
        action: Literal["start", "stop", "restart", "kill", "command"],
        command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a scheduled task on PufferPanel.
        """
        async with PufferPanelAPI(panel_url, client_id, client_secret) as api:
            # PufferPanel tasks are defined in the server's data. 
            # This is a simplified wrapper for common automated tasks.
            task_data = {
                "name": name,
                "cron": cron,
                "operations": [
                    {
                        "type": "command" if action == "command" else "power",
                        "command": command if action == "command" else action
                    }
                ]
            }
            # Note: Implementation details may vary based on PufferPanel version.
            # We use the generic server update method to inject schedules.
            server = await api.get_server(server_id)
            tasks = server.get("tasks", [])
            tasks.append(task_data)
            return await api.update_server(server_id, {"tasks": tasks})
