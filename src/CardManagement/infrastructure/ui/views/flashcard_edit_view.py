import logging
from typing import Callable, Optional, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.application.card_service import CardService
from Shared.ui.widgets.header_bar import HeaderBar


class FlashcardEditView(ttk.Frame):
    """View for creating and editing flashcards"""

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        card_service: CardService,
        navigation_controller,
        show_toast: Callable[[str, str], None],
        flashcard_id: Optional[int] = None,  # None for create mode, ID for edit mode
    ):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.card_service = card_service
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        self.flashcard_id = flashcard_id

        # State
        self.loading: bool = False
        self.saving: bool = False

        # Initialize UI
        self._init_ui()
        self._bind_events()

        # Load data if editing
        if self.flashcard_id:
            self.load_flashcard()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Content row
        self.grid_columnconfigure(0, weight=1)

        # Header
        mode = "Edytuj" if self.flashcard_id else "Nowa"
        self.header = HeaderBar(self, f"{mode} fiszka - {self.deck_name}", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)

        # Front text
        front_frame = ttk.LabelFrame(content, text="Przód", padding=10)
        front_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.front_text = ttk.Text(front_frame, height=4, width=50, wrap="word")
        self.front_text.pack(fill="both", expand=True)

        self.front_counter = ttk.Label(front_frame, text="0/200", style="secondary.TLabel")
        self.front_counter.pack(side=RIGHT, pady=(5, 0))

        # Back text
        back_frame = ttk.LabelFrame(content, text="Tył", padding=10)
        back_frame.grid(row=1, column=0, sticky="ew")

        self.back_text = ttk.Text(back_frame, height=8, width=50, wrap="word")
        self.back_text.pack(fill="both", expand=True)

        self.back_counter = ttk.Label(back_frame, text="0/500", style="secondary.TLabel")
        self.back_counter.pack(side=RIGHT, pady=(5, 0))

        # Button bar
        button_bar = ttk.Frame(content)
        button_bar.grid(row=2, column=0, sticky="e", pady=(10, 0))

        self.cancel_btn = ttk.Button(button_bar, text="Anuluj", style="secondary.TButton", command=self._on_back)
        self.cancel_btn.pack(side=RIGHT, padx=(5, 0))

        self.save_btn = ttk.Button(button_bar, text="Zapisz", style="primary.TButton", command=self._on_save)
        self.save_btn.pack(side=RIGHT)

        # Bind text change events
        self.front_text.bind("<<Modified>>", self._on_front_text_changed)
        self.back_text.bind("<<Modified>>", self._on_back_text_changed)

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self._on_back())
        self.bind("<Control-Return>", lambda e: self._on_save())

    def _on_front_text_changed(self, event=None) -> None:
        """Handle front text changes"""
        if not self.front_text.edit_modified():  # Skip if not actually modified
            return

        text = self.front_text.get("1.0", "end-1c")
        count = len(text)
        self.front_counter.configure(text=f"{count}/200", style="danger.TLabel" if count > 200 else "secondary.TLabel")
        self._update_save_button()
        self.front_text.edit_modified(False)

    def _on_back_text_changed(self, event=None) -> None:
        """Handle back text changes"""
        if not self.back_text.edit_modified():  # Skip if not actually modified
            return

        text = self.back_text.get("1.0", "end-1c")
        count = len(text)
        self.back_counter.configure(text=f"{count}/500", style="danger.TLabel" if count > 500 else "secondary.TLabel")
        self._update_save_button()
        self.back_text.edit_modified(False)

    def _update_save_button(self) -> None:
        """Update save button state based on validation"""
        front_text = self.front_text.get("1.0", "end-1c").strip()
        back_text = self.back_text.get("1.0", "end-1c").strip()

        valid = (
            bool(front_text)
            and bool(back_text)
            and len(front_text) <= 200
            and len(back_text) <= 500
            and not self.saving
        )

        self.save_btn.configure(state="normal" if valid else "disabled")

    def _on_back(self) -> None:
        """Handle back navigation"""
        self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

    def _on_save(self) -> None:
        """Handle save button click"""
        if self.saving:
            return

        self.saving = True
        self.save_btn.configure(state="disabled")

        try:
            front_text = self.front_text.get("1.0", "end-1c")
            back_text = self.back_text.get("1.0", "end-1c")

            if self.flashcard_id:
                # Update existing
                self.card_service.update_flashcard(
                    flashcard_id=self.flashcard_id, front_text=front_text, back_text=back_text
                )
                self.show_toast("Sukces", "Fiszka została zaktualizowana")
            else:
                # Create new
                self.card_service.create_flashcard(deck_id=self.deck_id, front_text=front_text, back_text=back_text)
                self.show_toast("Sukces", "Fiszka została utworzona")

            # Navigate back to list
            self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")

        except ValueError as e:
            self.show_toast("Błąd", str(e))
            self.saving = False
            self._update_save_button()
        except Exception as e:
            self.show_toast("Błąd", f"Wystąpił błąd podczas zapisywania: {str(e)}")
            logging.error(f"Error saving flashcard: {str(e)}")
            self.saving = False
            self._update_save_button()

    def load_flashcard(self) -> None:
        """Load flashcard data for editing"""
        self.loading = True
        try:
            assert self.flashcard_id is not None
            flashcard = self.card_service.get_flashcard(self.flashcard_id)
            if not flashcard:
                raise ValueError("Fiszka nie istnieje")

            # Set texts
            self.front_text.delete("1.0", "end")
            self.front_text.insert("1.0", flashcard.front_text)
            self.back_text.delete("1.0", "end")
            self.back_text.insert("1.0", flashcard.back_text)

            # Trigger counters update
            self._on_front_text_changed()
            self._on_back_text_changed()

        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się załadować fiszki: {str(e)}")
            logging.error(f"Error loading flashcard {self.flashcard_id}: {str(e)}")
            self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")
        finally:
            self.loading = False
