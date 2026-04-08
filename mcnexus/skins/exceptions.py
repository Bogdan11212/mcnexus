from mcnexus.players.exceptions import PlayerError

class SkinError(PlayerError):
    """Base exception for all skin-related errors."""
    pass

class SkinFetchError(SkinError):
    """Raised when an image cannot be downloaded."""
    pass

class InvalidSizeError(SkinError):
    """Raised when an invalid pixel size is requested."""
    pass
