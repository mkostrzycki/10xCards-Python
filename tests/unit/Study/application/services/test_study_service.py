import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from src.Study.application.services.study_service import StudyService
from src.CardManagement.domain.models.Flashcard import Flashcard
from src.UserProfile.domain.models.user import User


@pytest.fixture
def mock_flashcard_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_review_log_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_session_service(mocker):
    mock = mocker.Mock()
    # Domyślnie symulujemy zalogowanego użytkownika
    mock_user = User(id=1, username="testuser", hashed_password=None, default_llm_model=None, app_theme=None)
    mock.get_current_user.return_value = mock_user
    mock.is_authenticated.return_value = True
    return mock


@pytest.fixture
def service(mock_flashcard_repository, mock_review_log_repository, mock_session_service):
    with patch("src.Study.application.services.study_service.get_config") as mock_get_config:
        # Symulujemy konfigurację FSRS
        mock_get_config.return_value = {
            "FSRS_DEFAULT_PARAMETERS": [
                0.4,
                0.6,
                2.4,
                5.8,
                4.93,
                0.94,
                0.86,
                0.01,
                1.49,
                0.14,
                0.94,
                2.18,
                0.05,
                0.34,
                1.26,
                0.29,
                2.61,
            ],
            "FSRS_DEFAULT_DESIRED_RETENTION": 0.9,
            "FSRS_DEFAULT_LEARNING_STEPS_MINUTES": [1, 10],
            "FSRS_DEFAULT_RELEARNING_STEPS_MINUTES": [10],
            "FSRS_MAXIMUM_INTERVAL": 36500,
            "FSRS_ENABLE_FUZZING": True,
        }

        # Tworzymy serwis z mockami
        service = StudyService(mock_flashcard_repository, mock_review_log_repository, mock_session_service)

        # Mockujemy bibliotekę FSRS
        service.scheduler = MagicMock()

        yield service


@pytest.fixture
def sample_flashcards():
    return [
        Flashcard(
            id=1,
            deck_id=1,
            front_text="Pytanie 1",
            back_text="Odpowiedź 1",
            source="manual",
            fsrs_state=json.dumps({"due": datetime.now(timezone.utc).isoformat()}),
        ),
        Flashcard(
            id=2,
            deck_id=1,
            front_text="Pytanie 2",
            back_text="Odpowiedź 2",
            source="manual",
            fsrs_state=json.dumps({"due": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}),
        ),
        Flashcard(
            id=3,
            deck_id=1,
            front_text="Pytanie 3",
            back_text="Odpowiedź 3",
            source="manual",
            fsrs_state=None,  # Nowa fiszka bez stanu FSRS
        ),
    ]


def test_start_session_loads_due_cards(service, mock_flashcard_repository, sample_flashcards):
    # Arrange
    deck_id = 1
    mock_flashcard_repository.list_by_deck_id.return_value = sample_flashcards

    # Mockujemy metody prywatne
    service._initialize_scheduler = MagicMock()
    service._load_and_prepare_fsrs_cards = MagicMock()
    service._filter_and_sort_due_cards = MagicMock()

    # Symulujemy, że tylko pierwsza fiszka jest due
    mock_fsrs_card = MagicMock()
    service._load_and_prepare_fsrs_cards.return_value = [(sample_flashcards[0], mock_fsrs_card)]
    service._filter_and_sort_due_cards.return_value = [(sample_flashcards[0], mock_fsrs_card)]

    # Act
    result = service.start_session(deck_id)

    # Assert
    assert result is not None
    flashcard, fsrs_card = result
    assert flashcard.id == 1
    assert service.current_deck_id == deck_id
    assert service.current_card_index == 0
    assert len(service.current_study_session_queue) == 1

    # Verify method calls
    service._initialize_scheduler.assert_called_once()
    mock_flashcard_repository.list_by_deck_id.assert_called_once_with(deck_id)
    service._load_and_prepare_fsrs_cards.assert_called_once()
    service._filter_and_sort_due_cards.assert_called_once()


def test_start_session_handles_no_due_cards(service, mock_flashcard_repository, sample_flashcards):
    # Arrange
    deck_id = 1
    mock_flashcard_repository.list_by_deck_id.return_value = sample_flashcards

    # Mockujemy metody prywatne
    service._initialize_scheduler = MagicMock()
    service._load_and_prepare_fsrs_cards = MagicMock()
    service._filter_and_sort_due_cards = MagicMock()

    # Symulujemy, że żadna fiszka nie jest due
    service._load_and_prepare_fsrs_cards.return_value = [(f, MagicMock()) for f in sample_flashcards]
    service._filter_and_sort_due_cards.return_value = []  # Brak fiszek due

    # Act
    result = service.start_session(deck_id)

    # Assert
    assert result is None
    assert service.current_deck_id == deck_id
    assert service.current_card_index == -1
    assert len(service.current_study_session_queue) == 0


def test_start_session_requires_authenticated_user(service, mock_session_service):
    # Arrange
    deck_id = 1
    mock_session_service.get_current_user.return_value = None
    mock_session_service.is_authenticated.return_value = False

    # Act & Assert
    with pytest.raises(ValueError, match="User must be logged in"):
        service.start_session(deck_id)


def test_record_review_updates_flashcard_and_saves_log(
    service, mock_flashcard_repository, mock_review_log_repository, sample_flashcards
):
    # Arrange
    flashcard_id = 1
    rating = 3  # Good

    # Symulujemy aktywną sesję nauki
    mock_fsrs_card = MagicMock()
    mock_updated_fsrs_card = MagicMock()
    mock_review_log = MagicMock()
    mock_review_log.review_datetime = datetime.now(timezone.utc)

    service.scheduler.review_card.return_value = (mock_updated_fsrs_card, mock_review_log)
    service.current_study_session_queue = [(sample_flashcards[0], mock_fsrs_card)]
    service.current_card_index = 0

    # Mockujemy to_dict dla mock_updated_fsrs_card i mock_review_log
    mock_updated_fsrs_card.to_dict.return_value = {"state": "updated"}
    mock_review_log.to_dict.return_value = {"review": "data"}

    # Mockujemy parametry schedulera
    service.scheduler.parameters = (0.4, 0.6, 2.4, 5.8, 4.93)

    # Act
    result = service.record_review(flashcard_id, rating)

    # Assert
    assert result is not None
    updated_flashcard, updated_fsrs_card = result

    # Verify flashcard was updated
    mock_flashcard_repository.update.assert_called_once()
    assert json.loads(updated_flashcard.fsrs_state) == {"state": "updated"}

    # Verify review log was saved
    mock_review_log_repository.add.assert_called_once()
    call_args = mock_review_log_repository.add.call_args[1]
    assert call_args["user_id"] == 1
    assert call_args["flashcard_id"] == flashcard_id
    assert call_args["rating"] == rating
    assert call_args["review_log_data"] == {"review": "data"}

    # Verify session state was updated
    assert service.current_study_session_queue[0][1] == mock_updated_fsrs_card


def test_record_review_validates_rating(service):
    # Arrange
    flashcard_id = 1
    invalid_rating = 5  # Ratings should be 1-4

    # Symulujemy aktywną sesję nauki
    mock_fsrs_card = MagicMock()
    service.current_study_session_queue = [
        (Flashcard(id=1, deck_id=1, front_text="Test", back_text="Test", source="manual"), mock_fsrs_card)
    ]
    service.current_card_index = 0

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid rating value"):
        service.record_review(flashcard_id, invalid_rating)


def test_record_review_validates_flashcard_id(service):
    # Arrange
    wrong_flashcard_id = 999  # Nie pasuje do aktualnej fiszki
    rating = 3

    # Symulujemy aktywną sesję nauki
    mock_fsrs_card = MagicMock()
    service.current_study_session_queue = [
        (Flashcard(id=1, deck_id=1, front_text="Test", back_text="Test", source="manual"), mock_fsrs_card)
    ]
    service.current_card_index = 0

    # Act & Assert
    with pytest.raises(ValueError, match="Flashcard ID mismatch"):
        service.record_review(wrong_flashcard_id, rating)


def test_proceed_to_next_card_advances_index(service, sample_flashcards):
    # Arrange
    mock_fsrs_card1 = MagicMock()
    mock_fsrs_card2 = MagicMock()

    service.current_study_session_queue = [
        (sample_flashcards[0], mock_fsrs_card1),
        (sample_flashcards[1], mock_fsrs_card2),
    ]
    service.current_card_index = 0

    # Act
    result = service.proceed_to_next_card()

    # Assert
    assert result is not None
    assert service.current_card_index == 1
    flashcard, fsrs_card = result
    assert flashcard.id == 2
    assert fsrs_card == mock_fsrs_card2


def test_proceed_to_next_card_returns_none_at_end(service, sample_flashcards):
    # Arrange
    mock_fsrs_card = MagicMock()

    service.current_study_session_queue = [(sample_flashcards[0], mock_fsrs_card)]
    service.current_card_index = 0

    # Act
    result = service.proceed_to_next_card()

    # Assert
    assert result is None
    assert service.current_card_index == 1


def test_get_session_progress(service, sample_flashcards):
    # Arrange
    mock_fsrs_card1 = MagicMock()
    mock_fsrs_card2 = MagicMock()
    mock_fsrs_card3 = MagicMock()

    service.current_study_session_queue = [
        (sample_flashcards[0], mock_fsrs_card1),
        (sample_flashcards[1], mock_fsrs_card2),
        (sample_flashcards[2], mock_fsrs_card3),
    ]

    # Test różnych stanów indeksu

    # Case 1: Przed rozpoczęciem
    service.current_card_index = -1
    assert service.get_session_progress() == (0, 3)

    # Case 2: Pierwsza karta
    service.current_card_index = 0
    assert service.get_session_progress() == (1, 3)

    # Case 3: Środkowa karta
    service.current_card_index = 1
    assert service.get_session_progress() == (2, 3)

    # Case 4: Ostatnia karta
    service.current_card_index = 2
    assert service.get_session_progress() == (3, 3)

    # Case 5: Po zakończeniu
    service.current_card_index = 3
    assert service.get_session_progress() == (3, 3)


def test_end_session_clears_state(service, sample_flashcards):
    # Arrange
    mock_fsrs_card = MagicMock()

    service.current_study_session_queue = [(sample_flashcards[0], mock_fsrs_card)]
    service.current_card_index = 0
    service.current_deck_id = 1

    # Act
    service.end_session()

    # Assert
    assert service.current_study_session_queue == []
    assert service.current_card_index == -1
    assert service.current_deck_id is None


def test_get_current_card_returns_none_when_no_session(service):
    # Arrange
    service.current_study_session_queue = []
    service.current_card_index = -1

    # Act
    result = service.get_current_card_for_review()

    # Assert
    assert result is None


def test_get_current_card_returns_card_when_session_active(service, sample_flashcards):
    # Arrange
    mock_fsrs_card = MagicMock()

    service.current_study_session_queue = [(sample_flashcards[0], mock_fsrs_card)]
    service.current_card_index = 0

    # Act
    result = service.get_current_card_for_review()

    # Assert
    assert result is not None
    flashcard, fsrs_card = result
    assert flashcard.id == 1
    assert fsrs_card == mock_fsrs_card
