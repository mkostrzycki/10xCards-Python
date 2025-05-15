"""Presenter for the AI flashcard generation view."""

import logging
import threading
from typing import Protocol, List, Optional

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.api_clients.openrouter.exceptions import (
    AIAPIAuthError,
    FlashcardGenerationError,
)
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.application.navigation import NavigationControllerProtocol
from UserProfile.application.user_profile_service import UserProfileService
from Shared.application.session_service import SessionService

logger = logging.getLogger(__name__)


class IAIGenerateView(Protocol):
    """Interface for the AI flashcard generation view."""

    def show_toast(self, title: str, message: str) -> None: ...
    def show_generating_state(self, is_generating: bool) -> None: ...
    def update_progress_label(self, text: str) -> None: ...
    def update_cancel_button_state(self, is_enabled: bool) -> None: ...
    def update_generate_button_state(self, is_enabled: bool) -> None: ...
    def get_input_text(self) -> str: ...
    def get_selected_model(self) -> str: ...


class AIGeneratePresenter:
    """Presenter for the AI flashcard generation view."""

    # Constants
    MAX_TEXT_LENGTH = 10000

    def __init__(
        self,
        view: IAIGenerateView,
        ai_service: AIService,
        card_service: CardService,
        user_profile_service: UserProfileService,
        session_service: SessionService,
        navigation: NavigationControllerProtocol,
        deck_id: int,
        deck_name: str,
        available_llm_models: List[str],
    ):
        self._view = view
        self._ai_service = ai_service
        self._card_service = card_service
        self._user_profile_service = user_profile_service
        self._session_service = session_service
        self._navigation = navigation
        self._deck_id = deck_id
        self._deck_name = deck_name
        self._available_llm_models = available_llm_models

        # State
        self._is_generating = False
        self._generation_thread: Optional[threading.Thread] = None
        self._cancellation_requested = False

    def initialize(self) -> None:
        """Initialize the presenter."""
        self._view.update_generate_button_state(True)
        self._view.update_cancel_button_state(False)

    def handle_generate(self) -> None:
        """Handle flashcard generation request."""
        # Validate input
        raw_text = self._view.get_input_text().strip()
        if not raw_text:
            self._view.show_toast("Błąd", "Tekst nie może być pusty")
            return

        # Check text length
        if len(raw_text) > self.MAX_TEXT_LENGTH:
            self._view.show_toast("Błąd", f"Tekst jest zbyt długi (maksymalnie {self.MAX_TEXT_LENGTH} znaków)")
            return

        model = self._view.get_selected_model()

        logger.info(f"Starting flashcard generation for deck {self._deck_id} with model {model}")

        # Reset cancellation flag
        self._cancellation_requested = False

        # Update UI state
        self._set_generating_state(True)

        # Start generation in a background thread
        self._generation_thread = threading.Thread(target=self._generate_flashcards_thread, args=(raw_text, model))
        self._generation_thread.daemon = True
        self._generation_thread.start()

    def handle_cancel_generation(self) -> None:
        """Handle cancellation request."""
        self._cancellation_requested = True
        self._view.update_progress_label("Anulowanie generowania...")
        self._view.update_cancel_button_state(False)
        logger.info(f"User requested cancellation of flashcard generation for deck {self._deck_id}")

    def _set_generating_state(self, is_generating: bool) -> None:
        """Update UI state for generation process."""
        self._is_generating = is_generating
        self._view.show_generating_state(is_generating)
        self._view.update_generate_button_state(not is_generating)
        self._view.update_cancel_button_state(is_generating)
        if is_generating:
            self._view.update_progress_label("Generowanie fiszek...")
        else:
            self._view.update_progress_label("")

    def _generate_flashcards_thread(self, raw_text: str, model: str) -> None:
        """Background thread for flashcard generation."""
        try:
            # Check for cancellation
            if self._cancellation_requested:
                self._after_generation(cancelled=True)
                return

            # Log the generation attempt
            logger.info(
                f"Generating flashcards for deck {self._deck_id} with model {model}, text length: {len(raw_text)}"
            )

            flashcards = self._ai_service.generate_flashcards(raw_text=raw_text, deck_id=self._deck_id, model=model)

            # Check for cancellation again after generation
            if self._cancellation_requested:
                self._after_generation(cancelled=True)
                return

            # Check if we got any flashcards
            if not flashcards:
                self._after_generation(error="Nie udało się wygenerować żadnych fiszek")
                return

            logger.info(f"Successfully generated {len(flashcards)} flashcards for deck {self._deck_id}")

            # Navigate to the single flashcard review view
            self._navigate_to_review(flashcards, raw_text)

        except AIAPIAuthError:
            logger.error(f"Authentication error during flashcard generation for deck {self._deck_id}")
            self._after_generation(error="Sprawdź swój klucz API w ustawieniach profilu")

        except FlashcardGenerationError as e:
            error_message = str(e)
            logger.error(f"Flashcard generation error for deck {self._deck_id}: {error_message}")
            self._after_generation(error=error_message)

        except Exception as e:
            error_message = self._ai_service.explain_error(e)
            logger.error(
                f"Unexpected error during flashcard generation for deck {self._deck_id}: {str(e)}", exc_info=True
            )
            self._after_generation(error=error_message)

    def _after_generation(self, error: Optional[str] = None, cancelled: bool = False) -> None:
        """Handle post-generation cleanup and notifications."""
        self._set_generating_state(False)
        if cancelled:
            self._view.show_toast("Informacja", "Generowanie fiszek zostało anulowane")
        elif error:
            self._view.show_toast("Błąd", error)

    def _navigate_to_review(self, flashcards: List[FlashcardDTO], original_source_text: str) -> None:
        """Navigate to the flashcard review view."""
        self._navigation.navigate(
            "/decks/{deck_id}/cards/review".format(deck_id=self._deck_id),
            deck_id=self._deck_id,
            deck_name=self._deck_name,
            generated_flashcards_dtos=flashcards,
            current_flashcard_index=0,
            ai_service=self._ai_service,
            card_service=self._card_service,
            available_llm_models=self._available_llm_models,
            original_source_text=original_source_text,
        )

    def navigate_back(self) -> None:
        """Navigate back to the card list."""
        if self._is_generating:
            self.handle_cancel_generation()
        self._navigation.navigate(f"/decks/{self._deck_id}/cards")
