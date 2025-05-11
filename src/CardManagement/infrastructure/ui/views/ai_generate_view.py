import logging
import threading
from typing import Callable, Any, List, Optional, Protocol

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import MessageDialog
from ttkbootstrap.scrolled import ScrolledText

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.api_clients.openrouter.exceptions import (
    AIAPIAuthError,
    FlashcardGenerationError,
)
from CardManagement.infrastructure.ui.views.ai_review_single_flashcard_view import AIReviewSingleFlashcardView
from Shared.ui.widgets.header_bar import HeaderBar


class NavigationControllerProtocol(Protocol):
    """Protocol defining the navigation interface required by views."""

    def navigate(self, path: str) -> None: ...
    def navigate_to_view(self, view_class: type, **kwargs) -> None: ...


class AIGenerateView(ttk.Frame):
    """View for generating flashcards using AI"""

    # Constants
    MAX_TEXT_LENGTH = 10000

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        ai_service: AIService,
        card_service: CardService,
        navigation_controller: NavigationControllerProtocol,
        show_toast: Callable[[str, str], None],
        available_llm_models: List[str] = None,
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.ai_service = ai_service
        self.card_service = card_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        self.available_llm_models = available_llm_models or []

        # State variables
        self.is_generating = False
        self.generation_thread: Optional[threading.Thread] = None
        self.cancellation_requested = False

        # Logger
        self.logger = logging.getLogger(__name__)

        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Content row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, f"Generuj fiszki z AI - {self.deck_name}", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Content
        self.content = ttk.Frame(self)
        self.content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)  # Text area row

        # Instructions label
        ttk.Label(
            self.content,
            text="Wklej tekst z którego chcesz wygenerować fiszki:",
            style="primary.TLabel",
            font=("TkDefaultFont", 12),
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Text input area
        self.text_input = ScrolledText(
            self.content,
            height=10,
            width=80,
            wrap="word",
        )
        self.text_input.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Text length counter
        self.text_counter_frame = ttk.Frame(self.content)
        self.text_counter_frame.grid(row=2, column=0, sticky="ew")
        self.text_counter_frame.grid_columnconfigure(0, weight=1)

        self.char_count = ttk.Label(self.text_counter_frame, text=f"0/{self.MAX_TEXT_LENGTH} znaków")
        self.char_count.grid(row=0, column=1, sticky="e", pady=(0, 5))

        # Model selection
        models_frame = ttk.Frame(self.content)
        models_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(models_frame, text="Model AI:").grid(row=0, column=0, padx=(0, 10))

        default_model = self.available_llm_models[0] if self.available_llm_models else ""
        self.model_var = ttk.StringVar(value=default_model)
        models = self.available_llm_models
        self.model_combobox = ttk.Combobox(
            models_frame, textvariable=self.model_var, values=models, state="readonly", width=30
        )
        self.model_combobox.grid(row=0, column=1, sticky="w")

        # Buttons
        buttons_frame = ttk.Frame(self.content)
        buttons_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.generate_button = ttk.Button(
            buttons_frame,
            text="Generuj fiszki",
            style="primary.TButton",
            command=self._on_generate,
        )
        self.generate_button.grid(row=0, column=0, padx=(0, 10))

        self.back_button = ttk.Button(
            buttons_frame,
            text="Anuluj",
            style="secondary.TButton",
            command=self._on_back,
        )
        self.back_button.grid(row=0, column=1)

        # Progress indicator (initially hidden)
        self.progress_frame = ttk.Frame(self.content)
        self.progress_frame.grid(row=5, column=0, sticky="ew", pady=10)
        self.progress_frame.grid_remove()  # Hide initially

        self.progress_label = ttk.Label(self.progress_frame, text="Generowanie fiszek...")
        self.progress_label.grid(row=0, column=0, padx=(0, 10))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=300)
        self.progress_bar.grid(row=0, column=1)

        # Cancel button for generation (initially hidden)
        self.cancel_generation_button = ttk.Button(
            self.progress_frame,
            text="Anuluj generowanie",
            style="danger.TButton",
            command=self._on_cancel_generation,
        )
        self.cancel_generation_button.grid(row=0, column=2, padx=(10, 0))

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())
        self.bind("<Escape>", lambda e: self._on_back())
        self.bind("<Control-Return>", lambda e: self._on_generate())

        # Bind text changes for character count
        self.text_input.bind("<<Modified>>", self._on_text_changed)

    def _on_text_changed(self, event=None) -> None:
        """Update character count when text changes."""
        text = self.text_input.get("1.0", "end-1c")
        count = len(text)
        self.char_count.configure(text=f"{count}/{self.MAX_TEXT_LENGTH} znaków")

        # Change color to red if over limit
        if count > self.MAX_TEXT_LENGTH:
            self.char_count.configure(foreground="red")
            self.generate_button.configure(state="disabled")
        else:
            self.char_count.configure(foreground="black")
            self.generate_button.configure(state="normal")

        # Reset the modified flag
        self.text_input.edit_modified(False)

    def _on_back(self) -> None:
        """Handle back navigation"""
        if self.is_generating:
            # Confirm cancel
            confirm = MessageDialog.yesno(
                title="Anulować generowanie?", message="Czy na pewno chcesz anulować generowanie fiszek?", parent=self
            )
            if not confirm:
                return

            self._cancel_generation()

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_cancel_generation(self) -> None:
        """Handle cancellation of generation process."""
        confirm = MessageDialog.yesno(
            title="Anulować generowanie?", message="Czy na pewno chcesz anulować generowanie fiszek?", parent=self
        )
        if confirm:
            self._cancel_generation()

    def _cancel_generation(self) -> None:
        """Cancel the ongoing generation process."""
        self.cancellation_requested = True
        self.progress_label.configure(text="Anulowanie generowania...")
        self.cancel_generation_button.configure(state="disabled")
        self.logger.info(f"User requested cancellation of flashcard generation for deck {self.deck_id}")

    def _on_generate(self) -> None:
        """Handle flashcard generation"""
        # Validate input
        raw_text = self.text_input.get("1.0", "end-1c").strip()
        if not raw_text:
            self.show_toast("Błąd", "Tekst nie może być pusty")
            return

        # Check text length
        if len(raw_text) > self.MAX_TEXT_LENGTH:
            self.show_toast("Błąd", f"Tekst jest zbyt długi (maksymalnie {self.MAX_TEXT_LENGTH} znaków)")
            return

        model = self.model_var.get()

        self.logger.info(f"Starting flashcard generation for deck {self.deck_id} with model {model}")

        # Reset cancellation flag
        self.cancellation_requested = False

        # Update UI state
        self._set_generating_state(True)

        # Start generation in a background thread
        self.generation_thread = threading.Thread(target=self._generate_flashcards_thread, args=(raw_text, model))
        self.generation_thread.daemon = True
        self.generation_thread.start()

    def _generate_flashcards_thread(self, raw_text: str, model: str) -> None:
        """Background thread for flashcard generation."""
        try:
            # Check for cancellation
            if self.cancellation_requested:
                self.after(0, lambda: self._set_generating_state(False))
                self.after(0, lambda: self.show_toast("Informacja", "Generowanie fiszek zostało anulowane"))
                return

            # Log the generation attempt
            self.logger.info(
                f"Generating flashcards for deck {self.deck_id} with model {model}, text length: {len(raw_text)}"
            )

            flashcards = self.ai_service.generate_flashcards(raw_text=raw_text, deck_id=self.deck_id, model=model)

            # Check for cancellation again after generation
            if self.cancellation_requested:
                self.after(0, lambda: self._set_generating_state(False))
                self.after(0, lambda: self.show_toast("Informacja", "Generowanie fiszek zostało anulowane"))
                return

            # Check if we got any flashcards
            if not flashcards:
                self.after(0, lambda: self.show_toast("Uwaga", "Nie udało się wygenerować żadnych fiszek"))
                self.after(0, lambda: self._set_generating_state(False))
                self.logger.warning(f"No flashcards were generated for deck {self.deck_id}")
                return

            self.logger.info(f"Successfully generated {len(flashcards)} flashcards for deck {self.deck_id}")

            # Navigate to the single flashcard review view
            self.after(
                0,
                lambda: self.navigation_controller.navigate_to_view(
                    AIReviewSingleFlashcardView,
                    deck_id=self.deck_id,
                    deck_name=self.deck_name,
                    generated_flashcards_dtos=flashcards,
                    current_flashcard_index=0,
                    ai_service=self.ai_service,
                    card_service=self.card_service,
                    navigation_controller=self.navigation_controller,
                    show_toast=self.show_toast,
                    available_llm_models=self.available_llm_models,
                    original_source_text=raw_text,
                ),
            )

        except AIAPIAuthError:
            self.logger.error(f"Authentication error during flashcard generation for deck {self.deck_id}")
            self.after(
                0, lambda: self.show_toast("Błąd uwierzytelniania", "Sprawdź swój klucz API w ustawieniach profilu")
            )
            self.after(0, lambda: self._set_generating_state(False))

        except FlashcardGenerationError as e:
            error_message = str(e)
            self.logger.error(f"Flashcard generation error for deck {self.deck_id}: {error_message}")
            self.after(0, lambda: self.show_toast("Błąd generowania fiszek", error_message))
            self.after(0, lambda: self._set_generating_state(False))

        except Exception as e:
            error_message = self.ai_service.explain_error(e)
            self.logger.error(
                f"Unexpected error during flashcard generation for deck {self.deck_id}: {str(e)}", exc_info=True
            )
            self.after(0, lambda: self.show_toast("Błąd", error_message))
            self.after(0, lambda: self._set_generating_state(False))

    def _reset_view(self) -> None:
        """Reset the view to initial state."""
        # Clear text input
        self.text_input.delete("1.0", "end")
        # Reset model selection
        if self.available_llm_models:
            self.model_var.set(self.available_llm_models[0])
        # Reset UI state
        self._set_generating_state(False)
        # Reset character count
        self._on_text_changed()

    def _set_generating_state(self, generating: bool) -> None:
        """Update UI based on generation state."""
        self.is_generating = generating

        if generating:
            # Show progress, disable buttons
            self.progress_frame.grid()
            self.progress_bar.start(10)
            self.generate_button.configure(state="disabled")
            self.model_combobox.configure(state="disabled")
            # ScrolledText requires access to the internal text widget
            self.text_input.text.configure(state="disabled")
            # Reset the cancellation button state
            self.cancel_generation_button.configure(state="normal")
        else:
            # Hide progress, enable buttons
            self.progress_frame.grid_remove()
            self.progress_bar.stop()
            self.generate_button.configure(state="normal")
            self.model_combobox.configure(state="readonly")
            # ScrolledText requires access to the internal text widget
            self.text_input.text.configure(state="normal")
            # Reset cancellation flag
            self.cancellation_requested = False
