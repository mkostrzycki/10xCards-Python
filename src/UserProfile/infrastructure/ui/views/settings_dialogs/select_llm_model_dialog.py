"""Dialog for selecting default LLM model."""

import tkinter as tk
from typing import Callable, List, Optional, Union

import ttkbootstrap as ttk


class SelectLlmModelDialog(tk.Toplevel):
    """Dialog for selecting the default LLM model."""

    def __init__(
        self,
        parent: Union[tk.Toplevel, tk.Tk],
        current_model: Optional[str],
        available_models: List[str],
        on_save: Callable[[str], None],
    ):
        """Initialize the LLM model selection dialog.

        Args:
            parent: Parent widget
            current_model: Currently selected model or None
            available_models: List of available LLM models
            on_save: Callback function when model is selected
        """
        super().__init__(parent)
        self.title("Wybierz domyślny model LLM")
        self.geometry("450x300")

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
        self.current_model = current_model
        self.available_models = available_models
        self.on_save = on_save

        # Variables
        self.selected_model_var = ttk.StringVar(value=current_model if current_model else "")
        self.error_message = ttk.StringVar()

        # UI setup
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(container, text="Wybierz domyślny model LLM", style="h2.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 15))

        # Information text
        info_text = (
            "Wybierz model, który będzie domyślnie używany podczas generowania fiszek z pomocą AI. "
            "Każdy model ma inne właściwości i ograniczenia."
        )
        info_label = ttk.Label(container, text=info_text, wraplength=420, justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=(0, 15))

        # Model selection
        model_frame = ttk.Frame(container)
        model_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(model_frame, text="Wybierz model:").pack(anchor=tk.W)

        # Combobox with available models
        model_combobox = ttk.Combobox(
            model_frame, textvariable=self.selected_model_var, values=self.available_models, state="readonly", width=40
        )
        model_combobox.pack(fill=tk.X, pady=(5, 0))

        # Select the current model in the combobox
        if self.current_model and self.current_model in self.available_models:
            model_combobox.current(self.available_models.index(self.current_model))
        elif self.available_models:
            model_combobox.current(0)  # Select first model if no current

        # Validation message
        error_label = ttk.Label(container, textvariable=self.error_message, style="danger.TLabel")
        error_label.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)

        save_button = ttk.Button(button_frame, text="Zapisz", style="primary.TButton", command=self._validate_and_save)
        save_button.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_button = ttk.Button(button_frame, text="Anuluj", style="secondary.TButton", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def _validate_and_save(self) -> None:
        """Validate the selection and save if valid."""
        selected_model = self.selected_model_var.get()

        # Clear previous error
        self.error_message.set("")

        # Check if a model is selected
        if not selected_model:
            self.error_message.set("Wybierz model LLM")
            return

        # Check if selected model is in available models
        if selected_model not in self.available_models:
            self.error_message.set("Wybierz model z listy dostępnych modeli")
            return

        # Check if selection has changed
        if selected_model == self.current_model:
            self.destroy()
            return

        # Save the selected model
        self.on_save(selected_model)
        self.destroy()
