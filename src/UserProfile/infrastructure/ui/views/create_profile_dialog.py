from dataclasses import dataclass
from typing import Optional, Callable, cast
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import Wm


@dataclass
class CreateProfileDialogState:
    username_input: str = ""
    error_message: Optional[str] = None


class CreateProfileDialog(tk.Toplevel):
    """Dialog for creating a new user profile."""

    def __init__(self, parent: tk.Widget, on_create: Callable[[str], None]):
        """Initialize the create profile dialog.

        Args:
            parent: Parent widget
            on_create: Callback for profile creation
        """
        super().__init__(parent)
        self._on_create = on_create
        self._state = CreateProfileDialogState()

        self.title("Nowy profil")
        self.transient(cast(Wm, parent))  # Cast parent to Wm type for transient
        self.grab_set()  # Make dialog modal

        # Center the dialog
        window_width = 400
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self._setup_ui()

        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Focus username input
        self._username_input.focus_set()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        # Main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Prompt label
        prompt_label = ttk.Label(main_frame, text="Podaj nazwę nowego profilu:", style="primary.TLabel")
        prompt_label.pack(fill=tk.X, pady=(0, 10))

        # Username input
        self._username_input = ttk.Entry(main_frame, width=40)
        self._username_input.pack(fill=tk.X, pady=(0, 5))

        # Error label (hidden by default)
        self._error_label = ttk.Label(main_frame, text="", style="danger.TLabel", wraplength=350)
        self._error_label.pack(fill=tk.X, pady=(0, 10))

        # Button bar
        button_bar = ttk.Frame(main_frame)
        button_bar.pack(fill=tk.X, pady=(10, 0))

        cancel_btn = ttk.Button(button_bar, text="Anuluj", command=self._on_cancel, style="secondary.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        create_btn = ttk.Button(button_bar, text="Utwórz", command=self._on_create_clicked, style="primary.TButton")
        create_btn.pack(side=tk.RIGHT)

        # Bind events
        self._username_input.bind("<Return>", lambda e: self._on_create_clicked())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _validate_input(self) -> bool:
        """Validate the username input.

        Returns:
            bool: True if validation passes, False otherwise
        """
        username = self._username_input.get().strip()
        self._state.username_input = username

        if not username:
            self._show_error("Nazwa profilu nie może być pusta.")
            return False

        if len(username) > 30:
            self._show_error("Nazwa profilu nie może być dłuższa niż 30 znaków.")
            return False

        return True

    def _show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display
        """
        self._state.error_message = message
        self._error_label.configure(text=message)

    def _clear_error(self) -> None:
        """Clear the error message."""
        self._state.error_message = None
        self._error_label.configure(text="")

    def _on_create_clicked(self) -> None:
        """Handle create button click."""
        if not self._validate_input():
            return

        self._on_create(self._state.username_input)
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click or window close."""
        self.destroy()
