import json
import threading
from typing import Callable, Any, List

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.infrastructure.api_clients.openrouter.exceptions import (
    AIAPIAuthError,
    FlashcardGenerationError,
)
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.ui.widgets.header_bar import HeaderBar


class AIGenerateView(ttk.Frame):
    """View for generating flashcards using AI"""

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        ai_service: AIService,
        card_service: CardService,
        navigation_controller: Any,
        show_toast: Callable[[str, str], None],
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.ai_service = ai_service
        self.card_service = card_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast

        # State variables
        self.is_generating = False
        self.generated_flashcards: List[FlashcardDTO] = []
        self.selected_flashcards: List[int] = []  # Indices of selected flashcards

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

        # Model selection
        models_frame = ttk.Frame(self.content)
        models_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(models_frame, text="Model AI:").grid(row=0, column=0, padx=(0, 10))

        self.model_var = ttk.StringVar(value="gpt-4o-mini")
        models = ["gpt-4o-mini", "gpt-4o", "claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"]
        self.model_combobox = ttk.Combobox(
            models_frame, textvariable=self.model_var, values=models, state="readonly", width=30
        )
        self.model_combobox.grid(row=0, column=1, sticky="w")

        # Buttons
        buttons_frame = ttk.Frame(self.content)
        buttons_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

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
        self.progress_frame.grid(row=4, column=0, sticky="ew", pady=10)
        self.progress_frame.grid_remove()  # Hide initially

        self.progress_label = ttk.Label(self.progress_frame, text="Generowanie fiszek...")
        self.progress_label.grid(row=0, column=0, padx=(0, 10))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=300)
        self.progress_bar.grid(row=0, column=1)

        # Results frame (initially hidden)
        self.results_frame = ttk.Frame(self.content)
        self.results_frame.grid(row=5, column=0, sticky="nsew", pady=10)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_remove()  # Hide initially

        ttk.Label(
            self.results_frame,
            text="Wygenerowane fiszki (zaznacz te, które chcesz zapisać):",
            style="primary.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Flashcard list (scrollable)
        self.flashcard_frame = ttk.Frame(self.results_frame)
        self.flashcard_frame.grid(row=1, column=0, sticky="nsew")

        # Action buttons for flashcards
        actions_frame = ttk.Frame(self.results_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.save_button = ttk.Button(
            actions_frame,
            text="Zapisz zaznaczone",
            style="success.TButton",
            command=self._on_save_selected,
        )
        self.save_button.grid(row=0, column=0, padx=(0, 10))

        self.generate_more_button = ttk.Button(
            actions_frame,
            text="Generuj więcej",
            style="primary.TButton",
            command=self._on_generate_more,
        )
        self.generate_more_button.grid(row=0, column=1, padx=(0, 10))

        self.cancel_button = ttk.Button(
            actions_frame,
            text="Anuluj",
            style="secondary.TButton",
            command=self._reset_view,
        )
        self.cancel_button.grid(row=0, column=2)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())
        self.bind("<Escape>", lambda e: self._on_back())

    def _on_back(self) -> None:
        """Handle back navigation"""
        if self.is_generating:
            # Confirm cancel
            confirm = ttk.Messagebox.yesno(
                title="Anulować generowanie?", message="Czy na pewno chcesz anulować generowanie fiszek?", parent=self
            )
            if not confirm:
                return

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_generate(self) -> None:
        """Handle flashcard generation"""
        # Validate input
        raw_text = self.text_input.get("1.0", "end-1c").strip()
        if not raw_text:
            self.show_toast("Błąd", "Tekst nie może być pusty")
            return

        model = self.model_var.get()

        # Update UI state
        self._set_generating_state(True)

        # Clear previous results
        self.generated_flashcards = []
        self.selected_flashcards = []

        # Start generation in a background thread
        thread = threading.Thread(target=self._generate_flashcards_thread, args=(raw_text, model))
        thread.daemon = True
        thread.start()

    def _generate_flashcards_thread(self, raw_text: str, model: str) -> None:
        """Background thread for flashcard generation."""
        try:
            flashcards = self.ai_service.generate_flashcards(raw_text=raw_text, deck_id=self.deck_id, model=model)

            # Store results
            self.generated_flashcards = flashcards

            # Pre-select all flashcards
            self.selected_flashcards = list(range(len(flashcards)))

            # Update UI on the main thread
            self.after(0, lambda: self._display_flashcards(flashcards))

        except AIAPIAuthError:
            self.after(
                0, lambda: self.show_toast("Błąd uwierzytelniania", "Sprawdź swój klucz API w ustawieniach profilu")
            )
            self.after(0, lambda: self._set_generating_state(False))

        except FlashcardGenerationError as e:
            error_message = str(e)  # Przechwycenie wartości e
            self.after(0, lambda: self.show_toast("Błąd generowania fiszek", error_message))
            self.after(0, lambda: self._set_generating_state(False))

        except Exception as e:
            error_message = self.ai_service.explain_error(e)
            self.after(0, lambda: self.show_toast("Błąd", error_message))
            self.after(0, lambda: self._set_generating_state(False))

    def _display_flashcards(self, flashcards: List[FlashcardDTO]) -> None:
        """Display generated flashcards in the UI."""
        # Clear existing flashcards
        for widget in self.flashcard_frame.winfo_children():
            widget.destroy()

        # Create a canvas with scrollbar
        canvas = ttk.Canvas(self.flashcard_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.flashcard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Add flashcards to the scrollable frame
        check_vars = []
        for i, card in enumerate(flashcards):
            frame = ttk.LabelFrame(scrollable_frame, text=f"Fiszka {i+1}", padding=10)
            frame.grid(row=i, column=0, sticky="ew", pady=(0, 10), padx=5)

            # Checkbox for selection
            var = ttk.BooleanVar(value=True)  # Pre-select all
            check_vars.append(var)

            check = ttk.Checkbutton(
                frame,
                text="Wybierz",
                variable=var,
                command=lambda idx=i, v=var: self._on_flashcard_select(idx, v.get()),
            )
            check.grid(row=0, column=0, sticky="w", pady=(0, 5))

            # Front and back
            ttk.Label(frame, text="Przód:").grid(row=1, column=0, sticky="w")
            front_text = ttk.Text(frame, height=3, width=60, wrap="word")
            front_text.grid(row=2, column=0, sticky="ew", pady=(0, 5))
            front_text.insert("1.0", card.front)
            front_text.configure(state="disabled")

            ttk.Label(frame, text="Tył:").grid(row=3, column=0, sticky="w")
            back_text = ttk.Text(frame, height=3, width=60, wrap="word")
            back_text.grid(row=4, column=0, sticky="ew")
            back_text.insert("1.0", card.back)
            back_text.configure(state="disabled")

            # Tags if available
            if card.tags and card.tags:
                tag_text = ", ".join(card.tags)
                ttk.Label(frame, text=f"Tagi: {tag_text}", style="secondary.TLabel").grid(
                    row=5, column=0, sticky="w", pady=(5, 0)
                )

        # Show results and hide progress indicator
        self._set_generating_state(False)
        self.results_frame.grid()

    def _on_flashcard_select(self, index: int, selected: bool) -> None:
        """Handle flashcard selection/deselection."""
        if selected and index not in self.selected_flashcards:
            self.selected_flashcards.append(index)
        elif not selected and index in self.selected_flashcards:
            self.selected_flashcards.remove(index)

    def _on_save_selected(self) -> None:
        """Save selected flashcards to the database."""
        if not self.selected_flashcards:
            self.show_toast("Uwaga", "Nie wybrano żadnej fiszki do zapisania")
            return

        # Convert DTOs to domain models and save
        saved_count = 0
        for idx in self.selected_flashcards:
            if idx >= len(self.generated_flashcards):
                continue

            card = self.generated_flashcards[idx]
            flashcard = Flashcard(
                id=None,
                deck_id=self.deck_id,
                front=card.front,
                back=card.back,
                tags=card.tags if card.tags else [],
                metadata=json.dumps(card.metadata) if card.metadata else None,
            )

            try:
                self.card_service.add_flashcard(flashcard)
                saved_count += 1
            except Exception as e:
                self.show_toast("Błąd zapisywania", str(e))

        # Show success message
        self.show_toast("Zapisano fiszki", f"Pomyślnie zapisano {saved_count} fiszek do talii {self.deck_name}")

        # Navigate back to card list
        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_generate_more(self) -> None:
        """Reset view to generate more flashcards."""
        self._reset_view()

    def _reset_view(self) -> None:
        """Reset view to initial state."""
        # Hide results and progress frames
        self.results_frame.grid_remove()
        self.progress_frame.grid_remove()

        # Clear selection
        self.generated_flashcards = []
        self.selected_flashcards = []

        # Enable input
        self.text_input.configure(state="normal")
        self.generate_button.configure(state="normal")
        self.model_combobox.configure(state="readonly")

    def _set_generating_state(self, generating: bool) -> None:
        """Update UI based on generation state."""
        self.is_generating = generating

        if generating:
            # Show progress and disable input
            self.progress_frame.grid()
            self.progress_bar.start(10)
            self.text_input.configure(state="disabled")
            self.generate_button.configure(state="disabled")
            self.model_combobox.configure(state="disabled")
            self.results_frame.grid_remove()
        else:
            # Hide progress and enable input
            self.progress_frame.grid_remove()
            self.progress_bar.stop()
            self.text_input.configure(state="normal")
            self.generate_button.configure(state="normal")
            self.model_combobox.configure(state="readonly")
