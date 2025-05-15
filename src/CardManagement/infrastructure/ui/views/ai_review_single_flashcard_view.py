"""View for reviewing AI-generated flashcards one by one."""

from typing import Any, List, Optional
from tkinter.scrolledtext import ScrolledText
import logging

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT
from ttkbootstrap.dialogs import Messagebox

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from CardManagement.application.presenters.ai_review_single_flashcard_presenter import (
    AIReviewSingleFlashcardPresenter,
    IAIReviewSingleFlashcardView,
)
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.application.navigation import NavigationControllerProtocol
from Shared.ui.widgets.header_bar import HeaderBar

logger = logging.getLogger(__name__)


class AIReviewSingleFlashcardView(ttk.Frame, IAIReviewSingleFlashcardView):
    """View for reviewing AI-generated flashcards one by one"""

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
        available_llm_models: List[str],
        original_source_text: str,
    ):
        logger.debug(
            f"Initializing AIReviewSingleFlashcardView: deck_id={deck_id}, "
            f"index={current_flashcard_index}, flashcards={len(generated_flashcards_dtos)}"
        )
        super().__init__(parent)

        # Create presenter
        self.presenter = AIReviewSingleFlashcardPresenter(
            view=self,
            ai_service=ai_service,
            card_service=card_service,
            navigation=navigation_controller,
            deck_id=deck_id,
            deck_name=deck_name,
            generated_flashcards_dtos=generated_flashcards_dtos,
            current_flashcard_index=current_flashcard_index,
            available_llm_models=available_llm_models,
            original_source_text=original_source_text,
        )

        # Initialize UI
        self._init_ui()
        self._bind_events()

        # Initialize presenter
        logger.debug("About to initialize presenter")
        self.presenter.initialize()
        logger.debug("Presenter initialized successfully")

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Content row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(
            self,
            f"Przeglądanie wygenerowanych fiszek ({self.presenter._current_index + 1}/{len(self.presenter._flashcards)})",
            show_back_button=True,
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self.presenter.navigate_back)

        # Content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)

        # Front text
        front_frame = ttk.LabelFrame(content, text="Przód", padding=10)
        front_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.front_text = ScrolledText(front_frame, height=4, width=50, wrap="word")
        self.front_text.pack(fill="both", expand=True)

        self.front_counter = ttk.Label(
            front_frame, text=f"0/{self.presenter.FRONT_TEXT_MAX_LENGTH}", style="secondary.TLabel"
        )
        self.front_counter.pack(side=RIGHT, pady=(5, 0))

        # Back text
        back_frame = ttk.LabelFrame(content, text="Tył", padding=10)
        back_frame.grid(row=1, column=0, sticky="ew")

        self.back_text = ScrolledText(back_frame, height=8, width=50, wrap="word")
        self.back_text.pack(fill="both", expand=True)

        self.back_counter = ttk.Label(
            back_frame, text=f"0/{self.presenter.BACK_TEXT_MAX_LENGTH}", style="secondary.TLabel"
        )
        self.back_counter.pack(side=RIGHT, pady=(5, 0))

        # Button bar
        button_bar = ttk.Frame(content)
        button_bar.grid(row=2, column=0, sticky="e", pady=(10, 0))

        self.save_btn = ttk.Button(
            button_bar,
            text="Zapisz i kontynuuj",
            style="primary.TButton",
            command=self.presenter.save_and_continue,
        )
        self.save_btn.pack(side=RIGHT)

        self.discard_btn = ttk.Button(
            button_bar,
            text="Odrzuć",
            style="danger.TButton",
            command=self.presenter.discard_and_continue,
        )
        self.discard_btn.pack(side=RIGHT, padx=(0, 5))

        # Bind text change events
        self.front_text.bind("<<Modified>>", self._on_text_changed)
        self.back_text.bind("<<Modified>>", self._on_text_changed)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self.presenter.navigate_back())
        self.bind("<Control-Return>", lambda e: self.presenter.save_and_continue())
        self.bind("<Control-Delete>", lambda e: self.presenter.discard_and_continue())

    def _on_text_changed(self, event=None) -> None:
        """Handle text changes"""
        if not self.front_text.edit_modified() and not self.back_text.edit_modified():
            return

        self.presenter.handle_text_change()
        self.update_char_counts()

        # Reset modified flags
        self.front_text.edit_modified(False)
        self.back_text.edit_modified(False)

    # IAIReviewSingleFlashcardView implementation
    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification."""
        # This will be injected by the parent view/window
        logger.debug(f"Toast requested: {title} - {message}")
        pass

    def show_saving(self, is_saving: bool) -> None:
        """Show/hide saving state."""
        logger.debug(f"Showing saving state: {is_saving}")
        self.save_btn.configure(state="disabled" if is_saving else "normal")
        self.discard_btn.configure(state="disabled" if is_saving else "normal")
        self.front_text.configure(state="disabled" if is_saving else "normal")
        self.back_text.configure(state="disabled" if is_saving else "normal")

    def show_unsaved_changes_confirmation(self) -> bool:
        """Show unsaved changes confirmation dialog."""
        logger.debug("Showing unsaved changes confirmation dialog")
        return bool(
            Messagebox.yesno(
                title="Niezapisane zmiany",
                message="Masz niezapisane zmiany. Czy na pewno chcesz wyjść?",
                parent=self,
            )
        )

    def show_discard_confirmation(self) -> bool:
        """Show discard confirmation dialog."""
        logger.debug("Showing discard confirmation dialog")
        return bool(
            Messagebox.yesno(
                title="Potwierdź odrzucenie",
                message="Czy na pewno chcesz odrzucić tę fiszkę?",
                parent=self,
            )
        )

    def update_save_button_state(self, is_enabled: bool) -> None:
        """Update save button state."""
        logger.debug(f"Updating save button state: {is_enabled}")
        self.save_btn.configure(state="normal" if is_enabled else "disabled")

    def get_front_text(self) -> str:
        """Get the front text."""
        return self.front_text.get("1.0", "end-1c")

    def get_back_text(self) -> str:
        """Get the back text."""
        return self.back_text.get("1.0", "end-1c")

    def display_flashcard(self, front_text: str, back_text: str, tags: Optional[List[str]] = None) -> None:
        """Display flashcard data in the view."""
        logger.debug(f"Displaying flashcard - front: {front_text[:20]}..., back: {back_text[:20]}...")
        self.front_text.delete("1.0", "end")
        self.front_text.insert("1.0", front_text)
        self.back_text.delete("1.0", "end")
        self.back_text.insert("1.0", back_text)
        self.update_char_counts()

    def update_char_counts(self) -> None:
        """Update character counters."""
        front_text = self.get_front_text()
        back_text = self.get_back_text()

        front_count = len(front_text)
        back_count = len(back_text)

        self.front_counter.configure(
            text=f"{front_count}/{self.presenter.FRONT_TEXT_MAX_LENGTH}",
            style="danger.TLabel" if front_count > self.presenter.FRONT_TEXT_MAX_LENGTH else "secondary.TLabel",
        )

        self.back_counter.configure(
            text=f"{back_count}/{self.presenter.BACK_TEXT_MAX_LENGTH}",
            style="danger.TLabel" if back_count > self.presenter.BACK_TEXT_MAX_LENGTH else "secondary.TLabel",
        )
