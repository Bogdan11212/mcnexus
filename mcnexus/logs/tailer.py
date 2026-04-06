import asyncio
import os
import logging
from typing import Callable, Coroutine, Any, List, Optional, Type

from mcnexus.logs.parser import LogParser
from mcnexus.logs.events import LogEvent

logger = logging.getLogger(__name__)

class LogWatcher:
    """
    Main class for watching Minecraft logs and dispatching events.
    """
    def __init__(self, log_path: str, interval: float = 0.5):
        self.log_path = log_path
        self.interval = interval
        self.parser = LogParser()
        self._handlers: List[Dict[str, Any]] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def on_event(
        self, 
        event_type: Type[LogEvent], 
        callback: Callable[[LogEvent], Coroutine[Any, Any, None]]
    ):
        """Registers a callback for a specific event type."""
        self._handlers.append({"type": event_type, "callback": callback})

    async def start(self, follow_from_end: bool = True):
        """Starts watching the log file."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop(follow_from_end))

    async def stop(self):
        """Stops watching the log file."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _watch_loop(self, follow_from_end: bool):
        """Internal loop to tail the file and parse lines."""
        while self._running:
            if not os.path.exists(self.log_path):
                await asyncio.sleep(self.interval)
                continue

            try:
                with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                    if follow_from_end:
                        f.seek(0, os.SEEK_END)
                    
                    while self._running:
                        line = f.readline()
                        if not line:
                            # No new data, wait and check if file was rotated
                            curr_pos = f.tell()
                            if os.path.getsize(self.log_path) < curr_pos:
                                # File shrunk or rotated
                                break
                            
                            await asyncio.sleep(self.interval)
                            continue
                        
                        # Process the new line
                        event = self.parser.parse_line(line)
                        if event:
                            await self._dispatch(event)

            except Exception as e:
                logger.error(f"Error while watching log file: {e}")
                await asyncio.sleep(self.interval)

    async def _dispatch(self, event: LogEvent):
        """Dispatches an event to registered handlers."""
        for handler in self._handlers:
            if isinstance(event, handler["type"]):
                try:
                    await handler["callback"](event)
                except Exception as e:
                    logger.error(f"Error in log event handler: {e}")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
