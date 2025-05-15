from typing import Any, List

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText

from CardManagement.application.services.ai_service import AIService
from CardManagement.application.card_service import CardService
from Shared.application.session_service import SessionService
from UserProfile.application.user_profile_service import UserProfileService
from Shared.ui.widgets.header_bar import HeaderBar
from Shared.application.navigation import NavigationControllerProtocol
from CardManagement.application.presenters.ai_generate_presenter import AIGeneratePresenter, IAIGenerateView


class AIGenerateView(ttk.Frame, IAIGenerateView):
    """View for generating flashcards using AI"""

    # Constants
    MAX_TEXT_LENGTH = 10000

    def __init__(
        self,
        parent: Any,
        deck_id: int,
        deck_name: str,
        ai_service: AIService,
        card_service: CardService,
        user_profile_service: UserProfileService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        available_llm_models: List[str] = [],
    ):
        super().__init__(parent)

        # Create presenter
        self.presenter = AIGeneratePresenter(
            view=self,
            ai_service=ai_service,
            card_service=card_service,
            user_profile_service=user_profile_service,
            session_service=session_service,
            navigation=navigation_controller,
            deck_id=deck_id,
            deck_name=deck_name,
            available_llm_models=available_llm_models,
        )

        # Initialize UI
        self._init_ui()
        self._bind_events()

        # Initialize presenter
        self.presenter.initialize()

    def _init_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Text input row
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, "Generuj fiszki z tekstu", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self.presenter.navigate_back)

        # Content frame
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Model selection
        model_frame = ttk.Frame(content)
        model_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ttk.Label(model_frame, text="Model AI:").pack(side=ttk.LEFT, padx=(0, 5))
        self.model_var = ttk.StringVar(
            value=self.presenter._available_llm_models[0] if self.presenter._available_llm_models else ""
        )
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=self.presenter._available_llm_models,
            state="readonly",
            width=30,
        )
        self.model_combobox.pack(side=ttk.LEFT)

        # Text input
        text_frame = ttk.LabelFrame(content, text="Tekst źródłowy", padding=10)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        self.text_input = ScrolledText(text_frame, wrap=ttk.WORD)
        self.text_input.grid(row=0, column=0, sticky="nsew")

        # Progress frame
        progress_frame = ttk.Frame(content)
        progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        progress_frame.grid_columnconfigure(1, weight=1)

        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=1, sticky="w")

        # Button frame
        button_frame = ttk.Frame(content)
        button_frame.grid(row=3, column=0, sticky="e", pady=(5, 0))

        self.generate_button = ttk.Button(
            button_frame,
            text="Generuj fiszki",
            style="primary.TButton",
            command=self.presenter.handle_generate,
        )
        self.generate_button.pack(side=ttk.RIGHT)

        self.cancel_generation_button = ttk.Button(
            button_frame,
            text="Anuluj",
            style="danger.TButton",
            command=self.presenter.handle_cancel_generation,
            state="disabled",
        )
        self.cancel_generation_button.pack(side=ttk.RIGHT, padx=(0, 5))

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events"""
        self.bind("<BackSpace>", lambda e: self.presenter.navigate_back())
        self.bind("<Control-Return>", lambda e: self.presenter.handle_generate())

    # IAIGenerateView implementation
    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification."""
        # This will be injected by the parent view/window
        pass

    def show_generating_state(self, is_generating: bool) -> None:
        """Show/hide generating state."""
        self.text_input.configure(state="disabled" if is_generating else "normal")
        self.model_combobox.configure(state="disabled" if is_generating else "readonly")

    def update_progress_label(self, text: str) -> None:
        """Update the progress label text."""
        self.progress_label.configure(text=text)

    def update_cancel_button_state(self, is_enabled: bool) -> None:
        """Update cancel button state."""
        self.cancel_generation_button.configure(state="normal" if is_enabled else "disabled")

    def update_generate_button_state(self, is_enabled: bool) -> None:
        """Update generate button state."""
        self.generate_button.configure(state="normal" if is_enabled else "disabled")

    def get_input_text(self) -> str:
        """Get the input text."""
        return str(self.text_input.get("1.0", "end-1c"))

    def get_selected_model(self) -> str:
        """Get the selected model."""
        return str(self.model_var.get())
