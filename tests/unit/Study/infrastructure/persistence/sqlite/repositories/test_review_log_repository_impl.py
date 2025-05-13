import json
import pytest
from datetime import datetime, timezone
import sqlite3
from unittest.mock import patch

from src.Study.infrastructure.persistence.sqlite.repositories.ReviewLogRepositoryImpl import ReviewLogRepositoryImpl


@pytest.fixture
def mock_db_provider(mocker):
    mock_provider = mocker.Mock()
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Skonfiguruj mock connection aby używał row_factory
    mock_connection.row_factory = sqlite3.Row

    mock_provider.get_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.execute.return_value = mock_cursor
    mock_connection.commit = mocker.Mock()
    return mock_provider


@pytest.fixture
def repository(mock_db_provider):
    # Patch _row_to_dict, aby obsłużyć mocki
    with patch.object(ReviewLogRepositoryImpl, "_row_to_dict") as mock_row_to_dict:
        # Skonfiguruj mock do zwracania odpowiednio sformatowanych słowników
        def convert_row_to_dict(row):
            if isinstance(row, tuple):
                return {
                    "id": row[0],
                    "user_profile_id": row[1],
                    "flashcard_id": row[2],
                    "review_log_data": json.loads(row[3]) if row[3] else None,
                    "fsrs_rating": row[4],
                    "reviewed_at": row[5],
                    "scheduler_params_at_review": json.loads(row[6]) if row[6] else None,
                    "created_at": row[7] if len(row) > 7 else None,
                }
            return row  # Obsługa innych przypadków

        mock_row_to_dict.side_effect = convert_row_to_dict
        repo = ReviewLogRepositoryImpl(mock_db_provider)
        # Nadpisz _execute_query, aby zwracał mock cursor
        repo._execute_query = lambda query, params=(): mock_db_provider.get_connection().cursor()
        yield repo


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
    # Powinno przejść bez błędów
    repository.add(
        user_id=user_id,
        flashcard_id=flashcard_id,
        review_log_data=review_log_data,
        rating=rating,
        reviewed_at=reviewed_at,
        scheduler_params_json=scheduler_params_json,
    )

    # Assert
    # Sprawdzamy tylko czy wywołano commit, co oznacza że operacja została zakończona pomyślnie
    mock_connection.commit.assert_called_once()


def test_get_review_logs_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2

    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value

    # Symulujemy wyniki zapytania
    rows = [
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
        ),
    ]
    mock_cursor.fetchall.return_value = rows

    # Act
    result = repository.get_review_logs_for_flashcard(user_id, flashcard_id)

    # Assert
    assert len(result) == 2

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


def test_get_last_review_log_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2

    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value

    # Symulujemy wynik zapytania - jeden rekord (ostatni log)
    row = (
        1,  # id
        user_id,  # user_profile_id
        flashcard_id,  # flashcard_id
        json.dumps({"state": "learning"}),  # review_log_data
        3,  # fsrs_rating
        "2023-05-13T12:00:00Z",  # reviewed_at
        json.dumps([0.4, 0.6, 2.4]),  # scheduler_params_at_review
        "2023-05-13T12:00:00Z",  # created_at
    )
    mock_cursor.fetchone.return_value = row

    # Act
    result = repository.get_last_review_log_for_flashcard(user_id, flashcard_id)

    # Assert
    assert result is not None
    assert result["id"] == 1
    assert result["user_profile_id"] == user_id
    assert result["flashcard_id"] == flashcard_id
    assert result["review_log_data"] == {"state": "learning"}
    assert result["fsrs_rating"] == 3


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


def test_get_review_logs_for_user(repository, mock_db_provider):
    # Arrange
    user_id = 1

    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value

    # Symulujemy wyniki zapytania
    rows = [
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
        ),
    ]
    mock_cursor.fetchall.return_value = rows

    # Act
    result = repository.get_review_logs_for_user(user_id)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["flashcard_id"] == 101
    assert result[1]["id"] == 2
    assert result[1]["flashcard_id"] == 102


def test_delete_review_logs_for_flashcard(repository, mock_db_provider):
    # Arrange
    user_id = 1
    flashcard_id = 2

    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value

    # Ustaw konkretną wartość rowcount zamiast obiektu Mock
    mock_cursor.rowcount = 3

    # Act
    result = repository.delete_review_logs_for_flashcard(user_id, flashcard_id)

    # Assert
    assert result == 3
    mock_connection.commit.assert_called_once()


def test_delete_review_logs_for_user(repository, mock_db_provider):
    # Arrange
    user_id = 1

    mock_connection = mock_db_provider.get_connection.return_value
    mock_cursor = mock_connection.cursor.return_value

    # Ustaw konkretną wartość rowcount zamiast obiektu Mock
    mock_cursor.rowcount = 10

    # Act
    result = repository.delete_review_logs_for_user(user_id)

    # Assert
    assert result == 10
    mock_connection.commit.assert_called_once()
