import ttkbootstrap as ttk
import logging
from typing import Any, Dict, Optional, Protocol

# --- Project Imports ---
from Shared.infrastructure.logging import setup_logging
from Shared.infrastructure.persistence.sqlite.connection import SqliteConnectionProvider
from Shared.infrastructure.persistence.sqlite.migrations import run_migrations
from Shared.infrastructure.config import DATABASE_PATH, AVAILABLE_LLM_MODELS, AVAILABLE_APP_THEMES
from Shared.application.session_service import SessionService
from UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import UserRepositoryImpl
from UserProfile.application.user_profile_service import UserProfileService
from UserProfile.infrastructure.ui.views.profile_list_view import ProfileListView
from UserProfile.infrastructure.ui.views.settings_view import SettingsView
from DeckManagement.infrastructure.persistence.sqlite.repositories.DeckRepositoryImpl import DeckRepositoryImpl
from DeckManagement.application.deck_service import DeckService
from DeckManagement.infrastructure.ui.views.deck_list_view import DeckListView
from CardManagement.infrastructure.persistence.sqlite.repositories.FlashcardRepositoryImpl import (
    FlashcardRepositoryImpl,
)
from CardManagement.application.card_service import CardService
from CardManagement.application.services.ai_service import AIService
from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from CardManagement.infrastructure.ui.views.card_list_view import CardListView
from CardManagement.infrastructure.ui.views.flashcard_edit_view import FlashcardEditView
from CardManagement.infrastructure.ui.views.ai_generate_view import AIGenerateView
from Shared.ui.widgets.toast_container import ToastContainer


class NavigationProtocol(Protocol):
    """Protocol defining the navigation interface required by views"""

    def navigate(self, path: str) -> None: ...
    def show_deck_list(self) -> None: ...
    def show_profile_list(self) -> None: ...
    def show_settings(self) -> None: ...
    def update_session_info(self) -> None: ...


class AppView(ttk.Frame):
    """Main application view container"""

    def __init__(
        self,
        parent: ttk.Window,
        session_service: SessionService,
        navigation_controller: Optional[NavigationProtocol] = None,
    ):
        super().__init__(parent)
        self.session_service = session_service
        self.navigation_controller = navigation_controller

        # Create header frame
        self.header = ttk.Frame(self)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1)

        # Create main content frame
        self.main_content = ttk.Frame(self)
        self.main_content.grid(row=1, column=0, sticky="nsew")

        # Create session info label
        self.session_info = ttk.Label(self.header, text="", style="secondary.TLabel")
        self.session_info.pack(side=ttk.RIGHT, padx=5)

        # Settings button (shown only when logged in)
        self.settings_button = ttk.Button(
            self.header, text="Ustawienia", style="secondary.TButton", command=self._show_settings
        )

        # Create toast container (for in-app notifications)
        self.toast_container = ToastContainer(self)

        # Update session info
        self._update_session_info()

    def _update_session_info(self) -> None:
        """Update the session info label based on current session state."""
        user = self.session_service.get_current_user()
        if user:
            self.session_info.configure(text=f"Zalogowany jako: {user.username}")
            # Show settings button when logged in
            self.settings_button.pack(side=ttk.RIGHT, padx=5, before=self.session_info)
        else:
            self.session_info.configure(text="")
            # Hide settings button when not logged in
            self.settings_button.pack_forget()

    def _show_settings(self) -> None:
        """Navigate to settings view."""
        if self.navigation_controller:
            self.navigation_controller.show_settings()

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification using our custom toast container."""
        self.toast_container.show_toast(title, message)


class NavigationController:
    """Controller managing view navigation and routing"""

    def __init__(self, app_view: AppView):
        self.app_view = app_view
        self.views: Dict[str, ttk.Frame] = {}
        self.current_view: Optional[ttk.Frame] = None
        logging.info("NavigationController initialized")

    def register_view(self, path: str, view_instance: ttk.Frame) -> None:
        """Register a view instance for a static path."""
        self.views[path] = view_instance
        logging.info(f"View registered for path {path}")

    def navigate_to_view(self, view_class: type, **kwargs) -> None:
        """Create and navigate to a view instance directly with parameters.

        Args:
            view_class: The view class to instantiate
            **kwargs: Parameters to pass to the view constructor
        """
        if self.current_view:
            self.current_view.grid_remove()

        try:
            # Create the view instance
            new_view = view_class(parent=self.app_view.main_content, **kwargs)

            # Sprawdź czy widok posiada wymagane atrybuty przed wyświetleniem
            # (specjalnie dla AIReviewSingleFlashcardView)
            if hasattr(view_class, "__name__") and view_class.__name__ == "AIReviewSingleFlashcardView":
                if not hasattr(new_view, "save_button") or new_view.save_button is None:
                    raise AttributeError("View initialization incomplete: missing save_button attribute")
                if not hasattr(new_view, "_init_complete") or not new_view._init_complete:
                    raise AttributeError("View initialization incomplete: _init_complete is False")

            # Display the view
            new_view.grid(row=0, column=0, sticky="nsew")
            self.current_view = new_view
            self.app_view._update_session_info()

            # Trigger visibility event
            self.current_view.event_generate("<Visibility>")
            logging.info(f"Navigated to view {view_class.__name__} with params {kwargs}")

        except Exception as e:
            logging.error(f"Failed to create view {view_class.__name__}: {str(e)}")
            self.app_view.show_toast("Błąd", str(e))

    def navigate(self, path: str) -> None:
        """Navigate to a registered view."""
        if self.current_view:
            self.current_view.grid_remove()

        # Extract dynamic path parameters
        path_parts = path.split("/")
        for registered_path, view in self.views.items():
            registered_parts = registered_path.split("/")
            if len(path_parts) == len(registered_parts):
                params: Dict[str, Any] = {}
                matches = True
                for i, (path_part, registered_part) in enumerate(zip(path_parts, registered_parts)):
                    if registered_part.startswith("{") and registered_part.endswith("}"):
                        param_name = registered_part[1:-1]
                        # Jeśli nazwa parametru sugeruje, że to ID, konwertujemy na int
                        if param_name.endswith("_id"):
                            try:
                                params[param_name] = int(path_part)
                            except ValueError:
                                logging.error(f"Expected int for parameter {param_name}, got {path_part}")
                                matches = False
                                break
                        else:
                            params[param_name] = path_part
                    elif path_part != registered_part:
                        matches = False
                        break

                if matches:
                    if callable(view):
                        try:
                            new_view = view(**params)
                            self.views[path] = new_view
                            new_view.grid(row=0, column=0, sticky="nsew")
                            self.current_view = new_view
                            self.app_view._update_session_info()
                            # Wywołaj zdarzenie <Visibility> na widoku
                            self.current_view.event_generate("<Visibility>")
                            logging.info(f"Navigated to {path} with params {params}")
                            return
                        except Exception as e:
                            logging.error(f"Failed to create view for {path}: {str(e)}")
                            self.app_view.show_toast("Błąd", str(e))
                            return
                    else:
                        view.grid(row=0, column=0, sticky="nsew")
                        self.current_view = view
                        self.app_view._update_session_info()
                        # Wywołaj zdarzenie <Visibility> na widoku
                        self.current_view.event_generate("<Visibility>")
                        logging.info(f"Navigated to {path}")
                        return

        logging.error(f"No view registered for path {path}")

    def show_deck_list(self) -> None:
        """Navigate to the deck list view."""
        self.navigate("/decks")

    def show_profile_list(self) -> None:
        """Navigate back to the profile list view."""
        self.navigate("/profiles")

    def show_settings(self) -> None:
        """Navigate to the user settings view."""
        self.navigate("/settings")

    def show_login(self, profile) -> None:
        """Navigate to the login view for a password-protected profile.

        Args:
            profile: Profile to log into
        """
        from UserProfile.infrastructure.ui.views.profile_login_view import ProfileLoginView

        login_view = ProfileLoginView(
            self.app_view.main_content,
            profile,
            self.app_view.session_service._profile_service,
            self.app_view.session_service,
            self,
            self.app_view.show_toast,
        )

        # Temporarily register and navigate to the login view
        temp_path = f"/login/{profile.id}"
        self.views[temp_path] = login_view

        if self.current_view:
            self.current_view.grid_remove()

        login_view.grid(row=0, column=0, sticky="nsew")
        self.current_view = login_view
        self.app_view._update_session_info()
        login_view.event_generate("<Visibility>")
        logging.info(f"Navigated to login view for profile {profile.username}")

    def update_session_info(self) -> None:
        """Update the session info in the app view."""
        self.app_view._update_session_info()
        logging.info("Session info updated in header")


# --- Main Application Class ---
class TenXCardsApp(ttk.Window):
    """Main application window for 10xCards."""

    def __init__(self, dependencies: Dict[str, Any]) -> None:
        # Get dependencies before initializing the window
        db_provider = dependencies.get("db_provider")
        if db_provider is None:
            logging.error("Database provider not provided to TenXCardsApp")
            raise ValueError("Database provider not provided")

        session_service = dependencies.get("session_service")
        if session_service is None:
            logging.error("Session service not provided to TenXCardsApp")
            raise ValueError("Session service not provided")

        # Check if user is already logged in and has theme preference
        default_theme = "darkly"
        user = session_service.get_current_user()
        if user and user.app_theme:
            default_theme = user.app_theme
            logging.info(f"Using theme from user profile: {default_theme}")

        # Initialize window with correct theme
        super().__init__(title="10xCards", themename=default_theme)
        self.minsize(800, 600)
        self.geometry("800x600")
        # Disable window resizing
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Get OpenRouter API client
        openrouter_api_client = dependencies.get("openrouter_api_client")
        if openrouter_api_client is None:
            logging.error("OpenRouter API client not provided to TenXCardsApp")
            self.destroy()
            return

        # Repositories
        user_repo = UserRepositoryImpl(db_provider)
        deck_repo = DeckRepositoryImpl(db_provider)
        card_repo = FlashcardRepositoryImpl(db_provider)

        # Services
        profile_service = UserProfileService(user_repo)
        deck_service = DeckService(deck_repo)
        card_service = CardService(card_repo)

        # AI Service setup
        ai_service = dependencies.get("ai_service")
        if ai_service is None:
            logging.error("AI service not provided to TenXCardsApp")
            self.destroy()
            return

        # --- AppView and NavigationController setup ---
        app_view = AppView(self, session_service)
        app_view.grid(row=0, column=0, sticky="nsew")
        navigation_controller = NavigationController(app_view)
        app_view.navigation_controller = navigation_controller

        # --- Register Views ---
        # Static views
        navigation_controller.register_view(
            "/profiles",
            ProfileListView(
                app_view.main_content,
                profile_service,
                session_service,
                navigation_controller,
                app_view.show_toast,
            ),
        )

        navigation_controller.register_view(
            "/decks",
            DeckListView(
                app_view.main_content, deck_service, session_service, navigation_controller, app_view.show_toast
            ),
        )

        # Settings view
        navigation_controller.register_view(
            "/settings",
            SettingsView(
                app_view.main_content,
                profile_service,
                session_service,
                openrouter_api_client,
                navigation_controller,
                app_view.show_toast,
                AVAILABLE_LLM_MODELS,
                AVAILABLE_APP_THEMES,
            ),
        )

        # Dynamic views (card management)
        def create_card_list_view(deck_id: int) -> CardListView:
            user = session_service.get_current_user()
            if not user or not user.id:
                raise ValueError("Musisz być zalogowany aby przeglądać karty")
            deck = deck_service.get_deck(deck_id, user.id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return CardListView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                card_service=card_service,
                session_service=session_service,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
            )

        def create_new_card_view(deck_id: int) -> FlashcardEditView:
            user = session_service.get_current_user()
            if not user or not user.id:
                raise ValueError("Musisz być zalogowany aby tworzyć karty")
            deck = deck_service.get_deck(deck_id, user.id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return FlashcardEditView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                card_service=card_service,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
            )

        def create_edit_card_view(deck_id: int, flashcard_id: int) -> FlashcardEditView:
            user = session_service.get_current_user()
            if not user or not user.id:
                raise ValueError("Musisz być zalogowany aby edytować karty")
            deck = deck_service.get_deck(deck_id, user.id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return FlashcardEditView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                card_service=card_service,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
                flashcard_id=flashcard_id,
            )

        def create_ai_generate_view(deck_id: int) -> AIGenerateView:
            user = session_service.get_current_user()
            if not user or not user.id:
                raise ValueError("Musisz być zalogowany aby generować karty")
            deck = deck_service.get_deck(deck_id, user.id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return AIGenerateView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                ai_service=ai_service,
                card_service=card_service,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
                available_llm_models=AVAILABLE_LLM_MODELS,
            )

        # Register dynamic routes
        navigation_controller.register_view("/decks/{deck_id}/cards", create_card_list_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/new", create_new_card_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/{flashcard_id}/edit", create_edit_card_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/generate-ai", create_ai_generate_view)

        # --- Bind Events ---
        self.bind("<<NavigateToDeckList>>", lambda e: navigation_controller.navigate("/decks"))

        # Listener for theme changes - apply theme from user preferences after login
        def on_user_logged_in(event=None):
            user = session_service.get_current_user()
            if user and user.app_theme:
                logging.info(f"Applying user theme from preferences: {user.app_theme}")
                try:
                    # Apply theme with slight delay to ensure all widgets are ready
                    def apply_theme():
                        style = ttk.Style()
                        current_theme = style.theme_use()
                        if current_theme != user.app_theme:
                            style.theme_use(user.app_theme)
                            logging.info(f"Successfully applied theme: {user.app_theme}")

                    # Schedule theme change with a short delay
                    self.after(100, apply_theme)
                except Exception as e:
                    logging.error(f"Error applying theme from user preferences: {e}")

        # Bind to login event and navigation events
        self.bind("<<UserLoggedIn>>", on_user_logged_in)

        # Start with profiles view
        navigation_controller.navigate("/profiles")


# --- Main Entrypoint ---
def main() -> None:
    """Main application entry point."""
    # Set up logging first
    setup_logging()

    # Dodaj handler do przechwytywania błędów tkinter
    tkinter_error_log = logging.getLogger("tkinter_errors")
    tkinter_error_log.setLevel(logging.ERROR)

    # Zarejestruj oryginalny handler wyjątków Tkinter
    import sys

    original_excepthook = sys.excepthook

    # Nowy handler wyjątków, który będzie logować błędy Tkinter
    def log_tkinter_exceptions(exc_type, exc_value, exc_traceback):
        if "tkinter" in str(exc_type) or "_tkinter" in str(exc_type):
            tkinter_error_log.error("Tkinter error occurred", exc_info=(exc_type, exc_value, exc_traceback))
        # Wywołaj oryginalny handler
        original_excepthook(exc_type, exc_value, exc_traceback)

    # Ustaw nowy handler wyjątków
    sys.excepthook = log_tkinter_exceptions

    # Sprawdź czy SECRET_KEY istnieje, a jeśli nie to wygeneruj nowy
    logging.info("Starting 10xCards application")

    # Initialize DB and run migrations
    run_migrations(str(DATABASE_PATH))

    # Initialize dependencies
    db_provider = SqliteConnectionProvider(str(DATABASE_PATH))
    user_repo = UserRepositoryImpl(db_provider)
    profile_service = UserProfileService(user_repo)
    session_service = SessionService(profile_service)

    # Get logger
    app_logger = logging.getLogger("app")

    # Setup OpenRouter API client and AI service
    openrouter_api_client = OpenRouterAPIClient(
        logger=app_logger.getChild("openrouter"), default_model="openrouter/openai/gpt-4o-mini"
    )
    ai_service = AIService(
        api_client=openrouter_api_client, session_service=session_service, logger=app_logger.getChild("ai_service")
    )

    # Create dependencies dict
    dependencies = {
        "db_provider": db_provider,
        "session_service": session_service,
        "openrouter_api_client": openrouter_api_client,
        "ai_service": ai_service,
    }

    # Start application
    app = TenXCardsApp(dependencies)
    app.mainloop()


if __name__ == "__main__":
    main()
