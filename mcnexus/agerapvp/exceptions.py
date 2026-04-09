from mcnexus.players.exceptions import PlayerError

class AgeraError(PlayerError):
    """Base exception for all AgeraPVP-related errors."""
    pass

class AgeraAuthError(AgeraError):
    """Raised when the API key is invalid or missing."""
    pass

class AgeraNotFoundError(AgeraError):
    """Raised when a player or resource is not found."""
    pass

class AgeraAPIError(AgeraError):
    """Raised when the AgeraPVP API returns an unexpected error."""
    pass
