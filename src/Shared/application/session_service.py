from typing import Optional

from Shared.domain.errors import AuthenticationError
from UserProfile.domain.models.user import User
from UserProfile.application.user_profile_service import UserProfileService


class SessionService:
    """Service responsible for user session management and authentication."""

    def __init__(self, profile_service: UserProfileService):
        """Initialize the session service.

        Args:
            profile_service: Service for user profile operations
        """
        self._profile_service = profile_service
        self._current_user: Optional[User] = None

    def login(self, username: str, password: str = "") -> User:
        """Log in a user with the given credentials.

        Args:
            username: The username to log in with
            password: The password to verify (can be empty for unprotected profiles)

        Returns:
            The logged in User object

        Raises:
            AuthenticationError: If authentication fails (user not found or wrong password)
        """
        # Get user profile
        profiles = self._profile_service.get_all_profiles_summary()
        profile = next((p for p in profiles if p.username == username), None)
        if not profile:
            raise AuthenticationError("Profil nie istnieje")

        # For unprotected profiles, allow login without password
        if not profile.is_password_protected and not password:
            user = self._profile_service._user_repository.get_by_id(profile.id)
            if not user:  # This should never happen
                raise AuthenticationError("Wystąpił błąd podczas logowania")
            self._current_user = user
            return user

        # For protected profiles, verify password
        is_authenticated = self._profile_service.authenticate_user(profile.id, password)
        if not is_authenticated:
            raise AuthenticationError("Niepoprawne hasło")

        user = self._profile_service._user_repository.get_by_id(profile.id)
        if not user:  # This should never happen
            raise AuthenticationError("Wystąpił błąd podczas logowania")

        self._current_user = user
        return user

    def logout(self) -> None:
        """Log out the current user."""
        self._current_user = None

    def get_current_user(self) -> Optional[User]:
        """Get the currently logged in user.

        Returns:
            The current User object, or None if no user is logged in
        """
        return self._current_user

    def is_authenticated(self) -> bool:
        """Check if a user is currently logged in.

        Returns:
            True if a user is logged in, False otherwise
        """
        return self._current_user is not None
