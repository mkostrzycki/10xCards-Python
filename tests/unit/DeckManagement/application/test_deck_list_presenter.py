"""Unit tests for DeckListPresenter."""

import pytest
from unittest.mock import Mock, call
from datetime import datetime

from DeckManagement.application.presenters.deck_list_presenter import DeckListPresenter, DeckViewModel


@pytest.fixture
def mock_view():
    """Create a mock view implementing IDeckListView."""
    view = Mock()
    view.display_decks = Mock()
    view.show_loading = Mock()
    view.show_error = Mock()
    view.show_toast = Mock()
    view.clear_deck_selection = Mock()
    view.enable_study_button = Mock()
    return view


@pytest.fixture
def mock_deck_service():
    """Create a mock DeckService."""
    service = Mock()
    service.list_decks = Mock()
    service.create_deck = Mock()
    service.delete_deck = Mock()
    return service


@pytest.fixture
def mock_session_service():
    """Create a mock SessionService."""
    service = Mock()
    service.is_authenticated = Mock(return_value=True)
    service.get_current_user = Mock(return_value=Mock(id=1))
    return service


@pytest.fixture
def mock_navigation():
    """Create a mock navigation controller."""
    controller = Mock()
    controller.navigate = Mock()
    return controller


@pytest.fixture
def presenter(mock_view, mock_deck_service, mock_session_service, mock_navigation):
    """Create a DeckListPresenter instance with mock dependencies."""
    return DeckListPresenter(
        view=mock_view,
        deck_service=mock_deck_service,
        session_service=mock_session_service,
        navigation_controller=mock_navigation,
    )


@pytest.fixture
def deck_factory():
    """Factory for creating mock deck objects."""

    def _create_deck(id, name, created_at):
        return Mock(
            id=id,
            name=name,
            created_at=created_at,
            updated_at=created_at,  # Same as created_at for simplicity
            user_id=1,
        )

    return _create_deck


def test_load_decks_success(presenter, mock_view, mock_deck_service, deck_factory):
    """Test loading decks successfully."""
    # Arrange
    mock_decks = [
        deck_factory(1, "Test Deck 1", datetime(2024, 1, 1)),
        deck_factory(2, "Test Deck 2", datetime(2024, 1, 2)),
    ]
    mock_deck_service.list_decks.return_value = mock_decks

    # Act
    presenter.load_decks()

    # Assert
    mock_view.show_loading.assert_has_calls([call(True), call(False)])
    mock_deck_service.list_decks.assert_called_once_with(1)
    mock_view.display_decks.assert_called_once()
    displayed_decks = mock_view.display_decks.call_args[0][0]
    assert len(displayed_decks) == 2
    assert all(isinstance(deck, DeckViewModel) for deck in displayed_decks)
    assert displayed_decks[0].id == 1
    assert displayed_decks[1].id == 2
    mock_view.clear_deck_selection.assert_called_once()
    mock_view.enable_study_button.assert_called_once_with(False)


def test_load_decks_not_authenticated(presenter, mock_view, mock_session_service, mock_navigation):
    """Test loading decks when user is not authenticated."""
    # Arrange
    mock_session_service.is_authenticated.return_value = False

    # Act
    presenter.load_decks()

    # Assert
    mock_view.show_toast.assert_called_once_with("Błąd", "Musisz być zalogowany aby przeglądać talie.")
    mock_navigation.navigate.assert_called_once_with("/profiles")
    mock_view.show_loading.assert_not_called()


def test_load_decks_error(presenter, mock_view, mock_deck_service):
    """Test loading decks with error."""
    # Arrange
    mock_deck_service.list_decks.side_effect = Exception("Test error")

    # Act
    presenter.load_decks()

    # Assert
    mock_view.show_loading.assert_has_calls([call(True), call(False)])
    mock_view.show_error.assert_called_once()
    assert "Test error" in mock_view.show_error.call_args[0][0]


def test_handle_deck_creation_success(presenter, mock_view, mock_deck_service, mock_session_service):
    """Test successful deck creation."""
    # Act
    presenter.handle_deck_creation("Test Deck")

    # Assert
    mock_deck_service.create_deck.assert_called_once_with(name="Test Deck", user_id=1)
    mock_view.show_toast.assert_called_once_with("Sukces", "Utworzono nową talię: Test Deck")


def test_handle_deck_creation_validation(presenter, mock_view, mock_deck_service):
    """Test deck creation with validation errors."""
    # Act
    presenter.handle_deck_creation("")

    # Assert
    mock_deck_service.create_deck.assert_not_called()
    mock_view.show_toast.assert_called_once_with("Błąd", "Nazwa talii nie może być pusta")


def test_handle_deck_deletion_confirmed(presenter, mock_view, mock_deck_service):
    """Test successful deck deletion."""
    # Arrange
    presenter.deleting_deck_id = 1

    # Act
    presenter.handle_deck_deletion_confirmed()

    # Assert
    mock_deck_service.delete_deck.assert_called_once_with(1, 1)
    mock_view.show_toast.assert_called_once_with("Sukces", "Talia została usunięta")


def test_handle_deck_selected(presenter, mock_view, mock_navigation):
    """Test deck selection."""
    # Act
    presenter.handle_deck_selected(1)

    # Assert
    mock_view.enable_study_button.assert_called_once_with(True)
    mock_navigation.navigate.assert_called_once_with("/decks/1/cards")


def test_start_study_session(presenter, mock_view, mock_navigation):
    """Test starting study session."""
    # Act
    presenter.start_study_session(1)

    # Assert
    mock_navigation.navigate.assert_called_once_with("/study/session/1")
