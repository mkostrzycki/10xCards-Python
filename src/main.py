import ttkbootstrap as ttk
import logging
from typing import Any, Dict, Optional, Protocol

# --- Project Imports ---
from Shared.infrastructure.logging import setup_logging
from Shared.infrastructure.persistence.sqlite.connection import SqliteConnectionProvider
from Shared.application.session_service import SessionService
from UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import UserRepositoryImpl
from UserProfile.application.user_profile_service import UserProfileService
from UserProfile.infrastructure.ui.views.profile_list_view import ProfileListView
from DeckManagement.infrastructure.persistence.sqlite.repositories.DeckRepositoryImpl import DeckRepositoryImpl
from DeckManagement.application.deck_service import DeckService
from DeckManagement.infrastructure.ui.views.deck_list_view import DeckListView
from CardManagement.infrastructure.persistence.sqlite.repositories.FlashcardRepositoryImpl import (
    FlashcardRepositoryImpl,
)
from CardManagement.application.card_service import CardService
from CardManagement.infrastructure.ui.views.card_list_view import CardListView
from CardManagement.infrastructure.ui.views.flashcard_edit_view import FlashcardEditView
from CardManagement.infrastructure.ui.views.ai_generate_view import AIGenerateView
from Shared.infrastructure.persistence.sqlite.migrations import run_initial_migration_if_needed


class NavigationProtocol(Protocol):
    """Protocol defining the navigation interface required by views"""

    def navigate(self, path: str) -> None: ...
    def show_deck_list(self) -> None: ...
    def show_profile_list(self) -> None: ...


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

        # Update session info
        self._update_session_info()

    def _update_session_info(self) -> None:
        """Update the session info label based on current session state."""
        user = self.session_service.get_current_user()
        if user:
            self.session_info.configure(text=f"Zalogowany jako: {user.username}")
        else:
            self.session_info.configure(text="")

    def show_toast(self, title: str, message: str) -> None:
        """Show a toast notification."""
        ttk.Toast(
            title=title, message=message, duration=3000, position=("SE", 10, 50)  # Bottom-right corner
        ).show_toast()


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
                        logging.info(f"Navigated to {path}")
                        return

        logging.error(f"No view registered for path {path}")

    def show_deck_list(self) -> None:
        """Navigate to the deck list view."""
        self.navigate("/decks")

    def show_profile_list(self) -> None:
        """Navigate back to the profile list view."""
        self.navigate("/profiles")


# --- Main Application Class ---
class TenXCardsApp(ttk.Window):
    """Main application window for 10xCards."""

    def __init__(self, dependencies: Dict[str, Any]) -> None:
        super().__init__(title="10xCards", themename="darkly")
        self.minsize(800, 600)
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Get dependencies
        db_provider = dependencies.get("db_provider")
        if db_provider is None:
            logging.error("Database provider not provided to TenXCardsApp")
            self.destroy()
            return

        session_service = dependencies.get("session_service")
        if session_service is None:
            logging.error("Session service not provided to TenXCardsApp")
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
                app_view.main_content, profile_service, session_service, navigation_controller, app_view.show_toast
            ),
        )

        navigation_controller.register_view(
            "/decks",
            DeckListView(
                app_view.main_content, deck_service, session_service, navigation_controller, app_view.show_toast
            ),
        )

        # Dynamic views (card management)
        def create_card_list_view(deck_id: int) -> CardListView:
            deck = deck_service.get_deck(deck_id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return CardListView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                card_service=card_service,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
            )

        def create_new_card_view(deck_id: int) -> FlashcardEditView:
            deck = deck_service.get_deck(deck_id)
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
            deck = deck_service.get_deck(deck_id)
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
            deck = deck_service.get_deck(deck_id)
            if not deck:
                raise ValueError("Talia nie istnieje")
            return AIGenerateView(
                parent=app_view.main_content,
                deck_id=deck_id,
                deck_name=deck.name,
                navigation_controller=navigation_controller,
                show_toast=app_view.show_toast,
            )

        # Register dynamic routes
        navigation_controller.register_view("/decks/{deck_id}/cards", create_card_list_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/new", create_new_card_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/{flashcard_id}/edit", create_edit_card_view)
        navigation_controller.register_view("/decks/{deck_id}/cards/generate-ai", create_ai_generate_view)

        # --- Bind Events ---
        self.bind("<<NavigateToDeckList>>", lambda e: navigation_controller.navigate("/decks"))

        # Start with profiles view
        navigation_controller.navigate("/profiles")


# --- Main Entrypoint ---
def main() -> None:
    setup_logging()
    logging.info("Starting 10xCards application")

    # Initialize DB and run migration if needed
    db_path = "./data/10xcards.sqlite3"
    migration_sql_path = "./infrastructure/persistence/sqlite/migrations/20250413174854_initial_schema.sql"
    run_initial_migration_if_needed(db_path, migration_sql_path, target_version=1)

    # Initialize dependencies
    db_provider = SqliteConnectionProvider(db_path)
    user_repo = UserRepositoryImpl(db_provider)
    profile_service = UserProfileService(user_repo)
    dependencies = {
        "db_provider": db_provider,
        "session_service": SessionService(profile_service),
    }

    # Start application
    app = TenXCardsApp(dependencies)
    app.mainloop()


if __name__ == "__main__":
    main()
