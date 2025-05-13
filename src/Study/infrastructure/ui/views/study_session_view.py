"""Study session view for flashcard review."""

import logging
import tkinter as tk
from typing import Dict

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from Study.application.presenters.study_presenter import StudyPresenter
from Shared.ui.widgets.header_bar import HeaderBar

logger = logging.getLogger(__name__)


class StudySessionView(ttk.Frame):
    """View for studying flashcards with spaced repetition."""

    def __init__(self, parent: ttk.Frame, presenter: StudyPresenter, deck_name: str):
        """Initialize the study session view.

        Args:
            parent: The parent frame.
            presenter: The presenter for this view.
            deck_name: The name of the deck being studied.
        """
        super().__init__(parent)
        self.presenter = presenter
        self.deck_name = deck_name

        self._create_widgets()
        self._layout_widgets()

        # Initialize the session after UI is set up
        self.after(100, self.presenter.initialize_session)

    def _create_widgets(self) -> None:
        """Create the UI widgets."""
        # Header
        self.header = HeaderBar(self, f"Nauka: {self.deck_name}")

        # Progress frame
        self.progress_frame = ttk.Frame(self)
        self.progress_label = ttk.Label(self.progress_frame, text="Karta: 0/0", font=("TkDefaultFont", 10))

        # Card frame
        self.card_frame = ttk.Frame(self, padding=20)

        # Front side
        self.front_label = ttk.Label(self.card_frame, text="Pytanie", font=("TkDefaultFont", 12, "bold"))
        self.front_text = ttk.Text(self.card_frame, wrap="word", width=50, height=5, font=("TkDefaultFont", 12))
        self.front_text.configure(state="disabled")

        # Separator
        self.separator = ttk.Separator(self.card_frame, orient="horizontal")

        # Back side
        self.back_label = ttk.Label(self.card_frame, text="Odpowiedź", font=("TkDefaultFont", 12, "bold"))
        self.back_text = ttk.Text(self.card_frame, wrap="word", width=50, height=5, font=("TkDefaultFont", 12))
        self.back_text.configure(state="disabled")

        # Buttons frame
        self.buttons_frame = ttk.Frame(self, padding=10)

        # Show answer button
        self.show_answer_button = ttk.Button(
            self.buttons_frame, text="Pokaż odpowiedź", command=self._on_show_answer, style="primary.TButton", width=20
        )

        # Rating buttons frame
        self.rating_buttons_frame = ttk.Frame(self.buttons_frame)

        # Rating buttons
        self.rating_buttons: Dict[int, ttk.Button] = {}

        self.rating_buttons[1] = ttk.Button(
            self.rating_buttons_frame,
            text="Znowu (1)",
            command=lambda: self._on_rate(1),
            style="danger.TButton",
            width=15,
        )

        self.rating_buttons[2] = ttk.Button(
            self.rating_buttons_frame,
            text="Trudne (2)",
            command=lambda: self._on_rate(2),
            style="warning.TButton",
            width=15,
        )

        self.rating_buttons[3] = ttk.Button(
            self.rating_buttons_frame,
            text="Dobre (3)",
            command=lambda: self._on_rate(3),
            style="success.TButton",
            width=15,
        )

        self.rating_buttons[4] = ttk.Button(
            self.rating_buttons_frame,
            text="Łatwe (4)",
            command=lambda: self._on_rate(4),
            style="info.TButton",
            width=15,
        )

        # End session button
        self.end_session_button = ttk.Button(
            self.buttons_frame, text="Zakończ sesję", command=self._on_end_session, style="secondary.TButton", width=15
        )

    def _layout_widgets(self) -> None:
        """Layout the UI widgets."""
        # Main layout
        self.header.pack(side="top", fill="x", padx=10, pady=(10, 0))
        self.progress_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.card_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        self.buttons_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        # Progress frame
        self.progress_label.pack(side="right", padx=10)

        # Card frame
        self.front_label.pack(side="top", anchor="w", pady=(0, 5))
        self.front_text.pack(side="top", fill="both", expand=True, pady=(0, 10))
        self.separator.pack(side="top", fill="x", pady=10)
        self.back_label.pack(side="top", anchor="w", pady=(0, 5))
        self.back_text.pack(side="top", fill="both", expand=True, pady=(0, 10))

        # Buttons frame
        self.show_answer_button.pack(side="top", pady=5)
        self.rating_buttons_frame.pack(side="top", fill="x", pady=5)

        # Rating buttons
        for i, button in self.rating_buttons.items():
            button.pack(side="left", padx=5, expand=True)

        # Hide rating buttons initially
        self.rating_buttons_frame.pack_forget()

        # End session button
        self.end_session_button.pack(side="bottom", pady=10)

    def _on_show_answer(self) -> None:
        """Handle show answer button click."""
        self.presenter.handle_show_answer()

    def _on_rate(self, rating: int) -> None:
        """Handle rating button click.

        Args:
            rating: The rating value (1-4).
        """
        self.presenter.handle_rate_card(rating)

    def _on_end_session(self) -> None:
        """Handle end session button click."""
        self.presenter.handle_end_session()

    # StudySessionViewInterface implementation

    def display_card_front(self, front_text: str) -> None:
        """Display the front text of a flashcard.

        Args:
            front_text: The text to display.
        """
        self.front_text.configure(state="normal")
        self.front_text.delete("1.0", tk.END)
        self.front_text.insert("1.0", front_text)
        self.front_text.configure(state="disabled")

    def display_card_back(self, back_text: str) -> None:
        """Display the back text of a flashcard.

        Args:
            back_text: The text to display.
        """
        self.back_text.configure(state="normal")
        self.back_text.delete("1.0", tk.END)
        self.back_text.insert("1.0", back_text)
        self.back_text.configure(state="disabled")

    def show_rating_buttons(self) -> None:
        """Show the rating buttons."""
        self.rating_buttons_frame.pack(side="top", fill="x", pady=5)

    def hide_rating_buttons(self) -> None:
        """Hide the rating buttons."""
        self.rating_buttons_frame.pack_forget()

    def enable_show_answer_button(self) -> None:
        """Enable the show answer button."""
        self.show_answer_button.configure(state="normal")
        self.show_answer_button.pack(side="top", pady=5)

    def disable_show_answer_button(self) -> None:
        """Disable the show answer button."""
        self.show_answer_button.configure(state="disabled")
        self.show_answer_button.pack_forget()

    def update_progress(self, current: int, total: int) -> None:
        """Update the progress display.

        Args:
            current: The current card number (1-indexed).
            total: The total number of cards.
        """
        self.progress_label.configure(text=f"Karta: {current}/{total}")

    def show_session_complete_message(self) -> None:
        """Show a message when the session is complete."""
        self.front_text.configure(state="normal")
        self.front_text.delete("1.0", tk.END)
        self.front_text.insert("1.0", "Sesja zakończona! Nie ma więcej kart do nauki.")
        self.front_text.configure(state="disabled")

        self.back_text.configure(state="normal")
        self.back_text.delete("1.0", tk.END)
        self.back_text.configure(state="disabled")

        self.show_answer_button.pack_forget()
        self.rating_buttons_frame.pack_forget()

    def show_error_message(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display.
        """
        Messagebox.show_error(message, "Błąd")
