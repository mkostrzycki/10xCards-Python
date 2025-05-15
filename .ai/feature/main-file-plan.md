# Plan wdrożenia pliku startowego src/main.py dla 10xCards (zgodny z regułami)

**Cel:** Utworzenie pliku `src/main.py` zgodnie z przyjętą architekturą (Vertical Slice / MVP), stylem Pythona i zasadami UI Tkinter. Plik ten będzie punktem wejścia aplikacji, odpowiedzialnym za konfigurację, **inicjalizację zależności (Dependency Injection - DI)** i uruchomienie głównego okna aplikacji z początkowym widokiem (`ProfileListView`).

**Kroki:**

1.  **Utwórz plik `src/main.py`** (lub zastąp istniejący pusty plik). Upewnij się, że używasz kodowania UTF-8.

2.  **Dodaj niezbędne importy (zgodnie z PEP 8 i type hinting):**
    *   `tkinter` jako `tk` i `ttkbootstrap` jako `ttk` dla UI.
    *   Moduł `typing` dla wskazówek typów.
    *   **Komponenty z różnych warstw i kontekstów:**
        *   `Shared.infrastructure.logging_setup`: Funkcja do konfiguracji loggera (załóżmy, że istnieje lub stwórz placeholder).
        *   `Shared.infrastructure.database`: Funkcja/klasa do inicjalizacji połączenia z bazą danych SQLite (załóżmy, że istnieje lub stwórz placeholder).
        *   `Shared.ui.core.navigation.NavigationController`: Kontroler nawigacji UI.
        *   `Shared.ui.core.app_view.AppView`: Główny kontener widoków aplikacji.
        *   `UserProfile.infrastructure.persistence.user_profile_repository.UserProfileRepositoryImpl`: Konkretna implementacja repozytorium profili.
        *   `UserProfile.application.services.user_profile_service.UserProfileService`: Serwis do logiki biznesowej profili.
        *   `UserProfile.application.presenters.profile_list_presenter.ProfileListPresenter`: Prezenter dla widoku listy profili.
        *   `UserProfile.infrastructure.ui.views.profile_list_view.ProfileListView`: Widok listy profili.
        *   *(Dodaj inne niezbędne importy dla pozostałych widoków/prezenterów/serwisów/repozytoriów, które będą potrzebne na starcie lub do przekazania jako zależności).*
    *   *Uwaga: Dla nieistniejących jeszcze modułów/klas, utwórz tymczasowe placeholdery zgodnie ze strukturą w `architecture.mdc` i zasadami `python_style.mdc` (np. puste klasy z poprawnymi sygnaturami `__init__` i wskazówkami typów), aby uniknąć błędów importu i umożliwić statyczną analizę typów.*

3.  **Skonfiguruj podstawowe usługi (w `if __name__ == "__main__":` lub w dedykowanej funkcji):**
    *   Wywołaj funkcję konfigurującą **logging** (np. `logging_setup.configure_logging()`).
    *   Zainicjalizuj **połączenie z bazą danych** (np. `db_connection = database.initialize_database()`). Będzie ono wstrzykiwane do repozytoriów.

4.  **Zdefiniuj główną klasę aplikacji (zgodnie z `ui_tkinter.mdc` i `python_style.mdc`):**
    *   Stwórz klasę `TenXCardsApp(ttk.Window)` z poprawnymi wskazówkami typów.

5.  **Zaimplementuj `__init__` w klasie `TenXCardsApp`:**
    *   Wywołaj `super().__init__()`.
    *   Ustaw tytuł, minimalny rozmiar (800x600), domyślny motyw (`themename='darkly'` itp.).
    *   Skonfiguruj layout głównego okna (użyj `grid` z `weight=1` dla skalowania).
    *   **Przeprowadź ręczne wstrzykiwanie zależności (DI) - kluczowa rola `main.py`:**
        *   **Repozytoria:** Stwórz instancje implementacji repozytoriów (np. `profile_repo = UserProfileRepositoryImpl(db_connection)`).
        *   **Serwisy:** Stwórz instancje serwisów aplikacyjnych, wstrzykując im repozytoria (np. `profile_service = UserProfileService(profile_repo)`).
        *   **Prezentery:** Stwórz instancje prezenterów, wstrzykując im serwisy (np. `profile_list_presenter = ProfileListPresenter(profile_service)`). *Uwaga: Prezenterzy często potrzebują też referencji do `NavigationController`.*
        *   **Kontroler Nawigacji:** Stwórz instancję `NavigationController`, przekazując główne okno (`self`) i ewentualnie fabrykę/kontener zależności, jeśli DI stanie się bardziej złożone.
        *   **Widoki:** Stwórz instancje widoków, wstrzykując im odpowiednich **Prezenterów** (np. `profile_list_view = ProfileListView(self.navigation_controller, profile_list_presenter)`). *Ważne: Widoki nie dostają serwisów ani repozytoriów!*
        *   *Powtórz proces DI dla wszystkich komponentów potrzebnych na starcie.*
    *   **Rejestracja widoków w Nawigatorze:** Powiąż ścieżki (np. `'/profiles'`) z instancjami odpowiednich widoków w `NavigationController`.
    *   **Stworzenie głównego widoku (`AppView`):**
        *   Stwórz instancję `AppView`, przekazując jej `NavigationController` i ewentualnie inne globalne komponenty UI.
        *   Umieść `AppView` w głównym oknie (`grid`, `sticky="nsew"`). `AppView` będzie delegować wyświetlanie do aktualnie aktywnego widoku zarejestrowanego w `NavigationController`.
    *   **Nawigacja do początkowego widoku:**
        *   Wywołaj `self.navigation_controller.navigate('/profiles')`.

6.  **Dodaj blok startowy `if __name__ == "__main__":`:**
    *   W tym bloku:
        *   Wykonaj konfigurację (logging, DB - krok 3).
        *   Stwórz instancję `TenXCardsApp` (która w `__init__` zajmie się DI i resztą setupu UI - krok 5).
        *   Wywołaj `app.mainloop()`.

7.  **(Krok pomocniczy) Utwórz Placeholdery dla brakujących komponentów:**
    *   Zgodnie z potrzebami z kroku 2 i 5, stwórz minimalne, **poprawnie otypowane** placeholdery klas w odpowiednich katalogach, zgodnie ze strukturą `architecture.mdc`. Np.:
        ```python
        # Przykład src/Shared/ui/core/navigation.py
        import tkinter as tk
        from typing import Dict, Any, Type
        
        class NavigationController:
            def __init__(self, root: tk.Tk, dependencies: Dict[str, Any]): # Przykładowe zależności
                self.root = root
                self.views: Dict[str, tk.Frame] = {} # Lub bardziej specyficzny typ widoku
                self.current_view: tk.Frame | None = None 
                print("Placeholder: NavigationController initialized")

            def register_view(self, path: str, view_instance: tk.Frame) -> None:
                self.views[path] = view_instance
                print(f"Placeholder: View registered for path {path}")

            def navigate(self, path: str) -> None:
                print(f"Placeholder: Navigating to {path}")
                # Logika przełączania widoków (ukrywanie starego, pokazywanie nowego)
                new_view = self.views.get(path)
                if new_view:
                    if self.current_view:
                        self.current_view.grid_remove() # Lub pack_forget/place_forget
                    self.current_view = new_view
                    self.current_view.grid(row=0, column=0, sticky="nsew") # Zakładając, że widok jest w AppView
                else:
                     print(f"Error: No view registered for path {path}") 
        ```

**Przykład zaktualizowanego szkieletu `src/main.py`:**

```python
import tkinter as tk
import ttkbootstrap as ttk
from typing import Any # Użyj bardziej konkretnych typów, gdy będą znane

# --- Standard Library Imports ---
import logging # Placeholder for actual logger import

# --- Project Imports ---
# Assume these paths follow the architecture rules
# Shared Infrastructure
# from Shared.infrastructure.logging_setup import configure_logging # Placeholder
# from Shared.infrastructure.database import initialize_database, DBConnection # Placeholders

# Shared UI Core
from Shared.ui.core.navigation import NavigationController # Placeholder needed
from Shared.ui.core.app_view import AppView # Placeholder needed

# UserProfile Context Imports (Example)
from UserProfile.infrastructure.persistence.user_profile_repository import UserProfileRepositoryImpl # Placeholder
from UserProfile.application.services.user_profile_service import UserProfileService # Placeholder
from UserProfile.application.presenters.profile_list_presenter import ProfileListPresenter # Placeholder
from UserProfile.infrastructure.ui.views.profile_list_view import ProfileListView # Placeholder

# --- Type Aliases (Optional but helpful) ---
# Example: DBConnection = Any # Replace Any with the actual connection type


class TenXCardsApp(ttk.Window):
    """Main application window for 10xCards."""

    def __init__(self, dependencies: dict[str, Any]) -> None:
        """
        Initialize the main application window and components.

        Args:
            dependencies: A dictionary containing pre-initialized shared dependencies 
                          like database connection.
        """
        super().__init__(title="10xCards", themename="darkly")
        self.minsize(800, 600)
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Dependency Injection Setup ---
        db_connection = dependencies.get("db_connection")
        if db_connection is None:
            # Handle error: DB connection is mandatory
            logging.error("Database connection not provided to TenXCardsApp")
            self.destroy() # Close the app if critical dependency is missing
            return 

        # Repositories
        profile_repo = UserProfileRepositoryImpl(db_connection)
        # ... instantiate other repositories

        # Services
        profile_service = UserProfileService(profile_repo)
        # ... instantiate other services

        # Navigation Controller (needs access to self for view placement)
        self.navigation_controller = NavigationController(self, dependencies) 

        # Presenters (often need services and the navigator)
        profile_list_presenter = ProfileListPresenter(profile_service, self.navigation_controller)
        # ... instantiate other presenters

        # --- Main Application View Container ---
        app_view = AppView(self, self.navigation_controller) # AppView manages showing/hiding views
        app_view.grid(row=0, column=0, sticky="nsew")

        # --- View Instantiation & Registration ---
        # Views get the presenter injected (following ui_tkinter rules)
        profile_list_view_instance = ProfileListView(profile_list_presenter) 
        # ... instantiate other views

        # Register views with the navigation controller
        self.navigation_controller.register_view('/profiles', profile_list_view_instance)
        # ... register other views/paths

        # --- Start Navigation ---
        self.navigation_controller.navigate('/profiles') # Show the initial view


def main() -> None:
    """Configure dependencies and run the application."""
    # --- Basic Configuration ---
    # configure_logging() # Placeholder - Configure logging first
    logging.basicConfig(level=logging.INFO) # Simple fallback logger
    logging.info("Starting 10xCards application")

    # db_connection: DBConnection = initialize_database() # Placeholder
    # --- Dependency Container (Simple version) ---
    # In a larger app, this might be a dedicated DI container class
    dependencies = {
        "db_connection": "dummy_db_connection_string" # Replace with actual connection object
        # Add other shared dependencies if needed (e.g., config object)
    }

    # --- Run Application ---
    app = TenXCardsApp(dependencies)
    app.mainloop()


if __name__ == "__main__":
    main()

```

**Następne kroki po wdrożeniu tego planu:**

*   Implementacja placeholderów, zaczynając od tych w `Shared`, a potem w poszczególnych kontekstach (`UserProfile`, etc.), zgodnie z architekturą.
*   Upewnienie się, że zależności są poprawnie wstrzykiwane przez konstruktory.
*   Stopniowe dodawanie faktycznej logiki do serwisów, prezenterów i widoków.
*   Konfiguracja `black`, `flake8`, `mypy` w `pyproject.toml` i regularne ich używanie.
