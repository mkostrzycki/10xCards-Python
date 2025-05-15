"""Profile list view implementation."""

from typing import List, Callable
import tkinter as tk
import ttkbootstrap as ttk

from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from UserProfile.application.presenters.profile_list_presenter import ProfileListPresenter
from UserProfile.application.presenters.interfaces import IProfileListView
from Shared.application.session_service import SessionService
from Shared.application.navigation import NavigationControllerProtocol
from UserProfile.infrastructure.ui.views.create_profile_dialog import CreateProfileDialog


class ProfileListView(ttk.Frame, IProfileListView):
    """Main view displaying the list of user profiles."""

    def __init__(
        self,
        parent: tk.Widget,
        profile_service: UserProfileService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        toast_callback: Callable[[str, str], None],
    ):
        """Initialize the profile list view.

        Args:
            parent: Parent widget
            profile_service: Service for profile operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
            toast_callback: Callback for showing toast notifications
        """
        super().__init__(parent)
        self._show_toast = toast_callback

        # Create presenter
        self._presenter = ProfileListPresenter(
            view=self,
            profile_service=profile_service,
            session_service=session_service,
            navigation_controller=navigation_controller,
        )

        self._setup_ui()
        self._presenter.load_profiles()

        # Bind visibility event to refresh the list when view becomes visible
        self.bind("<Visibility>", self._on_visibility)

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        # Title
        title_label = ttk.Label(self, text="Wybierz profil", style="h1.TLabel", padding=(0, 10))
        title_label.pack(fill=tk.X, padx=10)

        # Profile list - use frame to contain both treeview and scrollbar
        profile_frame = ttk.Frame(self)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbar for profile list
        scrollbar = ttk.Scrollbar(profile_frame, orient=tk.VERTICAL)

        self._profile_list = ttk.Treeview(
            profile_frame,
            columns=("username", "protected"),
            show="headings",
            selectmode="browse",
            height=25,
            yscrollcommand=scrollbar.set,
        )

        self._profile_list.heading("username", text="Nazwa użytkownika")
        self._profile_list.heading("protected", text="Chroniony")

        self._profile_list.column("username", width=200)
        self._profile_list.column("protected", width=100, anchor=tk.CENTER)

        # Configure the scrollbar to control the treeview
        scrollbar.configure(command=self._profile_list.yview)

        # Place the treeview and scrollbar in the frame
        self._profile_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button bar
        button_bar = ttk.Frame(self)
        button_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Login button (will be enabled when profile is selected)
        self._login_btn = ttk.Button(
            button_bar, text="Zaloguj", command=self._on_login_clicked, state="disabled", style="primary.TButton"
        )
        self._login_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Add profile button
        add_profile_btn = ttk.Button(
            button_bar, text="Dodaj nowy profil", command=self._show_create_profile_dialog, style="primary.TButton"
        )
        add_profile_btn.pack(side=tk.RIGHT)

        # Bind events
        self._profile_list.bind("<<TreeviewSelect>>", self._on_profile_selected)
        self._profile_list.bind("<Double-1>", self._on_profile_activated)
        self._profile_list.bind("<Return>", self._on_profile_activated)

    # IProfileListView implementation
    def display_profiles(self, profiles: List[UserProfileSummaryViewModel]) -> None:
        """Display the list of profiles in the view.

        Args:
            profiles: List of profile summaries to display
        """
        # Clear existing items
        for item in self._profile_list.get_children():
            self._profile_list.delete(item)

        # Add profiles
        for profile in profiles:
            self._profile_list.insert(
                "",
                tk.END,
                values=(profile.username, "🔒" if profile.is_password_protected else ""),
                tags=(str(profile.id),),
            )

    def show_loading(self, is_loading: bool) -> None:
        """Show or hide loading state.

        Args:
            is_loading: Whether to show loading state
        """
        # TODO: Implement loading indicator if needed
        pass

    def show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: Error message to display
        """
        # Currently errors are shown via toast
        self.show_toast("Błąd", message)

    def enable_login_button(self, enabled: bool) -> None:
        """Enable or disable the login button.

        Args:
            enabled: Whether to enable the button
        """
        self._login_btn.configure(state="normal" if enabled else "disabled")

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification.

        Args:
            title: Toast title
            message: Toast message
        """
        self._show_toast(title, message)

    def trigger_user_logged_in_event(self) -> None:
        """Trigger the UserLoggedIn event."""
        self.winfo_toplevel().event_generate("<<UserLoggedIn>>")

    # Event handlers
    def _show_create_profile_dialog(self) -> None:
        """Show the dialog for creating a new profile."""
        dialog = CreateProfileDialog(self, on_create=self._presenter.handle_profile_creation)
        self.wait_window(dialog)

    def _on_profile_selected(self, event: tk.Event) -> None:
        """Handle profile selection event.

        Args:
            event: The selection event
        """
        selection = self._profile_list.selection()
        if not selection:
            self._presenter.handle_profile_selected(None)
            return

        profile_id = int(self._profile_list.item(selection[0])["tags"][0])
        self._presenter.handle_profile_selected(profile_id)

    def _on_profile_activated(self, event: tk.Event) -> None:
        """Handle profile activation (double click or Enter).

        Args:
            event: The activation event
        """
        self._presenter.handle_profile_activated()

    def _on_login_clicked(self) -> None:
        """Handle login button click."""
        self._presenter.handle_profile_activated()

    def _on_visibility(self, event: tk.Event) -> None:
        """Handle visibility event - refresh profiles when view becomes visible.

        Args:
            event: The visibility event
        """
        self._presenter.load_profiles()
