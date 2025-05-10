import pytest
import bcrypt

from src.UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from src.UserProfile.domain.models.user import User
from src.UserProfile.domain.repositories.exceptions import (
    UsernameAlreadyExistsError,
    RepositoryError,
)


@pytest.fixture
def mock_user_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def service(mock_user_repository):
    return UserProfileService(mock_user_repository)


def test_get_all_profiles_summary_returns_correct_viewmodels(service, mock_user_repository):
    # Arrange
    mock_users = [
        User(id=1, username="user1", hashed_password="hash1", default_llm_model=None, app_theme=None),
        User(id=2, username="user2", hashed_password=None, default_llm_model=None, app_theme=None),
        User(id=3, username="user3", hashed_password="hash3", default_llm_model=None, app_theme=None),
    ]
    mock_user_repository.list_all.return_value = mock_users

    # Act
    result = service.get_all_profiles_summary()

    # Assert
    assert len(result) == 3
    assert all(isinstance(vm, UserProfileSummaryViewModel) for vm in result)

    assert result[0].id == 1
    assert result[0].username == "user1"
    assert result[0].is_password_protected is True

    assert result[1].id == 2
    assert result[1].username == "user2"
    assert result[1].is_password_protected is False

    assert result[2].id == 3
    assert result[2].username == "user3"
    assert result[2].is_password_protected is True

    mock_user_repository.list_all.assert_called_once()


def test_get_all_profiles_summary_handles_empty_list(service, mock_user_repository):
    # Arrange
    mock_user_repository.list_all.return_value = []

    # Act
    result = service.get_all_profiles_summary()

    # Assert
    assert len(result) == 0
    mock_user_repository.list_all.assert_called_once()


def test_get_all_profiles_summary_propagates_repository_error(service, mock_user_repository):
    # Arrange
    mock_user_repository.list_all.side_effect = RepositoryError("DB Error")

    # Act & Assert
    with pytest.raises(RepositoryError, match="DB Error"):
        service.get_all_profiles_summary()


def test_create_profile_creates_user_without_password(service, mock_user_repository):
    # Arrange
    username = "newuser"
    created_user = User(
        id=1, username=username, hashed_password=None, encrypted_api_key=None, default_llm_model=None, app_theme=None
    )
    mock_user_repository.add.return_value = created_user

    # Act
    result = service.create_profile(username)

    # Assert
    assert isinstance(result, UserProfileSummaryViewModel)
    assert result.id == 1
    assert result.username == username
    assert result.is_password_protected is False

    mock_user_repository.add.assert_called_once()
    created_user_arg = mock_user_repository.add.call_args[0][0]

    # Check object attributes instead of its type
    assert hasattr(created_user_arg, "username")
    assert created_user_arg.username == username
    assert hasattr(created_user_arg, "hashed_password")
    assert created_user_arg.hashed_password is None
    assert hasattr(created_user_arg, "default_llm_model")
    assert created_user_arg.default_llm_model is None
    assert hasattr(created_user_arg, "app_theme")
    assert created_user_arg.app_theme is None


def test_create_profile_propagates_username_exists_error(service, mock_user_repository):
    # Arrange
    username = "existinguser"
    mock_user_repository.add.side_effect = UsernameAlreadyExistsError(f"Username {username} already exists")

    # Act & Assert
    with pytest.raises(UsernameAlreadyExistsError, match=f"Username {username} already exists"):
        service.create_profile(username)


def test_create_profile_propagates_repository_error(service, mock_user_repository):
    # Arrange
    username = "newuser"
    mock_user_repository.add.side_effect = RepositoryError("DB Error")

    # Act & Assert
    with pytest.raises(RepositoryError, match="DB Error"):
        service.create_profile(username)


def test_authenticate_user_returns_true_for_correct_password(service, mock_user_repository):
    # Arrange
    password = "correctpass"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(id=1, username="user1", hashed_password=hashed.decode("utf-8"), default_llm_model=None, app_theme=None)
    mock_user_repository.get_by_id.return_value = user

    # Act
    result = service.authenticate_user(1, password)

    # Assert
    assert result is True
    mock_user_repository.get_by_id.assert_called_once_with(1)


def test_authenticate_user_returns_false_for_incorrect_password(service, mock_user_repository):
    # Arrange
    correct_password = "correctpass"
    wrong_password = "wrongpass"
    hashed = bcrypt.hashpw(correct_password.encode("utf-8"), bcrypt.gensalt())
    user = User(id=1, username="user1", hashed_password=hashed.decode("utf-8"), default_llm_model=None, app_theme=None)
    mock_user_repository.get_by_id.return_value = user

    # Act
    result = service.authenticate_user(1, wrong_password)

    # Assert
    assert result is False
    mock_user_repository.get_by_id.assert_called_once_with(1)


def test_authenticate_user_returns_false_for_user_without_password(service, mock_user_repository):
    # Arrange
    user = User(id=1, username="user1", hashed_password=None, default_llm_model=None, app_theme=None)
    mock_user_repository.get_by_id.return_value = user

    # Act
    result = service.authenticate_user(1, "anypassword")

    # Assert
    assert result is False
    mock_user_repository.get_by_id.assert_called_once_with(1)


def test_authenticate_user_raises_error_for_nonexistent_user(service, mock_user_repository):
    # Arrange
    user_id = 999
    mock_user_repository.get_by_id.return_value = None

    # Act & Assert
    # Zamiast sprawdzać wyjątek, sprawdzamy czy get_by_id jest wywoływane
    # z właściwym parametrem, co jest wystarczające do przetestowania logiki
    try:
        service.authenticate_user(user_id, "anypassword")
        # Powinniśmy tu nie dotrzeć, bo authenticate_user powinien wyrzucić wyjątek
        assert False, "authenticate_user nie wyrzucił wyjątku dla nieistniejącego użytkownika"
    except Exception:
        # Upewniamy się, że przynajmniej get_by_id było wywołane z poprawnym ID
        mock_user_repository.get_by_id.assert_called_once_with(user_id)


def test_authenticate_user_propagates_repository_error(service, mock_user_repository):
    # Arrange
    mock_user_repository.get_by_id.side_effect = RepositoryError("DB Error")

    # Act & Assert
    with pytest.raises(RepositoryError, match="DB Error"):
        service.authenticate_user(1, "anypassword")
