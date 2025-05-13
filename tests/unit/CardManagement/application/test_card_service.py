import pytest
from datetime import datetime

from CardManagement.application.card_service import CardService
from CardManagement.domain.models.Flashcard import Flashcard


@pytest.fixture
def flashcard_repository_mock(mocker):
    """Mock dla repozytorium fiszek."""
    return mocker.Mock()


@pytest.fixture
def card_service(flashcard_repository_mock):
    """Serwis CardService z mockiem repozytorium."""
    return CardService(flashcard_repository_mock)


@pytest.fixture
def sample_flashcard():
    """Przykładowa fiszka do testów."""
    return Flashcard(
        id=1,
        deck_id=10,
        front_text="Co to jest Python?",
        back_text="Język programowania wysokiego poziomu.",
        fsrs_state=None,
        source="manual",
        ai_model_name=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestCreateFlashcard:
    """Testy dla metody create_flashcard."""

    def test_create_flashcard_success(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        deck_id = 10
        front_text = "Co to jest TDD?"
        back_text = "Test-driven development - metodologia pisania testów przed kodem."

        # Skonfigurowanie mocka repozytorium
        flashcard_repository_mock.add.return_value = sample_flashcard

        # Act
        result = card_service.create_flashcard(deck_id=deck_id, front_text=front_text, back_text=back_text)

        # Assert
        assert result == sample_flashcard
        flashcard_repository_mock.add.assert_called_once()
        # Sprawdzenie parametrów utworzonej fiszki
        created_flashcard = flashcard_repository_mock.add.call_args[0][0]
        assert created_flashcard.deck_id == deck_id
        assert created_flashcard.front_text == front_text
        assert created_flashcard.back_text == back_text
        assert created_flashcard.source == "manual"
        assert created_flashcard.ai_model_name is None

    def test_create_flashcard_with_ai_source(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        deck_id = 10
        front_text = "Co to jest AI?"
        back_text = "Sztuczna inteligencja."
        source = "ai-generated"
        ai_model_name = "gpt-4"

        # Skonfigurowanie mocka repozytorium
        flashcard_repository_mock.add.return_value = sample_flashcard

        # Act
        result = card_service.create_flashcard(
            deck_id=deck_id, front_text=front_text, back_text=back_text, source=source, ai_model_name=ai_model_name
        )

        # Assert
        assert result == sample_flashcard
        flashcard_repository_mock.add.assert_called_once()
        created_flashcard = flashcard_repository_mock.add.call_args[0][0]
        assert created_flashcard.source == source
        assert created_flashcard.ai_model_name == ai_model_name

    def test_create_flashcard_with_empty_front(self, card_service):
        # Arrange
        deck_id = 10
        front_text = ""  # Pusty tekst na przodzie
        back_text = "Jakaś odpowiedź"

        # Act & Assert
        with pytest.raises(ValueError, match="Tekst na przedniej stronie nie może być pusty"):
            card_service.create_flashcard(deck_id, front_text, back_text)

    def test_create_flashcard_with_empty_back(self, card_service):
        # Arrange
        deck_id = 10
        front_text = "Jakieś pytanie"
        back_text = ""  # Pusty tekst na tyle

        # Act & Assert
        with pytest.raises(ValueError, match="Tekst na tylnej stronie nie może być pusty"):
            card_service.create_flashcard(deck_id, front_text, back_text)

    def test_create_flashcard_with_too_long_front(self, card_service):
        # Arrange
        deck_id = 10
        front_text = "X" * 201  # 201 znaków - za długie
        back_text = "Odpowiedź"

        # Act & Assert
        with pytest.raises(ValueError, match="Tekst na przedniej stronie nie może być dłuższy niż 200 znaków"):
            card_service.create_flashcard(deck_id, front_text, back_text)

    def test_create_flashcard_with_too_long_back(self, card_service):
        # Arrange
        deck_id = 10
        front_text = "Pytanie"
        back_text = "X" * 501  # 501 znaków - za długie

        # Act & Assert
        with pytest.raises(ValueError, match="Tekst na tylnej stronie nie może być dłuższy niż 500 znaków"):
            card_service.create_flashcard(deck_id, front_text, back_text)

    def test_create_flashcard_repository_error(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_repository_mock.add.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            card_service.create_flashcard(10, "Pytanie", "Odpowiedź")


class TestUpdateFlashcard:
    """Testy dla metody update_flashcard."""

    def test_update_flashcard_success(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_id = 1
        new_front_text = "Nowe pytanie"
        new_back_text = "Nowa odpowiedź"

        # Skonfigurowanie mocka repozytorium
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard

        # Act
        card_service.update_flashcard(flashcard_id, new_front_text, new_back_text)

        # Assert
        flashcard_repository_mock.get_by_id.assert_called_once_with(flashcard_id)
        flashcard_repository_mock.update.assert_called_once()
        # Sprawdź czy pola zostały zaktualizowane
        assert sample_flashcard.front_text == new_front_text
        assert sample_flashcard.back_text == new_back_text

    def test_update_flashcard_change_source(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_id = 1
        new_source = "ai-edited"

        # Skonfigurowanie mocka repozytorium
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard

        # Act
        card_service.update_flashcard(
            flashcard_id, sample_flashcard.front_text, sample_flashcard.back_text, source=new_source
        )

        # Assert
        assert sample_flashcard.source == new_source
        flashcard_repository_mock.update.assert_called_once()

    def test_update_flashcard_not_found(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_id = 999  # Nieistniejące ID
        flashcard_repository_mock.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fiszka nie istnieje"):
            card_service.update_flashcard(flashcard_id, "Pytanie", "Odpowiedź")

    def test_update_flashcard_repository_error(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard
        flashcard_repository_mock.update.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            card_service.update_flashcard(1, "Nowe pytanie", "Nowa odpowiedź")


class TestListByDeckId:
    """Testy dla metody list_by_deck_id."""

    def test_list_by_deck_id_with_flashcards(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        deck_id = 10
        flashcards = [sample_flashcard, sample_flashcard]
        flashcard_repository_mock.list_by_deck_id.return_value = flashcards

        # Act
        result = card_service.list_by_deck_id(deck_id)

        # Assert
        assert result == flashcards
        flashcard_repository_mock.list_by_deck_id.assert_called_once_with(deck_id)

    def test_list_by_deck_id_empty(self, card_service, flashcard_repository_mock):
        # Arrange
        deck_id = 10
        flashcard_repository_mock.list_by_deck_id.return_value = []

        # Act
        result = card_service.list_by_deck_id(deck_id)

        # Assert
        assert result == []
        flashcard_repository_mock.list_by_deck_id.assert_called_once_with(deck_id)

    def test_list_by_deck_id_repository_error(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_repository_mock.list_by_deck_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            card_service.list_by_deck_id(10)


class TestDeleteFlashcard:
    """Testy dla metody delete_flashcard."""

    def test_delete_flashcard_success(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_id = 1
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard

        # Act
        card_service.delete_flashcard(flashcard_id)

        # Assert
        flashcard_repository_mock.get_by_id.assert_called_once_with(flashcard_id)
        flashcard_repository_mock.delete.assert_called_once_with(flashcard_id)

    def test_delete_flashcard_not_found(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_id = 999  # Nieistniejące ID
        flashcard_repository_mock.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fiszka nie istnieje"):
            card_service.delete_flashcard(flashcard_id)

        # Repository delete nie powinno być wywołane
        flashcard_repository_mock.delete.assert_not_called()

    def test_delete_flashcard_repository_error(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard
        flashcard_repository_mock.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            card_service.delete_flashcard(1)


class TestGetFlashcard:
    """Testy dla metody get_flashcard."""

    def test_get_flashcard_found(self, card_service, flashcard_repository_mock, sample_flashcard):
        # Arrange
        flashcard_id = 1
        flashcard_repository_mock.get_by_id.return_value = sample_flashcard

        # Act
        result = card_service.get_flashcard(flashcard_id)

        # Assert
        assert result == sample_flashcard
        flashcard_repository_mock.get_by_id.assert_called_once_with(flashcard_id)

    def test_get_flashcard_not_found(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_id = 999  # Nieistniejące ID
        flashcard_repository_mock.get_by_id.return_value = None

        # Act
        result = card_service.get_flashcard(flashcard_id)

        # Assert
        assert result is None
        flashcard_repository_mock.get_by_id.assert_called_once_with(flashcard_id)

    def test_get_flashcard_repository_error(self, card_service, flashcard_repository_mock):
        # Arrange
        flashcard_repository_mock.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            card_service.get_flashcard(1)
