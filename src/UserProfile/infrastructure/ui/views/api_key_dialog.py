"""Dialog for setting OpenRouter API key."""

import tkinter as tk
from typing import Callable, Optional, Union

import ttkbootstrap as ttk

from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient


class APIKeyDialog(tk.Toplevel):
    """Dialog for setting or updating OpenRouter API key."""

    def __init__(
        self,
        parent: Union[tk.Tk, tk.Toplevel],
        api_client: OpenRouterAPIClient,
        current_key: Optional[str] = None,
        on_save: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the API key dialog.

        Args:
            parent: Parent window
            api_client: OpenRouter API client for key validation
            current_key: Current API key (masked if exists)
            on_save: Callback function to save the API key
        """
        super().__init__(parent)
        self.title("Ustaw klucz API OpenRouter")
        self.geometry("500x350")

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
        self.api_client = api_client
        self.on_save = on_save
        self.current_key = current_key

        # Variables
        self.api_key_var = ttk.StringVar(value=self._mask_api_key() if current_key else "")
        self.is_validating = False
        self.validation_message = ttk.StringVar()

        # UI setup
        self._setup_ui()

    def _mask_api_key(self) -> str:
        """Mask the API key for display.

        Returns:
            Masked key string (first 4 chars + asterisks)
        """
        if not self.current_key:
            return ""

        if len(self.current_key) <= 8:
            return "●" * len(self.current_key)

        return self.current_key[:4] + "●" * (len(self.current_key) - 8) + self.current_key[-4:]

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = ttk.Frame(container)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="Klucz API OpenRouter", style="h2.TLabel").pack(anchor=tk.W)

        # Information section
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        info_text = (
            "Klucz API OpenRouter jest wymagany do generowania fiszek z użyciem AI.\n\n"
            "1. Utwórz konto na stronie https://openrouter.ai\n"
            "2. Przejdź do ustawień konta i utwórz nowy klucz API\n"
            "3. Skopiuj klucz i wklej go poniżej\n\n"
            "Twój klucz API jest przechowywany w postaci zaszyfrowanej."
        )

        info_label = ttk.Label(info_frame, text=info_text, wraplength=470, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

        # API Key input
        input_frame = ttk.Frame(container)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Klucz API:", style="primary.TLabel").pack(anchor=tk.W, pady=(0, 5))

        key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, width=50, show="*")
        key_entry.pack(fill=tk.X)

        # Validation message
        validation_label = ttk.Label(container, textvariable=self.validation_message, style="secondary.TLabel")
        validation_label.pack(fill=tk.X, pady=(0, 10))

        # Button bar
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Validation indicator
        self.progress_bar = ttk.Progressbar(button_frame, mode="indeterminate", length=100)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_bar.pack_forget()  # Hide initially

        # Buttons
        self.save_button = ttk.Button(
            button_frame, text="Zapisz i weryfikuj", style="primary.TButton", command=self._validate_and_save
        )
        self.save_button.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

        # Set initial focus
        key_entry.focus_set()

    def _validate_and_save(self) -> None:
        """Validate the API key and save if valid."""
        api_key = self.api_key_var.get().strip()

        # Check if the key was changed
        if self.current_key and api_key == self._mask_api_key():
            self.destroy()
            return

        # Check for empty key
        if not api_key:
            self.validation_message.set("Klucz API nie może być pusty")
            return

        # Show validation in progress
        self._set_validating(True)
        self.validation_message.set("Weryfikacja klucza API...")

        # Start validation in a separate thread
        self.after(100, lambda: self._do_validation(api_key))

    def _do_validation(self, api_key: str) -> None:
        """Perform API key validation.

        Args:
            api_key: The API key to validate
        """
        # Validate the key with the API client
        try:
            is_valid, message = self.api_client.verify_key(api_key)

            if is_valid:
                # Save the key if valid
                if self.on_save:
                    self.on_save(api_key)

                # Close the dialog
                self.destroy()
            else:
                # Show error message
                self.validation_message.set(f"Błąd weryfikacji: {message}")
                self._set_validating(False)
        except Exception as e:
            # Handle unexpected errors
            self.validation_message.set(f"Nieoczekiwany błąd: {str(e)}")
            self._set_validating(False)

    def _set_validating(self, validating: bool) -> None:
        """Update UI based on validation state.

        Args:
            validating: Whether validation is in progress
        """
        self.is_validating = validating

        if validating:
            # Show progress, disable buttons
            self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
            self.progress_bar.start(10)
            self.save_button.configure(state="disabled")
        else:
            # Hide progress, enable buttons
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.save_button.configure(state="normal")
