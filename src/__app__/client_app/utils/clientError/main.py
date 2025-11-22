"""Module defining a custom exception for client errors"""

class ClientError(Exception):
    """Custom exception class for client errors"""

    def __init__(self, message, level="error") -> None:
        """Initialize ClientError with message and level"""

        self.message = message
        self.level = level
        super().__init__({"message": message, "level": level})
