"""Dialog for changing username."""

import tkinter as tk
from typing import Callable, Union

import ttkbootstrap as ttk


class ChangeUsernameDialog(tk.Toplevel):
    """Dialog for changing the user's username."""

    def __init__(
        self,
        parent: Union[tk.Toplevel, tk.Tk],
        current_username: str,
        on_save: Callable[[str], None],
    ):
        """Initialize the username change dialog.

        Args:
            parent: Parent widget
            current_username: Current username
            on_save: Callback function when username is saved
        """
        super().__init__(parent)
        self.title("Zmień nazwę profilu")
        self.geometry("450x300")  # Zwiększony rozmiar okna dialogowego

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        # Store parameters
        self.current_username = current_username
        self.on_save = on_save

        # Variables
        self.new_username_var = ttk.StringVar(value=current_username)
        self.error_message = ttk.StringVar()

        # UI setup
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(container, text="Zmień nazwę profilu", style="h2.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 15))

        # Current username
        current_frame = ttk.Frame(container)
        current_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(current_frame, text="Aktualna nazwa:").pack(side=tk.LEFT)
        ttk.Label(current_frame, text=self.current_username, style="primary.TLabel").pack(side=tk.LEFT, padx=(5, 0))

        # New username
        new_frame = ttk.Frame(container)
        new_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(new_frame, text="Nowa nazwa profilu:").pack(anchor=tk.W)
        username_entry = ttk.Entry(new_frame, textvariable=self.new_username_var, width=30)
        username_entry.pack(fill=tk.X, pady=(5, 0))
        username_entry.focus_set()

        # Validation message
        error_label = ttk.Label(container, textvariable=self.error_message, style="danger.TLabel")
        error_label.pack(fill=tk.X, pady=(0, 10))

        # Help text
        help_text = "Nazwa profilu może zawierać maksymalnie 30 znaków."
        help_label = ttk.Label(container, text=help_text, style="secondary.TLabel")
        help_label.pack(fill=tk.X, pady=(0, 10))

        # Buttons - umieszczam w ramce zajmującej dolną część okna
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))

        save_button = ttk.Button(button_frame, text="Zapisz", style="primary.TButton", command=self._validate_and_save)
        save_button.pack(side=tk.RIGHT)

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Bind Enter key to save
        self.bind("<Return>", lambda e: self._validate_and_save())

    def _validate_and_save(self) -> None:
        """Validate the input and save if valid."""
        new_username = self.new_username_var.get().strip()

        # Clear previous error
        self.error_message.set("")

        # Check for empty username
        if not new_username:
            self.error_message.set("Nazwa profilu nie może być pusta")
            return

        # Check if username is too long
        if len(new_username) > 30:
            self.error_message.set("Nazwa profilu może zawierać maksymalnie 30 znaków")
            return

        # Check if username has changed
        if new_username == self.current_username:
            self.destroy()
            return

        # Save the new username
        self.on_save(new_username)
        self.destroy()
