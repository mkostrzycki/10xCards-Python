"""Presenter for the settings view."""

from dataclasses import dataclass
from typing import List, Optional, Protocol
import logging

from UserProfile.application.user_profile_service import (
    UserProfileService,
    SettingsViewModel,
    UpdateUserProfileDTO,
    SetUserPasswordDTO,
    UpdateUserPreferencesDTO,
)
from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from Shared.application.session_service import SessionService
from Shared.domain.errors import AuthenticationError
from .interfaces import ISettingsView


class NavigationControllerProtocol(Protocol):
    """Protocol for navigation controller."""

    def navigate(self, path: str) -> None:
        """Navigate to a specific path."""
        ...


@dataclass
class SettingsState:
    """State for the settings presenter."""

    settings: Optional[SettingsViewModel] = None
    is_loading: bool = False
    error_message: Optional[str] = None


class SettingsPresenter:
    """Presenter for the settings view."""

    def __init__(
        self,
        view: ISettingsView,
        user_service: UserProfileService,
        session_service: SessionService,
        api_client: OpenRouterAPIClient,
        navigation_controller: NavigationControllerProtocol,
        available_llm_models: List[str],
        available_app_themes: List[str],
    ) -> None:
        """Initialize the settings presenter.

        Args:
            view: View interface implementation
            user_service: Service for profile operations
            session_service: Service for session management
            api_client: OpenRouter API client
            navigation_controller: Controller for navigation
            available_llm_models: List of available LLM models
            available_app_themes: List of available app themes
        """
        self._view = view
        self._user_service = user_service
        self._session_service = session_service
        self._api_client = api_client
        self._navigation = navigation_controller
        self._available_llm_models = available_llm_models
        self._available_app_themes = available_app_themes
        self._state = SettingsState()

    def load_settings(self) -> None:
        """Load or refresh user settings."""
        user = self._session_service.get_current_user()
        if not user or not user.id:
            self._view.show_toast("Błąd", "Nie jesteś zalogowany")
            self._navigation.navigate("/profiles")
            return

        try:
            self._state.is_loading = True
            self._view.show_loading(True)

            self._state.settings = self._user_service.get_user_settings(
                user.id, self._available_llm_models, self._available_app_themes
            )
            self._view.display_settings(self._state.settings)
            self._state.error_message = None

        except Exception as e:
            error_msg = f"Nie udało się załadować ustawień: {str(e)}"
            self._state.error_message = error_msg
            logging.error(f"Failed to load settings: {str(e)}", exc_info=True)
            self._view.show_toast("Błąd", error_msg)
            self._navigation.navigate("/decks")

        finally:
            self._state.is_loading = False
            self._view.show_loading(False)

    def handle_username_change(self, new_username: str) -> None:
        """Handle username change.

        Args:
            new_username: New username to set
        """
        if not self._state.settings:
            return

        try:
            dto = UpdateUserProfileDTO(user_id=self._state.settings.user_id, new_username=new_username)
            self._user_service.update_username(dto)
            self._session_service.refresh_current_user()
            self.load_settings()
            self._view.update_session_info()
            self._view.show_toast("Sukces", "Nazwa profilu została zmieniona")

        except Exception as e:
            self._view.show_toast("Błąd", str(e))

    def handle_password_change(self, current_password: Optional[str], new_password: Optional[str]) -> None:
        """Handle password change.

        Args:
            current_password: Current password (if set)
            new_password: New password to set, or None to remove
        """
        if not self._state.settings:
            return

        try:
            dto = SetUserPasswordDTO(
                user_id=self._state.settings.user_id,
                current_password=current_password,
                new_password=new_password,
            )
            self._user_service.set_user_password(dto)
            self._session_service.refresh_current_user()
            self.load_settings()
            self._view.update_session_info()

            if new_password:
                self._view.show_toast("Sukces", "Hasło zostało zmienione")
            else:
                self._view.show_toast("Sukces", "Hasło zostało usunięte")

        except AuthenticationError as e:
            self._view.show_toast("Błąd uwierzytelniania", str(e))

        except Exception as e:
            self._view.show_toast("Błąd", str(e))

    def handle_api_key_change(self, api_key: Optional[str]) -> None:
        """Handle API key change.

        Args:
            api_key: New API key to set, or None to remove
        """
        if not self._state.settings:
            return

        try:
            if api_key and not api_key.strip():
                self._view.show_toast("Błąd", "Klucz API nie może być pusty")
                return

            self._user_service.set_api_key(self._state.settings.user_id, api_key)
            self._session_service.refresh_current_user()
            self.load_settings()
            self._view.update_session_info()

            if api_key:
                self._view.show_toast("Sukces", "Klucz API został zaktualizowany")
            else:
                self._view.show_toast("Sukces", "Klucz API został usunięty")

        except Exception as e:
            logging.error(f"Error saving API key: {str(e)}", exc_info=True)
            self._view.show_toast("Błąd", f"Nie udało się zapisać klucza API: {str(e)}")

    def handle_llm_model_change(self, model_name: str) -> None:
        """Handle LLM model change.

        Args:
            model_name: Name of the model to set
        """
        if not self._state.settings:
            return

        try:
            if model_name not in self._available_llm_models:
                self._view.show_toast("Błąd", "Wybierz prawidłowy model AI")
                return

            dto = UpdateUserPreferencesDTO(
                user_id=self._state.settings.user_id,
                default_llm_model=model_name,
                app_theme=self._state.settings.current_app_theme,
            )
            self._user_service.update_user_preferences(dto)
            self._session_service.refresh_current_user()
            self.load_settings()
            self._view.update_session_info()
            self._view.show_toast("Sukces", "Domyślny model LLM został zmieniony")

        except Exception as e:
            self._view.show_toast("Błąd", str(e))

    def handle_theme_change(self, theme_name: str) -> None:
        """Handle theme change.

        Args:
            theme_name: Name of the theme to set
        """
        if not self._state.settings:
            return

        try:
            if theme_name not in self._available_app_themes:
                self._view.show_toast("Błąd", "Wybierz prawidłowy motyw")
                return

            dto = UpdateUserPreferencesDTO(
                user_id=self._state.settings.user_id,
                default_llm_model=self._state.settings.current_llm_model,
                app_theme=theme_name,
            )
            self._user_service.update_user_preferences(dto)
            self._session_service.refresh_current_user()
            self.load_settings()
            self._view.update_session_info()

            # Apply theme after a short delay to allow dialog to close
            self._view.apply_theme(theme_name)
            self._view.show_toast("Sukces", "Schemat kolorystyczny został zmieniony")

        except Exception as e:
            self._view.show_toast("Błąd", str(e))

    def handle_back_navigation(self) -> None:
        """Handle back navigation."""
        self._navigation.navigate("/decks")

    def show_change_username_dialog(self) -> None:
        """Show dialog for changing username."""
        if not self._state.settings:
            self.load_settings()
            if not self._state.settings:
                return

        self._view.show_change_username_dialog(self._state.settings.current_username)

    def show_manage_password_dialog(self) -> None:
        """Show dialog for managing password."""
        if not self._state.settings:
            self.load_settings()
            if not self._state.settings:
                return

        self._view.show_manage_password_dialog(self._state.settings.has_password_set)

    def show_api_key_dialog(self) -> None:
        """Show dialog for managing API key."""
        if not self._state.settings:
            self.load_settings()
            if not self._state.settings:
                return

        current_key = None
        try:
            current_key = self._user_service.get_api_key(self._state.settings.user_id)
        except Exception:
            # If we can't get the key, just start with an empty one
            pass

        self._view.show_api_key_dialog(current_key)

    def show_select_llm_model_dialog(self) -> None:
        """Show dialog for selecting LLM model."""
        if not self._state.settings:
            self.load_settings()
            if not self._state.settings:
                return

        self._view.show_select_llm_model_dialog(
            self._state.settings.current_llm_model,
            self._state.settings.available_llm_models,
        )

    def show_select_theme_dialog(self) -> None:
        """Show dialog for selecting theme."""
        if not self._state.settings:
            self.load_settings()
            if not self._state.settings:
                return

        self._view.show_select_theme_dialog(
            self._state.settings.current_app_theme,
            self._state.settings.available_app_themes,
        )
