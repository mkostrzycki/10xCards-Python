"""Dialog for managing user password."""

import tkinter as tk
from typing import Callable, Optional

import ttkbootstrap as ttk


class ManagePasswordDialog(tk.Toplevel):
    """Dialog for setting, changing or removing user password."""

    def __init__(
        self,
        parent: tk.Widget,
        has_password_set: bool,
        on_save: Callable[[Optional[str], Optional[str]], None],
    ):
        """Initialize the password management dialog.

        Args:
            parent: Parent widget
            has_password_set: Whether user already has a password set
            on_save: Callback function when password is saved/changed/removed
        """
        super().__init__(parent)
        self.title("Zarządzaj hasłem")
        self.geometry("400x350")

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
        self.has_password_set = has_password_set
        self.on_save = on_save

        # Variables
        self.current_password_var = ttk.StringVar()
        self.new_password_var = ttk.StringVar()
        self.confirm_password_var = ttk.StringVar()
        self.error_message = ttk.StringVar()
        self.show_password_var = ttk.BooleanVar(value=False)

        # UI setup
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(container, text="Zarządzaj hasłem", style="h2.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 15))

        # Current password (only if password is already set)
        if self.has_password_set:
            current_frame = ttk.Frame(container)
            current_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(current_frame, text="Aktualne hasło:").pack(anchor=tk.W)
            self.current_password_entry = ttk.Entry(
                current_frame, textvariable=self.current_password_var, width=30, show="*"
            )
            self.current_password_entry.pack(fill=tk.X, pady=(5, 0))
            self.current_password_entry.focus_set()

        # New password
        new_password_frame = ttk.Frame(container)
        new_password_frame.pack(fill=tk.X, pady=(0, 10))

        if self.has_password_set:
            label_text = "Nowe hasło (zostaw puste by usunąć):"
        else:
            label_text = "Nowe hasło:"

        ttk.Label(new_password_frame, text=label_text).pack(anchor=tk.W)
        new_password_entry = ttk.Entry(new_password_frame, textvariable=self.new_password_var, width=30, show="*")
        new_password_entry.pack(fill=tk.X, pady=(5, 0))

        if not self.has_password_set:
            new_password_entry.focus_set()

        # Confirm password
        confirm_frame = ttk.Frame(container)
        confirm_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(confirm_frame, text="Potwierdź nowe hasło:").pack(anchor=tk.W)
        confirm_password_entry = ttk.Entry(confirm_frame, textvariable=self.confirm_password_var, width=30, show="*")
        confirm_password_entry.pack(fill=tk.X, pady=(5, 0))

        # Show password option
        show_password_frame = ttk.Frame(container)
        show_password_frame.pack(fill=tk.X, pady=(0, 10))

        show_password_cb = ttk.Checkbutton(
            show_password_frame,
            text="Pokaż hasło",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
        )
        show_password_cb.pack(anchor=tk.W)

        # Validation message
        error_label = ttk.Label(container, textvariable=self.error_message, style="danger.TLabel")
        error_label.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        save_button = ttk.Button(button_frame, text="Zapisz", style="primary.TButton", command=self._validate_and_save)
        save_button.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

        # Bind Enter key to save
        self.bind("<Return>", lambda e: self._validate_and_save())

    def _toggle_password_visibility(self) -> None:
        """Toggle the visibility of password fields."""
        show_char = "" if self.show_password_var.get() else "*"

        if self.has_password_set:
            self.current_password_entry.config(show=show_char)

        for entry in self.winfo_children()[0].winfo_children():
            if isinstance(entry, ttk.Frame):
                for widget in entry.winfo_children():
                    if isinstance(widget, ttk.Entry):
                        widget.config(show=show_char)

    def _validate_and_save(self) -> None:
        """Validate the input and save if valid."""
        current_password = self.current_password_var.get() if self.has_password_set else None
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()

        # Clear previous error
        self.error_message.set("")

        # Check current password if needed
        if self.has_password_set and not current_password:
            self.error_message.set("Wprowadź aktualne hasło")
            return

        # Check if new password is empty (allowed for removal)
        if not new_password and not self.has_password_set:
            self.error_message.set("Wprowadź nowe hasło")
            return

        # Check if passwords match when setting/changing password
        if new_password and new_password != confirm_password:
            self.error_message.set("Hasła nie są identyczne")
            return

        # Save the password change
        self.on_save(current_password, new_password)
        self.destroy()
