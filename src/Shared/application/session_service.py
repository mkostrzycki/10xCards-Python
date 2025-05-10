from typing import Optional, Protocol
import logging

from UserProfile.domain.models.user import User
from Shared.domain.errors import AuthenticationError


class ProfileServiceProtocol(Protocol):
    def get_profile_by_username(self, username: str) -> User: ...
    def authenticate_user(self, user_id: int, password: str) -> bool: ...


class SessionService:
    """Service responsible for user session management and authentication."""

    def __init__(self, profile_service: ProfileServiceProtocol):
        """Initialize the session service.

        Args:
            profile_service: Service for accessing user profiles
        """
        self._profile_service = profile_service
        self._current_user: Optional[User] = None
        logging.info("Session service initialized")

    def login(self, username: str, password: Optional[str] = None) -> None:
        """Log in a user by username.

        Args:
            username: Username to log in
            password: Optional password for password-protected profiles

        Raises:
            AuthenticationError: If no user exists with the given username or password is incorrect
        """
        try:
            user = self._profile_service.get_profile_by_username(username)

            # Verify password if provided and user has password protection
            if password and user.hashed_password:
                if not self._profile_service.authenticate_user(user.id, password):  # type: ignore
                    logging.error(f"Failed login attempt for user: {username} - incorrect password")
                    raise AuthenticationError("Niepoprawne hasło")

            self._current_user = user
            logging.info(f"User logged in: {username}")
        except Exception as e:
            logging.error(f"Unexpected error during login: {str(e)}")
            raise

    def logout(self) -> None:
        """Log out the current user."""
        if self._current_user:
            logging.info(f"User logged out: {self._current_user.username}")
            self._current_user = None

    def get_current_user(self) -> Optional[User]:
        """Get the currently logged in user.

        Returns:
            User object if logged in, None otherwise
        """
        return self._current_user

    def is_authenticated(self) -> bool:
        """Check if a user is currently logged in.

        Returns:
            True if a user is logged in, False otherwise
        """
        return self._current_user is not None

    def refresh_current_user(self) -> None:
        """Refresh the current user's data from the repository.

        This is useful when user data has been updated outside the session.
        """
        if not self._current_user:
            return

        try:
            # Get fresh user data
            username = self._current_user.username
            self._current_user = self._profile_service.get_profile_by_username(username)
            logging.info(f"User data refreshed: {username}")
        except Exception as e:
            logging.error(f"Failed to refresh user data: {str(e)}")
            # Keep current user data if refresh fails
