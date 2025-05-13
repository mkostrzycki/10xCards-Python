import pytest
from datetime import datetime
from sqlite3 import IntegrityError

from src.DeckManagement.application.deck_service import DeckService
from src.DeckManagement.domain.models.Deck import Deck


@pytest.fixture
def deck_repository_mock(mocker):
    """Mock dla repozytorium talii."""
    return mocker.Mock()


@pytest.fixture
def deck_service(deck_repository_mock):
    """Serwis DeckService z mockiem repozytorium."""
    return DeckService(deck_repository_mock)


@pytest.fixture
def sample_deck():
    """Przykładowa talia do testów."""
    return Deck(id=1, user_id=5, name="Python Basics", created_at=datetime.now(), updated_at=datetime.now())


class TestCreateDeck:
    """Testy dla metody create_deck."""

    def test_create_deck_success(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        user_id = 5
        name = "Python Basics"

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_name.return_value = None  # Brak istniejącej talii o tej nazwie
        deck_repository_mock.add.return_value = sample_deck

        # Act
        result = deck_service.create_deck(name=name, user_id=user_id)

        # Assert
        assert result == sample_deck
        deck_repository_mock.get_by_name.assert_called_once_with(name, user_id)
        deck_repository_mock.add.assert_called_once()
        # Sprawdzenie parametrów utworzonej talii
        created_deck = deck_repository_mock.add.call_args[0][0]
        assert created_deck.user_id == user_id
        assert created_deck.name == name

    def test_create_deck_with_empty_name(self, deck_service):
        # Arrange
        user_id = 5
        name = ""  # Pusta nazwa

        # Act & Assert
        with pytest.raises(ValueError, match="Nazwa talii nie może być pusta"):
            deck_service.create_deck(name=name, user_id=user_id)

    def test_create_deck_with_too_long_name(self, deck_service):
        # Arrange
        user_id = 5
        name = "X" * 51  # 51 znaków - za długa nazwa

        # Act & Assert
        with pytest.raises(ValueError, match="Nazwa talii nie może być dłuższa niż 50 znaków"):
            deck_service.create_deck(name=name, user_id=user_id)

    def test_create_deck_duplicate_name(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        user_id = 5
        name = "Python Basics"

        # Skonfigurowanie mocka repozytorium - talia o tej nazwie już istnieje
        deck_repository_mock.get_by_name.return_value = sample_deck

        # Act & Assert
        with pytest.raises(IntegrityError, match="Talia o tej nazwie już istnieje"):
            deck_service.create_deck(name=name, user_id=user_id)

    def test_create_deck_repository_error(self, deck_service, deck_repository_mock):
        # Arrange
        user_id = 5
        name = "Python Basics"

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_name.return_value = None  # Brak istniejącej talii o tej nazwie
        deck_repository_mock.add.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            deck_service.create_deck(name=name, user_id=user_id)


class TestGetDeck:
    """Testy dla metody get_deck."""

    def test_get_deck_found(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck

        # Act
        result = deck_service.get_deck(deck_id=deck_id, user_id=user_id)

        # Assert
        assert result == sample_deck
        deck_repository_mock.get_by_id.assert_called_once_with(deck_id, user_id)

    def test_get_deck_not_found(self, deck_service, deck_repository_mock):
        # Arrange
        deck_id = 999  # Nieistniejące ID
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = None

        # Act
        result = deck_service.get_deck(deck_id=deck_id, user_id=user_id)

        # Assert
        assert result is None
        deck_repository_mock.get_by_id.assert_called_once_with(deck_id, user_id)

    def test_get_deck_repository_error(self, deck_service, deck_repository_mock):
        # Arrange
        deck_id = 1
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            deck_service.get_deck(deck_id=deck_id, user_id=user_id)


class TestListDecks:
    """Testy dla metody list_decks."""

    def test_list_decks_with_items(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        user_id = 5
        decks = [
            sample_deck,
            Deck(id=2, user_id=user_id, name="Another Deck", created_at=datetime.now(), updated_at=datetime.now()),
        ]

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.list_all.return_value = decks

        # Act
        result = deck_service.list_decks(user_id=user_id)

        # Assert
        assert result == decks
        assert len(result) == 2
        deck_repository_mock.list_all.assert_called_once_with(user_id)

    def test_list_decks_empty(self, deck_service, deck_repository_mock):
        # Arrange
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.list_all.return_value = []

        # Act
        result = deck_service.list_decks(user_id=user_id)

        # Assert
        assert result == []
        deck_repository_mock.list_all.assert_called_once_with(user_id)

    def test_list_decks_repository_error(self, deck_service, deck_repository_mock):
        # Arrange
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.list_all.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            deck_service.list_decks(user_id=user_id)


class TestDeleteDeck:
    """Testy dla metody delete_deck."""

    def test_delete_deck_success(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck

        # Act
        deck_service.delete_deck(deck_id=deck_id, user_id=user_id)

        # Assert
        deck_repository_mock.get_by_id.assert_called_once_with(deck_id, user_id)
        deck_repository_mock.delete.assert_called_once_with(deck_id, user_id)

    def test_delete_deck_not_found(self, deck_service, deck_repository_mock):
        # Arrange
        deck_id = 999  # Nieistniejące ID
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Talia nie istnieje lub nie należy do tego użytkownika"):
            deck_service.delete_deck(deck_id=deck_id, user_id=user_id)

        # Repository delete nie powinno być wywołane
        deck_repository_mock.delete.assert_not_called()

    def test_delete_deck_repository_error(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck
        deck_repository_mock.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            deck_service.delete_deck(deck_id=deck_id, user_id=user_id)


class TestRenameDeck:
    """Testy dla metody rename_deck."""

    def test_rename_deck_success(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        new_name = "Python Advanced"

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck
        deck_repository_mock.get_by_name.return_value = None  # Brak innej talii o takiej nazwie

        # Act
        deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)

        # Assert
        deck_repository_mock.get_by_id.assert_called_once_with(deck_id, user_id)
        deck_repository_mock.get_by_name.assert_called_once_with(new_name, user_id)
        deck_repository_mock.update.assert_called_once()
        assert sample_deck.name == new_name

    def test_rename_deck_same_name(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        same_name = sample_deck.name  # Ta sama nazwa co wcześniej

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck

        # Act
        deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=same_name)

        # Assert
        deck_repository_mock.get_by_id.assert_called_once_with(deck_id, user_id)
        # Nie powinno sprawdzać duplikatu nazwy, jeśli to ta sama nazwa
        deck_repository_mock.get_by_name.assert_not_called()
        deck_repository_mock.update.assert_called_once()

    def test_rename_deck_empty_name(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        new_name = ""  # Pusta nazwa

        # Act & Assert
        with pytest.raises(ValueError, match="Nazwa talii nie może być pusta"):
            deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)

    def test_rename_deck_too_long_name(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        new_name = "X" * 51  # 51 znaków - za długa nazwa

        # Act & Assert
        with pytest.raises(ValueError, match="Nazwa talii nie może być dłuższa niż 50 znaków"):
            deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)

    def test_rename_deck_not_found(self, deck_service, deck_repository_mock):
        # Arrange
        deck_id = 999  # Nieistniejące ID
        user_id = 5
        new_name = "New Deck Name"

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Talia nie istnieje lub nie należy do tego użytkownika"):
            deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)

    def test_rename_deck_duplicate_name(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        new_name = "Another Deck"
        other_deck = Deck(id=2, user_id=user_id, name=new_name, created_at=datetime.now(), updated_at=datetime.now())

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck
        deck_repository_mock.get_by_name.return_value = other_deck  # Inna talia o tej samej nazwie już istnieje

        # Act & Assert
        with pytest.raises(IntegrityError, match="Talia o tej nazwie już istnieje"):
            deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)

    def test_rename_deck_repository_error(self, deck_service, deck_repository_mock, sample_deck):
        # Arrange
        deck_id = 1
        user_id = 5
        new_name = "Python Advanced"

        # Skonfigurowanie mocka repozytorium
        deck_repository_mock.get_by_id.return_value = sample_deck
        deck_repository_mock.get_by_name.return_value = None
        deck_repository_mock.update.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            deck_service.rename_deck(deck_id=deck_id, user_id=user_id, new_name=new_name)
