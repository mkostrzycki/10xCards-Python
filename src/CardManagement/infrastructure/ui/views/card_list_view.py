import logging
from datetime import datetime
from typing import Callable, List, Optional, Any, Protocol

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT, LEFT

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.application.card_service import CardService
from Shared.application.session_service import SessionService
from Shared.ui.widgets.header_bar import HeaderBar
from CardManagement.infrastructure.ui.widgets.flashcard_table import FlashcardTable
from CardManagement.infrastructure.ui.widgets.button_panel import ButtonPanel
from CardManagement.infrastructure.ui.widgets.delete_confirmation_dialog import DeleteConfirmationDialog


class FlashcardViewModel:
    """Data transfer object for flashcard display"""

    def __init__(self, id: int, front_text: str, back_text: str, source: str):
        self.id = id
        self.front_text = front_text
        self.back_text = back_text
        self.source = source

    @classmethod
    def from_flashcard(cls, flashcard: Flashcard) -> "FlashcardViewModel":
        """Creates a ViewModel from a domain Flashcard model"""
        if flashcard.id is None:
            raise ValueError("Cannot create FlashcardViewModel from Flashcard with None id")
        return cls(
            id=flashcard.id,
            front_text=flashcard.front_text,
            back_text=flashcard.back_text,
            source=flashcard.source
        )


class CardListView(ttk.Frame):
    """View for displaying and managing the list of flashcards in a deck"""

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        card_service: CardService,
        session_service: SessionService,
        navigation_controller,
        show_toast: Callable[[str, str], None],
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.card_service = card_service
        self.session_service = session_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast

        # State
        self.flashcards: List[FlashcardViewModel] = []
        self.loading: bool = False
        self.error: Optional[str] = None
        self.deleting_id: Optional[int] = None
        self.dialog_open: bool = False

        # Initialize UI
        self._init_ui()
        self._bind_events()

        # Load flashcards
        self.load_flashcards()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # FlashcardTable row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, f"Fiszki - {self.deck_name}", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Flashcard Table
        self.flashcard_table = FlashcardTable(
            self,
            on_edit=self._on_edit_flashcard,
            on_delete=self._on_delete_flashcard
        )
        self.flashcard_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Button Panel
        self.button_panel = ButtonPanel(
            self,
            on_add=self._on_add_flashcard,
            on_generate_ai=self._on_generate_ai,
            disabled=self.loading
        )
        self.button_panel.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())

    def _on_back(self) -> None:
        """Handle back navigation"""
        self.navigation_controller.navigate("/decks")

    def _on_add_flashcard(self) -> None:
        """Handle add flashcard button click"""
        if self.dialog_open:
            return

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards/new")

    def _on_generate_ai(self) -> None:
        """Handle generate with AI button click"""
        if self.dialog_open:
            return

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards/generate-ai")

    def _on_edit_flashcard(self, flashcard_id: int) -> None:
        """Handle flashcard edit request"""
        if self.dialog_open:
            return

        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards/{flashcard_id}/edit")

    def _on_delete_flashcard(self, flashcard_id: int) -> None:
        """Handle flashcard deletion request"""
        if self.dialog_open or self.deleting_id:
            return

        # Find flashcard
        flashcard = self._find_flashcard_by_id(flashcard_id)
        if not flashcard:
            return

        self.dialog_open = True
        self.deleting_id = flashcard_id
        DeleteConfirmationDialog(
            self,
            flashcard.front_text,
            self._handle_flashcard_deletion,
            self._handle_deletion_cancel
        )

    def _find_flashcard_by_id(self, flashcard_id: int) -> Optional[FlashcardViewModel]:
        """Find a flashcard by its ID

        Args:
            flashcard_id: ID of the flashcard to find

        Returns:
            Optional[FlashcardViewModel]: The flashcard if found, None otherwise
        """
        for flashcard in self.flashcards:
            if flashcard.id == flashcard_id:
                return flashcard
        return None

    def _handle_flashcard_deletion(self) -> None:
        """Handle confirmed flashcard deletion"""
        try:
            if self.deleting_id is None:
                logging.error("Attempting to delete a flashcard but deleting_id is None")
                self.show_toast("Błąd", "Nieprawidłowe ID fiszki")
                return

            self.card_service.delete_flashcard(self.deleting_id)
            self.show_toast("Sukces", "Fiszka została usunięta")
            self.load_flashcards()  # Refresh list
        except ValueError as e:
            self.show_toast("Błąd", str(e))
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się usunąć fiszki: {str(e)}")
            logging.error(f"Failed to delete flashcard: {str(e)}")
        finally:
            self._reset_deletion_state()

    def _handle_deletion_cancel(self) -> None:
        """Handle cancellation of flashcard deletion"""
        self._reset_deletion_state()

    def _reset_deletion_state(self) -> None:
        """Reset the state related to flashcard deletion"""
        self.dialog_open = False
        self.deleting_id = None

    def load_flashcards(self) -> None:
        """Load flashcards for the current deck"""
        self.loading = True
        self.button_panel.set_disabled(True)
        try:
            # Fetch flashcards
            flashcards = self.card_service.list_by_deck_id(self.deck_id)

            # Convert to view models
            self.flashcards = [FlashcardViewModel.from_flashcard(card) for card in flashcards]

            # Update table
            self.flashcard_table.set_items(self.flashcards)
        except Exception as e:
            self.error = str(e)
            self.show_toast("Błąd", f"Wystąpił błąd podczas ładowania fiszek: {str(e)}")
            logging.error(f"Error loading flashcards: {str(e)}")
        finally:
            self.loading = False
            self.button_panel.set_disabled(False)
