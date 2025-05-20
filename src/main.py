import ttkbootstrap as ttk
import logging
from typing import Any, Dict, Optional, Protocol, Callable, Type

# --- Project Imports ---
from Shared.infrastructure.logging import setup_logging
from Shared.infrastructure.persistence.sqlite.connection import SqliteConnectionProvider
from Shared.infrastructure.persistence.sqlite.migrations import run_migrations
from Shared.infrastructure.config import DATABASE_PATH, AVAILABLE_LLM_MODELS, AVAILABLE_APP_THEMES
from Shared.application.session_service import SessionService
from UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import UserRepositoryImpl
from UserProfile.application.user_profile_service import UserProfileService, UserProfileSummaryViewModel
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
from CardManagement.infrastructure.ui.views.ai_review_single_flashcard_view import AIReviewSingleFlashcardView
from Study.application.services.study_service import StudyService
from Study.application.presenters.study_presenter import StudyPresenter
from Study.infrastructure.ui.views.study_session_view import StudySessionView
from Study.infrastructure.persistence.sqlite.repositories.ReviewLogRepositoryImpl import ReviewLogRepositoryImpl
from Shared.ui.widgets.toast_container import ToastContainer
from Shared.application.navigation import NavigationControllerProtocol


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

        # Configure grid weights for proper layout
        self.grid_rowconfigure(0, weight=0)  # Header row - fixed height
        self.grid_rowconfigure(1, weight=1)  # Main content row - expands
        self.grid_columnconfigure(0, weight=1)  # Single column - expands

        # Create header frame with distinct style
        self.header = ttk.Frame(self, style="AppHeader.TFrame")
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Dodaj minimalną wysokość i wypełnienie dla paska nagłówka
        self.header.config(height=40)  # Minimalna wysokość
        self.header.pack_propagate(False)  # Zapobiega zmniejszaniu się ramki

        # Create main content frame
        self.main_content = ttk.Frame(self)
        self.main_content.grid(row=1, column=0, sticky="nsew")

        # Create session info label with right alignment
        self.session_info = ttk.Label(self.header, text="", style="AppHeader.TLabel")
        self.session_info.pack(side=ttk.RIGHT, padx=10, pady=5)

        # Settings button (shown only when logged in)
        self.settings_button = ttk.Button(
            self.header, text="Ustawienia", style="AppHeader.TButton", command=self._show_settings
        )

        # Create toast container (for in-app notifications)
        self.toast_container = ToastContainer(self)

        # Update session info
        self._update_session_info()

        # Bind to login/logout events for session info updates
        parent.bind("<<UserLoggedIn>>", lambda e: self._update_session_info())
        parent.bind("<<UserLoggedOut>>", lambda e: self._update_session_info())

    def _update_session_info(self) -> None:
        """Update the session info label based on current session state."""
        user = self.session_service.get_current_user()
        if user:
            self.session_info.configure(text=f"Zalogowany jako: {user.username}")
            # Show settings button when logged in
            self.settings_button.pack(side=ttk.RIGHT, padx=10, pady=5, before=self.session_info)
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


class NavigationController(NavigationControllerProtocol):
    """Controller for navigating between different views in the application."""

    def __init__(self, app_view: AppView):
        self.app_view = app_view
        self.views: Dict[str, ttk.Frame] = {}
        self.dynamic_view_factories: Dict[str, Callable] = {}
        self.current_view: Optional[ttk.Frame] = None
        # Storage for the last navigate kwargs
        self._last_navigate_kwargs: Dict[str, Any] = {}

    def show_login(self, profile: UserProfileSummaryViewModel) -> None:
        """Show the profile login view.

        Args:
            profile: Profile to log into
        """
        self.navigate(f"/profiles/{profile.id}/login")

    def register_view(self, path: str, view: ttk.Frame) -> None:
        """Register a static view.

        Args:
            path: The path to register the view at
            view: The view to register
        """
        self.views[path] = view

    def register_dynamic_view(self, path_pattern: str, view_factory: Callable) -> None:
        """Register a dynamic view factory.

        Args:
            path_pattern: The path pattern to match against
            view_factory: A function that creates the view
        """
        self.dynamic_view_factories[path_pattern] = view_factory

    def show_settings(self) -> None:
        """Navigate to settings view."""
        self.navigate("/settings")

    def show_deck_list(self) -> None:
        """Navigate to deck list view."""
        self.navigate("/decks")

    def show_profile_list(self) -> None:
        """Navigate to profile list view."""
        self.navigate("/profiles")

    def update_session_info(self) -> None:
        """Update the session info in AppView."""
        if hasattr(self.app_view, "_update_session_info"):
            self.app_view._update_session_info()

    def navigate(self, path: str, **kwargs) -> None:
        """Navigate to a specific path.

        Args:
            path: The path to navigate to
            **kwargs: Additional arguments to pass to the view constructor
        """
        # Set up logger
        import logging

        logger = logging.getLogger(__name__)

        # Store the kwargs for potential use in dynamic view creation
        self._last_navigate_kwargs = kwargs
        logger.debug(f"Navigate called with path: {path}, kwargs keys: {list(kwargs.keys())}")

        # If the path exists in static views, show it
        if path in self.views:
            logger.debug(f"Found static view for path: {path}")
            self._show_view(self.views[path])
            return

        # Handle profile login
        import re

        if re.match(r"^/profiles/\d+/login$", path):
            parts = path.split("/")
            try:
                profile_id = int(parts[2])

                # Uzyskaj dostęp do profile_service
                profile_service = self.app_view.session_service._profile_service

                # Pobierz profil bezpośrednio metodą profile_service
                try:
                    user = profile_service.get_profile_by_id(profile_id)

                    from UserProfile.application.user_profile_service import UserProfileSummaryViewModel
                    from UserProfile.infrastructure.ui.views.profile_login_view import ProfileLoginView

                    # Stwórz model widoku
                    profile = UserProfileSummaryViewModel(
                        id=profile_id, username=user.username, is_password_protected=bool(user.hashed_password)
                    )

                    # Stwórz widok logowania
                    view = ProfileLoginView(
                        parent=self.app_view.main_content,
                        profile=profile,
                        profile_service=profile_service,
                        session_service=self.app_view.session_service,
                        router=self,
                        toast_callback=self.app_view.show_toast,
                    )
                    self._show_view(view)
                    return
                except Exception as e:
                    self.app_view.show_toast("Błąd", f"Nie można znaleźć profilu: {str(e)}")
                    self.navigate("/profiles")
                    return

            except Exception as e:
                self.app_view.show_toast("Błąd", str(e))
                self.navigate("/profiles")
                return

        # Special handling for /decks/:id/cards/review
        if re.match(r"^/decks/\d+/cards/review$", path):
            logger.debug(f"Special handling for review path: {path}")
            parts = path.split("/")
            try:
                deck_id = int(parts[2])
                logger.debug(f"Review for deck_id: {deck_id}, kwargs: {list(kwargs.keys())}")

                factory = self.dynamic_view_factories.get("/decks/:id/cards/review")
                if factory:
                    # Create view with all kwargs
                    view = factory(**kwargs)
                    self._show_view(view)
                    return
                else:
                    logger.error("No factory found for /decks/:id/cards/review")
            except Exception as e:
                logger.error(f"Error handling review path: {str(e)}", exc_info=True)
                self.app_view.show_toast("Błąd", f"Nie można utworzyć widoku przeglądu: {str(e)}")
                return

        # Check if any dynamic view pattern matches
        for pattern, factory in self.dynamic_view_factories.items():
            logger.debug(f"Checking pattern: {pattern} for path: {path}")

            if pattern.endswith("/:id") and re.match(f"^{pattern[:-4]}/\\d+$", path):
                # Extract ID and create view
                id_str = path.split("/")[-1]
                try:
                    id_val = int(id_str)
                    view = factory(id_val)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

            # Pattern for cards: /decks/:id/cards
            if pattern == "/decks/:id/cards" and re.match(r"^/decks/\d+/cards$", path):
                parts = path.split("/")
                try:
                    deck_id = int(parts[2])  # Extract deck ID from /decks/{id}/cards
                    view = factory(deck_id)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

            # Pattern for card editing: /decks/:id/cards/:id/edit
            if pattern.endswith("/:id/cards/:card_id/edit") and re.match(
                f"^{pattern.replace('/:id', '/\\d+').replace('/:card_id', '/\\d+')}$", path
            ):
                parts = path.split("/")
                try:
                    deck_id = int(parts[2])  # Extract deck ID from /decks/{id}/cards/{card_id}/edit
                    card_id = int(parts[4])  # Extract card ID
                    view = factory(deck_id=deck_id, flashcard_id=card_id)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

            # Pattern for new card: /decks/:id/cards/new
            if pattern.endswith("/:id/cards/new") and re.match(
                f"^{pattern.replace('/:id', '/\\d+').replace('/new', '/new')}$", path
            ):
                parts = path.split("/")
                try:
                    deck_id = int(parts[-3])
                    view = factory(deck_id=deck_id)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

            # Pattern for AI generation: /decks/:id/cards/generate
            if pattern.endswith("/:id/cards/generate") and re.match(
                f"^{pattern.replace('/:id', '/\\d+').replace('/generate', '/generate')}$", path
            ):
                parts = path.split("/")
                try:
                    deck_id = int(parts[-3])
                    view = factory(deck_id=deck_id)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

            # Pattern for study session: /study/session/:id
            if pattern.endswith("/study/session/:id") and re.match("^/study/session/\\d+$", path):
                parts = path.split("/")
                try:
                    deck_id = int(parts[-1])
                    view = factory(deck_id=deck_id)
                    self._show_view(view)
                    return
                except (ValueError, Exception) as e:
                    self.app_view.show_toast("Błąd", str(e))
                    return

        # If we get here, no matching view was found
        logger.error(f"No view found for path: {path}")
        self.app_view.show_toast("Błąd", f"Widok '{path}' nie został znaleziony")

    def _show_view(self, view: ttk.Frame) -> None:
        """Show the specified view.

        Args:
            view: The view to show
        """
        # Hide current view if it exists
        if self.current_view is not None:
            self.current_view.grid_forget()

        # Show new view in the main_content area, not replacing the whole AppView
        view.grid(row=0, column=0, sticky="nsew")
        self.app_view.main_content.grid_rowconfigure(0, weight=1)
        self.app_view.main_content.grid_columnconfigure(0, weight=1)
        self.current_view = view

        # Update session info whenever view changes
        self.app_view._update_session_info()

    def navigate_to_view(self, view_class: Type, **kwargs) -> None:
        """Navigate to a view of specified class, passing keyword arguments.

        Args:
            view_class: The class of the view to navigate to
            kwargs: Arguments to pass to the view constructor
        """
        # Find registered view of this class
        for path, view in self.views.items():
            if isinstance(view, view_class):
                self._show_view(view)
                return

        # If not found, try to create a new instance
        try:
            parent = self.app_view.main_content
            # Import here to avoid circular imports
            from CardManagement.infrastructure.ui.views.ai_review_single_flashcard_view import (
                AIReviewSingleFlashcardView,
            )

            if issubclass(view_class, AIReviewSingleFlashcardView):
                view = view_class(
                    parent=parent,
                    navigation_controller=self,
                    show_toast=self.app_view.show_toast,
                    **kwargs,
                )
                self._show_view(view)
            else:
                raise ValueError(f"Direct navigation to {view_class.__name__} not supported")
        except Exception as e:
            self.app_view.show_toast("Błąd", f"Nie udało się wyświetlić widoku: {str(e)}")
            # Log the exception for debugging
            import logging

            logging.getLogger(__name__).error(f"Error in navigate_to_view: {str(e)}", exc_info=True)


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

        # Configure AppHeader style
        style = ttk.Style()
        header_bg = style.colors.bg  # Changed from style.colors.primary
        header_fg = style.colors.info

        # Tworzenie bardziej wyraźnego stylu dla nagłówka
        # Changed relief to "flat" and borderwidth to 0 for a less distinct look
        style.configure("AppHeader.TFrame", background=header_bg, relief="flat", borderwidth=0)
        style.configure(
            "AppHeader.TLabel", background=header_bg, foreground=header_fg, font=("TkDefaultFont", 10, "bold")
        )
        style.configure("AppHeader.TButton", background=header_bg)

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
        review_log_repo = ReviewLogRepositoryImpl(db_provider)

        # Services
        profile_service = UserProfileService(user_repo)
        deck_service = DeckService(deck_repo)
        card_service = CardService(card_repo)
        study_service = StudyService(card_repo, review_log_repo, session_service)

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

        # Create DeckListView with its presenter
        deck_list_view = DeckListView(
            app_view.main_content,
            deck_service,
            session_service,
            navigation_controller,
            app_view.show_toast,
        )
        navigation_controller.register_view("/decks", deck_list_view)

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
                deck_service=deck_service,
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
                user_profile_service=profile_service,
                session_service=session_service,
                navigation_controller=navigation_controller,
                available_llm_models=AVAILABLE_LLM_MODELS,
            )

        def create_study_session_view(deck_id: int) -> StudySessionView:
            user = session_service.get_current_user()
            if not user or not user.id:
                raise ValueError("Musisz być zalogowany aby rozpocząć naukę")
            deck = deck_service.get_deck(deck_id, user.id)
            if not deck:
                raise ValueError("Talia nie istnieje")

            # Create presenter first
            presenter = StudyPresenter(
                view=None,  # Will be set after view creation
                study_service=study_service,
                navigation=navigation_controller,
                session_service=session_service,
                deck_id=deck_id,
                deck_name=deck.name,
            )

            # Create view with presenter
            view = StudySessionView(parent=app_view.main_content, presenter=presenter, deck_name=deck.name)

            # Set view in presenter
            presenter.view = view

            return view

        def create_ai_review_flashcard_view(**kwargs) -> AIReviewSingleFlashcardView:
            """Create view for reviewing AI-generated flashcards."""
            import logging

            logger = logging.getLogger(__name__)

            logger.debug(f"create_ai_review_flashcard_view called with kwargs: {list(kwargs.keys())}")

            # Check required parameters
            required_params = [
                "deck_id",
                "deck_name",
                "generated_flashcards_dtos",
                "current_flashcard_index",
                "ai_service",
                "card_service",
                "available_llm_models",
                "original_source_text",
            ]

            for param in required_params:
                if param not in kwargs:
                    error_msg = f"Missing required parameter: {param}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            # Explicitly handle the parameters
            try:
                view = AIReviewSingleFlashcardView(
                    parent=app_view.main_content,
                    deck_id=kwargs["deck_id"],
                    deck_name=kwargs["deck_name"],
                    generated_flashcards_dtos=kwargs["generated_flashcards_dtos"],
                    current_flashcard_index=kwargs["current_flashcard_index"],
                    ai_service=kwargs["ai_service"],
                    card_service=kwargs["card_service"],
                    navigation_controller=navigation_controller,
                    available_llm_models=kwargs["available_llm_models"],
                    original_source_text=kwargs["original_source_text"],
                )
                logger.debug("AIReviewSingleFlashcardView created successfully")
                return view
            except Exception as e:
                logger.error(f"Error creating AIReviewSingleFlashcardView: {str(e)}", exc_info=True)
                raise

        # Register dynamic routes
        navigation_controller.register_dynamic_view("/decks/:id/cards", create_card_list_view)
        navigation_controller.register_dynamic_view("/decks/:id/cards/new", create_new_card_view)
        navigation_controller.register_dynamic_view("/decks/:id/cards/:card_id/edit", create_edit_card_view)
        navigation_controller.register_dynamic_view("/decks/:id/cards/generate", create_ai_generate_view)
        navigation_controller.register_dynamic_view("/decks/:id/cards/review", create_ai_review_flashcard_view)
        navigation_controller.register_dynamic_view("/study/session/:id", create_study_session_view)

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
                        # Update session info to show logged in user
                        navigation_controller.update_session_info()

                    # Schedule theme change with a short delay
                    self.after(100, apply_theme)
                except Exception as e:
                    logging.error(f"Error applying theme from user preferences: {e}")

        # Bind to login event and navigation events
        self.bind("<<UserLoggedIn>>", on_user_logged_in)
        self.bind("<<UserLoggedOut>>", lambda e: navigation_controller.update_session_info())

        # Start with profiles view
        navigation_controller.navigate("/profiles")


# --- Main Entrypoint ---
def main() -> None:
    """Main application entry point."""
    # Setup logging early
    setup_logging(log_file="./data/app.log", log_level=logging.DEBUG)  # Ensure DEBUG level

    # Initialize Tkinter and set theme
    # Ensure the window is created *after* dependencies for AppView are ready

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
