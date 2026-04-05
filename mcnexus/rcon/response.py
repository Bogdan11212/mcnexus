import re
from dataclasses import dataclass
from typing import List

# Matches Minecraft formatting codes (e.g. §a, §l, §r)
MINECRAFT_COLOR_REGEX = re.compile(r'§[0-9a-fk-or]', re.IGNORECASE)

def strip_colors(text: str) -> str:
    """Removes Minecraft formatting codes from a string."""
    return MINECRAFT_COLOR_REGEX.sub('', text)

@dataclass
class RCONResponse:
    """Represents a structured response from the RCON server."""
    raw: str
    time_taken: float  # In seconds

    @property
    def clean(self) -> str:
        """Returns the response text with Minecraft color codes removed."""
        return strip_colors(self.raw)
        
    @property
    def lines(self) -> List[str]:
        """Returns the clean response split by lines."""
        return [line.strip() for line in self.clean.split('\n') if line.strip()]

    def __str__(self) -> str:
        return self.clean
