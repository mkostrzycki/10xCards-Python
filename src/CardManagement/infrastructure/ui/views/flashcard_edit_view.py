from typing import Optional, Any
from tkinter.scrolledtext import ScrolledText

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT, LEFT
from ttkbootstrap.dialogs import Messagebox

from CardManagement.application.card_service import CardService
from CardManagement.application.presenters.flashcard_edit_presenter import FlashcardEditPresenter, IFlashcardEditView
from Shared.application.navigation import NavigationControllerProtocol
from Shared.ui.widgets.header_bar import HeaderBar


class FlashcardEditView(ttk.Frame, IFlashcardEditView):
    """View for creating and editing flashcards"""

    # Constants
    FRONT_TEXT_MAX_LENGTH = 200
    BACK_TEXT_MAX_LENGTH = 500

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        card_service: CardService,
        navigation_controller: NavigationControllerProtocol,
        flashcard_id: Optional[int] = None,  # None for create mode, ID for edit mode
    ):
        super().__init__(parent)
        self.deck_name = deck_name

        # Create presenter
        self.presenter = FlashcardEditPresenter(
            view=self,
            card_service=card_service,
            navigation=navigation_controller,
            deck_id=deck_id,
            flashcard_id=flashcard_id,
        )

        # Initialize UI
        self._init_ui()
        self._bind_events()

        # Initialize presenter
        self.presenter.initialize()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Content row
        self.grid_columnconfigure(0, weight=1)

        # Header
        mode = "Edytuj" if self.presenter._flashcard_id else "Nowa"
        self.header = HeaderBar(self, f"{mode} fiszka - {self.deck_name}", show_back_button=True)
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

        self.front_counter = ttk.Label(front_frame, text=f"0/{self.FRONT_TEXT_MAX_LENGTH}", style="secondary.TLabel")
        self.front_counter.pack(side=RIGHT, pady=(5, 0))

        # Back text
        back_frame = ttk.LabelFrame(content, text="Tył", padding=10)
        back_frame.grid(row=1, column=0, sticky="ew")

        self.back_text = ScrolledText(back_frame, height=8, width=50, wrap="word")
        self.back_text.pack(fill="both", expand=True)

        self.back_counter = ttk.Label(back_frame, text=f"0/{self.BACK_TEXT_MAX_LENGTH}", style="secondary.TLabel")
        self.back_counter.pack(side=RIGHT, pady=(5, 0))

        # Button bar
        button_bar = ttk.Frame(content)
        button_bar.grid(row=2, column=0, sticky="e", pady=(10, 0))

        self.save_btn = ttk.Button(button_bar, text="Zapisz", style="primary.TButton", command=self._on_save)
        self.save_btn.pack(side=RIGHT)

        self.cancel_btn = ttk.Button(
            button_bar, text="Anuluj", style="secondary.TButton", command=self.presenter.navigate_back
        )
        self.cancel_btn.pack(side=RIGHT, padx=(0, 5))

        # Delete button (only in edit mode)
        if self.presenter._flashcard_id:
            self.delete_btn = ttk.Button(button_bar, text="Usuń", style="danger.TButton", command=self.presenter.delete)
            self.delete_btn.pack(side=LEFT, padx=(0, 5))

        # Bind text change events
        self.front_text.bind("<<Modified>>", self._on_front_text_changed)
        self.back_text.bind("<<Modified>>", self._on_back_text_changed)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self.presenter.navigate_back())
        self.bind("<Control-Return>", lambda e: self._on_save())
        if self.presenter._flashcard_id:
            self.bind("<Delete>", lambda e: self.presenter.delete())

    def _on_front_text_changed(self, event=None) -> None:
        """Handle front text changes"""
        if not self.front_text.edit_modified():  # Skip if not actually modified
            return

        text = self.front_text.get("1.0", "end-1c")
        count = len(text)
        self.front_counter.configure(
            text=f"{count}/{self.FRONT_TEXT_MAX_LENGTH}",
            style="danger.TLabel" if count > self.FRONT_TEXT_MAX_LENGTH else "secondary.TLabel",
        )
        self._notify_text_change()
        self.front_text.edit_modified(False)

    def _on_back_text_changed(self, event=None) -> None:
        """Handle back text changes"""
        if not self.back_text.edit_modified():  # Skip if not actually modified
            return

        text = self.back_text.get("1.0", "end-1c")
        count = len(text)
        self.back_counter.configure(
            text=f"{count}/{self.BACK_TEXT_MAX_LENGTH}",
            style="danger.TLabel" if count > self.BACK_TEXT_MAX_LENGTH else "secondary.TLabel",
        )
        self._notify_text_change()
        self.back_text.edit_modified(False)

    def _notify_text_change(self) -> None:
        """Notify presenter about text changes"""
        front_text = self.front_text.get("1.0", "end-1c")
        back_text = self.back_text.get("1.0", "end-1c")
        self.presenter.handle_text_change(front_text, back_text)

    def _on_save(self) -> None:
        """Handle save button click"""
        self.presenter.save()

    # IFlashcardEditView implementation
    def display_flashcard(self, front_text: str, back_text: str) -> None:
        """Display flashcard data in the view."""
        self.front_text.delete("1.0", "end")
        self.front_text.insert("1.0", front_text)
        self.back_text.delete("1.0", "end")
        self.back_text.insert("1.0", back_text)
        self._notify_text_change()

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification."""
        # This will be injected by the parent view/window
        pass

    def show_loading(self, is_loading: bool) -> None:
        """Show/hide loading state."""
        if is_loading:
            self.save_btn.configure(state="disabled")
            if hasattr(self, "delete_btn"):
                self.delete_btn.configure(state="disabled")
        else:
            self._notify_text_change()  # This will update button states correctly

    def show_saving(self, is_saving: bool) -> None:
        """Show/hide saving state."""
        if is_saving:
            self.save_btn.configure(state="disabled")
            if hasattr(self, "delete_btn"):
                self.delete_btn.configure(state="disabled")
        else:
            self._notify_text_change()  # This will update button states correctly

    def show_delete_confirmation(self, on_confirm: bool) -> None:
        """Show delete confirmation dialog."""
        confirm = Messagebox.yesno(
            title="Potwierdź usunięcie",
            message="Czy na pewno chcesz usunąć fiszkę?",
            parent=self,
        )
        if confirm:
            self.presenter.handle_delete_confirmed()

    def update_save_button_state(self, is_enabled: bool) -> None:
        """Update save button state."""
        self.save_btn.configure(state="normal" if is_enabled else "disabled")
