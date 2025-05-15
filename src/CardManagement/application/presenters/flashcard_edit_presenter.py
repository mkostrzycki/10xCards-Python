"""Presenter for the flashcard edit view."""

import logging
from typing import Protocol, Optional

from CardManagement.application.card_service import CardService
from Shared.application.navigation import NavigationControllerProtocol

logger = logging.getLogger(__name__)


class IFlashcardEditView(Protocol):
    """Interface for the flashcard edit view."""

    def display_flashcard(self, front_text: str, back_text: str) -> None: ...
    def show_toast(self, title: str, message: str) -> None: ...
    def show_loading(self, is_loading: bool) -> None: ...
    def show_saving(self, is_saving: bool) -> None: ...
    def show_delete_confirmation(self, on_confirm: bool) -> None: ...
    def update_save_button_state(self, is_enabled: bool) -> None: ...


class FlashcardEditPresenter:
    """Presenter for the flashcard edit view."""

    def __init__(
        self,
        view: IFlashcardEditView,
        card_service: CardService,
        navigation: NavigationControllerProtocol,
        deck_id: int,
        flashcard_id: Optional[int] = None,
    ):
        self._view = view
        self._card_service = card_service
        self._navigation = navigation
        self._deck_id = deck_id
        self._flashcard_id = flashcard_id

        # State
        self._is_loading = False
        self._is_saving = False
        self._front_text = ""
        self._back_text = ""

    def initialize(self) -> None:
        """Initialize the presenter and load data if in edit mode."""
        if self._flashcard_id:
            self._load_flashcard()

    def _load_flashcard(self) -> None:
        """Load flashcard data for editing."""
        if not self._flashcard_id:
            return

        self._is_loading = True
        self._view.show_loading(True)
        try:
            flashcard = self._card_service.get_flashcard(self._flashcard_id)
            if not flashcard:
                raise ValueError("Fiszka nie istnieje")

            self._front_text = flashcard.front_text
            self._back_text = flashcard.back_text
            self._view.display_flashcard(self._front_text, self._back_text)

        except Exception as e:
            error_msg = f"Nie udało się załadować fiszki: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._view.show_toast("Błąd", error_msg)
            self.navigate_back()
        finally:
            self._is_loading = False
            self._view.show_loading(False)

    def handle_text_change(self, front_text: str, back_text: str) -> None:
        """Handle text changes in the view."""
        self._front_text = front_text
        self._back_text = back_text
        self._validate_and_update_save_button()

    def _validate_and_update_save_button(self) -> None:
        """Validate input and update save button state."""
        is_valid = (
            bool(self._front_text.strip())
            and bool(self._back_text.strip())
            and len(self._front_text) <= 200
            and len(self._back_text) <= 500
            and not self._is_saving
        )
        self._view.update_save_button_state(is_valid)

    def save(self) -> None:
        """Handle save action."""
        if self._is_saving:
            return

        self._is_saving = True
        self._view.show_saving(True)
        try:
            if self._flashcard_id:
                # Update existing
                self._card_service.update_flashcard(
                    flashcard_id=self._flashcard_id, front_text=self._front_text, back_text=self._back_text
                )
                self._view.show_toast("Sukces", "Fiszka została zaktualizowana")
            else:
                # Create new
                self._card_service.create_flashcard(
                    deck_id=self._deck_id, front_text=self._front_text, back_text=self._back_text
                )
                self._view.show_toast("Sukces", "Fiszka została utworzona")

            self.navigate_back()

        except ValueError as e:
            self._view.show_toast("Błąd", str(e))
        except Exception as e:
            error_msg = f"Wystąpił błąd podczas zapisywania: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._view.show_toast("Błąd", error_msg)
        finally:
            self._is_saving = False
            self._view.show_saving(False)

    def delete(self) -> None:
        """Handle delete action."""
        if not self._flashcard_id or self._is_saving:
            return

        self._view.show_delete_confirmation(True)

    def handle_delete_confirmed(self) -> None:
        """Handle confirmed deletion."""
        if not self._flashcard_id:
            return

        self._is_saving = True
        self._view.show_saving(True)
        try:
            self._card_service.delete_flashcard(flashcard_id=self._flashcard_id)
            self._view.show_toast("Sukces", "Fiszka została usunięta")
            self.navigate_back()
        except ValueError as e:
            self._view.show_toast("Błąd", str(e))
        except Exception as e:
            error_msg = f"Wystąpił błąd podczas usuwania: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._view.show_toast("Błąd", error_msg)
        finally:
            self._is_saving = False
            self._view.show_saving(False)

    def navigate_back(self) -> None:
        """Navigate back to the card list."""
        self._navigation.navigate(f"/decks/{self._deck_id}/cards")
