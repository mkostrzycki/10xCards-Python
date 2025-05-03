import logging
from datetime import datetime
from typing import Callable, List, Optional
from sqlite3 import IntegrityError

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT, LEFT

from src.DeckManagement.domain.models.Deck import Deck
from src.DeckManagement.application.deck_service import DeckService
from src.Shared.application.session_service import SessionService
from src.Shared.ui.widgets.header_bar import HeaderBar
from src.DeckManagement.infrastructure.ui.widgets.deck_table import DeckTable, DeckTableItem
from src.DeckManagement.infrastructure.ui.widgets.create_deck_dialog import CreateDeckDialog
from src.DeckManagement.infrastructure.ui.widgets.delete_confirmation_dialog import DeleteConfirmationDialog


class DeckViewModel(DeckTableItem):
    """Data transfer object for deck display"""

    def __init__(self, id: int | None, name: str, created_at: datetime | None):
        if id is None or created_at is None:
            raise ValueError("id and created_at must not be None for DeckViewModel")
        self.id = id
        self.name = name
        self.created_at = created_at

    @classmethod
    def from_deck(cls, deck: Deck) -> "DeckViewModel":
        """Creates a ViewModel from a domain Deck model"""
        if deck.id is None or deck.created_at is None:
            raise ValueError("Cannot create DeckViewModel from Deck with None id or created_at")
        return cls(id=deck.id, name=deck.name, created_at=deck.created_at)


class DeckListView(ttk.Frame):
    """View for displaying and managing the list of decks"""

    def __init__(
        self,
        parent: ttk.Widget,
        deck_service: DeckService,
        session_service: SessionService,
        navigation_controller,
        show_toast: Callable[[str, str], None],
    ):
        super().__init__(parent)
        self.deck_service = deck_service
        self.session_service = session_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast

        # State
        self.decks: List[DeckViewModel] = []
        self.is_loading: bool = False
        self.dialog_open: bool = False
        self.deleting_deck_id: Optional[int] = None

        # Check if user is authenticated
        if not self.session_service.is_authenticated():
            self.show_toast("Błąd", "Musisz być zalogowany aby przeglądać talie.")
            self.navigation_controller.navigate("/profiles")
            return

        self._init_ui()
        self._bind_events()
        self.load_decks()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # DeckTable row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, "Talie", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Add logout button to header
        user = self.session_service.get_current_user()
        if user:
            logout_frame = ttk.Frame(self.header)
            logout_frame.pack(side=RIGHT, padx=5)

            username_label = ttk.Label(logout_frame, text=f"Zalogowany jako: {user.username}", style="secondary.TLabel")
            username_label.pack(side=LEFT, padx=(0, 10))

            logout_btn = ttk.Button(logout_frame, text="Wyloguj", style="secondary.TButton", command=self._on_logout)
            logout_btn.pack(side=RIGHT)

        # Button Bar
        self.button_bar = ttk.Frame(self)
        self.button_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Create New Deck button
        self.create_deck_btn = ttk.Button(
            self.button_bar, text="Utwórz nową talię", style="primary.TButton", command=self._on_create_deck_click
        )
        self.create_deck_btn.pack(side=RIGHT, padx=5)

        # Deck Table
        self.deck_table = DeckTable(self, on_select=self._on_deck_select, on_delete=self._on_deck_delete)
        self.deck_table.grid(row=1, column=0, sticky="nsew", padx=5)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())

    def _on_back(self) -> None:
        """Handle back navigation"""
        self.navigation_controller.navigate("/profiles")

    def _on_create_deck_click(self) -> None:
        """Handle create deck button click"""
        if self.dialog_open:
            return

        if not self._ensure_user_authenticated("utworzyć talię"):
            return

        self.dialog_open = True
        CreateDeckDialog(self, self._handle_deck_creation, self._handle_dialog_cancel)

    def _ensure_user_authenticated(self, action_description: str) -> bool:
        """Verify user is authenticated for the specified action

        Args:
            action_description: Description of the action requiring authentication

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        if not self.session_service.is_authenticated():
            self.show_toast("Błąd", f"Musisz być zalogowany aby {action_description}.")
            self.navigation_controller.navigate("/profiles")
            return False
        return True

    def _get_authenticated_user_id(self) -> Optional[int]:
        """Get the current authenticated user ID

        Returns:
            Optional[int]: User ID if authenticated user with valid ID exists, None otherwise
        """
        user = self.session_service.get_current_user()
        if not user:
            self.show_toast("Błąd", "Musisz być zalogowany aby wykonać tę operację.")
            self.navigation_controller.navigate("/profiles")
            return None

        if user.id is None:
            self.show_toast("Błąd", "Błąd identyfikatora użytkownika.")
            self.navigation_controller.navigate("/profiles")
            return None

        return user.id

    def _handle_deck_creation(self, name: str) -> None:
        """Handle deck creation logic

        Args:
            name: Name of the deck to create
        """
        try:
            user_id = self._get_authenticated_user_id()
            if user_id is None:
                return

            self.deck_service.create_deck(name, user_id)
            self.show_toast("Sukces", "Talia została utworzona")
            self.load_decks()  # Refresh list
        except ValueError as e:
            self.show_toast("Błąd", str(e))
        except IntegrityError:
            self.show_toast("Błąd", "Talia o tej nazwie już istnieje")
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się utworzyć talii: {str(e)}")
            logging.error(f"Failed to create deck: {str(e)}")
        finally:
            self.dialog_open = False

    def _handle_dialog_cancel(self) -> None:
        """Handle dialog cancellation"""
        self.dialog_open = False

    def _on_deck_select(self, deck_id: int) -> None:
        """Handle deck selection"""
        if not self._ensure_user_authenticated("przeglądać talie"):
            return

        self.navigation_controller.navigate(f"/decks/{deck_id}/cards")

    def _on_deck_delete(self, deck_id: int) -> None:
        """Handle deck deletion request"""
        if self.dialog_open or self.deleting_deck_id:
            return

        if not self._ensure_user_authenticated("usunąć talię"):
            return

        # Find deck name
        deck_to_delete = self._find_deck_by_id(deck_id)
        if not deck_to_delete:
            return

        self.dialog_open = True
        self.deleting_deck_id = deck_id
        DeleteConfirmationDialog(self, deck_to_delete.name, self._handle_deck_deletion, self._handle_deletion_cancel)

    def _find_deck_by_id(self, deck_id: int) -> Optional[DeckViewModel]:
        """Find a deck by its ID

        Args:
            deck_id: ID of the deck to find

        Returns:
            Optional[DeckViewModel]: The deck if found, None otherwise
        """
        return next((d for d in self.decks if d.id == deck_id), None)

    def _handle_deck_deletion(self) -> None:
        """Handle confirmed deck deletion"""
        try:
            user_id = self._get_authenticated_user_id()
            if user_id is None:
                return

            if self.deleting_deck_id is None:
                logging.error("Attempting to delete a deck but deleting_deck_id is None")
                self.show_toast("Błąd", "Nieprawidłowe ID talii")
                return

            self.deck_service.delete_deck(self.deleting_deck_id, user_id)
            self.show_toast("Sukces", "Talia została usunięta")
            self.load_decks()  # Refresh list
        except ValueError as e:
            self.show_toast("Błąd", str(e))
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się usunąć talii: {str(e)}")
            logging.error(f"Failed to delete deck: {str(e)}")
        finally:
            self._reset_deletion_state()

    def _handle_deletion_cancel(self) -> None:
        """Handle cancellation of deck deletion"""
        self._reset_deletion_state()

    def _reset_deletion_state(self) -> None:
        """Reset the state related to deck deletion"""
        self.dialog_open = False
        self.deleting_deck_id = None

    def _on_logout(self) -> None:
        """Handle logout button click"""
        self.session_service.logout()
        self.show_toast("Info", "Wylogowano pomyślnie")
        self.navigation_controller.navigate("/profiles")

    def load_decks(self) -> None:
        """Load decks from the service"""
        if self.is_loading:
            return

        if not self._ensure_user_authenticated("przeglądać talie"):
            return

        self.is_loading = True
        try:
            user_id = self._get_authenticated_user_id()
            if user_id is None:
                return

            decks = self.deck_service.list_decks(user_id)
            self.decks = [DeckViewModel.from_deck(deck) for deck in decks]
            self.deck_table.set_items(self.decks)
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się załadować talii: {str(e)}")
            logging.error(f"Failed to load decks: {str(e)}")
        finally:
            self.is_loading = False
