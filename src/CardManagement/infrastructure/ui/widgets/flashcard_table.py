from typing import Callable, Protocol, Sequence, Any

from Shared.ui.widgets.generic_table_widget import GenericTableWidget


class FlashcardTableItem(Protocol):
    """Protocol defining the interface required for items displayed in the FlashcardTable"""

    id: int
    front_text: str
    back_text: str
    source: str


class FlashcardTable(GenericTableWidget):
    """A table widget for displaying flashcards with sorting and selection capabilities"""

    def __init__(self, parent: Any, on_edit: Callable[[int], None], on_delete: Callable[[int], None]):
        """
        Initialize the FlashcardTable widget.

        Args:
            parent: The parent widget
            on_edit: Callback for when edit is requested for a flashcard
            on_delete: Callback for when delete is requested for a flashcard
        """
        # Configure columns
        columns = [("front_text", "Przód"), ("back_text", "Tył"), ("source", "Źródło")]

        column_widths = {"front_text": 300, "back_text": 300, "source": 100}

        column_stretches = {"front_text": True, "back_text": True, "source": False}

        super().__init__(
            parent,
            columns,
            column_widths=column_widths,
            column_stretches=column_stretches,
            height=25,
            on_double_click=lambda id: on_edit(int(id)),
            on_delete_key=lambda id: on_delete(int(id)),
        )

    def set_items(self, items: Sequence[FlashcardTableItem]) -> None:
        """
        Update the table with new items.

        Args:
            items: Sequence of items implementing FlashcardTableItem protocol
        """
        self.clear()

        # Add new items
        for item in items:
            # Truncate text for display
            front_preview = (item.front_text[:30] + "...") if len(item.front_text) > 30 else item.front_text
            back_preview = (item.back_text[:30] + "...") if len(item.back_text) > 30 else item.back_text
            source_display = {"manual": "Ręcznie", "ai-generated": "AI", "ai-edited": "AI (edyt.)"}.get(
                item.source, item.source
            )

            self.add_item(str(item.id), [front_preview, back_preview, source_display])
