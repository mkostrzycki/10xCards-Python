# Przewodnik Implementacji Systemu Powtórek Rozłożonych w Czasie (SRS) z Py-FSRS

## 1. Opis Usługi

Celem tej funkcjonalności jest umożliwienie użytkownikom nauki fiszek z wykorzystaniem algorytmu powtórek rozłożonych w czasie (Spaced Repetition System - SRS) dostarczanego przez bibliotekę `Py-FSRS`. Kluczowe komponenty to:

*   **`StudyService`**: Centralny serwis aplikacyjny w nowym kontekście `Study`, odpowiedzialny za logikę sesji nauki, interakcję z `Py-FSRS`, zarządzanie stanem fiszek FSRS oraz komunikację z repozytoriami.
*   **`StudyPresenter`**: Prezentér dla widoku sesji nauki, pośredniczący między widokiem a `StudyService`.
*   **`StudySessionView`**: Nowy widok UI (Tkinter/ttkbootstrap) umożliwiający użytkownikowi interakcję podczas sesji nauki (wyświetlanie fiszek, ocenianie).
*   **`IReviewLogRepository` / `ReviewLogRepositoryImpl`**: Nowe repozytorium do zapisywania historii powtórek (`ReviewLog` z Py-FSRS), co jest kluczowe dla ewentualnej przyszłej optymalizacji parametrów FSRS.
*   **Modyfikacje w `Flashcard`**: Wykorzystanie istniejącego pola `Flashcard.fsrs_state` do przechowywania serializowanego stanu obiektu `fsrs.Card`.

Usługa będzie zgodna z architekturą Vertical Slice, zasadami DDD Lite oraz MVP, jak określono w dokumentacji projektu.

## 2. Konstruktor (`StudyService`)

Serwis `StudyService` będzie zlokalizowany w `src/Study/application/services/study_service.py`.

```python
# src/Study/application/services/study_service.py
import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any # Any for fsrs types if not fully stubbed
# from fsrs import Scheduler, Card as FSRSCard, Rating as FSRSRating, ReviewLog as FSRSReviewLog # Assuming fsrs types

from CardManagement.domain.models.Flashcard import Flashcard
from CardManagement.domain.repositories.IFlashcardRepository import IFlashcardRepository
from Study.domain.repositories.IReviewLogRepository import IReviewLogRepository
# from UserProfile.domain.repositories.IUserProfileRepository import IUserProfileRepository # If needed for user-specific FSRS params
from Shared.application.services.session_service import SessionService # To get current user
from Shared.infrastructure.config import get_config # To get default FSRS params

class StudyService:
    def __init__(
        self,
        flashcard_repository: IFlashcardRepository,
        review_log_repository: IReviewLogRepository,
        session_service: SessionService,
        # user_profile_repository: Optional[IUserProfileRepository] = None, # For future user-specific params
        # fsrs_scheduler_override: Optional[Scheduler] = None # For testing
    ):
        self.flashcard_repo = flashcard_repository
        self.review_log_repo = review_log_repository
        self.session_service = session_service
        # self.user_profile_repo = user_profile_repository 
        
        self._config = get_config()
        self._default_fsrs_parameters = tuple(self._config.get("FSRS_DEFAULT_PARAMETERS", [])) # Ensure config has this
        self._default_desired_retention = self._config.get("FSRS_DEFAULT_DESIRED_RETENTION", 0.9)
        self._default_learning_steps_minutes = self._config.get("FSRS_DEFAULT_LEARNING_STEPS_MINUTES", [1, 10])
        self._default_relearning_steps_minutes = self._config.get("FSRS_DEFAULT_RELEARNING_STEPS_MINUTES", [10])

        # self.scheduler: Optional[Scheduler] = fsrs_scheduler_override # Actual type from fsrs
        self.scheduler: Any = None # Placeholder for fsrs.Scheduler
        
        self.current_study_session_queue: List[Tuple[Flashcard, Any]] = [] # Tuple[Flashcard, FSRSCard]
        self.current_card_index: int = -1
        self.current_deck_id: Optional[int] = None
        
        # Dynamically import fsrs to avoid issues if the library is not available during type checking or early import phases
        try:
            global Scheduler, FSRSCard, FSRSRating, FSRSReviewLog
            from fsrs import Scheduler, Card as FSRSCard, Rating as FSRSRating, ReviewLog as FSRSReviewLog
        except ImportError:
            # Handle the case where fsrs is not installed, perhaps log a warning or raise an error
            # For now, this allows the class to be defined without fsrs installed
            pass


    def _initialize_scheduler(self, user_id: Optional[int]) -> None:
        # TODO: Later, attempt to load user-specific parameters from IUserFSRSParameterRepository
        # For now, use defaults from config.py
        # learning_steps = [timedelta(minutes=m) for m in self._default_learning_steps_minutes]
        # relearning_steps = [timedelta(minutes=m) for m in self._default_relearning_steps_minutes]
        
        # self.scheduler = Scheduler(
        #     parameters=self._default_fsrs_parameters,
        #     desired_retention=self._default_desired_retention,
        #     learning_steps=tuple(learning_steps),
        #     relearning_steps=tuple(relearning_steps)
        # )
        # Placeholder for actual fsrs.Scheduler initialization
        # For now, using Any to avoid direct dependency if fsrs is not yet integrated
        global Scheduler
        if 'Scheduler' in globals():
            self.scheduler = Scheduler(parameters=self._default_fsrs_parameters) # Simplified for example
        else:
            # This path should ideally not be hit in a running application
            # Or, handle it by preventing study sessions if fsrs is not available
            raise RuntimeError("FSRS library not loaded. Cannot initialize scheduler.")

```

## 3. Metody Publiczne i Pola (`StudyService`)

### Pola Publiczne

Brak pól publicznych (zgodnie z enkapsulacją). Stan zarządzany wewnętrznie lub przez metody.

### Metody Publiczne

*   `start_session(self, deck_id: int, user_id: int) -> Optional[Tuple[Flashcard, Any]]`:
    *   Inicjalizuje sesję nauki dla danego `deck_id` i `user_id`.
    *   Czyści stan poprzedniej sesji.
    *   Ładuje `_initialize_scheduler(user_id)`.
    *   Wywołuje `_load_and_prepare_fsrs_cards(deck_id, user_id)` do pobrania fiszek i ich stanów FSRS.
    *   Filtruje karty, które są "due" (`fsrs_card.due <= datetime.now(timezone.utc)`).
    *   Sortuje "due" karty (np. wg `fsrs_card.due` rosnąco).
    *   Ustawia `self.current_study_session_queue`.
    *   Ustawia `self.current_card_index = 0` jeśli kolejka nie jest pusta.
    *   Zwraca pierwszą kartę `(Flashcard, FSRSCard)` z kolejki lub `None`, jeśli brak kart do nauki.

*   `get_current_card_for_review(self) -> Optional[Tuple[Flashcard, Any]]`:
    *   Zwraca aktualną kartę `(Flashcard, FSRSCard)` na podstawie `current_card_index` z `current_study_session_queue`.
    *   Zwraca `None`, jeśli sesja się nie rozpoczęła, zakończyła, lub wystąpił błąd indeksu.

*   `record_review(self, flashcard_id: int, rating_value: int) -> Tuple[Flashcard, Any]`:
    *   Sprawdza, czy `flashcard_id` pasuje do ID aktualnej karty w sesji.
    *   Pobiera odpowiedni obiekt `FSRSCard` z `current_study_session_queue`.
    *   Konwertuje `rating_value` (np. 1-4) na obiekt `FSRSRating` (np. `FSRSRating(rating_value)`).
    *   Wywołuje `self.scheduler.review_card(current_fsrs_card, fsrs_rating_obj)` co zwraca `(updated_fsrs_card, review_log_obj)`.
    *   Aktualizuje `Flashcard.fsrs_state` w domenie: `flashcard_domain_obj.fsrs_state = json.dumps(updated_fsrs_card.to_dict())`.
    *   Zapisuje zaktualizowany `flashcard_domain_obj` przez `self.flashcard_repo.update()`.
    *   Zapisuje `review_log_obj` przez `self.review_log_repo.add(...)`, przekazując `user_id`, `flashcard_id`, `review_log_obj.to_dict()`, `rating_value`, `review_log_obj.review_datetime` oraz JSON parametrów obecnego schedulera (`json.dumps(list(self.scheduler.parameters))`).
    *   Zwraca zaktualizowaną krotkę `(flashcard_domain_obj, updated_fsrs_card)`.

*   `proceed_to_next_card(self) -> Optional[Tuple[Flashcard, Any]]`:
    *   Inkrementuje `self.current_card_index`.
    *   Jeśli indeks jest w granicach `current_study_session_queue`, zwraca następną kartę.
    *   W przeciwnym razie (koniec kolejki), zwraca `None`.

*   `get_session_progress(self) -> Tuple[int, int]`:
    *   Zwraca `(current_card_index + 1, len(current_study_session_queue))` jeśli sesja aktywna.
    *   Zwraca `(0, 0)` lub `(total, total)` w zależności od preferencji na starcie/końcu.

*   `end_session(self) -> None`:
    *   Czyści stan sesji: `current_study_session_queue`, `current_card_index`, `current_deck_id`. Może też zwolnić `self.scheduler` jeśli jest duży i tworzony per sesję.

## 4. Metody Prywatne i Pola (`StudyService`)

### Pola Prywatne

*   `_config`: Załadowana konfiguracja aplikacji.
*   `_default_fsrs_parameters`: Domyślne parametry dla `fsrs.Scheduler`.
*   `_default_desired_retention`, `_default_learning_steps_minutes`, `_default_relearning_steps_minutes`: Inne domyślne parametry FSRS.
*   `scheduler: Scheduler`: Instancja `fsrs.Scheduler`.
*   `current_study_session_queue: List[Tuple[Flashcard, FSRSCard]]`: Lista kart do przejrzenia w bieżącej sesji.
*   `current_card_index: int`: Indeks aktualnej karty w `current_study_session_queue`.
*   `current_deck_id: Optional[int]`: ID talii używanej w bieżącej sesji.

### Metody Prywatne

*   `_initialize_scheduler(self, user_id: Optional[int]) -> None`:
    *   Logika inicjalizacji `self.scheduler`. W MVP używa parametrów domyślnych z `_config`.
    *   Docelowo: próbuje załadować spersonalizowane parametry FSRS dla `user_id` z `IUserFSRSParameterRepository`. Jeśli brak, używa domyślnych.

*   `_load_and_prepare_fsrs_cards(self, deck_id: int, user_id: int) -> List[Tuple[Flashcard, Any]]`:
    *   Pobiera wszystkie `Flashcard` z `self.flashcard_repo.list_by_deck_id(deck_id)`.
    *   Dla każdej `Flashcard`:
        *   Jeśli `flashcard.fsrs_state` istnieje i nie jest pusty:
            *   `fsrs_card_dict = json.loads(flashcard.fsrs_state)`
            *   `fsrs_card = FSRSCard.from_dict(fsrs_card_dict)`
        *   W przeciwnym razie (nowa karta dla FSRS):
            *   `fsrs_card = FSRSCard()`
            *   Opcjonalnie: można od razu zapisać ten początkowy stan `fsrs_card.to_dict()` do `flashcard.fsrs_state` jeśli FSRS tego wymaga lub dla spójności. Jednak `review_card` i tak go zaktualizuje.
        *   Dodaje `(flashcard_domain_obj, fsrs_card)` do listy.
    *   Zwraca listę przygotowanych krotek.

*   `_filter_and_sort_due_cards(self, all_session_cards: List[Tuple[Flashcard, Any]]) -> List[Tuple[Flashcard, Any]]`:
    *   Iteruje po `all_session_cards`.
    *   Zachowuje te, dla których `fsrs_card.due <= datetime.now(timezone.utc)`.
    *   Sortuje wynikową listę wg `fsrs_card.due` (rosnąco).
    *   Zwraca przefiltrowaną i posortowaną listę.

## 5. Obsługa Błędów

*   **Brak kart do nauki:** `start_session` zwróci `None` lub pustą kolejkę. `StudyPresenter` powinien obsłużyć to i poinformować użytkownika.
*   **Błąd deserializacji `fsrs_state`:** W `_load_and_prepare_fsrs_cards`, jeśli `json.loads` lub `FSRSCard.from_dict` zawiedzie:
    *   Zalogować błąd.
    *   Traktować kartę jako nową dla FSRS (utworzyć `FSRSCard()`).
    *   Poinformować użytkownika (np. jednorazowy toast), jeśli błąd był krytyczny i dane mogły zostać utracone.
*   **Błędy Py-FSRS:** Np. `scheduler.review_card` może zgłosić wyjątek.
    *   Otoczyć wywołania metod Py-FSRS blokami `try-except`.
    *   Logować błędy zgodnie z FR-035.
    *   Przekazać stosowny komunikat do `StudyPresenter`, który wyświetli go użytkownikowi.
*   **Błędy bazy danych:** Podczas zapisu `Flashcard` lub `ReviewLog`.
    *   Repozytoria powinny propagować wyjątki (np. `sqlite3.Error`).
    *   `StudyService` powinien je łapać, logować i informować `StudyPresenter`.
*   **Nieoczekiwane błędy:** Ogólna obsługa wyjątków w `StudyService` i `StudyPresenter` w celu logowania i wyświetlania generycznego komunikatu o błędzie.

## 6. Kwestie Bezpieczeństwa

*   **Izolacja danych użytkownika:** Wszystkie zapytania do bazy danych muszą uwzględniać `user_profile_id` (lub `deck_id`, który jest powiązany z użytkownikiem), aby użytkownik miał dostęp tylko do swoich danych. `StudyService` powinien otrzymywać `user_id` i przekazywać go do repozytoriów.
*   **Walidacja danych wejściowych:** Upewnić się, że `deck_id` i `flashcard_id` przekazywane do metod `StudyService` są poprawne i należą do zalogowanego użytkownika (częściowo realizowane przez pobieranie danych w kontekście użytkownika).
*   **Parametry FSRS:** Jeśli parametry FSRS będą przechowywane per użytkownik, upewnić się, że są one poprawnie przypisane i odczytywane tylko dla danego użytkownika. Domyślne parametry w `config.py` są globalne i bezpieczne.

## 7. Plan Wdrożenia Krok po Kroku

### Krok 1: Zmiany w Bazie Danych i Konfiguracji

1.  **Zdefiniuj schemat tabeli `ReviewLogs`:**
    ```sql
    CREATE TABLE IF NOT EXISTS ReviewLogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_profile_id INTEGER NOT NULL,
        flashcard_id INTEGER NOT NULL,
        review_log_data TEXT NOT NULL, -- JSON of fsrs.ReviewLog.to_dict()
        fsrs_rating INTEGER NOT NULL,   -- 1:Again, 2:Hard, 3:Good, 4:Easy
        reviewed_at TEXT NOT NULL,      -- ISO8601 datetime string
        scheduler_params_at_review TEXT NOT NULL, -- JSON of fsrs.Scheduler.parameters active at review time
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_profile_id) REFERENCES UserProfiles(id) ON DELETE CASCADE,
        FOREIGN KEY (flashcard_id) REFERENCES Flashcards(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_reviewlogs_user_flashcard ON ReviewLogs (user_profile_id, flashcard_id);
    ```
2.  **(Opcjonalnie, dla przyszłego Optymalizatora) Zdefiniuj schemat tabeli `UserFSRSParameters`:**
    ```sql
    CREATE TABLE IF NOT EXISTS UserFSRSParameters (
        user_profile_id INTEGER PRIMARY KEY,
        parameters_json TEXT NOT NULL, -- JSON list/tuple of 19 FSRS parameters
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_profile_id) REFERENCES UserProfiles(id) ON DELETE CASCADE
    );
    ```
3.  **Dodaj migracje bazy danych** (jeśli system migracji jest używany) lub zaktualizuj skrypt inicjalizacji DB.
4.  **Dodaj domyślne parametry FSRS do `src/Shared/infrastructure/config.py`:**
    ```python
    # In your config dictionary or class
    "FSRS_DEFAULT_PARAMETERS": [
        0.4, 1.2, 3.0, 15.0, 7.0, 0.5, 1.4, 0.0, 
        1.5, 0.1, 1.0, 2.0, 0.1, 0.3, 2.3, 0.2, 
        3.0, 0.5, 0.6 # Example: Replace with actual py-fsrs defaults or desired defaults (19 params)
    ],
    "FSRS_DEFAULT_DESIRED_RETENTION": 0.9,
    "FSRS_DEFAULT_LEARNING_STEPS_MINUTES": [1, 10], # e.g. [1, 10] for 1m, 10m steps
    "FSRS_DEFAULT_RELEARNING_STEPS_MINUTES": [10], # e.g. [10] for 10m step
    "FSRS_MAXIMUM_INTERVAL": 36500, # Default from py-fsrs
    "FSRS_ENABLE_FUZZING": True, # Default from py-fsrs
    ```
    *Uwaga: Sprawdź aktualne wartości domyślne w dokumentacji `Py-FSRS` dla 19 parametrów.*

### Krok 2: Kontekst `Study` - Warstwa Domeny

1.  Utwórz strukturę katalogów: `src/Study/domain/repositories/`.
2.  Zdefiniuj interfejs `src/Study/domain/repositories/IReviewLogRepository.py`:
    ```python
    from abc import ABC, abstractmethod
    from typing import List, Dict, Any, Tuple # Any for ReviewLog dict for now
    from datetime import datetime

    class IReviewLogRepository(ABC):
        @abstractmethod
        def add(self, user_id: int, flashcard_id: int, review_log_data: Dict[str, Any], rating: int, reviewed_at: datetime, scheduler_params_json: str) -> None:
            pass

        @abstractmethod
        def get_all_for_user(self, user_id: int) -> List[Tuple[Dict[str, Any], str]]: # List of (review_log_data, scheduler_params_json)
            pass
        
        # Potentially other methods like get_for_flashcard, etc.
    ```
3.  **(Opcjonalnie) Zdefiniuj `IUserFSRSParameterRepository`** jeśli planujesz przechowywać spersonalizowane parametry.

### Krok 3: Kontekst `Study` - Warstwa Infrastruktury (Persystencja)

1.  Utwórz strukturę katalogów: `src/Study/infrastructure/persistence/sqlite/repositories/` i `src/Study/infrastructure/persistence/sqlite/mappers/`.
2.  Zaimplementuj `src/Study/infrastructure/persistence/sqlite/repositories/ReviewLogRepositoryImpl.py`:
    *   Będzie przyjmować `DbConnectionProvider` w konstruktorze.
    *   Metoda `add`: wykonuje `INSERT` do tabeli `ReviewLogs`, serializując `review_log_data` i `scheduler_params_json` do JSON, `reviewed_at` do stringa ISO.
    *   Metoda `get_all_for_user`: wykonuje `SELECT` z tabeli `ReviewLogs`, deserializując JSONy.
3.  **(Opcjonalnie) Zaimplementuj `UserFSRSParameterRepositoryImpl`**.

### Krok 4: Kontekst `Study` - Warstwa Aplikacji

1.  Utwórz strukturę katalogów: `src/Study/application/services/` i `src/Study/application/presenters/`.
2.  Zaimplementuj `src/Study/application/services/study_service.py` (jak opisano w sekcjach 2, 3, 4).
3.  Zaimplementuj `src/Study/application/presenters/study_presenter.py`:
    *   Konstruktor: `(view: StudySessionViewInterface, study_service: StudyService, navigation_controller, session_service)`
    *   Metody obsługujące akcje z widoku (np. `handle_start_session_request`, `handle_show_answer`, `handle_rate_again/hard/good/easy`, `handle_next_card`, `handle_end_session`).
    *   Metody aktualizujące widok (np. `_update_view_with_card`, `_show_session_summary`).

### Krok 5: Kontekst `Study` - Warstwa Infrastruktury (UI)

1.  Utwórz strukturę katalogów: `src/Study/infrastructure/ui/views/` i `src/Study/infrastructure/ui/widgets/` (jeśli potrzebne będą dedykowane widgety).
2.  Zaimplementuj `src/Study/infrastructure/ui/views/study_session_view.py`:
    *   Klasa dziedzicząca po `ttk.Frame`.
    *   Konstruktor: `(parent, presenter: StudyPresenter, deck_name: str)`
    *   Elementy UI:
        *   Etykieta na nazwę talii, postęp (np. "Karta 5/20").
        *   Duża etykieta/Text na przód fiszki.
        *   Duża etykieta/Text na tył fiszki (początkowo ukryta lub pusta).
        *   Przycisk "Pokaż odpowiedź".
        *   Przyciski ocen: "Again", "Hard", "Good", "Easy" (początkowo nieaktywne/ukryte, aktywują się po pokazaniu odpowiedzi).
        *   Przycisk "Zakończ sesję".
    *   Metody publiczne wywoływane przez prezentera do aktualizacji UI (np. `display_card_front`, `display_card_back_and_ratings`, `show_session_complete_message`, `update_progress`).
    *   Powiązanie akcji UI (kliknięcia przycisków) z metodami prezentera.
3.  **Integracja rozpoczęcia sesji:**
    *   Dodaj przycisk "Rozpocznij naukę" do `src/CardManagement/infrastructure/ui/views/card_list_view.py` (lub `DeckListView` jeśli taki istnieje i jest używany do wyboru talii do nauki).
    *   W odpowiednim prezenterze (np. `CardListPresenter`) obsłuż kliknięcie tego przycisku: pobierz `deck_id` i użyj `navigation_controller.navigate(f"/study/session/{deck_id}")`.
4.  **Routing:** Zaktualizuj główny router aplikacji (`NavigationController` lub podobny), aby dodać nową ścieżkę (np. `/study/session/<deck_id>`) i mapować ją na tworzenie i wyświetlanie `StudySessionView` (wraz z jego prezenterem i serwisem).

### Krok 6: Aktualizacja `Shared` i `main.py`

1.  **Dependency Injection w `main.py`:**
    *   Utwórz instancje `ReviewLogRepositoryImpl`, `StudyService`, `StudyPresenter`.
    *   Wstrzyknij zależności do konstruktorów.
    *   Przekaż `StudyPresenter` do `NavigationController` dla nowej ścieżki routingu.
2.  Upewnij się, że `SessionService` jest dostępny i dostarcza `user_id`.

### Krok 7: Testowanie

1.  **Testy jednostkowe:**
    *   `StudyService`: przetestuj logikę wyboru kart "due", procesowania ocen, interakcji z mockowanymi repozytoriami i `fsrs.Scheduler`.
    *   `StudyPresenter`: przetestuj logikę obsługi zdarzeń z widoku i wywołań `StudyService`.
    *   `ReviewLogRepositoryImpl`: przetestuj operacje CRUD na bazie danych (z testową bazą SQLite in-memory).
2.  **Testy behawioralne (Behave):**
    *   Zdefiniuj scenariusze dla User Stories US-014 i US-015 (`.feature` files).
    *   Zaimplementuj kroki (steps) symulujące interakcję użytkownika z UI sesji nauki, weryfikując zmiany stanu i danych.
3.  **Testy integracyjne:**
    *   Przetestuj współpracę `StudyService` z rzeczywistą implementacją `ReviewLogRepositoryImpl` i `FlashcardRepositoryImpl` (z testową bazą danych).

### Krok 8: Logowanie

1.  Dodaj logowanie do `StudyService` zgodnie z FR-035 (błędy Py-FSRS) oraz ogólne logowanie kluczowych operacji (np. rozpoczęcie/zakończenie sesji, zapis recenzji, błędy).
    *   Użyj standardowego modułu `logging`.
    *   Przykład: `logger.error("Error processing FSRS review for card %s: %s", flashcard_id, e, exc_info=True)`

### Krok 9: Dokumentacja i Refaktoryzacja

1.  Przejrzyj kod pod kątem zgodności z `python_style.mdc` i `architecture.mdc`.
2.  Dodaj komentarze i docstringi tam, gdzie to konieczne.
3.  Upewnij się, że konfiguracja parametrów FSRS jest jasna i łatwo modyfikowalna.
