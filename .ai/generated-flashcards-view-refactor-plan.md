## Plan Refaktoryzacji Generowania Fiszek AI

### Cel:
Zmiana przepływu użytkownika podczas przeglądania fiszek wygenerowanych przez AI. Zamiast listy wszystkich fiszek, użytkownik będzie przeglądał je pojedynczo, z możliwością edycji, zapisu lub odrzucenia każdej z nich przed przejściem do następnej.

### Krok 1: Stworzenie nowego widoku `AIReviewSingleFlashcardView`

1.  **Utwórz nowy plik** w `src/CardManagement/infrastructure/ui/views/` o nazwie np. `ai_review_single_flashcard_view.py`.
2.  **Zdefiniuj klasę `AIReviewSingleFlashcardView`** dziedziczącą po `ttk.Frame`.
3.  **Konstruktor (`__init__`):**
    *   Przyjmij argumenty: `parent`, `deck_id`, `deck_name`, `generated_flashcards_dtos: List[FlashcardDTO]`, `current_flashcard_index: int`, `ai_service: AIService`, `card_service: CardService`, `navigation_controller`, `show_toast`, `available_llm_models`, `original_source_text: str` (tekst, z którego generowano fiszki, na potrzeby przycisku "Generuj więcej" jeśli zdecydujemy się go przenieść/zachować).
    *   Zapisz te argumenty jako atrybuty instancji.
    *   Pobierz aktualną fiszkę do wyświetlenia: `current_dto = self.generated_flashcards_dtos[self.current_flashcard_index]`.
    *   Zainicjuj UI (`_init_ui()`).
4.  **Metoda `_init_ui()`:**
    *   **HeaderBar:** Wyświetl tytuł np. "Przeglądanie wygenerowanej fiszki (X/Y)" gdzie X to `current_flashcard_index + 1`, a Y to `len(generated_flashcards_dtos)`. Przycisk "Wstecz" powinien prowadzić do listy fiszek danej talii (`/decks/{self.deck_id}/cards`).
    *   **Wyświetlanie fiszki:**
        *   Etykieta "Przód:" i pole `ttk.Text` (lub `ScrolledText`) wypełnione `current_dto.front`. Pole powinno być edytowalne.
        *   Etykieta "Tył:" i pole `ttk.Text` (lub `ScrolledText`) wypełnione `current_dto.back`. Pole powinno być edytowalne.
        *   (Opcjonalnie) Wyświetl tagi, jeśli są: `current_dto.tags`.
    *   **Przyciski akcji na dole:**
        *   "Zapisz i kontynuuj": Przycisk (`ttk.Button`), który wywoła metodę `_on_save_and_continue`.
        *   "Odrzuć i kontynuuj": Przycisk (`ttk.Button`), który wywoła metodę `_on_discard_and_continue`.
        *   (Opcjonalnie, do rozważenia) Przycisk "Generuj więcej z tego samego tekstu" - jeśli chcemy zachować tę funkcjonalność z `AIGenerateView`.
5.  **Metoda `_on_save_and_continue()`:**
    *   Pobierz edytowaną treść z pól tekstowych "Przód" i "Tył".
    *   Pobierz oryginalną treść aktualnie przeglądanej fiszki (`current_dto.front`, `current_dto.back`).
    *   Ustal `source`:
        *   Jeśli edytowany przód != oryginalny przód LUB edytowany tył != oryginalny tył, `source = "ai-edited"`.
        *   W przeciwnym razie, `source = "ai-generated"`.
    *   Wywołaj `self.card_service.create_flashcard()` z:
        *   `deck_id=self.deck_id`
        *   `front_text=edytowany_przod`
        *   `back_text=edytowany_tyl`
        *   `source=ustalony_source`
        *   `ai_model_name=current_dto.metadata.get("model")` (lub inna ścieżka do nazwy modelu z `FlashcardDTO.metadata` - trzeba sprawdzić strukturę `FlashcardDTO` zwracaną przez `AIService`).
    *   Obsłuż ewentualne wyjątki z `card_service` (np. walidacja długości, błędy zapisu) i pokaż `show_toast`.
    *   Wywołaj `_proceed_to_next_flashcard()`.
6.  **Metoda `_on_discard_and_continue()`:**
    *   Wywołaj `_proceed_to_next_flashcard()`.
7.  **Metoda `_proceed_to_next_flashcard()`:**
    *   Zwiększ `self.current_flashcard_index` o 1.
    *   Jeśli `self.current_flashcard_index < len(self.generated_flashcards_dtos)`:
        *   Przejdź do nowego widoku `AIReviewSingleFlashcardView` dla następnej fiszki, przekazując wszystkie potrzebne parametry (w tym zaktualizowany `current_flashcard_index`).
        *   `self.navigation_controller.navigate_to_view(AIReviewSingleFlashcardView, deck_id=..., generated_flashcards_dtos=..., current_flashcard_index=self.current_flashcard_index, ...)` (lub podobny mechanizm nawigacji, który posiadasz).
    *   W przeciwnym razie (wszystkie fiszki przejrzane):
        *   Pokaż `show_toast` z informacją o zakończeniu przeglądania.
        *   Przejdź do widoku listy fiszek w talii: `self.navigation_controller.navigate(f"/decks/{self.deck_id}/cards")`.

### Krok 2: Modyfikacja istniejącego widoku `AIGenerateView`

1.  **W `AIGenerateView._init_ui()`:**
    *   Usuń sekcję `self.results_frame` (etykieta "Wygenerowane fiszki...", `self.flashcard_frame`, przyciski "Zapisz zaznaczone", "Generuj więcej", "Anuluj" spod listy fiszek).
    *   Przycisk "Generuj więcej" (`self.generate_more_button`) można usunąć lub przenieść logikę do `AIReviewSingleFlashcardView`, jeśli jest potrzebny.
    *   Przycisk "Anuluj" (`self.cancel_button`) spod listy fiszek można usunąć; główny przycisk "Anuluj" (`self.back_button`) obok "Generuj fiszki" powinien wystarczyć do powrotu.
2.  **W `AIGenerateView._generate_flashcards_thread()`:**
    *   Po pomyślnym wygenerowaniu fiszek (`flashcards: List[FlashcardDTO]`):
        *   Zamiast `self.after(0, lambda: self._display_flashcards(flashcards))`:
        *   Jeśli `flashcards` nie jest pusta:
            *   Wywołaj nawigację do `AIReviewSingleFlashcardView`:
                ```python
                # Wewnątrz _generate_flashcards_thread, po otrzymaniu 'flashcards'
                raw_text_for_review = raw_text # Zachowaj oryginalny tekst
                self.after(0, lambda: self.navigation_controller.navigate_to_view(
                    AIReviewSingleFlashcardView, # Załóżmy, że masz taki mechanizm
                    deck_id=self.deck_id,
                    deck_name=self.deck_name,
                    generated_flashcards_dtos=flashcards,
                    current_flashcard_index=0,
                    ai_service=self.ai_service,
                    card_service=self.card_service,
                    navigation_controller=self.navigation_controller,
                    show_toast=self.show_toast,
                    available_llm_models=self.available_llm_models,
                    original_source_text=raw_text_for_review 
                ))
                ```
            *   Jeśli nawigacja odbywa się przez zmianę ścieżki, musisz odpowiednio skonstruować parametry.
        *   Jeśli `flashcards` jest pusta:
            *   Pokaż `show_toast` z informacją, że AI nie wygenerowało żadnych fiszek.
            *   Pozostań w `AIGenerateView` lub zresetuj widok: `self.after(0, lambda: self._set_generating_state(False))`.
3.  **Usuń metody:** `_display_flashcards`, `_on_flashcard_select`, `_on_save_selected` z `AIGenerateView`.
4.  **Przejrzyj `_reset_view()`** w `AIGenerateView` - usuń odwołania do `results_frame` i powiązanych kontrolek.

### Krok 3: Modyfikacja `CardService`

1.  **W `CardService.create_flashcard()`:**
    *   Parametr `source` jest już obecny i używany. Upewnij się, że logika w `AIReviewSingleFlashcardView._on_save_and_continue()` poprawnie przekazuje `"manual"`, `"ai-generated"` lub `"ai-edited"`.
    *   Parametr `ai_model_name` jest już obecny. Upewnij się, że `AIReviewSingleFlashcardView` poprawnie go pobiera z metadanych `FlashcardDTO` i przekazuje.
    *   Logika walidacji długości tekstu (`FR-015`, `FR-021`) jest już w `create_flashcard`. Nowy widok `AIReviewSingleFlashcardView` powinien pozwolić na edycję, a `CardService` zweryfikuje ostateczną treść.
2.  **Nie jest wymagana nowa metoda w `CardService`**, o ile `create_flashcard` jest wystarczająco elastyczna.

### Krok 4: Modyfikacja `Flashcard.py` (Model Domenowy)

1.  Model `Flashcard` już posiada pola `source` i `ai_model_name`. Nie są tu potrzebne zmiany.

### Krok 5: Aktualizacja Nawigacji i Kontrolerów

1.  Upewnij się, że `NavigationController` (lub odpowiednik) potrafi obsłużyć nawigację do nowego widoku `AIReviewSingleFlashcardView` i przekazać mu niezbędne parametry. Może to wymagać dodania nowej metody do kontrolera nawigacji, np. `navigate_to_view(view_class, **kwargs)`.
2.  Jeśli używasz prezenterów, rozważ stworzenie `AIReviewSingleFlashcardPresenter` dla nowego widoku.

### Krok 6: Testowanie

1.  **Testy automatyczne (jeśli dotyczy):**
    *   Zaktualizuj istniejące testy jednostkowe dla `CardService`.
    *   Dodaj testy jednostkowe dla logiki w `AIReviewSingleFlashcardView` (jeśli jest tam logika poza UI, np. w prezenterze).
    *   Zaktualizuj testy behawioralne (Behave), aby odzwierciedlały nowy przepływ.

### Uwagi Dodatkowe:

*   **Struktura `FlashcardDTO`:** Upewnij się, że `FlashcardDTO` (zwracane przez `AIService` i przekazywane do nowego widoku) zawiera wszystkie potrzebne informacje, w tym `front`, `back`, `tags` (jeśli są) oraz metadane, z których można wyciągnąć `ai_model_name`.
*   **Obsługa błędów:** Zapewnij spójną obsługę błędów (np. problemy z API, walidacja) i informowanie użytkownika za pomocą `show_toast`.
*   **Styl i Konwencje:** Stosuj się do zasad z `python_style.mdc`, `ui_tkinter.mdc` i `architecture.mdc`.
*   **Limity znaków:** Limity znaków dla przodu (200) i tyłu (500) fiszki (FR-015, FR-021) powinny być nadal egzekwowane przez `CardService` przy zapisie. Można dodać wizualne wskazówki w UI `AIReviewSingleFlashcardView`, jeśli użytkownik zbliża się do limitu podczas edycji.
