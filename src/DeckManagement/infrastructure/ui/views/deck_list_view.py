from typing import Callable, List, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT

from DeckManagement.application.deck_service import DeckService
from DeckManagement.application.presenters.deck_list_presenter import DeckListPresenter, DeckViewModel, IDeckListView
from Shared.application.session_service import SessionService
from Shared.application.navigation import NavigationControllerProtocol
from Shared.ui.widgets.header_bar import HeaderBar
from Shared.ui.widgets.confirmation_dialog import ConfirmationDialog
from DeckManagement.infrastructure.ui.widgets.deck_table import DeckTable
from DeckManagement.infrastructure.ui.widgets.create_deck_dialog import CreateDeckDialog


class DeckListView(ttk.Frame, IDeckListView):
    """View for displaying and managing the list of decks"""

    def __init__(
        self,
        parent: Any,
        deck_service: DeckService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        show_toast: Callable[[str, str], None],
    ):
        """Initialize the deck list view.

        Args:
            parent: Parent widget
            deck_service: Service for deck operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
            show_toast: Callback for showing toast notifications
        """
        super().__init__(parent)
        self._show_toast_callback = show_toast
        self.dialog_open = False

        # Create presenter
        self.presenter = DeckListPresenter(
            view=self,
            deck_service=deck_service,
            session_service=session_service,
            navigation_controller=navigation_controller,
        )

        # Initialize UI
        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # DeckTable row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, "Talie", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self.presenter.navigate_back)

        # Button Bar
        self.button_bar = ttk.Frame(self)
        self.button_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Create New Deck button
        self.create_deck_btn = ttk.Button(
            self.button_bar, text="Utwórz nową talię", style="primary.TButton", command=self._show_create_deck_dialog
        )
        self.create_deck_btn.pack(side=RIGHT, padx=5)

        # Start Study button
        self.start_study_btn = ttk.Button(
            self.button_bar, text="Rozpocznij naukę", style="success.TButton", command=self._on_start_study_click
        )
        self.start_study_btn.pack(side=RIGHT, padx=5)
        self.start_study_btn.configure(state="disabled")  # Initially disabled

        # Deck Table
        self.deck_table = DeckTable(
            self, on_select=self.presenter.handle_deck_selected, on_delete=self._show_delete_confirmation
        )
        self.deck_table.grid(row=1, column=0, sticky="nsew", padx=5)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self.presenter.navigate_back())
        self.bind("<Visibility>", lambda e: self._on_visibility())

    def _on_visibility(self) -> None:
        """Handle visibility change event"""
        if self.winfo_viewable():
            self.presenter.load_decks()

    def _show_create_deck_dialog(self) -> None:
        """Show dialog for creating a new deck"""
        if self.dialog_open:
            return

        self.dialog_open = True
        CreateDeckDialog(self, on_confirm=self._handle_deck_creation, on_cancel=self._handle_dialog_cancelled)

    def _show_delete_confirmation(self, deck_id: int) -> None:
        """Show confirmation dialog for deck deletion"""
        if self.dialog_open:
            return

        self.dialog_open = True
        ConfirmationDialog(
            self,
            "Usuń Talię",
            "Czy na pewno chcesz usunąć tę talię? Tej operacji nie można cofnąć.",
            "Usuń",
            "danger.TButton",
            "Anuluj",
            lambda: self._handle_deck_deletion_confirmed(deck_id),
            self._handle_dialog_cancelled,
        )

    def _handle_deck_creation(self, deck_name: str) -> None:
        """Handle deck creation from dialog"""
        self.dialog_open = False
        self.presenter.handle_deck_creation(deck_name)

    def _handle_deck_deletion_confirmed(self, deck_id: int) -> None:
        """Handle confirmed deck deletion"""
        self.dialog_open = False
        self.presenter.handle_deck_deletion_confirmed()

    def _handle_dialog_cancelled(self) -> None:
        """Handle dialog cancellation"""
        self.dialog_open = False
        self.presenter.handle_deck_deletion_cancelled()

    def _on_start_study_click(self) -> None:
        """Handle start study button click"""
        selected_deck_id = self.deck_table.get_selected_id()
        if selected_deck_id is not None:
            self.presenter.start_study_session(selected_deck_id)
        else:
            self.show_toast("Błąd", "Wybierz talię, aby rozpocząć naukę.")

    # IDeckListView implementation
    def display_decks(self, decks: List[DeckViewModel]) -> None:
        """Display the list of decks"""
        self.deck_table.set_items(decks)

    def show_loading(self, is_loading: bool) -> None:
        """Show or hide loading state"""
        # TODO: Add loading indicator if needed
        pass

    def show_error(self, message: str) -> None:
        """Show error message"""
        self.show_toast("Błąd", message)

    def clear_deck_selection(self) -> None:
        """Clear the current deck selection"""
        self.deck_table.clear_selection()
        self.enable_study_button(False)

    def show_toast(self, title: str, message: str) -> None:
        """Show toast notification"""
        self._show_toast_callback(title, message)

    def enable_study_button(self, enabled: bool) -> None:
        """Enable or disable the study button"""
        self.start_study_btn.configure(state="normal" if enabled else "disabled")
