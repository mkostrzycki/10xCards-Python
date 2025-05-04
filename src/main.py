import ttkbootstrap as ttk
import logging
from typing import Any

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
from Shared.infrastructure.persistence.sqlite.migrations import run_initial_migration_if_needed


# --- Placeholders for missing core UI components ---
class AppView(ttk.Frame):
    def __init__(self, parent, session_service: SessionService, navigation_controller=None):
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


class NavigationController:
    def __init__(self, app_view: AppView):
        self.app_view = app_view
        self.views: dict[str, ttk.Frame] = {}
        self.current_view: ttk.Frame | None = None
        logging.info("NavigationController initialized")

    def register_view(self, path: str, view_instance: ttk.Frame) -> None:
        self.views[path] = view_instance
        logging.info(f"View registered for path {path}")

    def navigate(self, path: str) -> None:
        if self.current_view:
            self.current_view.grid_remove()
        new_view = self.views.get(path)
        if new_view:
            new_view.grid(row=0, column=0, sticky="nsew")
            self.current_view = new_view
            # Update session info after navigation
            self.app_view._update_session_info()
            logging.info(f"Navigated to {path}")
        else:
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

    def __init__(self, dependencies: dict[str, Any]) -> None:
        super().__init__(title="10xCards", themename="darkly")
        self.minsize(800, 600)
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

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

        # Services
        profile_service = UserProfileService(user_repo)
        deck_service = DeckService(deck_repo)

        # Toast callback placeholder
        def show_toast(title: str, message: str):
            logging.info(f"TOAST: {title}: {message}")

        # --- AppView and NavigationController setup ---
        app_view = AppView(self, session_service)
        app_view.grid(row=0, column=0, sticky="nsew")
        navigation_controller = NavigationController(app_view)
        app_view.navigation_controller = navigation_controller

        # --- Views ---
        profile_list_view = ProfileListView(
            app_view.main_content, profile_service, session_service, navigation_controller, show_toast
        )
        navigation_controller.register_view("/profiles", profile_list_view)

        deck_list_view = DeckListView(
            app_view.main_content, deck_service, session_service, navigation_controller, show_toast
        )
        navigation_controller.register_view("/decks", deck_list_view)

        # --- Bind Events ---
        # Obsługa wydarzenia nawigacji do widoku talii
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
    db_provider = SqliteConnectionProvider(db_path)
    user_repo = UserRepositoryImpl(db_provider)
    profile_service = UserProfileService(user_repo)
    dependencies = {
        "db_provider": db_provider,
        "session_service": SessionService(profile_service),
    }
    app = TenXCardsApp(dependencies)
    app.mainloop()


if __name__ == "__main__":
    main()
