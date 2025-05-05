from typing import Callable, Protocol, Sequence, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import W, VERTICAL, END


class FlashcardTableItem(Protocol):
    """Protocol defining the interface required for items displayed in the FlashcardTable"""

    id: int
    front_text: str
    back_text: str
    source: str


class FlashcardTable(ttk.Frame):
    """A table widget for displaying flashcards with sorting and selection capabilities"""

    def __init__(self, parent: Any, on_edit: Callable[[int], None], on_delete: Callable[[int], None]):
        """
        Initialize the FlashcardTable widget.

        Args:
            parent: The parent widget
            on_edit: Callback for when edit is requested for a flashcard
            on_delete: Callback for when delete is requested for a flashcard
        """
        super().__init__(parent)
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create Treeview
        self.tree = ttk.Treeview(
            self, columns=("front_text", "back_text", "source"), show="headings", selectmode="browse"
        )

        # Configure columns
        self.tree.heading("front_text", text="Przód", anchor=W)
        self.tree.heading("back_text", text="Tył", anchor=W)
        self.tree.heading("source", text="Źródło", anchor=W)

        self.tree.column("front_text", width=300, stretch=True, anchor=W)
        self.tree.column("back_text", width=300, stretch=True, anchor=W)
        self.tree.column("source", width=100, stretch=False, anchor=W)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    def _bind_events(self) -> None:
        """Bind widget events"""
        self.tree.bind("<Double-1>", self._on_double_click)  # Double click to edit
        self.tree.bind("<Delete>", self._on_delete_key)  # Delete key to delete

    def _on_double_click(self, event) -> None:
        """Handle double click on a row"""
        selection = self.tree.selection()
        if selection:
            flashcard_id = int(selection[0])  # We use flashcard_id as item ID
            self.on_edit(flashcard_id)

    def _on_delete_key(self, event) -> None:
        """Handle delete key press"""
        selection = self.tree.selection()
        if selection:
            flashcard_id = int(selection[0])
            self.on_delete(flashcard_id)

    def set_items(self, items: Sequence[FlashcardTableItem]) -> None:
        """
        Update the table with new items.

        Args:
            items: Sequence of items implementing FlashcardTableItem protocol
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add new items
        for item in items:
            # Truncate text for display
            front_preview = (item.front_text[:50] + "...") if len(item.front_text) > 50 else item.front_text
            back_preview = (item.back_text[:50] + "...") if len(item.back_text) > 50 else item.back_text
            source_display = {"manual": "Ręcznie", "ai-generated": "AI", "ai-edited": "AI (edyt.)"}.get(
                item.source, item.source
            )

            self.tree.insert("", END, iid=str(item.id), values=(front_preview, back_preview, source_display))
