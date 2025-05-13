import pytest
from unittest.mock import Mock
from typing import Dict, Optional

from Shared.application.session_service import SessionService
from UserProfile.domain.models.user import User


class MockProfileService:
    """Mock implementacja ProfileServiceProtocol do testów."""

    def __init__(self, users: Optional[Dict[str, User]] = None):
        self.users: Dict[str, User] = users or {}

    def get_profile_by_username(self, username: str) -> User:
        if username in self.users:
            return self.users[username]
        raise Exception(f"User {username} not found")

    def authenticate_user(self, user_id: int, password: str) -> bool:
        # W testach upraszczamy i zwracamy True dla hasła "correct_password"
        return password == "correct_password"

    def get_profile_by_id(self, user_id: int) -> User:
        for user in self.users.values():
            if user.id == user_id:
                return user
        raise Exception(f"User with ID {user_id} not found")


@pytest.fixture
def test_users():
    """Przygotowuje zestaw testowych użytkowników."""
    return {
        "testuser": User(id=1, username="testuser", hashed_password=None, default_llm_model=None, app_theme=None),
        "secureuser": User(
            id=2, username="secureuser", hashed_password="hashed_password", default_llm_model=None, app_theme=None
        ),
    }


@pytest.fixture
def mock_profile_service(test_users):
    """Tworzy mock dla ProfileService."""
    return MockProfileService(test_users)


@pytest.fixture
def session_service(mock_profile_service):
    """Tworzy SessionService z mockiem ProfileService."""
    return SessionService(mock_profile_service)


class TestLogin:
    """Testy dla metody login."""

    def test_login_success_without_password(self, session_service, test_users):
        # Arrange
        username = "testuser"

        # Act
        session_service.login(username)

        # Assert
        assert session_service.is_authenticated()
        assert session_service.get_current_user() == test_users[username]

    def test_login_with_password_success(self, session_service, test_users):
        # Arrange
        username = "secureuser"
        password = "correct_password"

        # Mock authenticate_user
        session_service._profile_service.authenticate_user = Mock(return_value=True)

        # Act
        session_service.login(username, password)

        # Assert
        assert session_service.is_authenticated()
        assert session_service.get_current_user() == test_users[username]
        session_service._profile_service.authenticate_user.assert_called_once_with(2, password)

    def test_login_with_password_failure(self, session_service):
        # Arrange
        username = "secureuser"
        password = "wrong_password"

        # Mock authenticate_user
        session_service._profile_service.authenticate_user = Mock(return_value=False)

        # Act & Assert
        try:
            session_service.login(username, password)
            pytest.fail("Should have raised an AuthenticationError")
        except Exception as e:
            # Check exception type by name to avoid import path issues
            assert e.__class__.__name__ == "AuthenticationError"
            assert "Niepoprawne hasło" in str(e)

        # Verify that the user is not authenticated
        assert not session_service.is_authenticated()
        assert session_service.get_current_user() is None

    def test_login_nonexistent_user(self, session_service):
        # Arrange
        username = "nonexistent"

        # Override mock to simulate user not found
        session_service._profile_service.get_profile_by_username = Mock(side_effect=Exception("User not found"))

        # Act & Assert
        with pytest.raises(Exception):
            session_service.login(username)

        # Verify that the user is not authenticated
        assert not session_service.is_authenticated()


class TestLogout:
    """Testy dla metody logout."""

    def test_logout(self, session_service, test_users):
        # Arrange - eerst inloggen
        username = "testuser"
        session_service.login(username)
        assert session_service.is_authenticated()

        # Act
        session_service.logout()

        # Assert
        assert not session_service.is_authenticated()
        assert session_service.get_current_user() is None


class TestGetCurrentUser:
    """Testy dla metody get_current_user."""

    def test_get_current_user_when_logged_in(self, session_service, test_users):
        # Arrange
        username = "testuser"
        session_service.login(username)

        # Act
        user = session_service.get_current_user()

        # Assert
        assert user == test_users[username]

    def test_get_current_user_when_not_logged_in(self, session_service):
        # Act
        user = session_service.get_current_user()

        # Assert
        assert user is None


class TestIsAuthenticated:
    """Testy dla metody is_authenticated."""

    def test_is_authenticated_when_logged_in(self, session_service):
        # Arrange
        session_service.login("testuser")

        # Act & Assert
        assert session_service.is_authenticated()

    def test_is_authenticated_when_not_logged_in(self, session_service):
        # Act & Assert
        assert not session_service.is_authenticated()


class TestRefreshCurrentUser:
    """Testy dla metody refresh_current_user."""

    def test_refresh_current_user_success(self, session_service, test_users):
        # Arrange
        username = "testuser"
        session_service.login(username)

        # Create updated user
        updated_user = User(
            id=1, username="testuser", hashed_password=None, default_llm_model="new_model", app_theme="new_theme"
        )

        # Mock get_profile_by_id to return updated user
        session_service._profile_service.get_profile_by_id = Mock(return_value=updated_user)

        # Act
        session_service.refresh_current_user()

        # Assert
        assert session_service.get_current_user() == updated_user
        session_service._profile_service.get_profile_by_id.assert_called_once_with(1)

    def test_refresh_current_user_no_user_logged_in(self, session_service):
        # Arrange - make sure no user is logged in
        assert not session_service.is_authenticated()

        # Mock get_profile_by_id to verify it's not called
        session_service._profile_service.get_profile_by_id = Mock()

        # Act
        session_service.refresh_current_user()

        # Assert
        assert not session_service.is_authenticated()
        session_service._profile_service.get_profile_by_id.assert_not_called()

    def test_refresh_current_user_error(self, session_service, test_users):
        # Arrange
        username = "testuser"
        session_service.login(username)
        original_user = session_service.get_current_user()

        # Mock get_profile_by_id to raise exception
        session_service._profile_service.get_profile_by_id = Mock(side_effect=Exception("Database error"))

        # Act
        session_service.refresh_current_user()

        # Assert - user data should remain unchanged
        assert session_service.get_current_user() == original_user
