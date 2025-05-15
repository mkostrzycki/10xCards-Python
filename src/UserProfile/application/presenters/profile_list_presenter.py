"""Presenter for the profile list view."""

from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
from UserProfile.domain.repositories.exceptions import UsernameAlreadyExistsError, RepositoryError
from Shared.application.session_service import SessionService
from Shared.domain.errors import AuthenticationError
from .interfaces import IProfileListView


class NavigationControllerProtocol(Protocol):
    """Protocol for navigation controller."""

    def navigate(self, path: str) -> None:
        """Navigate to a specific path."""
        ...


@dataclass
class ProfileListState:
    """State for the profile list presenter."""

    profiles: List[UserProfileSummaryViewModel] = field(default_factory=list)
    selected_profile_id: Optional[int] = None
    is_loading: bool = False
    error_message: Optional[str] = None


class ProfileListPresenter:
    """Presenter for the profile list view."""

    def __init__(
        self,
        view: IProfileListView,
        profile_service: UserProfileService,
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
    ) -> None:
        """Initialize the profile list presenter.

        Args:
            view: View interface implementation
            profile_service: Service for profile operations
            session_service: Service for session management
            navigation_controller: Controller for navigation
        """
        self._view = view
        self._profile_service = profile_service
        self._session_service = session_service
        self._navigation = navigation_controller
        self._state = ProfileListState()

    def load_profiles(self) -> None:
        """Load and display the list of profiles."""
        try:
            self._state.is_loading = True
            self._view.show_loading(True)

            self._state.profiles = self._profile_service.get_all_profiles_summary()
            self._view.display_profiles(self._state.profiles)
            self._state.error_message = None

        except RepositoryError:
            error_msg = "Nie można załadować profili. Błąd bazy danych."
            self._state.error_message = error_msg
            self._view.show_error(error_msg)
            self._view.show_toast("Błąd", error_msg)

        finally:
            self._state.is_loading = False
            self._view.show_loading(False)

    def handle_profile_creation(self, username: str) -> None:
        """Handle the creation of a new profile.

        Args:
            username: Username for the new profile
        """
        try:
            self._profile_service.create_profile(username)
            self._view.show_toast("Sukces", f"Profil {username} został utworzony.")
            self.load_profiles()

        except UsernameAlreadyExistsError:
            self._view.show_toast("Błąd", f"Nazwa profilu {username} już istnieje.")

        except Exception:
            self._view.show_toast("Błąd", "Wystąpił nieoczekiwany błąd podczas tworzenia profilu.")

    def handle_profile_selected(self, profile_id: Optional[int]) -> None:
        """Handle profile selection event.

        Args:
            profile_id: ID of the selected profile, or None if deselected
        """
        self._state.selected_profile_id = profile_id
        self._view.enable_login_button(profile_id is not None)

    def handle_profile_activated(self) -> None:
        """Handle profile activation (double click or Enter)."""
        if not self._state.selected_profile_id:
            return

        # Find the selected profile
        profile = next((p for p in self._state.profiles if p.id == self._state.selected_profile_id), None)
        if not profile:
            return

        try:
            if profile.is_password_protected:
                # TODO: Navigate to login view (implement login view first)
                # self._navigation.navigate(f"/login/{profile.id}")
                self._view.show_toast(
                    "Info", f"Logowanie na hasło jeszcze nie zaimplementowane dla profilu: {profile.username}"
                )
            else:
                # For unprotected profiles, log in directly
                self._session_service.login(profile.username)
                self._navigation.navigate("/decks")

                # Generate UserLoggedIn event through view
                self._view.trigger_user_logged_in_event()

        except AuthenticationError as e:
            self._view.show_toast("Błąd", str(e))
            self._navigation.navigate("/profiles")

        except Exception as e:
            self._view.show_toast("Błąd", f"Wystąpił nieoczekiwany błąd podczas logowania: {str(e)}")
            self._navigation.navigate("/profiles")
