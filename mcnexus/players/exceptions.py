class PlayerError(Exception):
    """Base exception for all player-related errors."""
    pass

class PlayerNotFoundError(PlayerError):
    """Raised when a player cannot be found by nickname or UUID."""
    pass

class PlayerAPIError(PlayerError):
    """Raised when an external API returns an error or is unreachable."""
    pass

class PlayerRateLimitError(PlayerError):
    """Raised when the Mojang or server API rate limit is exceeded."""
    pass
