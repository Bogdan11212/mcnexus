import re
from datetime import datetime
from typing import Optional, Union

from mcnexus.logs.events import (
    LogEvent, ChatEvent, JoinEvent, LeaveEvent, 
    DeathEvent, AdvancementEvent, GenericEvent
)

class LogParser:
    """
    Parses Minecraft log lines into structured events.
    Compatible with Vanilla, Paper, Spigot, and others using standard formatting.
    """
    # [12:34:56] [Server thread/INFO]: <Message>
    LOG_PATTERN = re.compile(r'^\[(\d{2}:\d{2}:\d{2})\] \[([^/]+)/([^\]]+)\]: (.*)$')
    
    # <Player> Message
    CHAT_PATTERN = re.compile(r'^<([^>]+)> (.*)$')
    
    # Player joined the game
    JOIN_PATTERN = re.compile(r'^(\w+) joined the game$')
    
    # Player [1.2.3.4:1234] logged in with entity id 123
    LOGIN_PATTERN = re.compile(r'^(\w+)\[/([\d\.]+):\d+\] logged in with entity id \d+')
    
    # Player left the game
    LEAVE_PATTERN = re.compile(r'^(\w+) left the game$')
    
    # Player has made the advancement [Advancement Name]
    ADVANCEMENT_PATTERN = re.compile(r'^(\w+) has made the advancement \[(.*)\]$')
    
    # Player was slain by Zombie, etc. (Heuristic for common death messages)
    DEATH_KEYWORDS = ["slain", "burned", "drowned", "fell", "hit", "blown up", "killed", "shot", "squashed", "withered"]

    def parse_line(self, line: str) -> Optional[LogEvent]:
        """
        Parses a single log line. 
        Returns a specific LogEvent subclass or None if parsing fails.
        """
        line = line.strip()
        if not line:
            return None

        match = self.LOG_PATTERN.match(line)
        if not match:
            return None

        time_str, thread, level, content = match.groups()
        
        # We don't have the date in latest.log, so we assume today
        now = datetime.now()
        try:
            timestamp = datetime.strptime(f"{now.year}-{now.month}-{now.day} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = now

        # 1. Check for Chat
        chat_match = self.CHAT_PATTERN.match(content)
        if chat_match:
            return ChatEvent(timestamp, line, thread, level, chat_match.group(1), chat_match.group(2))

        # 2. Check for Join
        join_match = self.JOIN_PATTERN.match(content)
        if join_match:
            return JoinEvent(timestamp, line, thread, level, join_match.group(1))
        
        login_match = self.LOGIN_PATTERN.match(content)
        if login_match:
            return JoinEvent(timestamp, line, thread, level, login_match.group(1), login_match.group(2))

        # 3. Check for Leave
        leave_match = self.LEAVE_PATTERN.match(content)
        if leave_match:
            return LeaveEvent(timestamp, line, thread, level, leave_match.group(1))

        # 4. Check for Advancement
        adv_match = self.ADVANCEMENT_PATTERN.match(content)
        if adv_match:
            return AdvancementEvent(timestamp, line, thread, level, adv_match.group(1), adv_match.group(2))

        # 5. Check for Death (Generic heuristic)
        # Note: This is simplified, as Minecraft has hundreds of death messages.
        if any(kw in content for kw in self.DEATH_KEYWORDS):
            parts = content.split(" ", 1)
            player = parts[0] if parts else ""
            return DeathEvent(timestamp, line, thread, level, player, content)

        # 6. Default fallback
        return GenericEvent(timestamp, line, thread, level, content)
