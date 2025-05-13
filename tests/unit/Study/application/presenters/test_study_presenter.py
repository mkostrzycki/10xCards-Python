import pytest
from unittest.mock import Mock
from datetime import datetime

from src.Study.application.presenters.study_presenter import StudyPresenter
from src.CardManagement.domain.models.Flashcard import Flashcard


@pytest.fixture
def mock_view(mocker):
    """Mock dla widoku sesji nauki."""
    return mocker.Mock()


@pytest.fixture
def mock_study_service(mocker):
    """Mock dla serwisu nauki."""
    return mocker.Mock()


@pytest.fixture
def mock_navigation_controller(mocker):
    """Mock dla kontrolera nawigacji."""
    return mocker.Mock()


@pytest.fixture
def mock_session_service(mocker):
    """Mock dla serwisu sesji."""
    return mocker.Mock()


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


@pytest.fixture
def study_presenter(mock_view, mock_study_service, mock_navigation_controller, mock_session_service):
    """Presenter do testów."""
    return StudyPresenter(
        view=mock_view,
        study_service=mock_study_service,
        navigation_controller=mock_navigation_controller,
        session_service=mock_session_service,
        deck_id=10,
        deck_name="Python Basics",
    )


class TestInitializeSession:
    """Testy dla metody initialize_session."""

    def test_initialize_session_with_cards(self, study_presenter, mock_study_service, mock_view, sample_flashcard):
        # Arrange
        mock_study_service.start_session.return_value = (sample_flashcard, Mock())
        mock_study_service.get_session_progress.return_value = (1, 10)

        # Act
        study_presenter.initialize_session()

        # Assert
        mock_study_service.start_session.assert_called_once_with(10)
        mock_view.display_card_front.assert_called_once_with(sample_flashcard.front_text)
        mock_view.display_card_back.assert_called_once_with("")
        mock_view.hide_rating_buttons.assert_called_once()
        mock_view.enable_show_answer_button.assert_called_once()
        mock_view.update_progress.assert_called_once_with(1, 10)
        assert study_presenter.current_flashcard_id == sample_flashcard.id
        assert not study_presenter.answer_shown

    def test_initialize_session_no_cards(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        mock_study_service.start_session.return_value = None

        # Act
        study_presenter.initialize_session()

        # Assert
        mock_study_service.start_session.assert_called_once_with(10)
        mock_view.show_session_complete_message.assert_called_once()
        mock_view.display_card_front.assert_not_called()

    def test_initialize_session_error(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        mock_study_service.start_session.side_effect = Exception("Test error")

        # Act
        study_presenter.initialize_session()

        # Assert
        mock_study_service.start_session.assert_called_once_with(10)
        mock_view.show_error_message.assert_called_once()
        assert "Failed to initialize study session" in mock_view.show_error_message.call_args[0][0]


class TestHandleShowAnswer:
    """Testy dla metody handle_show_answer."""

    def test_handle_show_answer(self, study_presenter, mock_study_service, mock_view, sample_flashcard):
        # Arrange
        study_presenter.answer_shown = False
        study_presenter.current_flashcard_id = sample_flashcard.id
        mock_study_service.get_current_card_for_review.return_value = (sample_flashcard, Mock())

        # Act
        study_presenter.handle_show_answer()

        # Assert
        mock_study_service.get_current_card_for_review.assert_called_once()
        mock_view.display_card_front.assert_called_once_with(sample_flashcard.front_text)
        mock_view.display_card_back.assert_called_once_with(sample_flashcard.back_text)
        mock_view.show_rating_buttons.assert_called_once()
        mock_view.disable_show_answer_button.assert_called_once()
        assert study_presenter.answer_shown

    def test_handle_show_answer_already_shown(self, study_presenter, mock_study_service):
        # Arrange
        study_presenter.answer_shown = True

        # Act
        study_presenter.handle_show_answer()

        # Assert
        mock_study_service.get_current_card_for_review.assert_not_called()

    def test_handle_show_answer_no_current_card(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        study_presenter.answer_shown = False
        mock_study_service.get_current_card_for_review.return_value = None

        # Act
        study_presenter.handle_show_answer()

        # Assert
        mock_study_service.get_current_card_for_review.assert_called_once()
        mock_view.display_card_back.assert_not_called()
        mock_view.show_rating_buttons.assert_not_called()
        assert not study_presenter.answer_shown


class TestHandleRateCard:
    """Testy dla metody handle_rate_card."""

    def test_handle_rate_card_with_next_card(self, study_presenter, mock_study_service, mock_view, sample_flashcard):
        # Arrange
        study_presenter.current_flashcard_id = 1
        next_flashcard = Flashcard(
            id=2,
            deck_id=10,
            front_text="Co to jest TDD?",
            back_text="Test-Driven Development",
            fsrs_state=None,
            source="manual",
            ai_model_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_study_service.proceed_to_next_card.return_value = (next_flashcard, Mock())
        mock_study_service.get_session_progress.return_value = (2, 10)

        # Act
        study_presenter.handle_rate_card(3)  # Rating 3 (Good)

        # Assert
        mock_study_service.record_review.assert_called_once_with(1, 3)
        mock_study_service.proceed_to_next_card.assert_called_once()
        mock_view.display_card_front.assert_called_once_with(next_flashcard.front_text)
        mock_view.display_card_back.assert_called_once_with("")
        mock_view.hide_rating_buttons.assert_called_once()
        mock_view.enable_show_answer_button.assert_called_once()
        mock_view.update_progress.assert_called_once_with(2, 10)
        assert study_presenter.current_flashcard_id == next_flashcard.id
        assert not study_presenter.answer_shown

    def test_handle_rate_card_session_complete(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        study_presenter.current_flashcard_id = 1
        mock_study_service.proceed_to_next_card.return_value = None  # Brak następnej karty

        # Act
        study_presenter.handle_rate_card(4)  # Rating 4 (Easy)

        # Assert
        mock_study_service.record_review.assert_called_once_with(1, 4)
        mock_study_service.proceed_to_next_card.assert_called_once()
        mock_view.show_session_complete_message.assert_called_once()
        mock_view.display_card_front.assert_not_called()

    def test_handle_rate_card_no_current_flashcard(self, study_presenter, mock_study_service):
        # Arrange
        study_presenter.current_flashcard_id = None

        # Act
        study_presenter.handle_rate_card(2)

        # Assert
        mock_study_service.record_review.assert_not_called()
        mock_study_service.proceed_to_next_card.assert_not_called()

    def test_handle_rate_card_error(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        study_presenter.current_flashcard_id = 1
        mock_study_service.record_review.side_effect = Exception("Test error")

        # Act
        study_presenter.handle_rate_card(1)

        # Assert
        mock_study_service.record_review.assert_called_once_with(1, 1)
        mock_view.show_error_message.assert_called_once()
        assert "Failed to process rating" in mock_view.show_error_message.call_args[0][0]


class TestHandleEndSession:
    """Testy dla metody handle_end_session."""

    def test_handle_end_session(self, study_presenter, mock_study_service, mock_navigation_controller):
        # Act
        study_presenter.handle_end_session()

        # Assert
        mock_study_service.end_session.assert_called_once()
        mock_navigation_controller.navigate.assert_called_once_with("/decks/10")


class TestHelperMethods:
    """Testy dla metod pomocniczych."""

    def test_update_view_with_card_show_answer(self, study_presenter, mock_view, sample_flashcard):
        # Act
        study_presenter._update_view_with_card(sample_flashcard, show_answer=True)

        # Assert
        mock_view.display_card_front.assert_called_once_with(sample_flashcard.front_text)
        mock_view.display_card_back.assert_called_once_with(sample_flashcard.back_text)
        mock_view.show_rating_buttons.assert_called_once()
        mock_view.disable_show_answer_button.assert_called_once()

    def test_update_view_with_card_hide_answer(self, study_presenter, mock_view, sample_flashcard):
        # Act
        study_presenter._update_view_with_card(sample_flashcard, show_answer=False)

        # Assert
        mock_view.display_card_front.assert_called_once_with(sample_flashcard.front_text)
        mock_view.display_card_back.assert_called_once_with("")
        mock_view.hide_rating_buttons.assert_called_once()
        mock_view.enable_show_answer_button.assert_called_once()

    def test_update_progress(self, study_presenter, mock_study_service, mock_view):
        # Arrange
        mock_study_service.get_session_progress.return_value = (3, 10)

        # Act
        study_presenter._update_progress()

        # Assert
        mock_study_service.get_session_progress.assert_called_once()
        mock_view.update_progress.assert_called_once_with(3, 10)
