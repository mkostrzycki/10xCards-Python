from dataclasses import dataclass
from typing import List
import bcrypt

from ..domain.repositories.IUserRepository import IUserRepository
from ..domain.models.user import User
from ..domain.repositories.exceptions import UserNotFoundError


@dataclass
class UserProfileSummaryViewModel:
    id: int
    username: str
    is_password_protected: bool


class UserProfileService:
    """Service for managing user profiles and authentication."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize the service with required dependencies.

        Args:
            user_repository: Repository for user data persistence
        """
        self._user_repository = user_repository

    def get_all_profiles_summary(self) -> List[UserProfileSummaryViewModel]:
        """Get a list of all user profiles with basic information.

        Returns:
            List of user profile summaries

        Raises:
            RepositoryError: If there's an error accessing the database
        """
        users = self._user_repository.list_all()
        return [
            UserProfileSummaryViewModel(
                id=user.id if user.id is not None else 0,  # This should never happen in practice
                username=user.username,
                is_password_protected=user.hashed_password is not None,
            )
            for user in users
        ]

    def create_profile(self, username: str) -> UserProfileSummaryViewModel:
        """Create a new user profile.

        Args:
            username: The username for the new profile

        Returns:
            Summary view model of the created profile

        Raises:
            UsernameAlreadyExistsError: If the username is already taken
            InvalidUserDataError: If the username is invalid
            RepositoryError: If there's an error accessing the database
        """
        # Create new user without password
        user = User(id=None, username=username, hashed_password=None, hashed_api_key=None)
        created_user = self._user_repository.add(user)

        # created_user should always have an id at this point
        assert created_user.id is not None, "Repository must assign an ID to created user"

        return UserProfileSummaryViewModel(
            id=created_user.id, username=created_user.username, is_password_protected=False
        )

    def authenticate_user(self, user_id: int, password: str) -> bool:
        """Authenticate a user with password.

        Args:
            user_id: The ID of the user to authenticate
            password: The password to verify

        Returns:
            True if authentication successful, False if password incorrect

        Raises:
            UserNotFoundError: If no user exists with the given ID
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)  # Pass just the ID

        if not user.hashed_password:
            return False

        return bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8"))
