from datetime import datetime
import sqlite3
import pytest
from pytest_mock import MockerFixture

from src.UserProfile.domain.models.user import User
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
    return User(
        id=None,
        username="testuser",
        hashed_password="hashedpass123",
        encrypted_api_key=b"hashedkey456",
        default_llm_model=None,
        app_theme=None,
    )


@pytest.fixture
def sample_db_row():
    return {
        "id": 1,
        "username": "testuser",
        "hashed_password": "hashedpass123",
        "encrypted_api_key": b"hashedkey456",
        "default_llm_model": None,
        "app_theme": None,
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
    assert result.encrypted_api_key == sample_user.encrypted_api_key
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)

    # Verify SQL query was executed with correct parameters
    mock_db_provider.get_connection.return_value.execute.assert_any_call(
        mocker.ANY, (sample_user.username, sample_user.hashed_password, sample_user.encrypted_api_key)
    )


def test_add_user_duplicate_username(mocker: MockerFixture, repository, mock_db_provider, sample_user):
    # Mock the repository's get_by_username method to simulate a duplicate username check
    # Mock the repository._db_provider to raise the appropriate exception

    # Create a connection mock with the right behavior
    mock_conn = mocker.Mock()

    # Set up a mock cursor for the PRAGMA call
    mock_pragma_cursor = mocker.Mock()

    # Set up behavior for the execute method to raise an integrity error for the INSERT
    def execute_mock(query, params=None):
        if "PRAGMA foreign_keys = ON" in query:
            return mock_pragma_cursor
        elif "INSERT INTO Users" in query:
            # This simulates a duplicate username error from SQLite
            raise sqlite3.IntegrityError("UNIQUE constraint failed: Users.username")
        else:
            raise AssertionError(f"Unexpected query in test: {query}")

    mock_conn.execute = mocker.Mock(side_effect=execute_mock)
    mock_conn.commit = mocker.Mock()

    # Configure the mock_db_provider to return our mock connection
    mock_db_provider.get_connection.return_value = mock_conn

    # Try/except approach to catch and verify the exception
    try:
        repository.add(sample_user)
        # If we get here, the test should fail
        pytest.fail("Expected UsernameAlreadyExistsError was not raised")
    except Exception as e:
        # Check if it's the right type of exception using the class name
        assert type(e).__name__ == "UsernameAlreadyExistsError", f"Wrong exception type: {type(e).__name__}"
        # Check if the message contains the username
        assert sample_user.username in str(e), f"Expected '{sample_user.username}' in error message: {str(e)}"

    # Verify that commit was not called
    mock_conn.commit.assert_not_called()


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
    mock_db_provider.get_connection.return_value.execute.assert_any_call(mocker.ANY, (1,))


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
    user_to_update = User(
        id=1,
        username="newusername",
        hashed_password="newhash123",
        encrypted_api_key=b"newkey456",
        default_llm_model="gpt-4o-mini",
        app_theme="darkly",
    )

    # Setup get_by_id mock
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = sample_db_row
    mock_cursor.rowcount = 1
    mock_db_provider.get_connection.return_value.execute.return_value = mock_cursor

    # Execute
    repository.update(user_to_update)

    # Verify SQL query was executed with correct parameters - updated to match actual implementation
    mock_db_provider.get_connection.return_value.execute.assert_any_call(
        mocker.ANY,
        [
            user_to_update.username,
            user_to_update.hashed_password,
            user_to_update.encrypted_api_key,
            user_to_update.default_llm_model,
            user_to_update.app_theme,
            user_to_update.id
        ],
    )


def test_update_user_not_found(mocker: MockerFixture, repository, mock_db_provider):
    user_to_update = User(
        id=999,
        username="newusername",
        hashed_password="newhash123",
        encrypted_api_key=b"newkey456",
        default_llm_model="gpt-4o-mini",
        app_theme="darkly",
    )

    # Create a mock connection
    mock_conn = mocker.Mock()

    # Set up a mock cursor for the get_by_id call that returns None (user not found)
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None

    # Set up behavior for the execute method
    def execute_mock(query, params=None):
        if "PRAGMA foreign_keys = ON" in query:
            return mocker.Mock()
        elif "SELECT" in query and "FROM Users" in query and "WHERE id = ?" in query:
            # For the get_by_id query, return a cursor that will yield None from fetchone
            return mock_cursor
        else:
            # No other queries should be executed since the user is not found
            raise AssertionError(f"Unexpected query in test: {query}")

    mock_conn.execute = mocker.Mock(side_effect=execute_mock)
    mock_conn.commit = mocker.Mock()

    # Configure the mock_db_provider
    mock_db_provider.get_connection.return_value = mock_conn

    # Try/except approach to catch and verify the exception
    try:
        repository.update(user_to_update)
        # If we get here, the test should fail
        pytest.fail("Expected UserNotFoundError was not raised")
    except Exception as e:
        # Check if it's the right type of exception using the class name
        assert type(e).__name__ == "UserNotFoundError", f"Wrong exception type: {type(e).__name__}"
        # Check if the message contains the user ID
        assert str(user_to_update.id) in str(e), f"Expected '{user_to_update.id}' in error message: {str(e)}"

    # Verify that commit was not called
    mock_conn.commit.assert_not_called()


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
    user_id_to_delete = 999

    # Create a mock connection
    mock_conn = mocker.Mock()

    # Set up a mock cursor for the get_by_id call that returns None (user not found)
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None

    # Set up behavior for the execute method
    def execute_mock(query, params=None):
        if "PRAGMA foreign_keys = ON" in query:
            return mocker.Mock()
        elif "SELECT" in query and "FROM Users" in query and "WHERE id = ?" in query:
            # For the get_by_id query, return a cursor that will yield None from fetchone
            return mock_cursor
        else:
            # No other queries should be executed since the user is not found
            raise AssertionError(f"Unexpected query in test: {query}")

    mock_conn.execute = mocker.Mock(side_effect=execute_mock)
    mock_conn.commit = mocker.Mock()

    # Configure the mock_db_provider
    mock_db_provider.get_connection.return_value = mock_conn

    # Try/except approach to catch and verify the exception
    try:
        repository.delete(user_id_to_delete)
        # If we get here, the test should fail
        pytest.fail("Expected UserNotFoundError was not raised")
    except Exception as e:
        # Check if it's the right type of exception using the class name
        assert type(e).__name__ == "UserNotFoundError", f"Wrong exception type: {type(e).__name__}"
        # Check if the message contains the user ID
        assert str(user_id_to_delete) in str(e), f"Expected '{user_id_to_delete}' in error message: {str(e)}"

    # Verify that commit was not called
    mock_conn.commit.assert_not_called()
