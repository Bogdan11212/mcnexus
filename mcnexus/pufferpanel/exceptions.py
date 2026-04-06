class PufferPanelError(Exception):
    """Base exception for all PufferPanel API errors."""
    pass

class PufferPanelAuthError(PufferPanelError):
    """Raised when authentication fails."""
    pass

class PufferPanelNotFoundError(PufferPanelError):
    """Raised when a resource is not found."""
    pass

class PufferPanelPermissionError(PufferPanelError):
    """Raised when the API key lacks permissions for an action."""
    pass

class PufferPanelServerError(PufferPanelError):
    """Raised when the panel returns a 500+ error."""
    pass
