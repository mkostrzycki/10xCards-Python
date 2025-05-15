"""Interfaces for UserProfile presenters and views."""

from typing import Protocol, List, Optional
from UserProfile.application.user_profile_service import UserProfileSummaryViewModel, SettingsViewModel


class IProfileListView(Protocol):
    """Interface for the profile list view."""

    def display_profiles(self, profiles: List[UserProfileSummaryViewModel]) -> None:
        """Display the list of profiles in the view.

        Args:
            profiles: List of profile summaries to display
        """
        ...

    def show_loading(self, is_loading: bool) -> None:
        """Show or hide loading state.

        Args:
            is_loading: Whether to show loading state
        """
        ...

    def show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: Error message to display
        """
        ...

    def enable_login_button(self, enabled: bool) -> None:
        """Enable or disable the login button.

        Args:
            enabled: Whether to enable the button
        """
        ...

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification.

        Args:
            title: Toast title
            message: Toast message
        """
        ...

    def trigger_user_logged_in_event(self) -> None:
        """Trigger the UserLoggedIn event."""
        ...


class ISettingsView(Protocol):
    """Interface for the settings view."""

    def display_settings(self, settings: SettingsViewModel) -> None:
        """Display the settings in the view.

        Args:
            settings: Settings view model to display
        """
        ...

    def show_loading(self, is_loading: bool) -> None:
        """Show or hide loading state.

        Args:
            is_loading: Whether to show loading state
        """
        ...

    def show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: Error message to display
        """
        ...

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification.

        Args:
            title: Toast title
            message: Toast message
        """
        ...

    def show_change_username_dialog(self, current_username: str) -> None:
        """Show dialog for changing username.

        Args:
            current_username: Current username to display
        """
        ...

    def show_manage_password_dialog(self, has_password_set: bool) -> None:
        """Show dialog for managing password.

        Args:
            has_password_set: Whether user has password set
        """
        ...

    def show_api_key_dialog(self, current_key: Optional[str]) -> None:
        """Show dialog for managing API key.

        Args:
            current_key: Current API key (if set)
        """
        ...

    def show_select_llm_model_dialog(self, current_model: Optional[str], available_models: List[str]) -> None:
        """Show dialog for selecting LLM model.

        Args:
            current_model: Currently selected model
            available_models: List of available models
        """
        ...

    def show_select_theme_dialog(self, current_theme: str, available_themes: List[str]) -> None:
        """Show dialog for selecting theme.

        Args:
            current_theme: Currently selected theme
            available_themes: List of available themes
        """
        ...

    def apply_theme(self, theme_name: str) -> None:
        """Apply the selected theme.

        Args:
            theme_name: Name of the theme to apply
        """
        ...

    def update_session_info(self) -> None:
        """Update the session information display."""
        ...
