from typing import Optional
import tkinter as tk
import ttkbootstrap as ttk


class BaseDialog(ttk.Toplevel):
    """Base class for all dialogs in the application.

    Provides common functionality for dialogs:
    - Window configuration (modal, transient)
    - Basic layout (content frame + button frame)
    - Automatic centering
    - Standard button placement
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        *,
        show_buttons: bool = True,
        ok_text: str = "OK",
        ok_style: str = "primary.TButton",
        cancel_text: str = "Cancel",
        cancel_style: str = "secondary.TButton",
    ) -> None:
        """Initialize the base dialog.

        Args:
            parent: The parent widget
            title: Dialog title
            show_buttons: Whether to show the standard OK/Cancel buttons
            ok_text: Text for the OK button
            ok_style: ttkbootstrap style for the OK button
            cancel_text: Text for the Cancel button
            cancel_style: ttkbootstrap style for the Cancel button
        """
        super().__init__(parent)

        # Configure dialog window
        self.title(title)
        self.transient(parent)
        self.grab_set()

        # Create main frame with padding
        self.main_frame = ttk.Frame(self, padding="20 10 20 10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Create content frame for derived classes
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # Create button frame if needed
        if show_buttons:
            self.button_frame = ttk.Frame(self.main_frame)
            self.button_frame.grid(row=1, column=0, pady=(0, 10))

            # Cancel button (on left)
            self.cancel_button = ttk.Button(
                self.button_frame, text=cancel_text, command=self._handle_cancel, style=cancel_style, width=10
            )
            self.cancel_button.grid(row=0, column=0, padx=(0, 10))

            # OK button (on right)
            self.ok_button = ttk.Button(
                self.button_frame, text=ok_text, command=self._handle_ok, style=ok_style, width=10
            )
            self.ok_button.grid(row=0, column=1)

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Result of the dialog
        self.result: Optional[bool] = None

        # Center dialog and make it modal
        self._center_on_parent()
        self.focus_set()

    def _center_on_parent(self) -> None:
        """Center the dialog window on its parent."""
        self.update_idletasks()
        parent = self.master

        # Get parent and dialog dimensions
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        # Set position
        self.geometry(f"+{x}+{y}")

    def _handle_ok(self) -> None:
        """Handle OK button click. Override in derived classes if needed."""
        self.result = True
        self.destroy()

    def _handle_cancel(self) -> None:
        """Handle Cancel button click. Override in derived classes if needed."""
        self.result = False
        self.destroy()

    def show(self) -> Optional[bool]:
        """Show the dialog and return the result.

        Returns:
            True if OK was clicked, False if Cancel was clicked, None if closed.
        """
        self.wait_window()
        return self.result
