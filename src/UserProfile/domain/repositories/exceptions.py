class RepositoryError(Exception):
    """Base exception for repository-related errors."""

    pass


class DatabaseConnectionError(RepositoryError):
    """Raised when there are problems with database connection."""

    pass


class DatabaseIntegrityError(RepositoryError):
    """Raised when database integrity constraints are violated."""

    pass


class UserNotFoundError(RepositoryError):
    """Raised when a requested user cannot be found in the repository."""

    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found")
        self.user_id = user_id


class UsernameAlreadyExistsError(DatabaseIntegrityError):
    """Raised when attempting to add/update a user with a username that already exists."""

    def __init__(self, username: str):
        super().__init__(f"User with username '{username}' already exists")
        self.username = username


class InvalidUserDataError(RepositoryError):
    """Raised when user data is invalid (e.g., missing required fields)."""

    pass
