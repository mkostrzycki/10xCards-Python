"""Presenter for the deck list view."""

import logging
from typing import Protocol, List, Optional
from datetime import datetime

from DeckManagement.domain.models.Deck import Deck
from DeckManagement.application.deck_service import DeckService
from Shared.application.session_service import SessionService
from Shared.application.navigation import NavigationControllerProtocol

logger = logging.getLogger(__name__)


class DeckViewModel:
    """Data transfer object for deck display"""

    def __init__(self, id: int, name: str, created_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at

    @classmethod
    def from_deck(cls, deck: Deck) -> "DeckViewModel":
        """Creates a ViewModel from a domain Deck model"""
        if deck.id is None or deck.created_at is None:
            raise ValueError("Cannot create DeckViewModel from Deck with None id or created_at")
        return cls(id=deck.id, name=deck.name, created_at=deck.created_at)


class IDeckListView(Protocol):
    """Protocol defining the interface for DeckListView"""

    def display_decks(self, decks: List[DeckViewModel]) -> None: ...
    def show_loading(self, is_loading: bool) -> None: ...
    def show_error(self, message: str) -> None: ...
    def show_toast(self, title: str, message: str) -> None: ...
    def clear_deck_selection(self) -> None: ...
    def enable_study_button(self, enabled: bool) -> None: ...


class DeckListPresenter:
    """Presenter for the deck list view."""

    def __init__(
        self,
        view: IDeckListView,
        deck_service: DeckService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
    ):
        """Initialize the deck list presenter.

        Args:
            view: The view implementing IDeckListView
            deck_service: Service for deck operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
        """
        self.view = view
        self.deck_service = deck_service
        self.session_service = session_service
        self.navigation = navigation_controller
        self.dialog_open: bool = False
        self.deleting_deck_id: Optional[int] = None

    def load_decks(self) -> None:
        """Load decks for the current user."""
        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby przeglądać talie.")
            self.navigation.navigate("/profiles")
            return

        self.view.show_loading(True)
        try:
            user = self.session_service.get_current_user()
            if not user or not user.id:
                self.view.show_error("Musisz być zalogowany aby przeglądać talie.")
                return

            decks = self.deck_service.list_decks(user.id)
            deck_viewmodels = [DeckViewModel.from_deck(deck) for deck in decks]
            self.view.display_decks(deck_viewmodels)
            self.view.clear_deck_selection()
            self.view.enable_study_button(False)

        except Exception as e:
            error_msg = f"Wystąpił błąd podczas ładowania talii: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.view.show_error(error_msg)
        finally:
            self.view.show_loading(False)

    def navigate_back(self) -> None:
        """Navigate back to profiles view."""
        self.navigation.navigate("/profiles")

    def show_create_deck_dialog(self) -> None:
        """Show dialog for creating a new deck."""
        if self.dialog_open:
            return

        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby utworzyć talię.")
            self.navigation.navigate("/profiles")
            return

        self.dialog_open = True
        # Note: The view will handle showing the dialog and calling handle_deck_creation

    def handle_deck_creation(self, deck_name: str) -> None:
        """Handle deck creation from dialog."""
        self.dialog_open = False

        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby utworzyć talię")
            return

        if not deck_name or not deck_name.strip():
            self.view.show_toast("Błąd", "Nazwa talii nie może być pusta")
            return

        if len(deck_name) > 50:
            self.view.show_toast("Błąd", "Nazwa talii nie może przekraczać 50 znaków")
            return

        try:
            user = self.session_service.get_current_user()
            if not user or not user.id:
                self.view.show_toast("Błąd", "Musisz być zalogowany aby utworzyć talię")
                return

            self.deck_service.create_deck(name=deck_name, user_id=user.id)
            self.view.show_toast("Sukces", f"Utworzono nową talię: {deck_name}")
            self.load_decks()
        except Exception as e:
            self.view.show_toast("Błąd", f"Nie udało się utworzyć talii: {str(e)}")
            logger.error(f"Error creating deck: {str(e)}")

    def handle_deck_selected(self, deck_id: int) -> None:
        """Handle deck selection."""
        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby przeglądać talie")
            return

        self.view.enable_study_button(True)
        self.navigation.navigate(f"/decks/{deck_id}/cards")

    def handle_deck_deletion(self, deck_id: int) -> None:
        """Handle deck deletion request."""
        if self.dialog_open or self.deleting_deck_id:
            return

        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby usunąć talię")
            return

        self.dialog_open = True
        self.deleting_deck_id = deck_id

        # Note: The view will handle showing the confirmation dialog and calling handle_deck_deletion_confirmed

    def handle_deck_deletion_confirmed(self) -> None:
        """Handle confirmed deck deletion."""
        self.dialog_open = False

        if not self.deleting_deck_id:
            return

        try:
            user = self.session_service.get_current_user()
            if not user or not user.id:
                self.view.show_toast("Błąd", "Musisz być zalogowany aby usunąć talię")
                return

            self.deck_service.delete_deck(self.deleting_deck_id, user.id)
            self.view.show_toast("Sukces", "Talia została usunięta")
            self.load_decks()
        except Exception as e:
            self.view.show_toast("Błąd", f"Nie udało się usunąć talii: {str(e)}")
            logger.error(f"Error deleting deck: {str(e)}")
        finally:
            self.deleting_deck_id = None

    def handle_deck_deletion_cancelled(self) -> None:
        """Handle cancellation of deck deletion."""
        self.dialog_open = False
        self.deleting_deck_id = None

    def handle_logout(self) -> None:
        """Handle logout action."""
        self.session_service.logout()
        self.navigation.navigate("/profiles")
        self.view.show_toast("Informacja", "Wylogowano pomyślnie")

    def start_study_session(self, deck_id: int) -> None:
        """Start a study session for the selected deck."""
        if not self.session_service.is_authenticated():
            self.view.show_toast("Błąd", "Musisz być zalogowany aby rozpocząć naukę")
            return

        try:
            self.navigation.navigate(f"/study/session/{deck_id}")
        except Exception as e:
            self.view.show_toast("Błąd", f"Nie udało się rozpocząć nauki: {str(e)}")
            logger.error(f"Error starting study session: {str(e)}", exc_info=True)
