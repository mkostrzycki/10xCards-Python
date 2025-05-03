import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class HeaderBar(ttk.Frame):
    """A reusable header bar widget with optional back button and title"""

    def __init__(self, parent: ttk.Widget, title: str, show_back_button: bool = False):
        super().__init__(parent)
        self.title = title

        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Title column expands

        # Back button (if enabled)
        if show_back_button:
            self.back_btn = ttk.Button(self, text="←", style="secondary.TButton", width=3)
            self.back_btn.grid(row=0, column=0, padx=(0, 10))

        # Title
        self.title_label = ttk.Label(
            self, text=self.title, style="primary.Inverse.TLabel", font=("TkDefaultFont", 16, "bold")
        )
        self.title_label.grid(row=0, column=1, sticky="w")

    def set_back_command(self, command) -> None:
        """Set the command to be executed when back button is clicked"""
        if hasattr(self, "back_btn"):
            self.back_btn.configure(command=command)
