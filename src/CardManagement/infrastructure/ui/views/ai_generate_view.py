import logging
from typing import Callable, Any

import ttkbootstrap as ttk

from Shared.ui.widgets.header_bar import HeaderBar


class AIGenerateView(ttk.Frame):
    """View for generating flashcards using AI (stub for future implementation)"""

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        navigation_controller,
        show_toast: Callable[[str, str], None],
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast

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
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)

        # Info message
        ttk.Label(
            content,
            text="Generowanie fiszek z AI będzie dostępne wkrótce! 🚀",
            style="primary.TLabel",
            font=("TkDefaultFont", 14)
        ).grid(row=0, column=0, pady=20)

        ttk.Label(
            content,
            text="Ta funkcjonalność jest w trakcie implementacji.\nSprawdź ponownie w następnej wersji aplikacji.",
            justify="center",
            wraplength=400
        ).grid(row=1, column=0)

        # Back button
        ttk.Button(
            content,
            text="Wróć do listy",
            style="primary.TButton",
            command=self._on_back
        ).grid(row=2, column=0, pady=(20, 0))

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())
        self.bind("<Escape>", lambda e: self._on_back())

    def _on_back(self) -> None:
        """Handle back navigation"""
        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")
