from dataclasses import dataclass
from typing import Optional, Callable, Protocol
import tkinter as tk
import ttkbootstrap as ttk

from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from Shared.application.session_service import SessionService
from Shared.domain.errors import AuthenticationError


@dataclass
class ProfileLoginViewState:
    user_id: int
    username: str
    password_input: str = ""
    is_logging_in: bool = False
    error_message: Optional[str] = None


class Router(Protocol):
    def show_deck_list(self, user_id: int) -> None: ...
    def show_profile_list(self) -> None: ...


class ProfileLoginView(ttk.Frame):
    """View for logging into a password-protected profile."""

    def __init__(
        self,
        parent: tk.Widget,
        profile: UserProfileSummaryViewModel,
        profile_service: UserProfileService,
        session_service: SessionService,
        router: Router,
        toast_callback: Callable[[str, str], None],
    ):
        """Initialize the profile login view.

        Args:
            parent: Parent widget
            profile: Profile to log into
            profile_service: Service for profile operations
            session_service: Service for session management
            router: Navigation router
            toast_callback: Callback for showing toast notifications
        """
        super().__init__(parent)
        self._profile_service = profile_service
        self._session_service = session_service
        self._router = router
        self._show_toast = toast_callback
        self._state = ProfileLoginViewState(user_id=profile.id, username=profile.username)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        # Title
        title_label = ttk.Label(
            self, text=f"Zaloguj do profilu: {self._state.username}", style="h1.TLabel", padding=(0, 10)
        )
        title_label.pack(fill=tk.X, padx=10)

        # Password entry frame
        self._password_frame = ttk.Frame(self)
        self._password_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        password_label = ttk.Label(self._password_frame, text="Hasło:", style="primary.TLabel")
        password_label.pack(side=tk.LEFT)

        self._password_input = ttk.Entry(self._password_frame, show="*", width=30)  # Hide password characters
        self._password_input.pack(side=tk.LEFT, padx=(10, 0))

        # Error label (hidden by default)
        self._error_label = ttk.Label(self, text="", style="danger.TLabel", padding=(10, 5))
        self._error_label.pack(fill=tk.X)

        # Button bar
        button_bar = ttk.Frame(self)
        button_bar.pack(fill=tk.X, padx=10, pady=10)

        cancel_btn = ttk.Button(button_bar, text="Anuluj", command=self._on_cancel, style="secondary.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self._login_btn = ttk.Button(
            button_bar, text="Zaloguj", command=self._on_login_attempt, style="primary.TButton"
        )
        self._login_btn.pack(side=tk.RIGHT)

        # Bind events
        self._password_input.bind("<Return>", lambda e: self._on_login_attempt())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Focus password input
        self._password_input.focus_set()

    def _show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display
        """
        self._state.error_message = message
        self._error_label.configure(text=message)

    def _clear_error(self) -> None:
        """Clear the error message."""
        self._state.error_message = None
        self._error_label.configure(text="")

    def _clear_password(self) -> None:
        """Clear the password input."""
        self._password_input.delete(0, tk.END)
        self._state.password_input = ""

    def _on_login_attempt(self) -> None:
        """Handle login button click or Enter key."""
        password = self._password_input.get()
        self._state.password_input = password
        self._state.is_logging_in = True

        try:
            # Attempt login through session service
            self._session_service.login(self._state.username, password)
            self._router.show_deck_list(self._state.user_id)
        except AuthenticationError as e:
            self._show_error(str(e))
            self._clear_password()
        except Exception as e:
            self._show_toast("Błąd", str(e))
            self._router.show_profile_list()
        finally:
            self._state.is_logging_in = False

    def _on_cancel(self) -> None:
        """Handle cancel button click or Escape key."""
        self._router.show_profile_list()
