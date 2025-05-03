from datetime import datetime
from typing import Callable, Optional, Protocol, Sequence

import ttkbootstrap as ttk
from ttkbootstrap.constants import W, VERTICAL, END


class DeckTableItem(Protocol):
    """Protocol defining the interface required for items displayed in the DeckTable"""

    id: int
    name: str
    created_at: datetime


class DeckTable(ttk.Frame):
    """A table widget for displaying decks with sorting and selection capabilities"""

    def __init__(self, parent: ttk.Widget, on_select: Callable[[int], None], on_delete: Callable[[int], None]):
        """
        Initialize the DeckTable widget.

        Args:
            parent: The parent widget
            on_select: Callback for when a deck is selected (double-clicked)
            on_delete: Callback for when delete is requested on a deck
        """
        super().__init__(parent)
        self.on_select = on_select
        self.on_delete = on_delete

        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=("name", "created_at"), show="headings", selectmode="browse")

        # Configure columns
        self.tree.heading("name", text="Nazwa", anchor=W)
        self.tree.heading("created_at", text="Utworzono", anchor=W)

        self.tree.column("name", width=300, stretch=True, anchor=W)
        self.tree.column("created_at", width=150, stretch=False, anchor=W)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    def _bind_events(self) -> None:
        """Bind widget events"""
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>", self._on_delete_key)

    def _on_double_click(self, event) -> None:
        """Handle double click on a row"""
        selection = self.tree.selection()
        if selection:
            deck_id = int(selection[0])  # We use deck_id as item ID
            self.on_select(deck_id)

    def _on_delete_key(self, event) -> None:
        """Handle delete key press"""
        selection = self.tree.selection()
        if selection:
            deck_id = int(selection[0])
            self.on_delete(deck_id)

    def set_items(self, items: Sequence[DeckTableItem]) -> None:
        """
        Update the table with new items.

        Args:
            items: Sequence of items implementing DeckTableItem protocol
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add new items
        for item in items:
            self.tree.insert("", END, iid=str(item.id), values=(item.name, item.created_at.strftime("%d-%m-%Y")))

    def get_selected_id(self) -> Optional[int]:
        """Get the ID of the currently selected item, if any"""
        selection = self.tree.selection()
        return int(selection[0]) if selection else None
