from datetime import datetime
import sqlite3
import pytest
from pytest_mock import MockerFixture

from src.UserProfile.domain.models.user import User
from src.UserProfile.domain.repositories.exceptions import (
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from src.UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import (
    UserRepositoryImpl,
    DbConnectionProvider,
)


@pytest.fixture
def mock_db_provider(mocker: MockerFixture):
    provider = mocker.Mock(spec=DbConnectionProvider)
    provider.get_connection = mocker.Mock(return_value=mocker.Mock(spec=sqlite3.Connection))
    return provider


@pytest.fixture
def repository(mock_db_provider):
    return UserRepositoryImpl(mock_db_provider)


@pytest.fixture
def sample_user():
    return User(id=None, username="testuser", hashed_password="hashedpass123", hashed_api_key="hashedkey456")


@pytest.fixture
def sample_db_row():
    return {
        "id": 1,
        "username": "testuser",
        "hashed_password": "hashedpass123",
        "hashed_api_key": "hashedkey456",
        "created_at": "2024-03-20T12:00:00",
        "updated_at": "2024-03-20T12:00:00",
    }


def test_add_user_success(mocker: MockerFixture, repository, mock_db_provider, sample_user, sample_db_row):
    # Setup mock cursor
    mock_cursor = mocker.Mock()
    mock_cursor.lastrowid = 1
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Setup get_by_id mock return
    mock_cursor.fetchone.return_value = sample_db_row

    # Execute
    result = repository.add(sample_user)

    # Assert
    assert result.id == 1
    assert result.username == sample_user.username
    assert result.hashed_password == sample_user.hashed_password
    assert result.hashed_api_key == sample_user.hashed_api_key
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)

    # Verify SQL query was executed with correct parameters
    mock_db_provider.get_connection.return_value.execute.assert_any_call(
        mocker.ANY, (sample_user.username, sample_user.hashed_password, sample_user.hashed_api_key)
    )


def test_add_user_duplicate_username(mocker: MockerFixture, repository, mock_db_provider, sample_user):
    # Setup mock to raise IntegrityError
    error = sqlite3.IntegrityError("UNIQUE constraint failed: Users.username")
    mock_db_provider.get_connection.return_value.execute.side_effect = error

    # Execute and assert
    with pytest.raises(UsernameAlreadyExistsError) as exc_info:
        repository.add(sample_user)
    assert sample_user.username in str(exc_info.value)


def test_get_by_id_found(mocker: MockerFixture, repository, mock_db_provider, sample_db_row):
    # Setup mock cursor
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = sample_db_row
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute
    result = repository.get_by_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.username == sample_db_row["username"]

    # Verify SQL query was executed with correct parameters
    mock_db_provider.get_connection.return_value.execute.assert_called_once_with(mocker.ANY, (1,))


def test_get_by_id_not_found(mocker: MockerFixture, repository, mock_db_provider):
    # Setup mock cursor
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute
    result = repository.get_by_id(999)

    # Assert
    assert result is None


def test_update_user_success(mocker: MockerFixture, repository, mock_db_provider, sample_db_row):
    # Setup user with ID
    user_to_update = User(id=1, username="newusername", hashed_password="newhash123", hashed_api_key="newkey456")

    # Setup get_by_id mock
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = sample_db_row
    mock_cursor.rowcount = 1
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute
    repository.update(user_to_update)

    # Verify SQL query was executed with correct parameters
    mock_db_provider.get_connection.return_value.execute.assert_any_call(
        mocker.ANY,
        (user_to_update.username, user_to_update.hashed_password, user_to_update.hashed_api_key, user_to_update.id),
    )


def test_update_user_not_found(mocker: MockerFixture, repository, mock_db_provider):
    # Setup user with non-existent ID
    user_to_update = User(id=999, username="newusername", hashed_password="newhash123", hashed_api_key="newkey456")

    # Setup get_by_id mock to return None
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute and assert
    with pytest.raises(UserNotFoundError) as exc_info:
        repository.update(user_to_update)
    assert str(user_to_update.id) in str(exc_info.value)


def test_delete_user_success(mocker: MockerFixture, repository, mock_db_provider, sample_db_row):
    # Setup get_by_id mock
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = sample_db_row
    mock_cursor.rowcount = 1
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute
    repository.delete(1)

    # Verify SQL query was executed with correct parameters
    mock_db_provider.get_connection.return_value.execute.assert_any_call(mocker.ANY, (1,))


def test_delete_user_not_found(mocker: MockerFixture, repository, mock_db_provider):
    # Setup get_by_id mock to return None
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute and assert
    with pytest.raises(UserNotFoundError) as exc_info:
        repository.delete(999)
    assert "999" in str(exc_info.value)
