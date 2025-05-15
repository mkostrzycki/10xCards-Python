# Plan implementacji widoku CardListView

## 1. Przegląd
Widok `CardListView` służy do przeglądania fiszek w wybranej talii oraz zapewnia przyciski do manualnego dodawania nowej fiszki i uruchamiania generatora AI. Wyświetla listę istniejących fiszek (fragmenty „przód/tył”), umożliwia edycję i usuwanie poszczególnych pozycji.

## 2. Routing widoku
Ścieżka: `/decks/{deck_id}/cards`
W `NavigationController` rejestrujemy ten widok pod kluczem `/decks/{deck_id}/cards` i nawigujemy do niego po wybraniu talii.

## 3. Struktura komponentów
- CardListView (główny kontener)
  - HeaderBar (Back + tytuł talii)
  - FlashcardTable (Treeview z kolumnami „Przód”, „Tył”, „Akcje”)
  - ButtonPanel (przyciski: Dodaj fiszkę, Generuj z AI)
  - ConfirmationDialog (modal usuwania)

## 4. Szczegóły komponentów

### CardListView
- Opis: główny widok osadzony w `ttk.Frame`, inicjuje stan, pobiera dane, renderuje subkomponenty.
- Główne elementy: HeaderBar, FlashcardTable, ButtonPanel, ConfirmationDialog.
- Obsługiwane zdarzenia:
  - on_load → pobierz listę fiszek
  - on_add_click → wywołaj `navigation_controller.navigate('/decks/{deck_id}/cards/new')`
  - on_generate_ai_click → `navigate('/decks/{deck_id}/cards/generate-ai')`
  - on_edit_click(flashcard_id) → `navigate('/decks/{deck_id}/cards/{flashcard_id}/edit')`
  - on_delete_click(flashcard_id) → pokaż ConfirmationDialog
  - on_confirm_delete → wywołaj `flashcardService.delete(flashcard_id)` i przeładuj listę
- Walidacja: `deck_id` nie może być pusty; potwierdzenie usuwania przed wykonaniem `delete`.
- Typy:
  - Props: `deck_id: int`, `deck_name: str`, `flashcardService: CardService`, `navigation_controller`, `show_toast`
  - Local State: `flashcards: List[FlashcardViewModel]`, `loading: bool`, `error: Optional[str]`, `deleting_id: Optional[int]`

### FlashcardTable
- Opis: tabelaryczny widok fiszek oparty na `ttk.Treeview`.
- Główne elementy: kolumny (front_preview, back_preview, actions), scrollbar.
- Obsługiwane zdarzenia: kliknięcie w komórkę akcji (ikona edit/delete) → callback
- Walidacja: brak (prezentacja danych)
- Typy: `FlashcardViewModel` z polami `id`, `front_text`, `back_text`
- Props: `items: List[FlashcardViewModel]`, `on_edit(id)`, `on_delete(id)`

### ButtonPanel
- Opis: pozioma grupa przycisków u dołu widoku.
- Elementy: `ttk.Button('Dodaj fiszkę')`, `ttk.Button('Generuj z AI')`
- Obsługiwane zdarzenia: click → odpowiedni handler przekazany z rodzica
- Walidacja: przyciski aktywne tylko gdy `!loading`
- Props: `on_add`, `on_generate_ai`, `disabled: bool`

### ConfirmationDialog
- Opis: prosty `tk.Toplevel` z komunikatem „Czy na pewno usunąć fiszkę?” i dwoma przyciskami Tak/Nie.
- Elementy: Label, Button Tak, Button Nie
- Obsługiwane zdarzenia: click Tak → confirm_callback, click Nie → close
- Walidacja: brak dodatkowej
- Props: `message`, `on_confirm`, `on_cancel`

## 5. Typy

### FlashcardViewModel
- id: int
- front_text: str  # pełny tekst frontu (do wyświetlenia w tabeli)
- back_text: str   # pełny tekst tyłu (do wyświetlenia w tabeli)

### CardListViewProps
- deck_id: int
- deck_name: str
- flashcardService: CardService
- navigation_controller: NavigationController
- show_toast(title: str, message: str): Callable

## 6. Zarządzanie stanem
- Przechowywane w instancji `CardListView`:
  - `flashcards`: lista VM
  - `loading`: bool (pokazuje spinner lub blokuje akcje)
  - `error`: Optional[str] (błąd podczas ładowania/działania)
  - `deleting_id`: Optional[int] (ID fiszki oczekującej na potwierdzenie usunięcia)

## 7. Integracja persystencji
- `flashcardService.list_by_deck_id(deck_id) -> List[Flashcard]` → mapowanie do `FlashcardViewModel`
- `flashcardService.delete(flashcard_id)` → usuwa fiszkę, po sukcesie wywołanie ponownego pobrania listy
- Inne operacje (add/edit) są realizowane w widokach formularzy, do których nawigujemy

## 8. Interakcje użytkownika
1. Otworzenie widoku → automatyczne pobranie i wyświetlenie listy fiszek.
2. Kliknięcie „Dodaj fiszkę” → przejście do FlashcardEditView (tryb tworzenia).
3. Kliknięcie „Generuj z AI” → przejście do AIReviewView.
4. Kliknięcie ikony edycji przy wierszu → FlashcardEditView (tryb edycji).
5. Kliknięcie ikony kosza → otwarcie ConfirmationDialog.
6. Potwierdzenie usunięcia → usunięcie i odświeżenie tabeli + toast.
7. Anulowanie usunięcia → zamknięcie dialogu.

## 9. Warunki i walidacja
- `deck_id` musi istnieć i należeć do aktualnego użytkownika (sprawdza DeckService przed renderem).
- ConfirmationDialog wymaga potwierdzenia przed usunięciem.
- Przycisk Dodaj/AI wyłączony podczas `loading`.

## 10. Obsługa błędów
- Błąd pobierania listy → wyświetlenie toasta z komunikatem + logowanie.
- Błąd usuwania → toast z błędem + log.
- Brak fiszek → komunikat „Brak fiszek w tej talii.” zamiast tabeli.

## 11. Kroki implementacji
1. Utworzyć serwis aplikacyjny `CardService` w `src/CardManagement/application/card_service.py`.
2. Utworzyć plik `src/CardManagement/infrastructure/ui/views/card_list_view.py`.
3. Zaimportować wymagane klasy: `ttk`, `CardService`, `NavigationController` (z `src/main.py`).
4. Zdefiniować `CardListView(ttk.Frame)`, przyjmujący `CardListViewProps`.
5. W konstruktorze:
   - Inicjalizować stan (`flashcards`, `loading`, ...).
   - Stworzyć i ułożyć HeaderBar, FlashcardTable, ButtonPanel.
   - Zarejestrować callbacki.
   - Wywołać `_load_flashcards()`.
6. Zaimplementować `_load_flashcards()`:
   - Ustaw `loading=True`, wywołaj `list_by_deck_id`, zmapuj na ViewModel, złap błędy.
   - Odśwież tabelę.
7. Zaimplementować callbacki:
   - `on_add`, `on_generate_ai`, `on_edit`, `on_delete`, `on_confirm_delete`.
8. Dodać ConfirmationDialog dla usuwania.
9. Zarejestrować widok w `main.py`:
   ```python
   card_list_view = CardListView(app_view.main_content, flashcardService=..., deck_id=..., deck_name=..., navigation_controller=..., show_toast=...)
   navigation_controller.register_view(f"/decks/{deck_id}/cards", card_list_view)
   ```
