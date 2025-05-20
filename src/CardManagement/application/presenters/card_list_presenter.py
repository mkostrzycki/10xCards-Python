"""Presenter for the card list view."""

import logging
from typing import Protocol, List, Optional

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.application.card_service import CardService
from DeckManagement.application.deck_service import DeckService
from Shared.application.session_service import SessionService
from Shared.application.navigation import NavigationControllerProtocol

logger = logging.getLogger(__name__)


class FlashcardViewModel:
    """Data transfer object for flashcard display"""

    def __init__(self, id: int, front_text: str, back_text: str, source: str):
        self.id = id
        self.front_text = front_text
        self.back_text = back_text
        self.source = source

    @classmethod
    def from_flashcard(cls, flashcard: Flashcard) -> "FlashcardViewModel":
        """Creates a ViewModel from a domain Flashcard model"""
        if flashcard.id is None:
            raise ValueError("Cannot create FlashcardViewModel from Flashcard with None id")
        return cls(
            id=flashcard.id, front_text=flashcard.front_text, back_text=flashcard.back_text, source=flashcard.source
        )


class ICardListView(Protocol):
    """Protocol defining the interface for CardListView"""

    def display_cards(self, cards: List[FlashcardViewModel]) -> None: ...
    def show_loading(self, is_loading: bool) -> None: ...
    def show_error(self, message: str) -> None: ...
    def show_toast(self, title: str, message: str) -> None: ...
    def clear_card_selection(self) -> None: ...


class CardListPresenter:
    """Presenter for the card list view."""

    def __init__(
        self,
        view: ICardListView,
        card_service: CardService,
        deck_service: DeckService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        deck_id: int,
        deck_name: str,
    ):
        """Initialize the card list presenter.

        Args:
            view: The view implementing ICardListView
            card_service: Service for card operations
            deck_service: Service for deck operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
            deck_id: ID of the deck to manage cards for
            deck_name: Name of the deck
        """
        self.view = view
        self.card_service = card_service
        self.deck_service = deck_service
        self.session_service = session_service
        self.navigation = navigation_controller
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.dialog_open: bool = False
        self.deleting_id: Optional[int] = None

    def load_cards(self) -> None:
        """Load cards for the current deck."""
        # Check if user is authenticated
        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby przeglądać fiszki.")
            self.navigation.navigate("/profiles")
            return

        self.view.show_loading(True)
        try:
            cards = self.card_service.list_by_deck_id(self.deck_id)
            card_viewmodels = [FlashcardViewModel.from_flashcard(card) for card in cards]
            self.view.display_cards(card_viewmodels)
        except Exception as e:
            error_msg = f"Wystąpił błąd podczas ładowania fiszek: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error(error_msg)
        finally:
            self.view.show_loading(False)

    def navigate_back(self) -> None:
        """Navigate back to deck list."""
        self.navigation.navigate("/decks")

    def add_flashcard(self) -> None:
        """Navigate to add flashcard view."""
        self.navigation.navigate(f"/decks/{self.deck_id}/cards/new")

    def generate_with_ai(self) -> None:
        """Navigate to AI generation view."""
        self.navigation.navigate(f"/decks/{self.deck_id}/cards/generate")

    def start_study_session(self) -> None:
        """Start a study session."""
        try:
            self.navigation.navigate(f"/study/session/{self.deck_id}")
        except Exception as e:
            error_msg = f"Nie udało się rozpocząć nauki: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error(error_msg)

    def edit_flashcard(self, flashcard_id: int) -> None:
        """Navigate to edit flashcard view."""
        if self.dialog_open:
            return

        self.navigation.navigate(f"/decks/{self.deck_id}/cards/{flashcard_id}/edit")

    def delete_flashcard(self, flashcard_id: int) -> None:
        """Handle flashcard deletion request."""
        if self.dialog_open or self.deleting_id:
            return

        self.dialog_open = True
        self.deleting_id = flashcard_id

        # Note: The view will handle showing the confirmation dialog and calling handle_flashcard_deletion_confirmed

    def handle_flashcard_deletion_confirmed(self) -> None:
        """Handle confirmed flashcard deletion."""
        try:
            if self.deleting_id is None:
                logger.error("Attempting to delete a flashcard but deleting_id is None")
                self.view.show_error("Nieprawidłowe ID fiszki")
                return

            self.card_service.delete_flashcard(self.deleting_id)
            self.view.show_toast("Sukces", "Fiszka została usunięta")
            self.load_cards()  # Refresh list
        except ValueError as e:
            self.view.show_error(str(e))
        except Exception as e:
            error_msg = f"Nie udało się usunąć fiszki: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error(error_msg)
        finally:
            self._reset_deletion_state()

    def handle_flashcard_deletion_cancelled(self) -> None:
        """Handle cancellation of flashcard deletion."""
        self._reset_deletion_state()

    def _reset_deletion_state(self) -> None:
        """Reset the state related to flashcard deletion."""
        self.dialog_open = False
        self.deleting_id = None

    def request_delete_current_deck(self) -> None:
        """Request deletion of the current deck."""
        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany, aby usunąć talię.")
            self.navigation.navigate("/profiles")
            return

        if self.dialog_open:  # Zapobieganie wielokrotnemu otwarciu dialogu
            return

        self.dialog_open = True
        # Note: The view will handle showing the confirmation dialog and calling _handle_deck_deletion_confirmed

    def _handle_deck_deletion_confirmed(self) -> None:
        """Handle confirmed deck deletion."""
        try:
            user_profile = self.session_service.get_current_user()
            if not user_profile or user_profile.id is None:
                self.view.show_error("Nie udało się zidentyfikować użytkownika.")
                return

            self.view.show_loading(True)
            self.deck_service.delete_deck(self.deck_id, user_profile.id)
            self.view.show_toast("Sukces", f"Talia '{self.deck_name}' została pomyślnie usunięta.")
            self.navigation.navigate("/decks")
        except ValueError as ve:
            logger.warning(f"Validation error while deleting deck {self.deck_id}: {str(ve)}")
            self.view.show_error(str(ve))
        except Exception as e:
            logger.error(f"Error deleting deck {self.deck_id}: {str(e)}", exc_info=True)
            self.view.show_error("Wystąpił nieoczekiwany błąd podczas usuwania talii.")
        finally:
            self.view.show_loading(False)
            self._reset_deck_deletion_state()

    def _handle_deck_deletion_cancelled(self) -> None:
        """Handle cancellation of deck deletion."""
        self._reset_deck_deletion_state()

    def _reset_deck_deletion_state(self) -> None:
        """Reset state related to deck deletion."""
        self.dialog_open = False
