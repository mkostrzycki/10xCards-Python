"""Presenter for the study session view."""

import logging
from typing import Optional, Protocol

from CardManagement.domain.models.Flashcard import Flashcard
from Study.application.services.study_service import StudyService
from Shared.application.session_service import SessionService

logger = logging.getLogger(__name__)


class StudySessionViewInterface(Protocol):
    """Interface for the study session view."""

    def display_card_front(self, front_text: str) -> None: ...
    def display_card_back(self, back_text: str) -> None: ...
    def show_rating_buttons(self) -> None: ...
    def hide_rating_buttons(self) -> None: ...
    def enable_show_answer_button(self) -> None: ...
    def disable_show_answer_button(self) -> None: ...
    def update_progress(self, current: int, total: int) -> None: ...
    def show_session_complete_message(self) -> None: ...
    def show_error_message(self, message: str) -> None: ...


class NavigationControllerInterface(Protocol):
    """Interface for the navigation controller."""

    def navigate(self, route: str) -> None: ...


class StudyPresenter:
    """Presenter for the study session view."""

    def __init__(
        self,
        view: StudySessionViewInterface,
        study_service: StudyService,
        navigation_controller: NavigationControllerInterface,
        session_service: SessionService,
        deck_id: int,
        deck_name: str,
    ):
        """Initialize the study presenter.

        Args:
            view: The study session view.
            study_service: The study service.
            navigation_controller: The navigation controller.
            session_service: The session service.
            deck_id: The ID of the deck being studied.
            deck_name: The name of the deck being studied.
        """
        self.view = view
        self.study_service = study_service
        self.navigation_controller = navigation_controller
        self.session_service = session_service
        self.deck_id = deck_id
        self.deck_name = deck_name

        # State
        self.current_flashcard_id: Optional[int] = None
        self.answer_shown: bool = False

    def initialize_session(self) -> None:
        """Initialize the study session."""
        try:
            # Start the session and get the first card
            first_card = self.study_service.start_session(self.deck_id)

            if first_card:
                flashcard, _ = first_card
                self.current_flashcard_id = flashcard.id
                self._update_view_with_card(flashcard, show_answer=False)
                self._update_progress()
            else:
                # No cards due for review
                self.view.show_session_complete_message()
                logger.info(f"No cards due for review in deck {self.deck_id}")
        except Exception as e:
            error_msg = f"Failed to initialize study session: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error_message(error_msg)

    def handle_show_answer(self) -> None:
        """Handle the show answer button click."""
        if not self.answer_shown:
            current_card = self.study_service.get_current_card_for_review()
            if current_card:
                flashcard, _ = current_card
                self._update_view_with_card(flashcard, show_answer=True)
                self.answer_shown = True
                logger.debug(f"Showing answer for flashcard {flashcard.id}")

    def handle_rate_card(self, rating: int) -> None:
        """Handle rating a card.

        Args:
            rating: The rating value (1-4).
        """
        if not self.current_flashcard_id:
            logger.error("Attempted to rate card but no current flashcard")
            return

        try:
            # Record the review
            self.study_service.record_review(self.current_flashcard_id, rating)

            # Move to the next card
            next_card = self.study_service.proceed_to_next_card()

            if next_card:
                flashcard, _ = next_card
                self.current_flashcard_id = flashcard.id
                self.answer_shown = False
                self._update_view_with_card(flashcard, show_answer=False)
                self._update_progress()
            else:
                # No more cards, session complete
                self.view.show_session_complete_message()
                logger.info("Study session completed")
        except Exception as e:
            error_msg = f"Failed to process rating: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error_message(error_msg)

    def handle_end_session(self) -> None:
        """Handle ending the study session."""
        self.study_service.end_session()
        # Navigate back to the deck view
        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")
        logger.info(f"Study session for deck {self.deck_id} ended")

    def _update_view_with_card(self, flashcard: Flashcard, show_answer: bool) -> None:
        """Update the view with the current card.

        Args:
            flashcard: The flashcard to display.
            show_answer: Whether to show the answer.
        """
        self.view.display_card_front(flashcard.front_text)

        if show_answer:
            self.view.display_card_back(flashcard.back_text)
            self.view.show_rating_buttons()
            self.view.disable_show_answer_button()
        else:
            self.view.display_card_back("")
            self.view.hide_rating_buttons()
            self.view.enable_show_answer_button()

    def _update_progress(self) -> None:
        """Update the progress display in the view."""
        current, total = self.study_service.get_session_progress()
        self.view.update_progress(current, total)
