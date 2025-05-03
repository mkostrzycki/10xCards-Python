import logging
from datetime import datetime
from typing import Callable, List, Optional

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlite3 import IntegrityError

from src.DeckManagement.domain.models.Deck import Deck
from src.DeckManagement.application.deck_service import DeckService
from src.Shared.ui.widgets.header_bar import HeaderBar
from src.DeckManagement.infrastructure.ui.widgets.deck_table import DeckTable, DeckTableItem
from src.DeckManagement.infrastructure.ui.widgets.create_deck_dialog import CreateDeckDialog
from src.DeckManagement.infrastructure.ui.widgets.delete_confirmation_dialog import DeleteConfirmationDialog


class DeckViewModel(DeckTableItem):
    """Data transfer object for deck display"""
    def __init__(self, id: int, name: str, created_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at

    @classmethod
    def from_deck(cls, deck: Deck) -> 'DeckViewModel':
        """Creates a ViewModel from a domain Deck model"""
        return cls(
            id=deck.id,
            name=deck.name,
            created_at=deck.created_at
        )


class DeckListView(ttk.Frame):
    """View for displaying and managing the list of decks"""

    def __init__(
        self,
        parent: ttk.Widget,
        deck_service: DeckService,
        navigation_controller,
        show_toast: Callable[[str, str], None]
    ):
        super().__init__(parent)
        self.deck_service = deck_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        
        # State
        self.decks: List[DeckViewModel] = []
        self.is_loading: bool = False
        self.dialog_open: bool = False
        self.deleting_deck_id: Optional[int] = None
        
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
        self.header.set_back_command(self._on_back)
        
        # Button Bar
        self.button_bar = ttk.Frame(self)
        self.button_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Create New Deck button
        self.create_deck_btn = ttk.Button(
            self.button_bar,
            text="Utwórz nową talię",
            style="primary.TButton",
            command=self._on_create_deck_click
        )
        self.create_deck_btn.pack(side=RIGHT, padx=5)
        
        # Deck Table
        self.deck_table = DeckTable(
            self,
            on_select=self._on_deck_select,
            on_delete=self._on_deck_delete
        )
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
            
        self.dialog_open = True
        
        def on_save(name: str) -> None:
            try:
                # TODO: Get current user_id from session/auth service
                user_id = 1  # Temporary hardcoded value
                deck = self.deck_service.create_deck(name, user_id)
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
                
        def on_cancel() -> None:
            self.dialog_open = False
            
        CreateDeckDialog(self, on_save, on_cancel)
        
    def _on_deck_select(self, deck_id: int) -> None:
        """Handle deck selection"""
        self.navigation_controller.navigate(f"/decks/{deck_id}/cards")
        
    def _on_deck_delete(self, deck_id: int) -> None:
        """Handle deck deletion request"""
        if self.dialog_open or self.deleting_deck_id:
            return
            
        # Find deck name
        deck = next((d for d in self.decks if d.id == deck_id), None)
        if not deck:
            return
            
        self.dialog_open = True
        self.deleting_deck_id = deck_id
        
        def on_confirm() -> None:
            try:
                # TODO: Get current user_id from session/auth service
                user_id = 1  # Temporary hardcoded value
                self.deck_service.delete_deck(deck_id, user_id)
                self.show_toast("Sukces", "Talia została usunięta")
                self.load_decks()  # Refresh list
            except ValueError as e:
                self.show_toast("Błąd", str(e))
            except Exception as e:
                self.show_toast("Błąd", f"Nie udało się usunąć talii: {str(e)}")
                logging.error(f"Failed to delete deck: {str(e)}")
            finally:
                self.dialog_open = False
                self.deleting_deck_id = None
                
        def on_cancel() -> None:
            self.dialog_open = False
            self.deleting_deck_id = None
            
        DeleteConfirmationDialog(self, deck.name, on_confirm, on_cancel)
        
    def load_decks(self) -> None:
        """Load decks from the service"""
        if self.is_loading:
            return
            
        self.is_loading = True
        try:
            # TODO: Get current user_id from session/auth service
            user_id = 1  # Temporary hardcoded value
            decks = self.deck_service.list_decks(user_id)
            self.decks = [DeckViewModel.from_deck(deck) for deck in decks]
            self.deck_table.set_items(self.decks)
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się załadować talii: {str(e)}")
            logging.error(f"Failed to load decks: {str(e)}")
        finally:
            self.is_loading = False
