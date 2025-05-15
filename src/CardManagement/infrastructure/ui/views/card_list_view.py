from typing import Callable, List, Any

import ttkbootstrap as ttk

from CardManagement.application.card_service import CardService
from CardManagement.application.presenters.card_list_presenter import (
    CardListPresenter,
    FlashcardViewModel,
    ICardListView,
)
from Shared.application.session_service import SessionService
from Shared.application.navigation import NavigationControllerProtocol
from Shared.ui.widgets.header_bar import HeaderBar
from Shared.ui.widgets.confirmation_dialog import ConfirmationDialog
from CardManagement.infrastructure.ui.widgets.flashcard_table import FlashcardTable
from CardManagement.infrastructure.ui.widgets.button_panel import ButtonPanel


class CardListView(ttk.Frame, ICardListView):
    """View for displaying and managing the list of flashcards in a deck"""

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        card_service: CardService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        show_toast: Callable[[str, str], None],
    ):
        """Initialize the card list view.

        Args:
            parent: Parent widget
            deck_id: ID of the deck to display cards for
            deck_name: Name of the deck
            card_service: Service for card operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
            show_toast: Callback for showing toast notifications
        """
        super().__init__(parent)
        self._show_toast_callback = show_toast
        self.deck_id = deck_id
        self.deck_name = deck_name

        # Create presenter
        self.presenter = CardListPresenter(
            view=self,
            card_service=card_service,
            session_service=session_service,
            navigation_controller=navigation_controller,
            deck_id=deck_id,
            deck_name=deck_name,
        )

        # Initialize UI
        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # FlashcardTable row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, f"Fiszki - {self.deck_name}", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self.presenter.navigate_back)

        # Flashcard Table
        self.flashcard_table = FlashcardTable(
            self, on_edit=self.presenter.edit_flashcard, on_delete=self._show_delete_confirmation
        )
        self.flashcard_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Button Panel
        self.button_panel = ButtonPanel(
            self, on_add=self.presenter.add_flashcard, on_generate_ai=self.presenter.generate_with_ai, disabled=False
        )
        self.button_panel.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Start Study Button
        self.start_study_btn = ttk.Button(
            self.button_panel,
            text="Rozpocznij naukę",
            style="success.TButton",
            command=self.presenter.start_study_session,
        )
        self.start_study_btn.pack(side=ttk.LEFT, padx=5)

        # Ładuj karty po inicjalizacji UI
        self.presenter.load_cards()

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self.presenter.navigate_back())
        self.bind("<Visibility>", lambda e: self._on_visibility())

    def _on_visibility(self) -> None:
        """Handle visibility change event"""
        if self.winfo_viewable():
            self.presenter.load_cards()

    def _show_delete_confirmation(self, flashcard_id: int) -> None:
        """Show confirmation dialog for flashcard deletion"""
        ConfirmationDialog(
            self,
            "Usuń Fiszkę",
            "Czy na pewno chcesz usunąć tę fiszkę? Tej operacji nie można cofnąć.",
            "Usuń",
            "danger.TButton",
            "Anuluj",
            lambda: self.presenter.delete_flashcard(flashcard_id),
            lambda: None,
        )

    # ICardListView implementation
    def display_cards(self, cards: List[FlashcardViewModel]) -> None:
        """Display the list of cards"""
        self.flashcard_table.set_items(cards)

    def show_loading(self, is_loading: bool) -> None:
        """Show or hide loading state"""
        self.button_panel.set_disabled(is_loading)

    def show_error(self, message: str) -> None:
        """Show error message"""
        self.show_toast("Błąd", message)

    def show_toast(self, title: str, message: str) -> None:
        """Show toast notification"""
        self._show_toast_callback(title, message)

    def clear_card_selection(self) -> None:
        """Clear the current card selection"""
        self.flashcard_table.clear_selection()
