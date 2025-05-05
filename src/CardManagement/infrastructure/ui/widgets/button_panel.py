from typing import Callable, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import RIGHT


class ButtonPanel(ttk.Frame):
    """Panel containing action buttons for card management"""

    def __init__(
        self, parent: Any, on_add: Callable[[], None], on_generate_ai: Callable[[], None], disabled: bool = False
    ):
        """
        Initialize the button panel.

        Args:
            parent: The parent widget
            on_add: Callback for when Add Card button is clicked
            on_generate_ai: Callback for when Generate with AI button is clicked
            disabled: Whether the buttons should be disabled initially
        """
        super().__init__(parent)
        self.on_add = on_add
        self.on_generate_ai = on_generate_ai

        self._init_ui(disabled)

    def _init_ui(self, disabled: bool) -> None:
        """Initialize the UI components"""
        # Create buttons
        self.generate_ai_btn = ttk.Button(
            self,
            text="Generuj z AI",
            style="primary.TButton",
            command=self.on_generate_ai,
            state="disabled" if disabled else "normal",
        )
        self.generate_ai_btn.pack(side=RIGHT, padx=5)

        self.add_card_btn = ttk.Button(
            self,
            text="Dodaj fiszkę",
            style="primary.TButton",
            command=self.on_add,
            state="disabled" if disabled else "normal",
        )
        self.add_card_btn.pack(side=RIGHT)

    def set_disabled(self, disabled: bool) -> None:
        """Set the disabled state of the buttons"""
        state = "disabled" if disabled else "normal"
        self.add_card_btn.configure(state=state)
        self.generate_ai_btn.configure(state=state)
