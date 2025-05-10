"""Dialog for selecting application theme."""

import tkinter as tk
from typing import Callable, List, Union

import ttkbootstrap as ttk


class SelectThemeDialog(tk.Toplevel):
    """Dialog for selecting the application color theme."""

    def __init__(
        self,
        parent: Union[tk.Toplevel, tk.Tk],
        current_theme: str,
        available_themes: List[str],
        on_save: Callable[[str], None],
    ):
        """Initialize the theme selection dialog.

        Args:
            parent: Parent widget
            current_theme: Currently selected theme
            available_themes: List of available themes
            on_save: Callback function when theme is selected
        """
        super().__init__(parent)
        self.title("Wybierz schemat kolorystyczny")
        self.geometry("450x350")

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
        self.current_theme = current_theme
        self.available_themes = available_themes
        self.on_save = on_save

        # Variables
        self.selected_theme_var = ttk.StringVar(value=current_theme)
        self.error_message = ttk.StringVar()

        # Style for preview
        self.style = ttk.Style()

        # UI setup
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(container, text="Wybierz schemat kolorystyczny", style="h2.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 15))

        # Information text
        info_text = "Wybierz schemat kolorystyczny aplikacji. Zmiana zostanie zastosowana natychmiast."
        info_label = ttk.Label(container, text=info_text, wraplength=420, justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=(0, 15))

        # Theme selection
        theme_frame = ttk.Frame(container)
        theme_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(theme_frame, text="Schemat kolorystyczny:").pack(anchor=tk.W)

        # Combobox with available themes
        self.theme_combobox = ttk.Combobox(
            theme_frame, textvariable=self.selected_theme_var, values=self.available_themes, state="readonly", width=30
        )
        self.theme_combobox.pack(fill=tk.X, pady=(5, 0))

        # Set the current theme in the combobox
        if self.current_theme in self.available_themes:
            self.theme_combobox.current(self.available_themes.index(self.current_theme))

        # Preview frame
        preview_frame = ttk.Labelframe(container, text="Podgląd", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create a small preview of the selected theme (buttons, label, entry)
        self.preview_content = ttk.Frame(preview_frame)
        self.preview_content.pack(fill=tk.BOTH, expand=True)

        # Bind theme change on combobox selection
        self.theme_combobox.bind("<<ComboboxSelected>>", self._on_theme_preview)

        # Create initial preview
        self._create_theme_preview()

        # Validation message
        error_label = ttk.Label(container, textvariable=self.error_message, style="danger.TLabel")
        error_label.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        apply_button = ttk.Button(
            button_frame, text="Zastosuj", style="primary.TButton", command=self._validate_and_save
        )
        apply_button.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def _create_theme_preview(self) -> None:
        """Create a preview of UI elements with current theme."""
        # Clear previous preview
        for widget in self.preview_content.winfo_children():
            widget.destroy()

        # Sample label
        ttk.Label(self.preview_content, text="Przykładowa etykieta").pack(pady=5, anchor=tk.W)

        # Sample entry
        ttk.Entry(self.preview_content, width=30).pack(pady=5, fill=tk.X)

        # Sample buttons frame
        buttons_frame = ttk.Frame(self.preview_content)
        buttons_frame.pack(pady=5, fill=tk.X)

        # Regular button
        ttk.Button(buttons_frame, text="Przycisk").pack(side=tk.LEFT, padx=(0, 5))

        # Primary button
        ttk.Button(buttons_frame, text="Akcja", style="primary.TButton").pack(side=tk.LEFT, padx=5)

        # Secondary button
        ttk.Button(buttons_frame, text="Anuluj", style="secondary.TButton").pack(side=tk.LEFT, padx=5)

        # Checkbutton
        ttk.Checkbutton(self.preview_content, text="Opcja zaznaczania").pack(pady=5, anchor=tk.W)

    def _on_theme_preview(self, event=None) -> None:
        """Preview the selected theme."""
        selected_theme = self.selected_theme_var.get()
        if selected_theme in self.available_themes:
            # Store current theme
            current_theme = self.style.theme_use()

            # Apply selected theme temporarily
            self.style.theme_use(selected_theme)

            # Refresh preview elements
            self._create_theme_preview()

            # Restore current theme (don't apply globally yet)
            self.style.theme_use(current_theme)

    def _validate_and_save(self) -> None:
        """Validate the selection and save if valid."""
        selected_theme = self.selected_theme_var.get()

        # Clear previous error
        self.error_message.set("")

        # Check if a theme is selected
        if not selected_theme:
            self.error_message.set("Wybierz schemat kolorystyczny")
            return

        # Check if selected theme is in available themes
        if selected_theme not in self.available_themes:
            self.error_message.set("Wybierz schemat z listy dostępnych schematów")
            return

        # Check if selection has changed
        if selected_theme == self.current_theme:
            self.destroy()
            return

        # Save the selected theme
        self.on_save(selected_theme)
        self.destroy()
