class PterodactylError(Exception):
    """Base exception for all Pterodactyl API errors."""
    pass

class PterodactylAuthError(PterodactylError):
    """Raised when the API key is invalid or missing."""
    pass

class PterodactylNotFoundError(PterodactylError):
    """Raised when a requested resource is not found (404)."""
    pass

class PterodactylRateLimitError(PterodactylError):
    """Raised when the API rate limit is exceeded (429)."""
    pass

class PterodactylServerError(PterodactylError):
    """Raised when the Pterodactyl panel returns a 500+ error."""
    pass

class PterodactylValidationError(PterodactylError):
    """Raised when the provided data is invalid (422)."""
    def __init__(self, message: str, errors: list):
        super().__init__(message)
        self.errors = errors
