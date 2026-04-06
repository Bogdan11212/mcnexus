class SparkError(Exception):
    """Base exception for all Spark-related errors."""
    pass

class SparkFetchError(SparkError):
    """Raised when fetching profile data from spark.lucko.me fails."""
    pass

class SparkParseError(SparkError):
    """Raised when the profile data cannot be parsed correctly."""
    pass

class SparkInvalidURLError(SparkError):
    """Raised when the provided spark URL is malformed."""
    pass
