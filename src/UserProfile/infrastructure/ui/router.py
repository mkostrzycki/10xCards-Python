from typing import Optional, Dict, Callable
import tkinter as tk
from tkinter import ttk

from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from Shared.application.session_service import SessionService
from UserProfile.infrastructure.ui.views.profile_list_view import ProfileListView
from UserProfile.infrastructure.ui.views.profile_login_view import ProfileLoginView


class Router:
    """Manages navigation between views in the application."""

    def __init__(
        self,
        root: tk.Widget,
        profile_service: UserProfileService,
        session_service: SessionService,
        main_content_area: ttk.Frame,
        toast_callback: Callable[[str, str], None],
    ):
        """Initialize the router.

        Args:
            root: Root window
            profile_service: Service for profile operations
            session_service: Service for session management
            main_content_area: Frame where views will be displayed
            toast_callback: Callback for showing toast notifications
        """
        self._root = root
        self._profile_service = profile_service
        self._session_service = session_service
        self._main_content_area = main_content_area
        self._show_toast = toast_callback

        self._current_view: Optional[ttk.Frame] = None
        self._view_cache: Dict[str, ttk.Frame] = {}

    def navigate(self, path: str) -> None:
        """Navigate to a specific path.

        Args:
            path: Path to navigate to
        """
        if path == "/profiles":
            self.show_profile_list()
        elif path == "/decks":
            self.show_deck_list()
        else:
            # Dla innych ścieżek używamy event generatora, aby główny NavigationController obsłużył nawigację
            # W środowisku testowym to nie zadziała, więc pokazujemy komunikat
            self._show_toast("Info", f"Nawigacja do: {path}")
            print(f"Router.navigate: Redirecting to path {path}")

    def _clear_current_view(self) -> None:
        """Remove the current view from display."""
        if self._current_view:
            self._current_view.pack_forget()
            self._current_view = None

    def _show_view(self, view: ttk.Frame) -> None:
        """Display a view in the main content area.

        Args:
            view: View to display
        """
        self._clear_current_view()
        view.pack(fill=tk.BOTH, expand=True)
        self._current_view = view

    def show_profile_list(self) -> None:
        """Show the profile list view."""
        # Create new instance each time to ensure fresh state
        view = ProfileListView(
            self._main_content_area, self._profile_service, self._session_service, self, self._show_toast
        )
        self._show_view(view)

    def show_login(self, profile: UserProfileSummaryViewModel) -> None:
        """Show the profile login view.

        Args:
            profile: Profile to log into
        """
        view = ProfileLoginView(
            self._main_content_area, profile, self._profile_service, self._session_service, self, self._show_toast
        )
        self._show_view(view)

    def show_deck_list(self) -> None:
        """Show the deck list view."""
        # Upewnij się, że użytkownik jest zalogowany
        if not self._session_service.is_authenticated():
            self._show_toast("Błąd", "Musisz być zalogowany, aby przeglądać talie.")
            self.show_profile_list()
            return

        # Przekieruj do widoku talii
        self._root.event_generate("<<NavigateToDeckList>>")
        self._show_toast("Info", "Przechodzę do listy talii...")
