# Przewodnik Implementacji: Usuwanie Talii Fiszlek

## 1. Opis Funkcjonalności

Funkcjonalność umożliwia użytkownikowi usunięcie całej talii fiszek bezpośrednio z widoku listy fiszek tej talii (`CardListView`). Usunięcie talii pociąga za sobą usunięcie wszystkich powiązanych z nią fiszek oraz zapisów historii powtórek (review logs) dla tych fiszek. Operacja jest nieodwracalna i wymaga potwierdzenia od użytkownika.

## 2. Zmiany w Komponentach

### Widok (`src/CardManagement/infrastructure/ui/views/card_list_view.py`)

#### Zmiany w Konstruktorze (`__init__`)
Konstruktor `CardListView` będzie musiał przyjmować dodatkową zależność: `deck_service: DeckService`, która następnie zostanie przekazana do `CardListPresenter`.

```python
# Przykład modyfikacji __init__ w CardListView
def __init__(
    self,
    parent: Any,
    deck_id: int,
    deck_name: str,
    card_service: CardService,
    deck_service: DeckService, # NOWA ZALEŻNOŚĆ
    session_service: SessionService,
    navigation_controller: NavigationControllerProtocol,
    show_toast: Callable[[str, str], None],
):
    super().__init__(parent)
    self._show_toast_callback = show_toast
    self.deck_id = deck_id
    self.deck_name = deck_name

    # Przekazanie deck_service do prezentera
    self.presenter = CardListPresenter(
        view=self,
        card_service=card_service,
        deck_service=deck_service, # PRZEKAZANIE NOWEJ ZALEŻNOŚCI
        session_service=session_service,
        navigation_controller=navigation_controller,
        deck_id=deck_id,
        deck_name=deck_name,
    )
    # ... reszta inicjalizacji ...
```

#### Nowe Elementy UI
W panelu przycisków (`ButtonPanel`) zostanie dodany nowy przycisk "Usuń Tę Talię".

```python
# W metodzie _init_ui() w CardListView, w sekcji Button Panel
# ... istniejące przyciski w button_panel ...

# Przycisk Usuń Tę Talię
self.delete_deck_btn = ttk.Button(
    self.button_panel,
    text="Usuń Tę Talię",
    style="danger.TButton", # Styl sugerujący operację destrukcyjną
    command=self.presenter.request_delete_current_deck # Nowa metoda w prezenterze
)
self.delete_deck_btn.pack(side=ttk.LEFT, padx=5, pady=5) # Lub inna odpowiednia pozycja
```

### Prezenter (`src/CardManagement/application/presenters/card_list_presenter.py`)

#### Zmiany w Konstruktorze (`__init__`)
Konstruktor `CardListPresenter` będzie musiał przyjmować i przechowywać `deck_service: DeckService`.

```python
# Przykład modyfikacji __init__ w CardListPresenter
from DeckManagement.application.deck_service import DeckService # DODAJ IMPORT

class CardListPresenter:
    def __init__(
        self,
        view: ICardListView,
        card_service: CardService,
        deck_service: DeckService, # NOWA ZALEŻNOŚĆ
        session_service: SessionService,
        navigation_controller: NavigationControllerProtocol,
        deck_id: int,
        deck_name: str,
    ):
        self.view = view
        self.card_service = card_service
        self.deck_service = deck_service # PRZECHOWANIE NOWEJ ZALEŻNOŚCI
        self.session_service = session_service
        self.navigation = navigation_controller
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.dialog_open: bool = False # Istniejące pole, może być reużyte
        self.deleting_id: Optional[int] = None # Istniejące pole, może być reużyte dla ID fiszki
        # Można dodać nowe pole np. self.is_deleting_deck: bool = False jeśli potrzebne rozróżnienie
```

#### Nowe Metody Publiczne

*   `request_delete_current_deck(self) -> None`:
    *   Sprawdza, czy użytkownik jest zalogowany.
    *   Wyświetla `ConfirmationDialog` z pytaniem o potwierdzenie usunięcia talii.
    *   W przypadku potwierdzenia, wywołuje `_handle_deck_deletion_confirmed()`.
    *   W przypadku anulowania, wywołuje `_handle_deck_deletion_cancelled()`.

#### Nowe Metody Prywatne

*   `_handle_deck_deletion_confirmed(self) -> None`:
    *   Pobiera `user_id` z `session_service`.
    *   Wywołuje `self.deck_service.delete_deck(self.deck_id, user_id)`.
    *   W przypadku sukcesu:
        *   Wyświetla `self.view.show_toast("Sukces", "Talia została usunięta.")`.
        *   Nawiguje do widoku listy talii: `self.navigation.navigate("/decks")`.
    *   W przypadku błędu (np. `ValueError` z `DeckService` lub `sqlite3.Error`):
        *   Loguje błąd.
        *   Wyświetla `self.view.show_error("Wystąpił błąd podczas usuwania talii.")`.
    *   Resetuje stan (np. `self.dialog_open = False`).
*   `_handle_deck_deletion_cancelled(self) -> None`:
    *   Resetuje stan (np. `self.dialog_open = False`).

### Serwis Aplikacyjny (`src/DeckManagement/application/deck_service.py`)

Metoda `delete_deck(self, deck_id: int, user_id: int)` **już istnieje** i jest odpowiednia. Wykonuje ona sprawdzenie, czy talia należy do użytkownika, a następnie woła `self.deck_repository.delete(deck_id, user_id)`. Nie są wymagane żadne zmiany.

### Repozytorium (`src/DeckManagement/infrastructure/persistence/sqlite/repositories/DeckRepositoryImpl.py`)

Metoda `delete(self, deck_id: int, user_id: int)` **już istnieje** i wykonuje polecenie SQL `DELETE FROM Decks WHERE id = ? AND user_id = ?`. Dzięki mechanizmowi `ON DELETE CASCADE` zdefiniowanemu w schemacie bazy danych:
1.  Usunięcie rekordu z tabeli `Decks` automatycznie usunie wszystkie powiązane rekordy z tabeli `Flashcards` (gdzie `Flashcards.deck_id` pasuje do usuniętego `Decks.id`).
2.  Usunięcie rekordów z tabeli `Flashcards` automatycznie usunie wszystkie powiązane rekordy z tabeli `ReviewLogs` (gdzie `ReviewLogs.flashcard_id` pasuje do usuniętych `Flashcards.id`).

Nie są wymagane żadne zmiany w kodzie repozytorium.

## 3. Kluczowe Metody i Pola (szczegóły implementacji)

### `CardListPresenter.request_delete_current_deck(self) -> None`

```python
def request_delete_current_deck(self) -> None:
    if not self.session_service.is_authenticated():
        self.view.show_toast("Błąd", "Musisz być zalogowany, aby usunąć talię.")
        self.navigation.navigate("/profiles")
        return

    if self.dialog_open: # Zapobieganie wielokrotnemu otwarciu dialogu
        return

    self.dialog_open = True
    # Użycie istniejącego ConfirmationDialog
    ConfirmationDialog(
        parent=self.view, # Zakładając, że widok jest widgetem Tkinter
        title="Usuń Tę Talię",
        message=f"Czy na pewno chcesz usunąć talię '{self.deck_name}' wraz ze wszystkimi jej fiszkami? Tej operacji nie można cofnąć.",
        confirm_text="Usuń Talię",
        confirm_style="danger.TButton",
        cancel_text="Anuluj",
        on_confirm=self._handle_deck_deletion_confirmed,
        on_cancel=self._handle_deck_deletion_cancelled,
    )
```

### `CardListPresenter._handle_deck_deletion_confirmed(self) -> None`

```python
def _handle_deck_deletion_confirmed(self) -> None:
    try:
        user_profile = self.session_service.get_current_user()
        if not user_profile or user_profile.id is None:
            self.view.show_error("Nie udało się zidentyfikować użytkownika.")
            return

        self.view.show_loading(True)
        self.deck_service.delete_deck(self.deck_id, user_profile.id)
        self.view.show_toast("Sukces", f"Talia '{self.deck_name}' została pomyślnie usunięta.")
        self.navigation.navigate("/decks")
    except ValueError as ve:
        logger.warning(f"Validation error while deleting deck {self.deck_id}: {str(ve)}")
        self.view.show_error(str(ve))
    except Exception as e:
        logger.error(f"Error deleting deck {self.deck_id}: {str(e)}", exc_info=True)
        self.view.show_error("Wystąpił nieoczekiwany błąd podczas usuwania talii.")
    finally:
        self.view.show_loading(False)
        self._reset_deck_deletion_state() # Nowa metoda do resetowania stanu
```

### `CardListPresenter._handle_deck_deletion_cancelled(self) -> None`

```python
def _handle_deck_deletion_cancelled(self) -> None:
    self._reset_deck_deletion_state()
```

### `CardListPresenter._reset_deck_deletion_state(self) -> None` (Nowa metoda pomocnicza)

```python
def _reset_deck_deletion_state(self) -> None:
    self.dialog_open = False
    # Można dodać inne flagi jeśli byłyby używane, np. self.is_deleting_deck = False
```

## 4. Prywatne Metody i Pola

Pola `self.dialog_open` w `CardListPresenter` może być współdzielone lub można dodać dedykowane pole `self.is_deck_delete_dialog_open: bool` dla większej klarowności, jeśli operacje usuwania fiszek i talii mogą się przeplatać w sposób problematyczny. Dla MVP, reużycie `self.dialog_open` z odpowiednim resetowaniem powinno być wystarczające.

## 5. Obsługa Błędów

1.  **Brak zalogowanego użytkownika:** Prezenter sprawdza sesję i przekierowuje do logowania.
2.  **Anulowanie przez użytkownika:** Dialog potwierdzenia obsługuje anulowanie, stan jest resetowany.
3.  **Talia nie istnieje lub nie należy do użytkownika:** `DeckService.delete_deck` zgłasza `ValueError`. Prezenter łapie błąd i wyświetla stosowny komunikat użytkownikowi (`view.show_error()`).
4.  **Błąd bazy danych (np. `sqlite3.Error`):**
    *   `DeckRepositoryImpl` propaguje błąd.
    *   `DeckService` może go złapać, zalogować i ewentualnie opakować we własny wyjątek domenowy lub aplikacyjny (np. `DeckOperationError`). W obecnej implementacji `DeckService` propaguje błędy repozytorium.
    *   Prezenter łapie błąd i wyświetla ogólny komunikat błędu (`view.show_error("Wystąpił nieoczekiwany błąd...")`).
5.  **Nieoczekiwane błędy w logice prezentera/serwisu:** Ogólne bloki `try-except Exception` w prezenterze i serwisie logują błąd i informują użytkownika.

## 6. Kwestie Bezpieczeństwa

1.  **Autoryzacja:** `DeckService.delete_deck` i `DeckRepositoryImpl.delete` używają `user_id` do filtrowania operacji, co zapobiega usunięciu talii innego użytkownika. Kluczowe jest, aby `user_id` pochodziło z zaufanego źródła (np. `SessionService`).
2.  **Potwierdzenie operacji:** Użycie `ConfirmationDialog` jest kluczowe, aby zapobiec przypadkowemu usunięciu danych. Komunikat w dialogu powinien jasno informować o nieodwracalności operacji i o tym, że wszystkie fiszki w talii zostaną usunięte.
3.  **Walidacja danych wejściowych:** Chociaż w tym przypadku `deck_id` pochodzi z wewnętrznego stanu aplikacji, ogólna zasada walidacji jest ważna.

## 7. Plan Wdrożenia Krok Po Kroku

1.  **Modyfikacja `CardListPresenter` (`src/CardManagement/application/presenters/card_list_presenter.py`):**
    a.  Dodaj import `DeckService` z modułu `DeckManagement.application.deck_service`.
    b.  Zmodyfikuj konstruktor `__init__`, aby przyjmował i przechowywał instancję `DeckService`.
    c.  Zaimplementuj nową metodę publiczną `request_delete_current_deck(self) -> None` (jak opisano w sekcji 8).
    d.  Zaimplementuj nowe metody prywatne: `_handle_deck_deletion_confirmed(self) -> None`, `_handle_deck_deletion_cancelled(self) -> None` oraz `_reset_deck_deletion_state(self) -> None` (jak opisano w sekcji 8). Pamiętaj o logowaniu błędów.

2.  **Modyfikacja `CardListView` (`src/CardManagement/infrastructure/ui/views/card_list_view.py`):**
    a.  Dodaj import `DeckService` z modułu `DeckManagement.application.deck_service`.
    b.  Zmodyfikuj konstruktor `__init__`, aby przyjmował instancję `DeckService` i przekazywał ją do konstruktora `CardListPresenter`.
    c.  W metodzie `_init_ui()`, w sekcji `ButtonPanel`, dodaj nowy `ttk.Button` "Usuń Tę Talię". Ustaw jego `command` na `self.presenter.request_delete_current_deck`. Wybierz odpowiedni styl (np. `danger.TButton`).
    d.  Upewnij się, że `parent` przekazywany do `ConfirmationDialog` w `request_delete_current_deck` jest poprawnym widgetem nadrzędnym (np. `self` jeśli `CardListView` jest widgetem Tkinter).

3.  **Aktualizacja Inicjalizacji Aplikacji (Miejsce tworzenia `CardListView`):**
    a.  W miejscu, gdzie tworzona jest instancja `CardListView` (prawdopodobnie w głównym pliku aplikacji lub w komponencie odpowiedzialnym za nawigację i tworzenie widoków), upewnij się, że instancja `DeckService` jest dostępna i przekazywana do konstruktora `CardListView`. Może to wymagać pobrania `DeckService` z kontenera DI lub ręcznego utworzenia i przekazania.

4.  **Weryfikacja `DeckService` i `DeckRepositoryImpl`:**
    a.  Sprawdź, czy `DeckService.delete_deck` i `DeckRepositoryImpl.delete` działają zgodnie z oczekiwaniami i czy obsługa `user_id` jest poprawna. (Zgodnie z analizą, istniejące implementacje są wystarczające).

5.  **Testowanie:**
    a.  **Testy jednostkowe:**
        *   Dla `CardListPresenter`: przetestuj logikę `request_delete_current_deck`, interakcję z `ConfirmationDialog` (można mockować), wywołanie `DeckService`, nawigację i obsługę błędów.
    b.  **Testy integracyjne/behawioralne (jeśli dotyczy):**
        *   Przetestuj cały przepływ: kliknięcie przycisku -> dialog -> potwierdzenie -> usunięcie danych z bazy (sprawdź `Decks`, `Flashcards`, `ReviewLogs`) -> przekierowanie.
        *   Sprawdź przypadek anulowania operacji.
        *   Sprawdź, czy próba usunięcia talii przez nieautoryzowanego użytkownika (jeśli możliwe do zasymulowania) jest blokowana.
        *   Sprawdź obsługę błędów (np. symulując błąd bazy danych).
    c.  **Testy manualne UI:**
        *   Sprawdź wizualne aspekty przycisku i dialogu.
        *   Przetestuj responsywność i działanie na różnych etapach.

6.  **Przegląd Kodu i Merge:**
    a.  Upewnij się, że kod przestrzega zasad PEP 8, zawiera type hinting i jest zgodny z przyjętymi wzorcami architektonicznymi.
