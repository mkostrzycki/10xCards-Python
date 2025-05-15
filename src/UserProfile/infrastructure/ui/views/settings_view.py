"""Settings View for user profile and application preferences."""

import tkinter as tk
from typing import Callable, List, Optional
import logging

import ttkbootstrap as ttk

from Shared.application.session_service import SessionService
from UserProfile.application.user_profile_service import (
    SettingsViewModel,
    UserProfileService,
)
from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from UserProfile.application.presenters.settings_presenter import SettingsPresenter
from UserProfile.application.presenters.interfaces import ISettingsView
from UserProfile.infrastructure.ui.views.settings_dialogs.change_username_dialog import ChangeUsernameDialog
from UserProfile.infrastructure.ui.views.settings_dialogs.manage_password_dialog import ManagePasswordDialog
from UserProfile.infrastructure.ui.views.settings_dialogs.api_key_dialog import APIKeyDialog
from UserProfile.infrastructure.ui.views.settings_dialogs.select_llm_model_dialog import SelectLlmModelDialog
from UserProfile.infrastructure.ui.views.settings_dialogs.select_theme_dialog import SelectThemeDialog


class SettingsView(ttk.Frame, ISettingsView):
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
        initial_tab: str = "",
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
            initial_tab: Initial tab to select when view is loaded
        """
        super().__init__(parent)
        self._show_toast = show_toast
        self.initial_tab = initial_tab

        # Create presenter
        self._presenter = SettingsPresenter(
            view=self,
            user_service=user_service,
            session_service=session_service,
            api_client=api_client,
            navigation_controller=navigation_controller,
            available_llm_models=available_llm_models,
            available_app_themes=available_app_themes,
        )

        # Style configuration
        self.padding = 20

        # Setup UI components
        self._setup_ui()

        # Load settings on visibility (when view is shown)
        self.bind("<Visibility>", self._on_visibility)

    def _on_visibility(self, event):
        """Handle visibility event (when view becomes visible)."""
        self._presenter.load_settings()

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
            command=self._presenter.show_change_username_dialog,
        )
        username_btn.pack(fill=tk.X, padx=10, pady=10)

        # Manage password button
        password_btn = ttk.Button(
            profile_frame,
            text="Zarządzaj hasłem",
            style="primary.TButton",
            command=self._presenter.show_manage_password_dialog,
        )
        password_btn.pack(fill=tk.X, padx=10, pady=10)

        # API settings section
        api_frame = ttk.Labelframe(settings_frame, text="Ustawienia AI")
        api_frame.pack(fill=tk.X, pady=(0, 15))

        # API key button
        api_key_btn = ttk.Button(
            api_frame,
            text="Klucz API OpenRouter",
            style="primary.TButton",
            command=self._presenter.show_api_key_dialog,
        )
        api_key_btn.pack(fill=tk.X, padx=10, pady=10)

        # LLM model button
        llm_model_btn = ttk.Button(
            api_frame,
            text="Domyślny model LLM",
            style="primary.TButton",
            command=self._presenter.show_select_llm_model_dialog,
        )
        llm_model_btn.pack(fill=tk.X, padx=10, pady=10)

        # App settings section
        app_frame = ttk.Labelframe(settings_frame, text="Wygląd Aplikacji")
        app_frame.pack(fill=tk.X, pady=(0, 15))

        # Theme button
        theme_btn = ttk.Button(
            app_frame,
            text="Schemat kolorystyczny",
            style="primary.TButton",
            command=self._presenter.show_select_theme_dialog,
        )
        theme_btn.pack(fill=tk.X, padx=10, pady=10)

        # Navigation button
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        back_btn = ttk.Button(
            button_frame,
            text="Wróć",
            style="secondary.TButton",
            command=self._presenter.handle_back_navigation,
        )
        back_btn.pack(side=tk.LEFT)

    # ISettingsView implementation
    def display_settings(self, settings: SettingsViewModel) -> None:
        """Display the settings in the view.

        Args:
            settings: Settings view model to display
        """
        # Currently no direct display needed as we use dialogs
        pass

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
        self.show_toast("Błąd", message)

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification.

        Args:
            title: Toast title
            message: Toast message
        """
        self._show_toast(title, message)

    def show_change_username_dialog(self, current_username: str) -> None:
        """Show dialog for changing username.

        Args:
            current_username: Current username to display
        """
        dialog = ChangeUsernameDialog(self, current_username, self._presenter.handle_username_change)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def show_manage_password_dialog(self, has_password_set: bool) -> None:
        """Show dialog for managing password.

        Args:
            has_password_set: Whether user has password set
        """
        dialog = ManagePasswordDialog(self, has_password_set, self._presenter.handle_password_change)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def show_api_key_dialog(self, current_key: Optional[str]) -> None:
        """Show dialog for managing API key.

        Args:
            current_key: Current API key (if set)
        """
        APIKeyDialog(self, self._presenter._api_client, current_key, self._presenter.handle_api_key_change)

    def show_select_llm_model_dialog(self, current_model: Optional[str], available_models: List[str]) -> None:
        """Show dialog for selecting LLM model.

        Args:
            current_model: Currently selected model
            available_models: List of available models
        """
        dialog = SelectLlmModelDialog(
            self,
            current_model,
            available_models,
            self._presenter.handle_llm_model_change,
        )
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def show_select_theme_dialog(self, current_theme: str, available_themes: List[str]) -> None:
        """Show dialog for selecting theme.

        Args:
            current_theme: Currently selected theme
            available_themes: List of available themes
        """
        dialog = SelectThemeDialog(
            self,
            current_theme,
            available_themes,
            self._presenter.handle_theme_change,
        )
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self.wait_window(dialog)

    def apply_theme(self, theme_name: str) -> None:
        """Apply the selected theme.

        Args:
            theme_name: Name of the theme to apply
        """
        try:
            style = ttk.Style()
            style.theme_use(theme_name)
            logging.info(f"Theme changed to {theme_name}")
        except Exception as e:
            error_msg = f"Błąd podczas zmiany stylu: {str(e)}"
            logging.error(error_msg)
            self.show_toast(
                "Ostrzeżenie",
                "Wystąpił błąd przy zmianie wyglądu aplikacji, ale ustawienia zostały zapisane",
            )

    def update_session_info(self) -> None:
        """Update the session information display."""
        # This is handled by the navigation controller in the parent window
