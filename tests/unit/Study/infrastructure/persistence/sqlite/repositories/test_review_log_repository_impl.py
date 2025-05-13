import json
import pytest
from datetime import datetime, timezone

from src.Study.infrastructure.persistence.sqlite.repositories.ReviewLogRepositoryImpl import ReviewLogRepositoryImpl


@pytest.fixture
def mock_db_provider(mocker):
    mock_provider = mocker.Mock()
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_provider.get_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    return mock_provider


@pytest.fixture
def repository(mock_db_provider):
    return ReviewLogRepositoryImpl(mock_db_provider)


def test_add_inserts_review_log(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    review_log_data = {"state": "learning", "scheduled_days": 1}
    rating = 3
    reviewed_at = datetime.now(timezone.utc)
    scheduler_params_json = json.dumps([0.4, 0.6, 2.4, 5.8, 4.93])
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    mock_cursor.lastrowid = 1
    
    # Act
    repository.add(
        user_id=user_id,
        flashcard_id=flashcard_id,
        review_log_data=review_log_data,
        rating=rating,
        reviewed_at=reviewed_at,
        scheduler_params_json=scheduler_params_json
    )
    
    # Assert
    mock_cursor.execute.assert_called_once()
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO ReviewLogs" in sql_call
    
    # Sprawdzamy parametry
    params = mock_cursor.execute.call_args[0][1]
    assert params[0] == user_id
    assert params[1] == flashcard_id
    assert json.loads(params[2]) == review_log_data
    assert params[3] == rating
    assert isinstance(params[4], str)  # reviewed_at jako string
    assert params[5] == scheduler_params_json
    
    # Sprawdzamy czy wykonano commit
    mock_connection.commit.assert_called_once()


def test_get_review_logs_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy wyniki zapytania
    mock_cursor.fetchall.return_value = [
        (
            1,  # id
            user_id,  # user_profile_id
            flashcard_id,  # flashcard_id
            json.dumps({"state": "learning"}),  # review_log_data
            3,  # fsrs_rating
            "2023-05-13T12:00:00Z",  # reviewed_at
            json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
            "2023-05-13T12:00:00Z",  # created_at
        ),
        (
            2,  # id
            user_id,  # user_profile_id
            flashcard_id,  # flashcard_id
            json.dumps({"state": "review"}),  # review_log_data
            4,  # fsrs_rating
            "2023-05-14T12:00:00Z",  # reviewed_at
            json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
            "2023-05-14T12:00:00Z",  # created_at
        )
    ]
    
    # Act
    result = repository.get_review_logs_for_flashcard(user_id, flashcard_id)
    
    # Assert
    assert len(result) == 2
    
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "SELECT * FROM ReviewLogs" in sql_call
    assert "WHERE user_profile_id = ? AND flashcard_id = ?" in sql_call
    
    # Sprawdzamy parametry
    params = mock_cursor.execute.call_args[0][1]
    assert params[0] == user_id
    assert params[1] == flashcard_id
    
    # Sprawdzamy zawartość wyników
    assert result[0]["id"] == 1
    assert result[0]["user_profile_id"] == user_id
    assert result[0]["flashcard_id"] == flashcard_id
    assert result[0]["review_log_data"] == {"state": "learning"}
    assert result[0]["fsrs_rating"] == 3
    
    assert result[1]["id"] == 2
    assert result[1]["fsrs_rating"] == 4
    assert result[1]["review_log_data"] == {"state": "review"}


def test_get_review_logs_for_flashcard_empty_result(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy pusty wynik
    mock_cursor.fetchall.return_value = []
    
    # Act
    result = repository.get_review_logs_for_flashcard(user_id, flashcard_id)
    
    # Assert
    assert len(result) == 0
    mock_cursor.execute.assert_called_once()


def test_get_last_review_log_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy wynik zapytania - jeden rekord (ostatni log)
    mock_cursor.fetchone.return_value = (
        1,  # id
        user_id,  # user_profile_id
        flashcard_id,  # flashcard_id
        json.dumps({"state": "learning"}),  # review_log_data
        3,  # fsrs_rating
        "2023-05-13T12:00:00Z",  # reviewed_at
        json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
        "2023-05-13T12:00:00Z",  # created_at
    )
    
    # Act
    result = repository.get_last_review_log_for_flashcard(user_id, flashcard_id)
    
    # Assert
    assert result is not None
    assert result["id"] == 1
    assert result["user_profile_id"] == user_id
    assert result["flashcard_id"] == flashcard_id
    assert result["review_log_data"] == {"state": "learning"}
    assert result["fsrs_rating"] == 3
    
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "SELECT * FROM ReviewLogs" in sql_call
    assert "WHERE user_profile_id = ? AND flashcard_id = ?" in sql_call
    assert "ORDER BY reviewed_at DESC LIMIT 1" in sql_call


def test_get_last_review_log_for_flashcard_no_result(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy brak wyniku
    mock_cursor.fetchone.return_value = None
    
    # Act
    result = repository.get_last_review_log_for_flashcard(user_id, flashcard_id)
    
    # Assert
    assert result is None
    mock_cursor.execute.assert_called_once()


def test_get_review_logs_for_user(repository, mock_db_provider):
    # Arrange
    user_id = 1
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy wyniki zapytania
    mock_cursor.fetchall.return_value = [
        (
            1,  # id
            user_id,  # user_profile_id
            101,  # flashcard_id
            json.dumps({"state": "learning"}),  # review_log_data
            3,  # fsrs_rating
            "2023-05-13T12:00:00Z",  # reviewed_at
            json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
            "2023-05-13T12:00:00Z",  # created_at
        ),
        (
            2,  # id
            user_id,  # user_profile_id
            102,  # flashcard_id
            json.dumps({"state": "review"}),  # review_log_data
            4,  # fsrs_rating
            "2023-05-14T12:00:00Z",  # reviewed_at
            json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
            "2023-05-14T12:00:00Z",  # created_at
        )
    ]
    
    # Act
    result = repository.get_review_logs_for_user(user_id)
    
    # Assert
    assert len(result) == 2
    
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "SELECT * FROM ReviewLogs" in sql_call
    assert "WHERE user_profile_id = ?" in sql_call
    
    # Sprawdzamy parametry
    params = mock_cursor.execute.call_args[0][1]
    assert params[0] == user_id
    
    # Sprawdzamy zawartość wyników
    assert result[0]["flashcard_id"] == 101
    assert result[1]["flashcard_id"] == 102


def test_delete_review_logs_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy liczbę usuniętych wierszy
    mock_cursor.rowcount = 3
    
    # Act
    result = repository.delete_review_logs_for_flashcard(user_id, flashcard_id)
    
    # Assert
    assert result == 3
    
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "DELETE FROM ReviewLogs" in sql_call
    assert "WHERE user_profile_id = ? AND flashcard_id = ?" in sql_call
    
    # Sprawdzamy parametry
    params = mock_cursor.execute.call_args[0][1]
    assert params[0] == user_id
    assert params[1] == flashcard_id
    
    # Sprawdzamy czy wykonano commit
    mock_connection.commit.assert_called_once()


def test_delete_review_logs_for_user(repository, mock_db_provider):
    # Arrange
    user_id = 1
    
    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value
    
    # Symulujemy liczbę usuniętych wierszy
    mock_cursor.rowcount = 10
    
    # Act
    result = repository.delete_review_logs_for_user(user_id)
    
    # Assert
    assert result == 10
    
    # Sprawdzamy czy wywołano execute z odpowiednim zapytaniem SQL
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args[0][0]
    assert "DELETE FROM ReviewLogs" in sql_call
    assert "WHERE user_profile_id = ?" in sql_call
    
    # Sprawdzamy parametry
    params = mock_cursor.execute.call_args[0][1]
    assert params[0] == user_id
    
    # Sprawdzamy czy wykonano commit
    mock_connection.commit.assert_called_once()
