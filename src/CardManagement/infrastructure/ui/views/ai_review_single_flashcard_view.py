import logging
from typing import Callable, List, Any, Optional
from tkinter.scrolledtext import ScrolledText

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.ui.widgets.header_bar import HeaderBar
from Shared.application.navigation import NavigationControllerProtocol


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
        self.save_button: Optional[ttk.Button] = None

        # Get current flashcard DTO
        self.current_dto = self.generated_flashcards_dtos[self.current_flashcard_index]

        # Initialize UI
        self._init_ui()
        self._bind_text_area_events()
        self._init_complete = True
        self._update_save_button_state()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        total_cards = len(self.generated_flashcards_dtos)
        current_number = self.current_flashcard_index + 1
        self.header = HeaderBar(
            self, f"Przeglądanie wygenerowanej fiszki ({current_number}/{total_cards})", show_back_button=True
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.content_frame, text="Przód:", font=("TkDefaultFont", 12)).grid(
            row=0, column=0, sticky="nw", pady=(0, 5), padx=(0, 5)
        )
        self.front_text = ScrolledText(self.content_frame, height=6, width=50, wrap=ttk.WORD)
        self.front_text.grid(row=0, column=1, sticky="ewns", pady=(0, 2))
        self.front_text.insert("1.0", self.current_dto.front)

        self.front_char_count = ttk.Label(self.content_frame, text=f"0/{self.FRONT_TEXT_MAX_LENGTH}")
        self.front_char_count.grid(row=1, column=1, sticky="ne", pady=(0, 10))

        ttk.Label(self.content_frame, text="Tył:", font=("TkDefaultFont", 12)).grid(
            row=2, column=0, sticky="nw", pady=(0, 5), padx=(0, 5)
        )
        self.back_text = ScrolledText(self.content_frame, height=10, width=50, wrap=ttk.WORD)
        self.back_text.grid(row=2, column=1, sticky="ewns", pady=(0, 2))
        self.back_text.insert("1.0", self.current_dto.back)

        self.back_char_count = ttk.Label(self.content_frame, text=f"0/{self.BACK_TEXT_MAX_LENGTH}")
        self.back_char_count.grid(row=3, column=1, sticky="ne", pady=(0, 10))

        if self.current_dto.tags:
            ttk.Label(self.content_frame, text="Tagi:").grid(row=4, column=0, sticky="nw", pady=(0, 5), padx=(0, 5))
            tags_text = ", ".join(self.current_dto.tags)
            ttk.Label(self.content_frame, text=tags_text).grid(row=4, column=1, sticky="w", pady=(0, 10))

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)

        self._update_char_count(self.front_text, self.front_char_count, self.FRONT_TEXT_MAX_LENGTH)
        self._update_char_count(self.back_text, self.back_char_count, self.BACK_TEXT_MAX_LENGTH)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.save_button = ttk.Button(
            self.button_frame,
            text="Zapisz i kontynuuj",
            style="success.TButton",
            command=self._on_save_and_continue,
        )
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.discard_button = ttk.Button(
            self.button_frame,
            text="Odrzuć i kontynuuj",
            style="danger.TButton",
            command=self._on_discard_and_continue,
        )
        self.discard_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def _bind_text_area_events(self) -> None:
        """Bind <<Modified>> event to text area UI elements."""
        self.front_text.bind(
            "<<Modified>>",
            self._handle_front_text_changed,
        )
        self.back_text.bind(
            "<<Modified>>",
            self._handle_back_text_changed,
        )

    def _handle_front_text_changed(self, event: Any) -> None:
        """Handles text change in the front text area."""
        self._on_text_changed(self.front_text, self.front_char_count, self.FRONT_TEXT_MAX_LENGTH)

    def _handle_back_text_changed(self, event: Any) -> None:
        """Handles text change in the back text area."""
        self._on_text_changed(self.back_text, self.back_char_count, self.BACK_TEXT_MAX_LENGTH)

    def _on_text_changed(self, text_widget: ScrolledText, count_label: ttk.Label, max_length: int) -> None:
        """Generic handler for text change events for both front and back text fields."""
        if not self._init_complete:
            if text_widget.edit_modified():
                text_widget.edit_modified(False)
            return

        self.has_unsaved_changes = True
        self._update_char_count(text_widget, count_label, max_length)
        self._update_save_button_state()
        text_widget.edit_modified(False)

    def _update_char_count(self, text_widget: ScrolledText, count_label: ttk.Label, max_length: int) -> None:
        """Update character count display and text color if over limit."""
        text = text_widget.get("1.0", "end-1c")
        count = len(text)
        count_label.configure(text=f"{count}/{max_length}")

        if count > max_length:
            count_label.configure(foreground="red")
        else:
            style = ttk.Style()
            default_fg = style.lookup("TLabel", "foreground")
            count_label.configure(foreground=default_fg)

    def _update_save_button_state(self) -> None:
        """Update the save button state based on text lengths and validity."""
        if not self._init_complete or self.save_button is None:
            return

        front_text = self.front_text.get("1.0", "end-1c")
        back_text = self.back_text.get("1.0", "end-1c")

        front_valid = 0 < len(front_text) <= self.FRONT_TEXT_MAX_LENGTH
        back_valid = 0 < len(back_text) <= self.BACK_TEXT_MAX_LENGTH

        if front_valid and back_valid:
            self.save_button.configure(state="normal")
        else:
            self.save_button.configure(state="disabled")

    def _on_back(self) -> None:
        """Handle back button click (from header)."""
        if self.has_unsaved_changes:
            confirm = Messagebox.yesno(
                title="Anulować przeglądanie?",
                message="Masz niezapisane zmiany. Czy na pewno chcesz przerwać przeglądanie fiszek?",
                parent=self,
            )
            if not confirm:
                return
        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_save_and_continue(self) -> None:
        """Save the current flashcard and move to the next one."""
        front_text = self.front_text.get("1.0", "end-1c").strip()
        back_text = self.back_text.get("1.0", "end-1c").strip()

        original_front = self.current_dto.front.strip()
        original_back = self.current_dto.back.strip()

        source = "ai-edited" if front_text != original_front or back_text != original_back else "ai-generated"
        ai_model_name = self.current_dto.metadata.get("model") if self.current_dto.metadata else None

        try:
            self.card_service.create_flashcard(
                deck_id=self.deck_id,
                front_text=front_text,
                back_text=back_text,
                source=source,
                ai_model_name=ai_model_name,
            )
            self.show_toast("Sukces", "Fiszka została zapisana")
            self.has_unsaved_changes = False
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
        confirm = Messagebox.yesno(
            title="Odrzucić fiszkę?",
            message="Czy na pewno chcesz odrzucić tę fiszkę?",
            parent=self,
        )
        if not confirm:
            return
        self._proceed_to_next_flashcard()

    def _proceed_to_next_flashcard(self) -> None:
        """Proceed to the next flashcard or finish if all are reviewed."""
        self.current_flashcard_index += 1
        if self.current_flashcard_index < len(self.generated_flashcards_dtos):
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
                self.show_toast("Błąd", "Wystąpił błąd podczas przechodzenia do następnej fiszki.")
        else:
            total_count = len(self.generated_flashcards_dtos)
            self.show_toast("Zakończono", f"Zakończono przeglądanie {total_count} wygenerowanych fiszek.")
            self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def destroy(self) -> None:
        """Override destroy. No specific toplevel bindings to manage from this view anymore."""
        super().destroy()
