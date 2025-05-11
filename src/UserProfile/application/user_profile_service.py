from dataclasses import dataclass
from typing import List, Optional
import bcrypt

from UserProfile.domain.repositories.IUserRepository import IUserRepository
from UserProfile.domain.models.user import User
from UserProfile.domain.repositories.exceptions import UserNotFoundError
from Shared.infrastructure.security.crypto import crypto_manager
from Shared.domain.errors import AuthenticationError


@dataclass
class UserProfileSummaryViewModel:
    id: int
    username: str
    is_password_protected: bool


@dataclass
class SettingsViewModel:
    """ViewModel containing user settings for the SettingsView."""

    user_id: int
    current_username: str
    has_password_set: bool
    current_api_key_masked: Optional[str]
    current_llm_model: Optional[str]
    current_app_theme: str
    available_llm_models: List[str]
    available_app_themes: List[str]


@dataclass
class UpdateUserProfileDTO:
    """DTO for updating user profile username."""

    user_id: int
    new_username: str


@dataclass
class SetUserPasswordDTO:
    """DTO for setting or changing user password."""

    user_id: int
    current_password: Optional[str]
    new_password: Optional[str]


@dataclass
class UpdateUserApiKeyDTO:
    """DTO for updating user API key."""

    user_id: int
    api_key: Optional[str]


@dataclass
class UpdateUserPreferencesDTO:
    """DTO for updating user preferences like LLM model and theme."""

    user_id: int
    default_llm_model: Optional[str] = None
    app_theme: Optional[str] = None


class UserProfileService:
    """Service for managing user profiles and authentication."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize the service with required dependencies.

        Args:
            user_repository: Repository for user data persistence
        """
        self._user_repository = user_repository

    def get_profile_by_username(self, username: str) -> User:
        """Get a user profile by username.

        Args:
            username: The username to find

        Returns:
            User object if found

        Raises:
            AuthenticationError: If no user exists with the given username
        """
        user = self._user_repository.get_by_username(username)
        if not user:
            raise AuthenticationError(f"Użytkownik '{username}' nie istnieje")
        return user

    def get_profile_by_id(self, user_id: int) -> User:
        """Get a user profile by ID.

        Args:
            user_id: The user ID to find

        Returns:
            User object if found

        Raises:
            AuthenticationError: If no user exists with the given ID
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationError(f"Użytkownik o ID {user_id} nie istnieje")
        return user

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
        user = User(
            id=None,
            username=username,
            hashed_password=None,
            encrypted_api_key=None,
            default_llm_model=None,
            app_theme=None,
        )
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

    def get_api_key(self, user_id: int) -> Optional[str]:
        """Get the OpenRouter API key for a user if one exists.

        Args:
            user_id: The ID of the user

        Returns:
            The decrypted API key or None if not set

        Raises:
            UserNotFoundError: If no user exists with the given ID
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        if not user.encrypted_api_key:
            return None

        # Decrypt the API key using the crypto manager
        decrypted_key: str = crypto_manager.decrypt_api_key(user.encrypted_api_key)
        return decrypted_key

    def set_api_key(self, user_id: int, api_key: str) -> None:
        """Set or update the OpenRouter API key for a user.

        Args:
            user_id: The ID of the user
            api_key: The plain API key to encrypt and store

        Raises:
            UserNotFoundError: If no user exists with the given ID
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Encrypt the API key
        encrypted_key = crypto_manager.encrypt_api_key(api_key)

        # Update the user model
        user.encrypted_api_key = encrypted_key

        # Save changes
        self._user_repository.update(user)

    def get_user_settings(
        self, user_id: int, available_llm_models: List[str], available_app_themes: List[str]
    ) -> SettingsViewModel:
        """Get user settings for the SettingsView.

        Args:
            user_id: The ID of the user
            available_llm_models: List of available LLM models from config
            available_app_themes: List of available app themes from config

        Returns:
            SettingsViewModel with user settings and available options

        Raises:
            UserNotFoundError: If no user exists with the given ID
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Get API key if present and mask it
        api_key = None
        if user.encrypted_api_key:
            decrypted_key = self.get_api_key(user_id)
            if decrypted_key:
                # Mask the key - show first 4 and last 4 chars
                if len(decrypted_key) <= 8:
                    api_key = "●" * len(decrypted_key)
                else:
                    api_key = decrypted_key[:4] + "●" * (len(decrypted_key) - 8) + decrypted_key[-4:]

        # Ensure default_llm_model is valid or use first available
        current_llm_model = user.default_llm_model
        if current_llm_model and current_llm_model not in available_llm_models:
            current_llm_model = available_llm_models[0] if available_llm_models else None

        # Ensure app_theme is valid or use first available
        current_app_theme = user.app_theme
        if not current_app_theme or current_app_theme not in available_app_themes:
            current_app_theme = available_app_themes[0] if available_app_themes else "darkly"

        return SettingsViewModel(
            user_id=user_id,
            current_username=user.username,
            has_password_set=user.hashed_password is not None,
            current_api_key_masked=api_key,
            current_llm_model=current_llm_model,
            current_app_theme=current_app_theme,
            available_llm_models=available_llm_models,
            available_app_themes=available_app_themes,
        )

    def update_username(self, dto: UpdateUserProfileDTO) -> User:
        """Update a user's username.

        Args:
            dto: Data transfer object with user ID and new username

        Returns:
            Updated User object

        Raises:
            UserNotFoundError: If no user exists with the given ID
            UsernameAlreadyExistsError: If the new username is already taken
            InvalidUserDataError: If the new username is invalid
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError(dto.user_id)

        # Validation should be done in the application layer
        if not dto.new_username:
            raise ValueError("Nazwa użytkownika nie może być pusta")

        if len(dto.new_username) > 30:
            raise ValueError("Nazwa użytkownika nie może być dłuższa niż 30 znaków")

        # Check if new username is different from current
        if user.username == dto.new_username:
            return user

        # Check if username is already taken
        existing_user = self._user_repository.get_by_username(dto.new_username)
        if existing_user:
            raise ValueError(f"Nazwa '{dto.new_username}' jest już zajęta")

        # Update user model
        user.username = dto.new_username
        self._user_repository.update(user)

        return user

    def set_user_password(self, dto: SetUserPasswordDTO) -> bool:
        """Set, change or remove a user's password.

        Args:
            dto: Data transfer object with user ID, current and new password

        Returns:
            True if operation was successful

        Raises:
            UserNotFoundError: If no user exists with the given ID
            AuthenticationError: If current_password doesn't match the stored password
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError(dto.user_id)

        # Check current password if password is already set
        if user.hashed_password:
            if not dto.current_password:
                raise AuthenticationError("Wymagane jest aktualne hasło")

            if not bcrypt.checkpw(dto.current_password.encode("utf-8"), user.hashed_password.encode("utf-8")):
                raise AuthenticationError("Nieprawidłowe aktualne hasło")

        # Handle password removal
        if not dto.new_password:
            user.hashed_password = None
            self._user_repository.update(user)
            return True

        # Hash and set new password
        hashed = bcrypt.hashpw(dto.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.hashed_password = hashed
        self._user_repository.update(user)

        return True

    def update_user_preferences(self, dto: UpdateUserPreferencesDTO) -> User:
        """Update user preferences like default LLM model and app theme.

        Args:
            dto: Data transfer object with user ID and preferences to update

        Returns:
            Updated User object

        Raises:
            UserNotFoundError: If no user exists with the given ID
            RepositoryError: If there's an error accessing the database
        """
        user = self._user_repository.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError(dto.user_id)

        # Update only provided fields
        if dto.default_llm_model is not None:
            user.default_llm_model = dto.default_llm_model

        if dto.app_theme is not None:
            user.app_theme = dto.app_theme

        # Save changes
        self._user_repository.update(user)

        return user
