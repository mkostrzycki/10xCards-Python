from typing import Callable

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CreateDeckDialog(ttk.Toplevel):
    """Dialog for creating a new deck"""

    MAX_NAME_LENGTH = 50

    def __init__(self, parent: ttk.Widget, on_save: Callable[[str], None], on_cancel: Callable[[], None]):
        """
        Initialize the dialog.

        Args:
            parent: The parent widget
            on_save: Callback for when save is clicked with valid name
            on_cancel: Callback for when dialog is cancelled
        """
        super().__init__(parent)
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Configure window
        self.title("Utwórz nową talię")
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

        # Name label and entry
        name_frame = ttk.Frame(container)
        name_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(name_frame, text="Nazwa:").grid(row=0, column=0, sticky="w")

        self.name_var = ttk.StringVar()
        self.name_var.trace_add("write", self._on_name_changed)

        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=1, column=0, sticky="ew")

        # Character counter
        self.counter_label = ttk.Label(name_frame, text=f"0/{self.MAX_NAME_LENGTH}", style="secondary.TLabel")
        self.counter_label.grid(row=1, column=1, padx=(5, 0))

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=1, column=0, sticky="e", pady=(10, 0))

        ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self._on_cancel_click).grid(
            row=0, column=0, padx=(0, 5)
        )

        self.save_btn = ttk.Button(button_frame, text="Zapisz", style="primary.TButton", command=self._on_save_click)
        self.save_btn.grid(row=0, column=1)

        # Initial state
        self._update_save_button()
        self.name_entry.focus_set()

    def _bind_events(self) -> None:
        """Bind keyboard events"""
        self.bind("<Return>", lambda e: self._on_save_click())
        self.bind("<Escape>", lambda e: self._on_cancel_click())

    def _on_name_changed(self, *args) -> None:
        """Handle name input changes"""
        name = self.name_var.get()
        count = len(name)
        self.counter_label.configure(
            text=f"{count}/{self.MAX_NAME_LENGTH}",
            style="danger.TLabel" if count > self.MAX_NAME_LENGTH else "secondary.TLabel",
        )
        self._update_save_button()

    def _update_save_button(self) -> None:
        """Update save button state based on validation"""
        name = self.name_var.get().strip()
        valid = bool(name and len(name) <= self.MAX_NAME_LENGTH)
        self.save_btn.configure(state="normal" if valid else "disabled")

    def _on_save_click(self) -> None:
        """Handle save button click"""
        name = self.name_var.get().strip()
        if name and len(name) <= self.MAX_NAME_LENGTH:
            self.on_save(name)
            self.destroy()

    def _on_cancel_click(self) -> None:
        """Handle cancel button click"""
        self.on_cancel()
        self.destroy()
