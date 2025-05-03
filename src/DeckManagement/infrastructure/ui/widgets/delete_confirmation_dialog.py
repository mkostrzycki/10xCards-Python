from typing import Callable

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import MessageDialog


class DeleteConfirmationDialog(ttk.Toplevel):
    """Dialog for confirming deck deletion"""
    
    def __init__(
        self,
        parent: ttk.Widget,
        deck_name: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None]
    ):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent widget
            deck_name: Name of the deck to delete
            on_confirm: Callback for when deletion is confirmed
            on_cancel: Callback for when dialog is cancelled
        """
        super().__init__(parent)
        self.deck_name = deck_name
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        # Configure window
        self.title("Usuń talię")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._init_ui()
        self._bind_events()
        
        # Center on parent
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")
        
    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Main container
        container = ttk.Frame(self, padding=10)
        container.grid(sticky="nsew")
        
        # Warning message
        message = f"Czy na pewno usunąć talię '{self.deck_name}' i wszystkie jej fiszki?"
        ttk.Label(
            container,
            text=message,
            wraplength=300
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Buttons
        ttk.Button(
            container,
            text="Nie",
            style="secondary.TButton",
            command=self._on_cancel_click
        ).grid(row=1, column=0, padx=(0, 5))
        
        ttk.Button(
            container,
            text="Tak",
            style="danger.TButton",
            command=self._on_confirm_click
        ).grid(row=1, column=1)
        
    def _bind_events(self) -> None:
        """Bind keyboard events"""
        self.bind("<Return>", lambda e: self._on_confirm_click())
        self.bind("<Escape>", lambda e: self._on_cancel_click())
        
    def _on_confirm_click(self) -> None:
        """Handle confirm button click"""
        self.on_confirm()
        self.destroy()
        
    def _on_cancel_click(self) -> None:
        """Handle cancel button click"""
        self.on_cancel()
        self.destroy()
