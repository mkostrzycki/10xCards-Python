from datetime import datetime
from typing import Callable, Optional, Protocol, Sequence, Any

from Shared.ui.widgets.generic_table_widget import GenericTableWidget


class DeckTableItem(Protocol):
    """Protocol defining the interface required for items displayed in the DeckTable"""

    id: int
    name: str
    created_at: datetime


class DeckTable(GenericTableWidget):
    """A table widget for displaying decks with sorting and selection capabilities"""

    def __init__(self, parent: Any, on_select: Callable[[int], None], on_delete: Callable[[int], None]):
        """
        Initialize the DeckTable widget.

        Args:
            parent: The parent widget
            on_select: Callback for when a deck is selected (double-clicked)
            on_delete: Callback for when delete is requested on a deck
        """
        # Configure columns
        columns = [("name", "Nazwa"), ("created_at", "Utworzono")]

        column_widths = {"name": 300, "created_at": 150}

        column_stretches = {"name": True, "created_at": False}

        super().__init__(
            parent,
            columns,
            column_widths=column_widths,
            column_stretches=column_stretches,
            height=25,
            on_double_click=lambda id: on_select(int(id)),
            on_delete_key=lambda id: on_delete(int(id)),
        )

    def set_items(self, items: Sequence[DeckTableItem]) -> None:
        """
        Update the table with new items.

        Args:
            items: Sequence of items implementing DeckTableItem protocol
        """
        self.clear()

        # Add new items
        for item in items:
            self.add_item(str(item.id), [item.name, item.created_at.strftime("%d-%m-%Y")])

    def get_selected_id(self) -> Optional[int]:
        """Get the ID of the currently selected item, if any"""
        selected_id = super().get_selected_id()
        return int(selected_id) if selected_id else None
