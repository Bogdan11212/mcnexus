import asyncio
import logging
from typing import Callable, Coroutine, Any, List

from mcnexus.rcon.client import RCONClient
from mcnexus.rcon.response import RCONResponse

logger = logging.getLogger(__name__)

class RCONWatcher:
    """
    Simulates event-driven behavior by polling the RCON server.
    Allows registering callbacks that trigger when specific conditions are met.
    """
    def __init__(self, client: RCONClient, interval: float = 1.0):
        self.client = client
        self.interval = interval
        self._tasks: List[asyncio.Task] = []
        self._running = False

    async def start(self):
        """Starts the watcher."""
        self._running = True

    async def stop(self):
        """Stops the watcher and cancels all polling tasks."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []

    def on_command_output(
        self, 
        command: str, 
        callback: Callable[[RCONResponse], Coroutine[Any, Any, None]]
    ):
        """
        Polls a command and executes the callback with the structured response.
        """
        async def _poll_loop():
            while self._running:
                try:
                    response = await self.client.command(command)
                    await callback(response)
                except Exception as e:
                    logger.error(f"Watcher error while polling '{command}' on {self.client.host}:{self.client.port}: {e}")
                
                await asyncio.sleep(self.interval)

        task = asyncio.create_task(_poll_loop())
        self._tasks.append(task)
        return task

    def on_output_contains(
        self, 
        command: str, 
        substring: str, 
        callback: Callable[[RCONResponse], Coroutine[Any, Any, None]]
    ):
        """
        Polls a command and executes the callback if the cleaned output contains a specific substring.
        """
        async def _filtered_callback(response: RCONResponse):
            if substring in response.clean:
                await callback(response)

        return self.on_command_output(command, _filtered_callback)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
