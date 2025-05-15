"""Unit tests for CardListPresenter."""

import pytest
from unittest.mock import Mock, call
from datetime import datetime

from CardManagement.application.presenters.card_list_presenter import CardListPresenter, FlashcardViewModel


@pytest.fixture
def mock_view():
    """Create a mock view implementing ICardListView."""
    view = Mock()
    view.display_cards = Mock()
    view.show_loading = Mock()
    view.show_error = Mock()
    view.show_toast = Mock()
    view.clear_card_selection = Mock()
    return view


@pytest.fixture
def mock_card_service():
    """Create a mock CardService."""
    service = Mock()
    service.list_by_deck_id = Mock()
    service.delete_flashcard = Mock()
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
def presenter(mock_view, mock_card_service, mock_session_service, mock_navigation):
    """Create a CardListPresenter instance with mock dependencies."""
    return CardListPresenter(
        view=mock_view,
        card_service=mock_card_service,
        session_service=mock_session_service,
        navigation_controller=mock_navigation,
        deck_id=1,
        deck_name="Test Deck",
    )


@pytest.fixture
def flashcard_factory():
    """Factory for creating mock flashcard objects."""

    def _create_flashcard(id, front_text, back_text):
        return Mock(
            id=id,
            front_text=front_text,
            back_text=back_text,
            source="manual",
            deck_id=1,
            fsrs_state=None,
            ai_model_name=None,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

    return _create_flashcard


def test_load_cards_success(presenter, mock_view, mock_card_service, flashcard_factory):
    """Test loading cards successfully."""
    # Arrange
    mock_cards = [flashcard_factory(1, "Front 1", "Back 1"), flashcard_factory(2, "Front 2", "Back 2")]
    mock_card_service.list_by_deck_id.return_value = mock_cards

    # Act
    presenter.load_cards()

    # Assert
    mock_view.show_loading.assert_has_calls([call(True), call(False)])
    mock_card_service.list_by_deck_id.assert_called_once_with(1)
    mock_view.display_cards.assert_called_once()
    displayed_cards = mock_view.display_cards.call_args[0][0]
    assert len(displayed_cards) == 2
    assert all(isinstance(card, FlashcardViewModel) for card in displayed_cards)
    assert displayed_cards[0].id == 1
    assert displayed_cards[1].id == 2


def test_load_cards_not_authenticated(presenter, mock_view, mock_session_service, mock_navigation):
    """Test loading cards when user is not authenticated."""
    # Arrange
    mock_session_service.is_authenticated.return_value = False

    # Act
    presenter.load_cards()

    # Assert
    mock_view.show_toast.assert_called_once_with("Błąd", "Musisz być zalogowany aby przeglądać fiszki.")
    mock_navigation.navigate.assert_called_once_with("/profiles")
    mock_view.show_loading.assert_not_called()


def test_load_cards_error(presenter, mock_view, mock_card_service):
    """Test loading cards with error."""
    # Arrange
    mock_card_service.list_by_deck_id.side_effect = Exception("Test error")

    # Act
    presenter.load_cards()

    # Assert
    mock_view.show_loading.assert_has_calls([call(True), call(False)])
    mock_view.show_error.assert_called_once()
    assert "Test error" in mock_view.show_error.call_args[0][0]


def test_add_flashcard(presenter, mock_navigation):
    """Test navigating to add flashcard view."""
    # Act
    presenter.add_flashcard()

    # Assert
    mock_navigation.navigate.assert_called_once_with("/decks/1/cards/new")


def test_edit_flashcard(presenter, mock_navigation):
    """Test navigating to edit flashcard view."""
    # Act
    presenter.edit_flashcard(1)

    # Assert
    mock_navigation.navigate.assert_called_once_with("/decks/1/cards/1/edit")


def test_delete_flashcard_success(presenter, mock_view, mock_card_service):
    """Test successful flashcard deletion."""
    # Setup
    presenter.deleting_id = 1

    # Act
    presenter.handle_flashcard_deletion_confirmed()

    # Assert
    mock_card_service.delete_flashcard.assert_called_once_with(1)
    mock_view.show_toast.assert_called_once_with("Sukces", "Fiszka została usunięta")


def test_delete_flashcard_error(presenter, mock_view, mock_card_service):
    """Test flashcard deletion with error."""
    # Setup
    presenter.deleting_id = 1
    mock_card_service.delete_flashcard.side_effect = Exception("Test error")

    # Act
    presenter.handle_flashcard_deletion_confirmed()

    # Assert
    mock_card_service.delete_flashcard.assert_called_once_with(1)
    mock_view.show_error.assert_called_once()
    assert "Test error" in mock_view.show_error.call_args[0][0]


def test_generate_with_ai(presenter, mock_navigation):
    """Test navigating to AI generation view."""
    # Act
    presenter.generate_with_ai()

    # Assert
    mock_navigation.navigate.assert_called_once_with("/decks/1/cards/generate-ai")


def test_start_study_session(presenter, mock_navigation):
    """Test starting study session."""
    # Act
    presenter.start_study_session()

    # Assert
    mock_navigation.navigate.assert_called_once_with("/study/session/1")
