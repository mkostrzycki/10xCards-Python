"""Presenter for the AI-generated flashcard review view."""

import logging
from typing import Protocol, List, Optional

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.application.navigation import NavigationControllerProtocol

logger = logging.getLogger(__name__)


class IAIReviewSingleFlashcardView(Protocol):
    """Interface for the AI-generated flashcard review view."""

    def show_toast(self, title: str, message: str) -> None: ...
    def show_saving(self, is_saving: bool) -> None: ...
    def show_unsaved_changes_confirmation(self) -> bool: ...
    def show_discard_confirmation(self) -> bool: ...
    def update_save_button_state(self, is_enabled: bool) -> None: ...
    def get_front_text(self) -> str: ...
    def get_back_text(self) -> str: ...
    def display_flashcard(self, front_text: str, back_text: str, tags: Optional[List[str]] = None) -> None: ...
    def update_char_counts(self) -> None: ...


class AIReviewSingleFlashcardPresenter:
    """Presenter for the AI-generated flashcard review view."""

    # Constants
    FRONT_TEXT_MAX_LENGTH = 200
    BACK_TEXT_MAX_LENGTH = 500

    def __init__(
        self,
        view: IAIReviewSingleFlashcardView,
        ai_service: AIService,
        card_service: CardService,
        navigation: NavigationControllerProtocol,
        deck_id: int,
        deck_name: str,
        generated_flashcards_dtos: List[FlashcardDTO],
        current_flashcard_index: int,
        available_llm_models: List[str],
        original_source_text: str,
    ):
        self._view = view
        self._ai_service = ai_service
        self._card_service = card_service
        self._navigation = navigation
        self._deck_id = deck_id
        self._deck_name = deck_name
        self._flashcards = generated_flashcards_dtos
        self._current_index = current_flashcard_index
        self._available_llm_models = available_llm_models
        self._original_source_text = original_source_text

        # State
        self._has_unsaved_changes = False
        self._is_saving = False

    def initialize(self) -> None:
        """Initialize the presenter and display the current flashcard."""
        current_dto = self._flashcards[self._current_index]
        self._view.display_flashcard(current_dto.front, current_dto.back, current_dto.tags)
        self._view.update_char_counts()

    def handle_text_change(self) -> None:
        """Handle text changes in the view."""
        self._has_unsaved_changes = True
        self._validate_and_update_save_button()

    def _validate_and_update_save_button(self) -> None:
        """Validate input and update save button state."""
        front_text = self._view.get_front_text()
        back_text = self._view.get_back_text()

        is_valid = (
            bool(front_text.strip())
            and bool(back_text.strip())
            and len(front_text) <= self.FRONT_TEXT_MAX_LENGTH
            and len(back_text) <= self.BACK_TEXT_MAX_LENGTH
            and not self._is_saving
        )
        self._view.update_save_button_state(is_valid)

    def save_and_continue(self) -> None:
        """Save the current flashcard and move to the next one."""
        if self._is_saving:
            return

        front_text = self._view.get_front_text().strip()
        back_text = self._view.get_back_text().strip()

        original_front = self._flashcards[self._current_index].front.strip()
        original_back = self._flashcards[self._current_index].back.strip()

        source = "ai-edited" if front_text != original_front or back_text != original_back else "ai-generated"
        ai_model_name = (
            self._flashcards[self._current_index].metadata.get("model")
            if self._flashcards[self._current_index].metadata
            else None
        )

        self._is_saving = True
        self._view.show_saving(True)
        try:
            self._card_service.create_flashcard(
                deck_id=self._deck_id,
                front_text=front_text,
                back_text=back_text,
                source=source,
                ai_model_name=ai_model_name,
            )
            self._view.show_toast("Sukces", "Fiszka została zapisana")
            self._has_unsaved_changes = False
            self._proceed_to_next_flashcard()
        except ValueError as e:
            self._view.show_toast("Błąd", str(e))
            logger.warning(f"Validation error saving flashcard for deck {self._deck_id}: {str(e)}")
        except Exception as e:
            error_msg = f"Error saving flashcard for deck {self._deck_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._view.show_toast("Błąd", f"Wystąpił błąd podczas zapisywania: {str(e)}")
        finally:
            self._is_saving = False
            self._view.show_saving(False)

    def discard_and_continue(self) -> None:
        """Discard the current flashcard and move to the next one."""
        if not self._view.show_discard_confirmation():
            return
        self._proceed_to_next_flashcard()

    def _proceed_to_next_flashcard(self) -> None:
        """Proceed to the next flashcard or finish if all are reviewed."""
        self._current_index += 1
        if self._current_index < len(self._flashcards):
            try:
                self._navigation.navigate(
                    "/decks/{deck_id}/cards/review".format(deck_id=self._deck_id),
                    deck_id=self._deck_id,
                    deck_name=self._deck_name,
                    generated_flashcards_dtos=self._flashcards,
                    current_flashcard_index=self._current_index,
                    ai_service=self._ai_service,
                    card_service=self._card_service,
                    available_llm_models=self._available_llm_models,
                    original_source_text=self._original_source_text,
                )
            except Exception as e:
                error_msg = f"Failed to navigate to next flashcard view: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self._view.show_toast("Błąd", "Wystąpił błąd podczas przechodzenia do następnej fiszki.")
        else:
            total_count = len(self._flashcards)
            self._view.show_toast("Zakończono", f"Zakończono przeglądanie {total_count} wygenerowanych fiszek.")
            self.navigate_back()

    def navigate_back(self) -> None:
        """Navigate back to the card list."""
        if self._has_unsaved_changes and not self._view.show_unsaved_changes_confirmation():
            return
        self._navigation.navigate(f"/decks/{self._deck_id}/cards")
