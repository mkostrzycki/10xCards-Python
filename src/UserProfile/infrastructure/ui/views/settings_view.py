"""Settings View for user profile and application preferences."""

import tkinter as tk
from typing import Callable, List, Optional, Dict, Any
import logging

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from Shared.application.session_service import SessionService
from UserProfile.application.user_profile_service import (
    SettingsViewModel,
    UserProfileService,
    UpdateUserProfileDTO,
    SetUserPasswordDTO,
    UpdateUserPreferencesDTO,
    UpdateUserApiKeyDTO,
)
from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from UserProfile.infrastructure.ui.views.api_key_dialog import APIKeyDialog
from Shared.ui.widgets.header_bar import HeaderBar
from UserProfile.domain.repositories.exceptions import UserNotFoundError
from Shared.domain.errors import AuthenticationError


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

        # Store dependencies
        self.user_profile_service = user_service
        self.session_service = session_service
        self.api_client = api_client
        self.navigation_controller = navigation_controller
        self.show_toast = show_toast
        self.available_llm_models = available_llm_models
        self.available_app_themes = available_app_themes
        self.initial_tab = initial_tab

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
            self.settings_model = self.user_profile_service.get_user_settings(
                user.id, self.available_llm_models, self.available_app_themes
            )
        except Exception as e:
            # Add detailed logging to diagnose the error
            logging.error(f"Failed to load settings: {str(e)}", exc_info=True)
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
            self.user_profile_service.update_username(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            # Update session info in the header
            self.navigation_controller.update_session_info()
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
            self.user_profile_service.set_user_password(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            # Update session info in the header
            self.navigation_controller.update_session_info()
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
            current_key = self.user_profile_service.get_api_key(user.id)
        except Exception:
            # If we can't get the key, just start with an empty one
            pass

        APIKeyDialog(self, self.api_client, current_key, lambda key: self._on_api_key_changed(user.id, key))

    def _on_api_key_changed(self, user_id: int, api_key: str) -> None:
        """Handle API key change."""
        try:
            logging.info(f"API key changed event for user {user_id} (length: {len(api_key)})")

            if not api_key.strip():
                logging.warning("Empty API key after stripping whitespace - rejecting")
                self.show_toast("Błąd", "Klucz API nie może być pusty")
                return

            logging.info("About to call user_service.set_api_key")
            self.user_profile_service.set_api_key(user_id, api_key)
            logging.info("API key saved successfully via user_service.set_api_key")

            # Odśwież dane sesji aby odzwierciedlić zmiany
            logging.info("Refreshing session user data")
            self.session_service.refresh_current_user()

            # Odśwież ustawienia widoku
            logging.info("Refreshing settings view data")
            self.refresh_settings()

            # Update session info in the header
            logging.info("Updating session info in header")
            self.navigation_controller.update_session_info()

            # Pokażmy klucz w debugach aby sprawdzić czy jest prawidłowy (tylko pierwsze i ostatnie 4 znaki)
            if len(api_key) > 8:
                masked_key = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                masked_key = "***"
            logging.info(f"API key updated successfully (masked: {masked_key})")

            self.show_toast("Sukces", "Klucz API został zaktualizowany")
        except Exception as e:
            logging.error(f"Error saving API key: {str(e)}", exc_info=True)
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
            self.user_profile_service.update_user_preferences(dto)
            self.session_service.refresh_current_user()
            self.refresh_settings()
            # Update session info in the header
            self.navigation_controller.update_session_info()
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
            # Zapisz preferencje użytkownika
            dto = UpdateUserPreferencesDTO(user_id=self.settings_model.user_id, app_theme=theme_name)
            self.user_profile_service.update_user_preferences(dto)

            # Odśwież dane sesji i ustawień
            self.session_service.refresh_current_user()
            self.refresh_settings()

            # Update session info in the header
            self.navigation_controller.update_session_info()

            # Zastosuj temat po krótkim opóźnieniu, aby dialog miał czas się zamknąć
            def apply_theme_after_delay():
                try:
                    style = ttk.Style()
                    style.theme_use(theme_name)
                    logging.info(f"Theme changed to {theme_name}")
                except Exception as style_error:
                    # Łapiemy błędy wynikające z samej zmiany stylu
                    error_msg = f"Błąd podczas zmiany stylu: {str(style_error)}"
                    logging.error(error_msg)
                    self.show_toast(
                        "Ostrzeżenie", "Wystąpił błąd przy zmianie wyglądu aplikacji, ale ustawienia zostały zapisane"
                    )
                    # Kontynuujemy, ponieważ preferencje zostały zapisane pomyślnie
                    # Styl zostanie poprawnie zastosowany przy ponownym uruchomieniu aplikacji

            # Opóźnij zmianę stylu o 100ms
            self.after(100, apply_theme_after_delay)

            self.show_toast("Sukces", "Schemat kolorystyczny został zmieniony")
        except Exception as e:
            error_msg = f"Błąd przy zapisywaniu schematu kolorystycznego: {str(e)}"
            logging.error(error_msg)
            self.show_toast("Błąd", str(e))

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = HeaderBar(self, "Ustawienia profilu", show_back_button=True)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header.set_back_command(self._on_back)

        # Main content area with tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Profile tab
        self.profile_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.profile_tab, text="Profil")
        self._setup_profile_tab()

        # Security tab
        self.security_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.security_tab, text="Zabezpieczenia")
        self._setup_security_tab()

        # API tab
        self.api_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.api_tab, text="Klucz API")
        self._setup_api_tab()

        # Appearance tab
        self.appearance_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.appearance_tab, text="Wygląd")
        self._setup_appearance_tab()

    def _setup_profile_tab(self) -> None:
        """Set up the profile tab with username settings."""
        self.profile_tab.grid_columnconfigure(1, weight=1)

        # Username section
        ttk.Label(self.profile_tab, text="Nazwa użytkownika:", style="primary.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        username_frame = ttk.Frame(self.profile_tab)
        username_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        username_frame.grid_columnconfigure(0, weight=1)

        self.username_var = ttk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.username_save_btn = ttk.Button(
            username_frame,
            text="Zapisz",
            style="primary.TButton",
            command=self._save_username,
        )
        self.username_save_btn.grid(row=0, column=1)

    def _setup_security_tab(self) -> None:
        """Set up the security tab with password settings."""
        self.security_tab.grid_columnconfigure(1, weight=1)

        # Current password (required for changing password)
        ttk.Label(self.security_tab, text="Aktualne hasło:", style="primary.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.current_password_var = ttk.StringVar()
        self.current_password_entry = ttk.Entry(self.security_tab, textvariable=self.current_password_var, show="•", width=30)
        self.current_password_entry.grid(row=0, column=1, sticky="w", pady=(0, 10))

        # New password
        ttk.Label(self.security_tab, text="Nowe hasło:", style="primary.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )
        self.new_password_var = ttk.StringVar()
        self.new_password_entry = ttk.Entry(self.security_tab, textvariable=self.new_password_var, show="•", width=30)
        self.new_password_entry.grid(row=1, column=1, sticky="w", pady=(0, 10))

        # Confirm password
        ttk.Label(self.security_tab, text="Potwierdź hasło:", style="primary.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.confirm_password_var = ttk.StringVar()
        self.confirm_password_entry = ttk.Entry(self.security_tab, textvariable=self.confirm_password_var, show="•", width=30)
        self.confirm_password_entry.grid(row=2, column=1, sticky="w", pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(self.security_tab)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="w")

        self.save_password_btn = ttk.Button(
            button_frame,
            text="Ustaw hasło",
            style="primary.TButton",
            command=self._save_password,
        )
        self.save_password_btn.grid(row=0, column=0, padx=(0, 10))

        self.remove_password_btn = ttk.Button(
            button_frame,
            text="Usuń hasło",
            style="secondary.TButton",
            command=self._remove_password,
        )
        self.remove_password_btn.grid(row=0, column=1)

    def _setup_api_tab(self) -> None:
        """Set up the API key tab."""
        self.api_tab.grid_columnconfigure(1, weight=1)

        # API key section
        ttk.Label(
            self.api_tab,
            text="Klucz API OpenRouter:",
            style="primary.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        api_key_frame = ttk.Frame(self.api_tab)
        api_key_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        api_key_frame.grid_columnconfigure(0, weight=1)

        # Current key display (masked)
        self.current_api_key_label = ttk.Label(api_key_frame, text="Nie ustawiono")
        self.current_api_key_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # New key entry
        ttk.Label(self.api_tab, text="Nowy klucz API:", style="primary.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )

        api_key_entry_frame = ttk.Frame(self.api_tab)
        api_key_entry_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        api_key_entry_frame.grid_columnconfigure(0, weight=1)

        self.api_key_var = ttk.StringVar()
        self.api_key_entry = ttk.Entry(api_key_entry_frame, textvariable=self.api_key_var, width=40, show="•")
        self.api_key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.save_api_key_btn = ttk.Button(
            api_key_entry_frame,
            text="Zapisz",
            style="primary.TButton",
            command=self._save_api_key,
        )
        self.save_api_key_btn.grid(row=0, column=1)

        # Help text
        help_text = (
            "Aby korzystać z funkcji AI, musisz podać klucz API z OpenRouter.\n"
            "1. Zarejestruj się na stronie https://openrouter.ai\n"
            "2. Utwórz klucz API (format: sk-or-...)\n"
            "3. Wklej klucz API powyżej i kliknij 'Zapisz'\n\n"
            "Twój klucz API jest szyfrowany i przechowywany lokalnie."
        )
        help_label = ttk.Label(self.api_tab, text=help_text, wraplength=450, justify="left")
        help_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Napraw klucz API button
        self.repair_api_key_frame = ttk.LabelFrame(self.api_tab, text="Rozwiązywanie problemów", padding=10)
        self.repair_api_key_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        repair_text = (
            "Jeśli masz problemy z funkcjami AI (błędy uwierzytelniania pomimo prawidłowego klucza API), "
            "może to wynikać z problemu z szyfrowaniem. Kliknij poniżej, aby zresetować klucz."
        )
        ttk.Label(self.repair_api_key_frame, text=repair_text, wraplength=450, justify="left").pack(pady=(0, 10))
        
        self.repair_api_key_btn = ttk.Button(
            self.repair_api_key_frame,
            text="Zresetuj klucz API",
            style="warning.TButton",
            command=self._repair_api_key,
        )
        self.repair_api_key_btn.pack()

    def _setup_appearance_tab(self) -> None:
        """Set up the appearance tab with theme settings."""
        self.appearance_tab.grid_columnconfigure(1, weight=1)

        # LLM model selection
        ttk.Label(self.appearance_tab, text="Domyślny model AI:", style="primary.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.llm_model_var = ttk.StringVar()
        self.llm_model_combobox = ttk.Combobox(
            self.appearance_tab, textvariable=self.llm_model_var, values=self.available_llm_models, state="readonly", width=30
        )
        self.llm_model_combobox.grid(row=0, column=1, sticky="w", pady=(0, 20))

        # Theme selection
        ttk.Label(self.appearance_tab, text="Motyw aplikacji:", style="primary.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )
        self.theme_var = ttk.StringVar()
        self.theme_combobox = ttk.Combobox(
            self.appearance_tab, textvariable=self.theme_var, values=self.available_app_themes, state="readonly", width=30
        )
        self.theme_combobox.grid(row=1, column=1, sticky="w", pady=(0, 20))

        # Save button
        self.save_appearance_btn = ttk.Button(
            self.appearance_tab,
            text="Zapisz",
            style="primary.TButton",
            command=self._save_appearance,
        )
        self.save_appearance_btn.grid(row=2, column=0, sticky="w")

    def _load_user_settings(self) -> None:
        """Load user settings from the database."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.navigation_controller.navigate("/profiles")
                return

            # Get settings data from service
            settings: SettingsViewModel = self.user_profile_service.get_user_settings(
                user_id, self.available_llm_models, self.available_app_themes
            )

            # Set values in UI
            self.username_var.set(settings.current_username)

            # Set API key display (masked)
            if settings.current_api_key_masked:
                self.current_api_key_label.config(text=settings.current_api_key_masked)
            else:
                self.current_api_key_label.config(text="Nie ustawiono")

            # Set appearance settings
            if settings.current_llm_model:
                self.llm_model_var.set(settings.current_llm_model)
            else:
                self.llm_model_var.set(self.available_llm_models[0])

            self.theme_var.set(settings.current_app_theme)

            # Update password buttons state
            if settings.has_password_set:
                self.save_password_btn.config(text="Zmień hasło")
                self.remove_password_btn.config(state="normal")
                self.current_password_entry.config(state="normal")
            else:
                self.save_password_btn.config(text="Ustaw hasło")
                self.remove_password_btn.config(state="disabled")
                self.current_password_entry.config(state="disabled")

            # Select initial tab if provided
            if self.initial_tab:
                if self.initial_tab == "api":
                    self.tabs.select(2)  # API tab index
                elif self.initial_tab == "security":
                    self.tabs.select(1)  # Security tab index
                elif self.initial_tab == "appearance":
                    self.tabs.select(3)  # Appearance tab index

        except Exception as e:
            logging.error(f"Error loading user settings: {str(e)}", exc_info=True)
            self.show_toast("Błąd", f"Nie udało się załadować ustawień: {str(e)}")
            self.navigation_controller.navigate("/profiles")

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts and events."""
        self.bind("<BackSpace>", lambda e: self._on_back())
        self.bind("<Escape>", lambda e: self._on_back())

    def _on_back(self) -> None:
        """Handle back navigation."""
        self.navigation_controller.navigate("/decks")

    def _save_username(self) -> None:
        """Save the username."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return

            new_username = self.username_var.get().strip()
            if not new_username:
                self.show_toast("Błąd", "Nazwa użytkownika nie może być pusta")
                return

            update_dto = UpdateUserProfileDTO(user_id=user_id, new_username=new_username)
            self.user_profile_service.update_username(update_dto)

            # Update session with new username
            current_user = self.session_service.get_current_user()
            if current_user:
                current_user.username = new_username
                self.session_service.update_current_user(current_user)

            self.show_toast("Sukces", "Nazwa użytkownika została zaktualizowana")
        except ValueError as e:
            self.show_toast("Błąd", str(e))
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zaktualizować nazwy użytkownika: {str(e)}")

    def _save_password(self) -> None:
        """Save the password."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return

            # Get password values
            current_password = self.current_password_var.get()
            new_password = self.new_password_var.get()
            confirm_password = self.confirm_password_var.get()

            # Validate
            settings: SettingsViewModel = self.user_profile_service.get_user_settings(
                user_id, self.available_llm_models, self.available_app_themes
            )

            if settings.has_password_set and not current_password:
                self.show_toast("Błąd", "Musisz podać aktualne hasło")
                return

            if not new_password:
                self.show_toast("Błąd", "Hasło nie może być puste")
                return

            if new_password != confirm_password:
                self.show_toast("Błąd", "Hasła nie są zgodne")
                return

            if len(new_password) < 4:
                self.show_toast("Błąd", "Hasło musi mieć co najmniej 4 znaki")
                return

            # Update password
            password_dto = SetUserPasswordDTO(
                user_id=user_id, current_password=current_password, new_password=new_password
            )
            self.user_profile_service.set_user_password(password_dto)

            # Clear fields and update UI
            self.current_password_var.set("")
            self.new_password_var.set("")
            self.confirm_password_var.set("")
            self._load_user_settings()  # Refresh UI state

            self.show_toast("Sukces", "Hasło zostało zaktualizowane")
        except AuthenticationError as e:
            self.show_toast("Błąd uwierzytelniania", str(e))
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zaktualizować hasła: {str(e)}")

    def _remove_password(self) -> None:
        """Remove the password."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return

            # Ask for confirmation
            confirm = Messagebox.yesno(
                title="Potwierdzenie", message="Czy na pewno chcesz usunąć hasło? Dostęp do profilu będzie niezabezpieczony."
            )
            if not confirm:
                return

            # Get current password for verification
            current_password = self.current_password_var.get()
            if not current_password:
                self.show_toast("Błąd", "Musisz podać aktualne hasło, aby je usunąć")
                return

            # Remove password
            password_dto = SetUserPasswordDTO(user_id=user_id, current_password=current_password, new_password=None)
            self.user_profile_service.set_user_password(password_dto)

            # Clear fields and update UI
            self.current_password_var.set("")
            self.new_password_var.set("")
            self.confirm_password_var.set("")
            self._load_user_settings()  # Refresh UI state

            self.show_toast("Sukces", "Hasło zostało usunięte")
        except AuthenticationError as e:
            self.show_toast("Błąd uwierzytelniania", str(e))
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się usunąć hasła: {str(e)}")

    def _save_api_key(self) -> None:
        """Save the OpenRouter API key."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return

            api_key = self.api_key_var.get().strip()
            if not api_key:
                self.show_toast("Błąd", "Klucz API nie może być pusty")
                return

            # Very basic format validation
            if not api_key.startswith("sk-or-"):
                if not Messagebox.yesno(
                    title="Nieprawidłowy format",
                    message="Ten klucz API nie wygląda na poprawny klucz OpenRouter (powinien zaczynać się od 'sk-or-'). Czy na pewno chcesz go zapisać?",
                ):
                    return

            # Save API key
            api_key_dto = UpdateUserApiKeyDTO(user_id=user_id, api_key=api_key)
            self.user_profile_service.set_api_key(user_id, api_key)

            # Clear field and refresh
            self.api_key_var.set("")
            self._load_user_settings()

            self.show_toast("Sukces", "Klucz API został zaktualizowany")
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zaktualizować klucza API: {str(e)}")

    def _repair_api_key(self) -> None:
        """Reset the API key encryption in case of corruption."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return
                
            # Ask for confirmation
            confirm = Messagebox.yesno(
                title="Potwierdzenie", 
                message="Ta operacja usunie aktualny klucz API i będziesz musiał wprowadzić go ponownie. Kontynuować?"
            )
            if not confirm:
                return
                
            # Reset API key by setting to None
            self.user_profile_service.set_api_key(user_id, None)
            
            # Refresh settings display
            self._load_user_settings()
            
            # Focus on API key entry for immediate input
            self.tabs.select(2)  # Select API tab
            self.api_key_entry.focus_set()
            
            self.show_toast("Sukces", "Klucz API został zresetowany. Wprowadź nowy klucz.")
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zresetować klucza API: {str(e)}")
            logging.error(f"Error resetting API key: {str(e)}", exc_info=True)

    def _save_appearance(self) -> None:
        """Save appearance settings."""
        try:
            user_id = self.session_service.get_current_user_id()
            if not user_id:
                self.show_toast("Błąd", "Nie jesteś zalogowany")
                return

            # Get theme and model values
            theme = self.theme_var.get()
            llm_model = self.llm_model_var.get()

            # Validate
            if not theme or theme not in self.available_app_themes:
                self.show_toast("Błąd", "Wybierz prawidłowy motyw")
                return

            if llm_model and llm_model not in self.available_llm_models:
                self.show_toast("Błąd", "Wybierz prawidłowy model AI")
                return

            # Update preferences
            prefs_dto = UpdateUserPreferencesDTO(user_id=user_id, default_llm_model=llm_model, app_theme=theme)
            self.user_profile_service.update_user_preferences(prefs_dto)

            # Update theme immediately
            self.master.style.theme_use(theme)

            self.show_toast("Sukces", "Ustawienia wyglądu zostały zaktualizowane")
        except Exception as e:
            self.show_toast("Błąd", f"Nie udało się zaktualizować ustawień wyglądu: {str(e)}")
