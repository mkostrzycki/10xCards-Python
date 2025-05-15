from typing import Any, Callable, Dict, List, Optional, Tuple
import tkinter as tk
import ttkbootstrap as ttk


class GenericTableWidget(ttk.Frame):
    """A generic table widget based on ttk.Treeview.

    Features:
    - Automatic scrollbar
    - Column configuration (width, alignment)
    - Row selection handling
    - Double-click handling
    - Delete key handling
    - Basic sorting
    """

    def __init__(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, str]],  # [(id, display_name), ...]
        *,
        column_widths: Optional[Dict[str, int]] = None,  # {column_id: width}
        column_stretches: Optional[Dict[str, bool]] = None,  # {column_id: stretch}
        height: Optional[int] = None,  # Number of rows to display
        on_select: Optional[Callable[[str], None]] = None,  # Called with selected item id
        on_double_click: Optional[Callable[[str], None]] = None,  # Called with double-clicked item id
        on_delete_key: Optional[Callable[[str], None]] = None,  # Called with selected item id when Delete pressed
    ) -> None:
        """Initialize the generic table widget.

        Args:
            parent: The parent widget
            columns: List of (column_id, display_name) tuples
            column_widths: Optional dict of column widths
            column_stretches: Optional dict specifying which columns should stretch
            height: Optional height in rows
            on_select: Optional callback for selection changes
            on_double_click: Optional callback for double-clicks
            on_delete_key: Optional callback for Delete key press
        """
        super().__init__(parent)

        # Store callbacks
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._on_delete_key = on_delete_key

        # Create treeview with scrollbar
        self.tree = ttk.Treeview(
            self,
            columns=[col_id for col_id, _ in columns],
            show="headings",  # Don't show the first empty column
            height=height if height is not None else 10,
        )

        # Configure scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure columns
        for col_id, display_name in columns:
            self.tree.heading(col_id, text=display_name)
            # Set column width if specified
            if column_widths and col_id in column_widths:
                self.tree.column(col_id, width=column_widths[col_id])
            # Set column stretch if specified
            if column_stretches and col_id in column_stretches:
                self.tree.column(col_id, stretch=column_stretches[col_id])

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Bind events
        if on_select:
            self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        if on_double_click:
            self.tree.bind("<Double-1>", self._handle_double_click)
        if on_delete_key:
            self.tree.bind("<Delete>", self._handle_delete_key)

    def clear(self) -> None:
        """Remove all items from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_item(self, item_id: str, values: List[Any]) -> None:
        """Add a new item to the table.

        Args:
            item_id: Unique identifier for the item
            values: List of values for each column
        """
        self.tree.insert("", "end", item_id, values=values)

    def update_item(self, item_id: str, values: List[Any]) -> None:
        """Update an existing item in the table.

        Args:
            item_id: Identifier of the item to update
            values: New values for each column
        """
        self.tree.item(item_id, values=values)

    def delete_item(self, item_id: str) -> None:
        """Delete an item from the table.

        Args:
            item_id: Identifier of the item to delete
        """
        self.tree.delete(item_id)

    def get_selected_id(self) -> Optional[str]:
        """Get the ID of the currently selected item.

        Returns:
            The selected item ID or None if nothing is selected.
        """
        selection = self.tree.selection()
        return selection[0] if selection else None

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.tree.selection_remove(self.tree.selection())

    def _handle_select(self, event: tk.Event) -> None:
        """Handle selection change event."""
        if self._on_select:
            selected_id = self.get_selected_id()
            if selected_id:
                self._on_select(selected_id)

    def _handle_double_click(self, event: tk.Event) -> None:
        """Handle double-click event."""
        if self._on_double_click:
            selected_id = self.get_selected_id()
            if selected_id:
                self._on_double_click(selected_id)

    def _handle_delete_key(self, event: tk.Event) -> None:
        """Handle Delete key press event."""
        if self._on_delete_key:
            selected_id = self.get_selected_id()
            if selected_id:
                self._on_delete_key(selected_id)
