# Plan implementacji widoku DeckListView

## 1. Przegląd
DeckListView to ekran prezentujący listę talii dla zalogowanego użytkownika. Umożliwia przegląd istniejących talii, tworzenie nowej talii oraz usuwanie wybranych talii z potwierdzeniem. Po wyborze talii następuje nawigacja do widoku listy fiszek w danej talii.

## 2. Routing widoku
Ścieżka dostępu: `/decks`

## 3. Struktura komponentów
- DeckListView (główny kontener)
  - HeaderBar (Back, tytuł, opcje ustawień)
  - ButtonBar (przycisk "Utwórz nową talię")
  - DeckTable (Treeview wyświetlający listę talii)
  - ToastContainer (wyświetlanie powiadomień sukcesu/błędu)
  - CreateDeckDialog (modal/ramka do tworzenia talii)
  - DeleteConfirmationDialog (potwierdzenie usunięcia)

## 4. Szczegóły komponentów

### 4.1 DeckListView
- Opis: Główny komponent widoku, zarządza układem i logiką operacji na talii.
- Główne elementy:
  - HeaderBar: przycisk Wstecz (pop), tytuł "Talie"
  - ButtonBar: przycisk "Utwórz nową talię"
  - DeckTable: tabela z kolumnami "Nazwa" i "Utworzono" (sorted by created_at)
  - ToastContainer: globalne toasty
- Obsługiwane zdarzenia:
  - kliknięcie w wiersz tabeli → nawigacja do `/decks/{deck_id}/cards`
  - kliknięcie przycisku "Utwórz nową talię" → otwarcie CreateDeckDialog
  - kliknięcie ikony kosza przy wierszu → otwarcie DeleteConfirmationDialog
  - skrót BackSpace → powrót do `/profiles`
- Walidacja:
  - w CreateDeckDialog: nazwa niepusta, max 50 znaków, unikalna w kontekście user_id
- Typy (DTO/ViewModel):
  - DeckViewModel:
    - `id: int`
    - `name: str`
    - `created_at: datetime`
  - CreateDeckDTO:
    - `name: str`
  - DeleteDeckDTO:
    - `deck_id: int`
- Properties:
  - `deck_service: IDeckService` (wrapper nad IDeckRepository)
  - `navigation_controller: NavigationController`
  - `show_toast: Callable[[str, str], None]`

### 4.2 DeckTable
- Opis: Treeview prezentujący decki w tabeli
- Główne elementy:
  - Kolumny: "Nazwa" (rozciągana), "Utworzono" (data: DD-MM-RRRR)
  - Wiersze z ikonką kosza przy każdym elemencie
- Obsługiwane zdarzenia:
  - double-click na wierszu → on_deck_select(deck_id)
  - klik ikony kosza → on_deck_delete(deck_id)
- Properties:
  - `decks: List[DeckViewModel]`
  - `on_select: Callable[[int], None]`
  - `on_delete: Callable[[int], None]`

### 4.3 CreateDeckDialog
- Opis: Formularz do wprowadzenia nazwy nowej talii
- Główne elementy:
  - `Entry` dla nazwy
  - `Button` Zapisz, `Button` Anuluj
  - Label z licznikiem znaków
- Obsługiwane zdarzenia:
  - on_save_clicked(name)
  - on_cancel_clicked()
- Walidacja przed wywołaniem on_save:
  - `name.strip() != ''`
  - `len(name) <= 50`
- Properties:
  - `on_save: Callable[[str], None]`
  - `on_cancel: Callable[[], None]`

### 4.4 DeleteConfirmationDialog
- Opis: Proste okno potwierdzenia usunięcia talii
- Główne elementy:
  - Tekst: "Czy na pewno usunąć talię '{name}' i wszystkie jej fiszki?"
  - Button Tak, Button Nie
- Obsługiwane zdarzenia:
  - on_confirm()
  - on_cancel()
- Properties:
  - `deck_name: str`
  - `on_confirm: Callable[[], None]`
  - `on_cancel: Callable[[], None]`

### 4.5 ToastContainer
- Opis: Wyświetlanie komunikatów sukcesu/błędu
- Główne elementy: Toastery w rogu ekranu, auto-dismiss po 3s
- Properties:
  - `show_success(title, message)`
  - `show_error(title, message)`

## 5. Typy
- DeckViewModel:
  ```python
  class DeckViewModel:
      id: int
      name: str
      created_at: datetime
  ```
- CreateDeckDTO:
  ```python
  class CreateDeckDTO:
      name: str
  ```
- DeleteDeckDTO:
  ```python
  class DeleteDeckDTO:
      deck_id: int
  ```

## 6. Zarządzanie stanem
- `self.decks: List[DeckViewModel]` – aktualny zestaw talii
- `self.is_loading: bool` – flag do wyświetlenia spinnera
- `self.dialog_open: bool` – czy modal jest otwarty
- `self.deleting_deck_id: Optional[int]` – ID talii w trakcie usuwania

## 7. Integracja persystencji
- Użycie warstwy serwisów:
  - `deck_service.list_all(user_id)` → zwraca List[Deck]
  - `deck_service.add(user_id, name)` → zwraca Deck
  - `deck_service.delete(deck_id, user_id)` → usuwa rekord
- Mapowanie `Deck` → `DeckViewModel` (np. przez DeckMapper)

## 8. Interakcje użytkownika
1. Wejście na widok → `load_decks()` → aktualizacja tabeli
2. Klik "Utwórz nową talię" → CreateDeckDialog
3. Save w dialogu:
   - Walidacja
   - `deck_service.add(...)`
   - Refresh listy + `show_toast("Sukces", "Talia została utworzona")`
   - Zamknięcie dialogu
4. Klik kosza → DeleteConfirmationDialog
5. Potwierdź:
   - `deck_service.delete(...)`
   - Refresh listy + `show_toast("Sukces", "Talia została usunięta")`
6. Double-click w tabeli → `navigation_controller.navigate("/decks/{id}/cards")`
7. Naciśnięcie BackSpace → `navigation_controller.navigate("/profiles")`

## 9. Warunki i walidacja
- Nazwa talii: niepusta + max 50 znaków (komponent CreateDeckDialog)
- Unikalność: przed zapisem `deck_service.get_by_name(name, user_id)` musi zwrócić None
- Potwierdzenie usunięcia przed wywołaniem delete

## 10. Obsługa błędów
- Błędy DB/duplikat → `IntegrityError` → `show_toast("Błąd", "Talia o tej nazwie już istnieje")`
- Inne wyjątki serwisowe → `show_toast("Błąd", e.message)`
- Błąd ładowania listy → komunikat błędu i ewentualne disable UI

## 11. Kroki implementacji
1. Stworzyć plik `src/DeckManagement/infrastructure/ui/views/deck_list_view.py`.
2. Zaimplementować klasę `DeckListView(ttk.Frame)` z DI: `deck_service`, `navigation_controller`, `show_toast`.
3. Dodać `HeaderBar` i powiązać BackSpace.
4. Stworzyć `DeckTable` na bazie `ttk.Treeview` i skonfigurować kolumny.
5. Utworzyć `ButtonBar` z przyciskiem "Utwórz nową talię".
6. Zaimplementować `CreateDeckDialog` jako `tk.Toplevel` lub ramkę.
7. Dodać `DeleteConfirmationDialog` (może korzystać z `tk.messagebox`).
8. Podpiąć metody serwisowe (`list_all`, `add`, `delete`) i mapowanie wyników do `DeckViewModel`.
9. Dodać logikę odświeżania listy po operacjach.
10. Wdrożyć `ToastContainer` w głównym widoku (`src/Shared/ui/widgets/toast_container.py`).
11. Dopisać obsługę wyjątków i toasty.
12. Wpiąć widok listy talii w główny widok aplikacji (`src/main.py`).
