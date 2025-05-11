from dataclasses import dataclass, field
from typing import List, Optional, Protocol, Callable
import tkinter as tk
import ttkbootstrap as ttk
import logging

from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from UserProfile.domain.repositories.exceptions import UsernameAlreadyExistsError, RepositoryError
from Shared.application.session_service import SessionService
from Shared.domain.errors import AuthenticationError
from UserProfile.infrastructure.ui.views.create_profile_dialog import CreateProfileDialog


@dataclass
class ProfileListViewState:
    profiles: List[UserProfileSummaryViewModel] = field(default_factory=list)
    selected_profile_id: Optional[int] = None
    is_loading: bool = False
    error_message: Optional[str] = None


class Router(Protocol):
    def show_login(self, profile: UserProfileSummaryViewModel) -> None: ...
    def show_deck_list(self) -> None: ...
    def show_profile_list(self) -> None: ...


class ProfileListView(ttk.Frame):
    """Main view displaying the list of user profiles."""

    def __init__(
        self,
        parent: tk.Widget,
        profile_service: UserProfileService,
        session_service: SessionService,
        router: Router,
        toast_callback: Callable[[str, str], None],
    ):
        """Initialize the profile list view.

        Args:
            parent: Parent widget
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
        self._state = ProfileListViewState()

        self._setup_ui()
        self._load_profiles()

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
            height=10,
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
            button_bar, text="Zaloguj", command=self._handle_login, state="disabled", style="primary.TButton"
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

    def _load_profiles(self) -> None:
        """Load and display the list of profiles."""
        try:
            self._state.is_loading = True
            self._state.profiles = self._profile_service.get_all_profiles_summary()
            self._populate_profile_list()
            self._state.error_message = None
        except RepositoryError:
            self._state.error_message = "Nie można załadować profili. Błąd bazy danych."
            self._show_toast("Błąd", self._state.error_message)
        finally:
            self._state.is_loading = False

    def _populate_profile_list(self) -> None:
        """Populate the profile list with current data."""
        # Clear existing items
        for item in self._profile_list.get_children():
            self._profile_list.delete(item)

        # Add profiles
        for profile in self._state.profiles:
            self._profile_list.insert(
                "",
                tk.END,
                values=(profile.username, "🔒" if profile.is_password_protected else ""),
                tags=(str(profile.id),),
            )

    def _show_create_profile_dialog(self) -> None:
        """Show the dialog for creating a new profile."""
        dialog = CreateProfileDialog(self, on_create=self._handle_profile_creation)
        self.wait_window(dialog)

    def _handle_profile_creation(self, username: str) -> None:
        """Handle the creation of a new profile.

        Args:
            username: Username for the new profile
        """
        try:
            self._profile_service.create_profile(username)
            self._show_toast("Sukces", f"Profil {username} został utworzony.")
            self._load_profiles()  # Refresh the list
        except UsernameAlreadyExistsError:
            self._show_toast("Błąd", f"Nazwa profilu {username} już istnieje.")
        except Exception:
            self._show_toast("Błąd", "Wystąpił nieoczekiwany błąd podczas tworzenia profilu.")

    def _handle_login(self) -> None:
        """Handle login button click - same as double-clicking a profile."""
        # Stworzenie sztucznego zdarzenia, które można przekazać do _on_profile_activated
        dummy_event = type("Event", (), {"type": "ButtonClick"})()
        self._on_profile_activated(dummy_event)

    def _on_profile_selected(self, event: tk.Event) -> None:
        """Handle profile selection event.

        Args:
            event: The selection event
        """
        selection = self._profile_list.selection()
        if not selection:
            self._state.selected_profile_id = None
            self._login_btn.configure(state="disabled")
            return

        profile_id = int(self._profile_list.item(selection[0])["tags"][0])
        self._state.selected_profile_id = profile_id

        # Enable login button when profile is selected
        self._login_btn.configure(state="normal")

    def _on_profile_activated(self, event: tk.Event) -> None:
        """Handle profile activation (double click or Enter).

        Args:
            event: The activation event
        """
        if not self._state.selected_profile_id:
            return

        # Find the selected profile
        profile = next((p for p in self._state.profiles if p.id == self._state.selected_profile_id), None)
        if not profile:
            return

        try:
            if profile.is_password_protected:
                self._router.show_login(profile)
            else:
                # For unprotected profiles, log in directly
                self._session_service.login(profile.username)
                self._router.show_deck_list()
        except AuthenticationError as e:
            self._show_toast("Błąd", str(e))
            self._router.show_profile_list()
        except Exception as e:
            self._show_toast("Błąd", "Wystąpił nieoczekiwany błąd podczas logowania.")
            logging.error(f"Unexpected error during login: {str(e)}")
            self._router.show_profile_list()

    def _on_visibility(self, event: tk.Event) -> None:
        """Handle visibility event - refresh profiles when view becomes visible."""
        self._load_profiles()
