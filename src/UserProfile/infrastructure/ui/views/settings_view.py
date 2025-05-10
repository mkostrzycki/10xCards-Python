"""Settings View for user profile and application preferences."""

import tkinter as tk
from typing import Callable, List, Optional

import ttkbootstrap as ttk

from Shared.application.session_service import SessionService
from UserProfile.application.user_profile_service import (
    SettingsViewModel,
    UserProfileService,
    UpdateUserProfileDTO,
    SetUserPasswordDTO,
    UpdateUserPreferencesDTO,
)
from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from UserProfile.infrastructure.ui.views.api_key_dialog import APIKeyDialog


class SettingsView(ttk.Frame):
    """Main settings view displaying user profile and application settings."""

    def __init__(
        self,
        parent: ttk.Frame,
        user_service: UserProfileService,
        session_service: SessionService,
        api_client: OpenRouterAPIClient,
        navigation_controller,
        show_toast: Callable[[str, str], None],
        available_llm_models: List[str],
        available_app_themes: List[str],
    ):
        """Initialize the Settings View.

        Args:
            parent: Parent frame
            user_service: User profile service
            session_service: Session service
            api_client: OpenRouter API client for key validation
            navigation_controller: Navigation controller for routing
            show_toast: Function to show toast notifications
            available_llm_models: List of available LLM models from config
            available_app_themes: List of available app themes from config
        """
        super().__init__(parent)

        # Store dependencies
        self.user_service = user_service
        self.session_service = session_service
        self.api_client = api_client
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        self.available_llm_models = available_llm_models
        self.available_app_themes = available_app_themes

        # Settings model - will be loaded in refresh_settings()
        self.settings_model: Optional[SettingsViewModel] = None

        # Style configuration
        self.padding = 20

        # Setup UI components
        self._setup_ui()

        # Load settings on visibility (when view is shown)
        self.bind("<Visibility>", self._on_visibility)

    def _on_visibility(self, event):
        """Handle visibility event (when view becomes visible)."""
        self.refresh_settings()

    def refresh_settings(self) -> None:
        """Load or refresh user settings."""
        user = self.session_service.get_current_user()
        if not user or not user.id:
            self.show_toast("Błąd", "Nie jesteś zalogowany")
            self.navigation_controller.show_profile_list()
            return

        try:
            self.settings_model = self.user_service.get_user_settings(
                user.id, self.available_llm_models, self.available_app_themes
            )
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się załadować ustawień: {str(e)}")
            self.navigation_controller.show_deck_list()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main container with padding
        container = ttk.Frame(self, padding=self.padding)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(container, text="Panel Ustawień", style="h1.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 20))

        # Settings buttons frame
        settings_frame = ttk.Frame(container)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Profile settings section
        profile_frame = ttk.Labelframe(settings_frame, text="Ustawienia Profilu")
        profile_frame.pack(fill=tk.X, pady=(0, 15))

        # Change username button
        username_btn = ttk.Button(
            profile_frame,
            text="Zmień nazwę profilu",
            style="primary.TButton",
            command=self._open_change_username_dialog,
        )
        username_btn.pack(fill=tk.X, padx=10, pady=10)

        # Manage password button
        password_btn = ttk.Button(
            profile_frame, text="Zarządzaj hasłem", style="primary.TButton", command=self._open_manage_password_dialog
        )
        password_btn.pack(fill=tk.X, padx=10, pady=10)

        # API settings section
        api_frame = ttk.Labelframe(settings_frame, text="Ustawienia AI")
        api_frame.pack(fill=tk.X, pady=(0, 15))

        # API key button
        api_key_btn = ttk.Button(
            api_frame, text="Klucz API OpenRouter", style="primary.TButton", command=self._open_api_key_dialog
        )
        api_key_btn.pack(fill=tk.X, padx=10, pady=10)

        # LLM model button
        llm_model_btn = ttk.Button(
            api_frame, text="Domyślny model LLM", style="primary.TButton", command=self._open_select_llm_model_dialog
        )
        llm_model_btn.pack(fill=tk.X, padx=10, pady=10)

        # App settings section
        app_frame = ttk.Labelframe(settings_frame, text="Wygląd Aplikacji")
        app_frame.pack(fill=tk.X, pady=(0, 15))

        # Theme button
        theme_btn = ttk.Button(
            app_frame, text="Schemat kolorystyczny", style="primary.TButton", command=self._open_select_theme_dialog
        )
        theme_btn.pack(fill=tk.X, padx=10, pady=10)

        # Navigation button
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        back_btn = ttk.Button(button_frame, text="Wróć", style="secondary.TButton", command=self._on_back_click)
        back_btn.pack(side=tk.LEFT)

    def _on_back_click(self) -> None:
        """Handle back button click."""
        self.navigation_controller.show_deck_list()

    def _open_change_username_dialog(self) -> None:
        """Open dialog for changing username."""
        from UserProfile.infrastructure.ui.views.settings_dialogs.change_username_dialog import ChangeUsernameDialog

        if not self.settings_model:
            self.refresh_settings()
            if not self.settings_model:
                return

        dialog = ChangeUsernameDialog(self, self.settings_model.current_username, self._on_username_changed)
        # Make dialog modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def _on_username_changed(self, new_username: str) -> None:
        """Handle username change."""
        if not self.settings_model:
            return

        try:
            dto = UpdateUserProfileDTO(user_id=self.settings_model.user_id, new_username=new_username)
            self.user_service.update_username(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            self.show_toast("Sukces", "Nazwa profilu została zmieniona")
        except Exception as e:
            self.show_toast("Błąd", str(e))

    def _open_manage_password_dialog(self) -> None:
        """Open dialog for managing password."""
        from UserProfile.infrastructure.ui.views.settings_dialogs.manage_password_dialog import ManagePasswordDialog

        if not self.settings_model:
            self.refresh_settings()
            if not self.settings_model:
                return

        dialog = ManagePasswordDialog(self, self.settings_model.has_password_set, self._on_password_changed)
        # Make dialog modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def _on_password_changed(self, current_password: Optional[str], new_password: Optional[str]) -> None:
        """Handle password change."""
        if not self.settings_model:
            return

        try:
            dto = SetUserPasswordDTO(
                user_id=self.settings_model.user_id, current_password=current_password, new_password=new_password
            )
            self.user_service.set_user_password(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            if new_password:
                self.show_toast("Sukces", "Hasło zostało zmienione")
            else:
                self.show_toast("Sukces", "Hasło zostało usunięte")
        except Exception as e:
            self.show_toast("Błąd", str(e))

    def _open_api_key_dialog(self) -> None:
        """Open dialog for managing API key."""
        user = self.session_service.get_current_user()
        if not user or not user.id:
            self.show_toast("Błąd", "Nie jesteś zalogowany")
            return

        current_key = None
        try:
            current_key = self.user_service.get_api_key(user.id)
        except Exception:
            # If we can't get the key, just start with an empty one
            pass

        dialog = APIKeyDialog(self, self.api_client, current_key, lambda key: self._on_api_key_changed(user.id, key))

    def _on_api_key_changed(self, user_id: int, api_key: str) -> None:
        """Handle API key change."""
        try:
            self.user_service.set_api_key(user_id, api_key)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            self.show_toast("Sukces", "Klucz API został zaktualizowany")
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zapisać klucza API: {str(e)}")

    def _open_select_llm_model_dialog(self) -> None:
        """Open dialog for selecting default LLM model."""
        from UserProfile.infrastructure.ui.views.settings_dialogs.select_llm_model_dialog import SelectLlmModelDialog

        if not self.settings_model:
            self.refresh_settings()
            if not self.settings_model:
                return

        dialog = SelectLlmModelDialog(
            self,
            self.settings_model.current_llm_model,
            self.settings_model.available_llm_models,
            self._on_llm_model_changed,
        )
        # Make dialog modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def _on_llm_model_changed(self, model_name: str) -> None:
        """Handle LLM model change."""
        if not self.settings_model:
            return

        try:
            dto = UpdateUserPreferencesDTO(user_id=self.settings_model.user_id, default_llm_model=model_name)
            self.user_service.update_user_preferences(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            self.show_toast("Sukces", "Domyślny model LLM został zmieniony")
        except Exception as e:
            self.show_toast("Błąd", str(e))

    def _open_select_theme_dialog(self) -> None:
        """Open dialog for selecting app theme."""
        from UserProfile.infrastructure.ui.views.settings_dialogs.select_theme_dialog import SelectThemeDialog

        if not self.settings_model:
            self.refresh_settings()
            if not self.settings_model:
                return

        dialog = SelectThemeDialog(
            self,
            self.settings_model.current_app_theme,
            self.settings_model.available_app_themes,
            self._on_theme_changed,
        )
        # Make dialog modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        if not self.settings_model:
            return

        try:
            dto = UpdateUserPreferencesDTO(user_id=self.settings_model.user_id, app_theme=theme_name)
            self.user_service.update_user_preferences(dto)

            # Apply theme immediately
            style = ttk.Style()
            style.theme_use(theme_name)

            self.session_service.refresh_current_user()
            self.refresh_settings()
            self.show_toast("Sukces", "Schemat kolorystyczny został zmieniony")
        except Exception as e:
            self.show_toast("Błąd", str(e))
