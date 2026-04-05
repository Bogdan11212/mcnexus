from typing import Optional

class RCONError(Exception):
    """Base exception for all RCON-related errors."""
    def __init__(self, message: str, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host
        self.port = port
        prefix = f"[{host}:{port}] " if host and port else ""
        super().__init__(f"{prefix}{message}")

class RCONAuthError(RCONError):
    """Raised when authentication fails (usually invalid password)."""
    pass

class RCONConnectionError(RCONError):
    """Raised when there is a connection-level issue (refused, dropped, etc.)."""
    pass

class RCONTimeoutError(RCONError):
    """Raised when an operation or connection times out."""
    pass

class RCONProtocolError(RCONError):
    """Raised when receiving unexpected or malformed data from the server."""
    pass

class RCONDisconnectedError(RCONConnectionError):
    """Raised when an operation is attempted on a disconnected client."""
    pass

class RCONCommandError(RCONError):
    """Raised when a specific command fails to execute."""
    def __init__(self, message: str, host: str, port: int, command: str):
        self.command = command
        super().__init__(f"Command '{command}' failed: {message}", host, port)
