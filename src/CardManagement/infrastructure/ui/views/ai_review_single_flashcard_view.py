import logging
from typing import Callable, List, Any, Protocol, Optional

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import MessageDialog
from ttkbootstrap.scrolled import ScrolledText

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.ui.widgets.header_bar import HeaderBar


class NavigationControllerProtocol(Protocol):
    """Protocol defining the navigation interface required by views."""

    def navigate(self, path: str) -> None: ...
    def navigate_to_view(self, view_class: type, **kwargs) -> None: ...


class AIReviewSingleFlashcardView(ttk.Frame):
    """View for reviewing a single AI-generated flashcard with options to edit, save, and discard."""

    # Constants
    FRONT_TEXT_MAX_LENGTH = 200
    BACK_TEXT_MAX_LENGTH = 500

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        generated_flashcards_dtos: List[FlashcardDTO],
        current_flashcard_index: int,
        ai_service: AIService,
        card_service: CardService,
        navigation_controller: NavigationControllerProtocol,
        show_toast: Callable[[str, str], None],
        available_llm_models: List[str],
        original_source_text: str,
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.generated_flashcards_dtos = generated_flashcards_dtos
        self.current_flashcard_index = current_flashcard_index
        self.ai_service = ai_service
        self.card_service = card_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        self.available_llm_models = available_llm_models
        self.original_source_text = original_source_text

        # State variables
        self.has_unsaved_changes = False
        self._init_complete = False
        self.save_button: Optional[ttk.Button] = None  # Inicjalizacja zmiennej przed jej użyciem

        # Get current flashcard DTO
        self.current_dto = self.generated_flashcards_dtos[self.current_flashcard_index]

        # Initialize UI
        self._init_ui()
        self._bind_events()
        self._init_complete = True

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Configure grid
        self.grid_rowconfigure(2, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1)

        # Header Bar with title showing progress (X/Y)
        total_cards = len(self.generated_flashcards_dtos)
        current_number = self.current_flashcard_index + 1
        self.header = HeaderBar(
            self, f"Przeglądanie wygenerowanej fiszki ({current_number}/{total_cards})", show_back_button=True
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Main content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Front text
        ttk.Label(self.content_frame, text="Przód:", font=("TkDefaultFont", 12)).grid(
            row=0, column=0, sticky="nw", pady=(0, 5)
        )
        self.front_text = ScrolledText(self.content_frame, height=6, width=50)
        self.front_text.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        self.front_text.insert("1.0", self.current_dto.front)

        # Back text
        ttk.Label(self.content_frame, text="Tył:", font=("TkDefaultFont", 12)).grid(
            row=1, column=0, sticky="nw", pady=(0, 5)
        )
        self.back_text = ScrolledText(self.content_frame, height=10, width=50)
        self.back_text.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        self.back_text.insert("1.0", self.current_dto.back)

        # Optional: Display tags if available
        if self.current_dto.tags:
            ttk.Label(self.content_frame, text="Tagi:").grid(row=2, column=0, sticky="nw", pady=(0, 5))
            tags_text = ", ".join(self.current_dto.tags)
            ttk.Label(self.content_frame, text=tags_text).grid(row=2, column=1, sticky="w", pady=(0, 10))

        # Add character count indicators
        self.front_char_count = ttk.Label(self.content_frame, text=f"0/{self.FRONT_TEXT_MAX_LENGTH}")
        self.front_char_count.grid(row=0, column=2, sticky="ne", padx=(5, 0))

        self.back_char_count = ttk.Label(self.content_frame, text=f"0/{self.BACK_TEXT_MAX_LENGTH}")
        self.back_char_count.grid(row=1, column=2, sticky="ne", padx=(5, 0))

        # Update character counts initially
        self._update_char_count(self.front_text, self.front_char_count, self.FRONT_TEXT_MAX_LENGTH)
        self._update_char_count(self.back_text, self.back_char_count, self.BACK_TEXT_MAX_LENGTH)

        # Button frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        self.save_button = ttk.Button(
            self.button_frame,
            text="Zapisz i kontynuuj (Ctrl+S)",
            style="success.TButton",
            command=self._on_save_and_continue,
        )
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.discard_button = ttk.Button(
            self.button_frame,
            text="Odrzuć i kontynuuj (Ctrl+D)",
            style="danger.TButton",
            command=self._on_discard_and_continue,
        )
        self.discard_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def _bind_events(self) -> None:
        """Bind events to UI elements."""
        # Bind text changes to update character counts and track changes
        self.front_text.bind(
            "<<Modified>>",
            lambda e: self._on_text_changed(self.front_text, self.front_char_count, self.FRONT_TEXT_MAX_LENGTH),
        )
        self.back_text.bind(
            "<<Modified>>",
            lambda e: self._on_text_changed(self.back_text, self.back_char_count, self.BACK_TEXT_MAX_LENGTH),
        )

        # Keyboard shortcuts
        self.bind("<Control-s>", lambda e: self._on_save_and_continue())
        self.bind("<Control-d>", lambda e: self._on_discard_and_continue())
        self.bind("<Escape>", lambda e: self._on_back())

    def _on_text_changed(self, text_widget: ScrolledText, count_label: ttk.Label, max_length: int) -> None:
        """Handle text change events for both front and back text fields."""
        self.has_unsaved_changes = True
        self._update_char_count(text_widget, count_label, max_length)

    def _update_char_count(self, text_widget: ScrolledText, count_label: ttk.Label, max_length: int) -> None:
        """Update character count display and validation."""
        text = text_widget.get("1.0", "end-1c")
        count = len(text)
        count_label.configure(text=f"{count}/{max_length}")

        # Change color to red if over limit
        if count > max_length:
            count_label.configure(foreground="red")
            if self.save_button is not None:
                self.save_button.configure(state="disabled")
        else:
            count_label.configure(foreground="black")
            self._update_save_button()

        # Reset the modified flag
        text_widget.edit_modified(False)

    def _update_save_button(self) -> None:
        """Update the save button state based on text lengths."""
        # Nie aktualizuj, jeśli inicjalizacja nie jest zakończona lub save_button nie istnieje
        if not self._init_complete or self.save_button is None:
            return

        front_text = self.front_text.get("1.0", "end-1c")
        back_text = self.back_text.get("1.0", "end-1c")

        front_valid = len(front_text) <= self.FRONT_TEXT_MAX_LENGTH and len(front_text) > 0
        back_valid = len(back_text) <= self.BACK_TEXT_MAX_LENGTH and len(back_text) > 0

        if front_valid and back_valid:
            self.save_button.configure(state="normal")
        else:
            self.save_button.configure(state="disabled")

    def _on_back(self) -> None:
        """Handle back button click."""
        if self.has_unsaved_changes:
            confirm = MessageDialog.yesno(
                title="Anulować przeglądanie?",
                message="Masz niezapisane zmiany. Czy na pewno chcesz przerwać przeglądanie fiszek?",
                parent=self,
            )
            if not confirm:
                return

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_save_and_continue(self) -> None:
        """Save the current flashcard and move to the next one."""
        # Get edited texts
        front_text = self.front_text.get("1.0", "end-1c").strip()
        back_text = self.back_text.get("1.0", "end-1c").strip()

        # Get original texts
        original_front = self.current_dto.front.strip()
        original_back = self.current_dto.back.strip()

        # Determine source based on whether text was edited
        if front_text != original_front or back_text != original_back:
            source = "ai-edited"
        else:
            source = "ai-generated"

        # Get AI model name from metadata if available
        ai_model_name = None
        if self.current_dto.metadata and "model" in self.current_dto.metadata:
            ai_model_name = self.current_dto.metadata["model"]

        try:
            # Create the flashcard
            self.card_service.create_flashcard(
                deck_id=self.deck_id,
                front_text=front_text,
                back_text=back_text,
                source=source,
                ai_model_name=ai_model_name,
            )
            self.show_toast("Sukces", "Fiszka została zapisana")

            # Reset unsaved changes flag
            self.has_unsaved_changes = False

            # Move to the next flashcard
            self._proceed_to_next_flashcard()

        except ValueError as e:
            self.show_toast("Błąd", str(e))
            logging.warning(f"Validation error saving flashcard for deck {self.deck_id}: {str(e)}")
        except Exception as e:
            error_msg = f"Error saving flashcard for deck {self.deck_id}: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.show_toast("Błąd", f"Wystąpił błąd podczas zapisywania: {str(e)}")

    def _on_discard_and_continue(self) -> None:
        """Discard the current flashcard and move to the next one."""
        if self.has_unsaved_changes:
            confirm = MessageDialog.yesno(
                title="Odrzucić fiszkę?", message="Czy na pewno chcesz odrzucić tę fiszkę?", parent=self
            )
            if not confirm:
                return

        self._proceed_to_next_flashcard()

    def _proceed_to_next_flashcard(self) -> None:
        """Proceed to the next flashcard or finish if all are reviewed."""
        # Increment the index
        self.current_flashcard_index += 1

        # Check if we have more flashcards to review
        if self.current_flashcard_index < len(self.generated_flashcards_dtos):
            # Navigate to a new instance of this view with the next flashcard
            try:
                self.navigation_controller.navigate_to_view(
                    AIReviewSingleFlashcardView,
                    deck_id=self.deck_id,
                    deck_name=self.deck_name,
                    generated_flashcards_dtos=self.generated_flashcards_dtos,
                    current_flashcard_index=self.current_flashcard_index,
                    ai_service=self.ai_service,
                    card_service=self.card_service,
                    navigation_controller=self.navigation_controller,
                    show_toast=self.show_toast,
                    available_llm_models=self.available_llm_models,
                    original_source_text=self.original_source_text,
                )
            except Exception as e:
                error_msg = f"Failed to navigate to next flashcard view: {str(e)}"
                logging.error(error_msg, exc_info=True)
                self.show_toast("Błąd", "Wystąpił błąd podczas przechodzenia do następnej fiszki")
        else:
            # All flashcards reviewed, show success message and navigate to card list
            total_count = len(self.generated_flashcards_dtos)
            self.show_toast("Zakończono", f"Zakończono przeglądanie {total_count} wygenerowanych fiszek")
            self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")
