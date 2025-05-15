"""Dialog for setting OpenRouter API key."""

import tkinter as tk
import threading
from typing import Callable, Optional, Union
import logging
import sys

import ttkbootstrap as ttk

from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from Shared.infrastructure.security.crypto import crypto_manager


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
        self.geometry("500x380")  # Zwiększona wysokość dla komunikatów

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
        self.validation_thread: Optional[threading.Thread] = None

        # Variables
        self.api_key_var = ttk.StringVar(value=self._mask_api_key() if current_key else "")
        self.is_validating = False
        self.validation_message = ttk.StringVar()
        self.validation_status = ttk.StringVar(value="")

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

    def _test_crypto_with_key(self, api_key: str) -> bool:
        """Test encryption and decryption of the key before saving.

        Args:
            api_key: The API key to test

        Returns:
            True if encryption and decryption works, False if there are issues
        """
        try:
            # Test roundtrip encryption/decryption
            logging.info(f"Testing encryption/decryption for API key of length {len(api_key)}")
            encrypted = crypto_manager.encrypt_api_key(api_key)
            decrypted = crypto_manager.decrypt_api_key(encrypted)

            if decrypted == api_key:
                logging.info("Encryption/decryption test passed")
                return True
            else:
                logging.error("Encryption/decryption test failed: decrypted value doesn't match original")
                return False
        except Exception as e:
            logging.error(f"Encryption/decryption test error: {str(e)}", exc_info=True)
            return False

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
            "Klucz powinien zaczynać się od 'sk-or-'. Zostanie on zweryfikowany online."
        )

        info_label = ttk.Label(info_frame, text=info_text, wraplength=470, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

        # API Key input
        input_frame = ttk.Frame(container)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Klucz API:", style="primary.TLabel").pack(anchor=tk.W, pady=(0, 5))

        key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, width=50, show="*")
        key_entry.pack(fill=tk.X)

        # Status indicator
        status_frame = ttk.Frame(container)
        status_frame.pack(fill=tk.X, pady=(5, 5))

        self.status_label = ttk.Label(
            status_frame, textvariable=self.validation_status, foreground="gray", font=("TkDefaultFont", 9, "italic")
        )
        self.status_label.pack(anchor=tk.W)

        # Validation message
        validation_label = ttk.Label(container, textvariable=self.validation_message, wraplength=470, justify=tk.LEFT)
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

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self._cancel)
        cancel_button.pack(side=tk.RIGHT)

        # Set initial focus
        key_entry.focus_set()

        # Bind protocol for window close
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _validate_and_save(self) -> None:
        """Validate the API key and save if valid."""
        api_key = self.api_key_var.get().strip()

        # Check if the key was changed from the masked version
        if self.current_key and api_key == self._mask_api_key():
            # Użytkownik nie zmienił zamaskowanego klucza, więc używamy istniejącego klucza
            self.destroy()
            return

        # Check for empty key
        if not api_key:
            self.validation_message.set("Klucz API nie może być pusty")
            return

        # Basic format validation before network request
        if not api_key.startswith("sk-or-"):
            self.validation_message.set("Nieprawidłowy format klucza API (powinien zaczynać się od 'sk-or-')")
            return

        # Show validation in progress
        self._set_validating(True)
        self.validation_message.set("")
        self.validation_status.set("Weryfikacja klucza API...")

        # Start validation in a separate thread to avoid UI freeze
        self.validation_thread = threading.Thread(target=self._threaded_validation, args=(api_key,))
        self.validation_thread.daemon = True
        self.validation_thread.start()

    def _threaded_validation(self, api_key: str) -> None:
        """Run validation in a separate thread.

        Args:
            api_key: The API key to validate
        """
        try:
            is_valid, message = self.api_client.verify_key(api_key)
            # Schedule UI update on the main thread
            self.after(0, lambda: self._handle_validation_result(is_valid, message, api_key))
        except Exception:
            # Schedule error handling on the main thread
            error_msg = str(sys.exc_info()[1])
            self.after(0, lambda: self._handle_validation_error(error_msg))

    def _handle_validation_result(self, is_valid: bool, message: str, api_key: str) -> None:
        """Process validation results on the main thread.

        Args:
            is_valid: Whether the key is valid
            message: Status message from verification
            api_key: The validated API key
        """
        if is_valid:
            # Test encryption/decryption before saving
            if not self._test_crypto_with_key(api_key):
                self.validation_status.set("Weryfikacja klucza zakończona, ale wystąpił błąd szyfrowania!")
                self.validation_message.set(
                    "Błąd: Nie można poprawnie zaszyfrować klucza. Skontaktuj się z administratorem."
                )
                self._set_validating(False)
                return

            self.validation_status.set("Klucz API zweryfikowany pomyślnie!")
            if self.on_save:
                try:
                    self.on_save(api_key)
                    # Close dialog after successful save
                    self.destroy()
                except Exception:
                    logging.error("Error saving API key", exc_info=True)
                    self.validation_message.set("Błąd zapisu klucza. Sprawdź logi aplikacji.")
                    self._set_validating(False)
            else:
                self.validation_message.set("Błąd wewnętrzny: Brak funkcji zapisującej.")
                self._set_validating(False)
        else:
            self.validation_status.set("Weryfikacja klucza nieudana!")
            self.validation_message.set(f"Błąd weryfikacji: {message}")
            self._set_validating(False)

    def _handle_validation_error(self, error_message: str) -> None:
        """Handle validation errors on the main thread.

        Args:
            error_message: Error description
        """
        self.validation_status.set("Błąd podczas weryfikacji!")
        self.validation_message.set(f"Nieoczekiwany błąd: {error_message}")
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

    def _cancel(self) -> None:
        """Cancel operation and close dialog."""
        # Stop validation thread if running
        if self.validation_thread and self.validation_thread.is_alive() and self.is_validating:
            logging.info("Cancelling validation in progress")
            # We can't directly stop the thread, but we can close the dialog
            self._set_validating(False)

        self.destroy()
