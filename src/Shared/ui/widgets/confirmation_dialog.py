from typing import Callable, Optional
import tkinter as tk
import ttkbootstrap as ttk


class ConfirmationDialog(ttk.Toplevel):
    """A reusable confirmation dialog that follows ttkbootstrap styling guidelines.

    This dialog is designed to be used for any confirmation action, with customizable
    title, message, and button text. It follows the UI guidelines of placing the
    primary action button on the right.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        message: str,
        confirm_text: str = "OK",
        confirm_style: str = "primary.TButton",
        cancel_text: str = "Cancel",
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            parent: The parent widget
            title: Dialog title
            message: Main message to display
            confirm_text: Text for the confirmation button
            confirm_style: ttkbootstrap style for the confirmation button
            cancel_text: Text for the cancel button
            on_confirm: Callback for confirmation
            on_cancel: Callback for cancellation
        """
        super().__init__(parent)

        # Configure dialog window
        self.title(title)
        self.transient(parent)
        self.grab_set()

        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="20 10 20 10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure message
        message_label = ttk.Label(
            main_frame, text=message, wraplength=300, justify="center"  # Ensure text wraps at reasonable width
        )
        message_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Button frame (for proper button spacing)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Cancel button (on left)
        cancel_button = ttk.Button(
            button_frame, text=cancel_text, command=self._handle_cancel, style="secondary.TButton", width=10
        )
        cancel_button.grid(row=0, column=0, padx=(0, 10))

        # Confirm button (on right)
        confirm_button = ttk.Button(
            button_frame, text=confirm_text, command=self._handle_confirm, style=confirm_style, width=10
        )
        confirm_button.grid(row=0, column=1)

        # Store callbacks
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Center dialog on parent
        self._center_on_parent()

        # Make dialog modal
        self.focus_set()
        self.wait_window()

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

    def _handle_confirm(self) -> None:
        """Handle confirmation button click."""
        if self._on_confirm:
            self._on_confirm()
        self.destroy()

    def _handle_cancel(self) -> None:
        """Handle cancel button click."""
        if self._on_cancel:
            self._on_cancel()
        self.destroy()
