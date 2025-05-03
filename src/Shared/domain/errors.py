class AppError(Exception):
    """Base class for application-specific errors."""

    pass


class AuthenticationError(AppError):
    """Raised when authentication fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
