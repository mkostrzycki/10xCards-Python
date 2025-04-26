from typing import Optional, Dict, Type, Callable
import tkinter as tk
from tkinter import ttk

from ...application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from .views.profile_list_view import ProfileListView
from .views.profile_login_view import ProfileLoginView


class Router:
    """Manages navigation between views in the application."""

    def __init__(
        self,
        root: tk.Widget,
        profile_service: UserProfileService,
        main_content_area: ttk.Frame,
        toast_callback: Callable[[str, str], None],
    ):
        """Initialize the router.

        Args:
            root: Root window
            profile_service: Service for profile operations
            main_content_area: Frame where views will be displayed
            toast_callback: Callback for showing toast notifications
        """
        self._root = root
        self._profile_service = profile_service
        self._main_content_area = main_content_area
        self._show_toast = toast_callback

        self._current_view: Optional[ttk.Frame] = None
        self._view_cache: Dict[str, ttk.Frame] = {}

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
        view = ProfileListView(self._main_content_area, self._profile_service, self, self._show_toast)
        self._show_view(view)

    def show_login(self, profile: UserProfileSummaryViewModel) -> None:
        """Show the profile login view.

        Args:
            profile: Profile to log into
        """
        view = ProfileLoginView(self._main_content_area, profile, self._profile_service, self, self._show_toast)
        self._show_view(view)

    def show_deck_list(self, user_id: int) -> None:
        """Show the deck list view.

        Args:
            user_id: ID of the user whose decks to display
        """
        # This will be implemented when DeckManagement context is ready
        self._show_toast("Info", "Przekierowanie do listy talii (niezaimplementowane).")
