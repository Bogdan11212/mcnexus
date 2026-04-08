class MigrationError(Exception):
    """Base exception for all database migration errors."""
    pass

class DatabaseConnectionError(MigrationError):
    """Raised when the migrator fails to connect to the source or target database."""
    pass

class MigrationUnsupportedError(MigrationError):
    """Raised when trying to migrate between incompatible databases."""
    pass

class MigrationDataError(MigrationError):
    """Raised when data cannot be successfully read or written during migration."""
    pass
