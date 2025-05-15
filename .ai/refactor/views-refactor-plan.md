# Przewodnik Refaktoryzacji Widoków UI aplikacji 10xCards

## 1. Opis Problemu

Obecna implementacja widoków UI w aplikacji 10xCards wykazuje pewne niespójności oraz odchylenia od założonego wzorca architektonicznego Model-View-Presenter (MVP), szczególnie poza modułem `Study`. Logika biznesowa i zarządzanie stanem są często zaszyte bezpośrednio w klasach widoków, co utrudnia testowanie, konserwację i dalszy rozwój. Dodatkowo, zidentyfikowano duplikację niektórych komponentów UI (np. dialogów potwierdzenia) oraz potencjalne obszary do lepszego ujednolicenia wykorzystania biblioteki `ttkbootstrap` i jej systemów stylizacji, aby zapewnić spójny wygląd i poprawne działanie dynamicznej zmiany motywów.

Celem tej refaktoryzacji jest:
- Ujednolicenie implementacji widoków w całej aplikacji zgodnie z wzorcem MVP.
- Wydzielenie logiki biznesowej i zarządzania stanem z widoków do dedykowanych prezenterów.
- Centralizacja współdzielonych komponentów UI (widgetów, dialogów) w module `Shared`.
- Zapewnienie spójnego i efektywnego wykorzystania `ttkbootstrap` pod kątem widgetów i stylizacji, z uwzględnieniem dynamicznej zmiany motywów.
- Poprawa ogólnej czytelności, testowalności i łatwości konserwacji kodu UI.

## 2. Analiza Krytyczna Obecnego Rozwiązania

### Mocne Strony:
- Moduł `Study` (`StudySessionView` i `StudyPresenter`) stanowi dobry przykład implementacji MVP i powinien służyć jako wzór.
- Wykorzystanie `ttkbootstrap` zapewnia nowoczesny wygląd aplikacji.
- Istnienie modułu `Shared/ui/widgets` z komponentami takimi jak `HeaderBar` i `ToastContainer` to dobry początek centralizacji.
- Podstawowe struktury widoków list (np. `ProfileListView`, `CardListView` z użyciem `ttk.Treeview`) są na miejscu.
- Wstrzykiwanie zależności (serwisów, prezenterów tam gdzie są) jest stosowane.

### Obszary do Poprawy:
- **Wzorzec MVP**: Większość widoków (poza `StudySessionView`) zawiera znaczną część logiki aplikacji i zarządza własnym stanem, zamiast delegować te zadania do prezenterów.
- **Duplikacja Komponentów**: `DeleteConfirmationDialog` jest zduplikowany w `CardManagement` i `DeckManagement`.
- **Potencjał do Współdzielenia**: Tabele (`FlashcardTable`, `DeckTable`) oraz różne dialogi (np. te z `UserProfile/settings_dialogs/`) mogą posiadać wspólną logikę bazową, którą można by wydzielić.
- **Zarządzanie Stanem w Widokach**: Przechowywanie stanu (np. `_state` w `ProfileListView`, `flashcards` w `CardListView`) bezpośrednio w widokach narusza zasady MVP.
- **Bezpośrednie Wywołania Serwisów z Widoków**: Widoki często bezpośrednio komunikują się z serwisami aplikacyjnymi. W MVP ta komunikacja powinna przechodzić przez prezentera.
- **Stylizacja i `ttkbootstrap`**: Chociaż `ttkbootstrap` jest używany, istnieje pole do upewnienia się, że wszystkie widgety są w pełni "temowalne" i że niestandardowe style/czcionki nie kolidują z mechanizmem zmiany motywów. Konieczne jest konsekwentne stosowanie predefiniowanych stylów `ttkbootstrap`.
- **Nawigacja**: Logika nawigacji jest czasem inicjowana bezpośrednio z widoku. Powinna być zarządzana przez prezentera w odpowiedzi na akcje użytkownika.

## 3. Lista Zmian do Wprowadzenia (z podziałem na domeny i Shared)

### A. Moduł `Shared`

1.  **`Shared/ui/widgets/confirmation_dialog.py`**:
    *   Stworzyć nowy, generyczny `ConfirmationDialog(ttk.Toplevel)`.
    *   Parametry konstruktora: `parent`, `title`, `message`, `confirm_text`, `confirm_style` (np. "danger.TButton", "success.TButton"), `cancel_text`, `on_confirm_callback`, `on_cancel_callback`.
    *   Przyciski powinny być umieszczone zgodnie z `ui_tkinter.mdc` (akcja główna po prawej).
    *   Usunąć `DeleteConfirmationDialog` z `CardManagement` i `DeckManagement`. Zastąpić użyciem `Shared.ui.widgets.confirmation_dialog.ConfirmationDialog`.
        *   Przykład użycia: `ConfirmationDialog(self, "Usuń Talię", "Czy na pewno...", "Usuń", "danger.TButton", "Anuluj", self.presenter.confirm_delete_deck, self.presenter.cancel_delete_deck)`

2.  **`Shared/ui/widgets/base_dialog.py`** (Opcjonalnie, ale zalecane):
    *   Stworzyć `BaseDialog(ttk.Toplevel)`.
    *   Obsługa podstawowej konfiguracji okna dialogowego: `title`, `transient`, `grab_set`, centrowanie, podstawowa struktura z ramką na zawartość i ramką na przyciski ("OK", "Anuluj" lub "Zapisz", "Anuluj").
    *   Specyficzne dialogi (np. `CreateProfileDialog`, dialogi z `settings_dialogs/`) mogą dziedziczyć po `BaseDialog`.

3.  **`Shared/ui/widgets/generic_table_widget.py`** (Potencjalnie):
    *   Przeanalizować `FlashcardTable` i `DeckTable`. Jeśli istnieje wystarczająco dużo wspólnej logiki (konfiguracja `ttk.Treeview`, kolumn, nagłówków, scrollbara, podstawowe sortowanie, bindowanie zdarzeń wyboru), stworzyć `GenericTableWidget`.
    *   Mógłby on przyjmować definicje kolumn, callbacki dla akcji (np. podwójne kliknięcie, klawisz Delete).
    *   Alternatywnie, stworzyć `BaseTableWidget` z podstawową funkcjonalnością, po którym dziedziczyłyby specyficzne tabele.

4.  **`Shared/ui/styling.py`** (Opcjonalnie):
    *   Jeśli okaże się, że potrzebne są niestandardowe, dynamiczne style ponad to, co oferuje `ttkbootstrap` w prosty sposób, można tu umieścić logikę zarządzania stylami lub stałe definicje stylów. Na razie trzymać się standardowych stylów `ttkbootstrap`.

5.  **`Shared/ui/views/base_view.py`** (Opcjonalnie):
    *   Można rozważyć stworzenie `BaseView(ttk.Frame)`, która mogłaby zawierać wspólną logikę dla wszystkich widoków, np. integrację z `ToastContainer` lub standardowe metody cyklu życia (choć Tkinter nie ma ich tak rozbudowanych jak inne frameworki UI).

### B. Moduł `UserProfile`

1.  **`UserProfile/application/presenters/profile_list_presenter.py`**:
    *   Stworzyć `ProfileListPresenter`.
    *   Przeniesie stan (`ProfileListViewState`) i logikę z `ProfileListView` (`_load_profiles`, `_handle_profile_creation`, `_handle_login`, `_on_profile_selected`, `_on_profile_activated`) do tego prezentera.
    *   Prezenter będzie komunikował się z `UserProfileService` i `SessionService`.
    *   Prezenter będzie używał `Router` (lub `NavigationController`) do nawigacji.
2.  **`UserProfile/infrastructure/ui/views/profile_list_view.py`**:
    *   Uprościć widok. Powinien przyjmować `ProfileListPresenter` w konstruktorze.
    *   Zdefiniować i implementować interfejs (np. `IProfileListView`) dla komunikacji Prezenter -> Widok (np. `display_profiles`, `show_error`, `enable_login_button`).
    *   Metody obsługi zdarzeń (`_on_...`) powinny jedynie wywoływać metody na prezenterze.
3.  **`UserProfile/application/presenters/settings_presenter.py`**:
    *   Stworzyć `SettingsPresenter`.
    *   Przeniesie stan (`settings_model`) i logikę z `SettingsView` (np. `refresh_settings`, `_on_username_changed`, `_on_password_changed`, `_on_api_key_changed` etc.) do tego prezentera. Logika obsługi poszczególnych dialogów (np. zmiany nazwy użytkownika) również powinna być koordynowana przez ten prezenter.
    *   Prezenter będzie komunikował się z `UserProfileService`, `SessionService`, `OpenRouterAPIClient` (dla walidacji klucza).
4.  **`UserProfile/infrastructure/ui/views/settings_view.py`**:
    *   Uprościć widok. Powinien przyjmować `SettingsPresenter`.
    *   Zdefiniować i implementować interfejs (np. `ISettingsView`) dla komunikacji Prezenter -> Widok (np. `display_settings`, `show_api_key_masked`, `update_available_llms_themes`).
    *   Otwieranie dialogów powinno być inicjowane przez prezentera, lub widok może otwierać dialog, ale wynik przekazywać do prezentera. Preferowane jest, aby prezenter koordynował przepływ.
    *   Dialogi w `settings_dialogs/` (np. `ChangeUsernameDialog`, `ManagePasswordDialog`, `APIKeyDialog`, `SelectLLMModelDialog`, `SelectThemeDialog`):
        *   Każdy z tych dialogów powinien być jak najprostszy. Jeśli mają logikę walidacji lub komunikacji z serwisami, ta logika powinna być w `SettingsPresenter` lub w dedykowanych "sub-prezenterach/handlerach" zarządzanych przez `SettingsPresenter`.
        *   Rozważyć użycie `Shared.ui.widgets.BaseDialog` jeśli został stworzony.
5.  **Ujednolicenie Stylów**: Przejrzeć wszystkie widgety pod kątem spójnego użycia stylów `ttkbootstrap`.

### C. Moduł `CardManagement`

1.  **`CardManagement/application/presenters/card_list_presenter.py`**:
    *   Stworzyć `CardListPresenter`.
    *   Przeniesie stan (`flashcards`, `loading`, `error`, `deleting_id`, `dialog_open`) i logikę z `CardListView` (`load_flashcards`, `_on_edit_flashcard`, `_on_delete_flashcard`, `_handle_flashcard_deletion` etc.) do tego prezentera.
    *   Prezenter będzie komunikował się z `CardService`.
2.  **`CardManagement/infrastructure/ui/views/card_list_view.py`**:
    *   Uprościć widok. Powinien przyjmować `CardListPresenter`.
    *   Zdefiniować i implementować interfejs (np. `ICardListView`) dla komunikacji Prezenter -> Widok.
    *   Zaktualizować użycie `DeleteConfirmationDialog` na współdzieloną wersję.
    *   `FlashcardTable` i `ButtonPanel` - ich interakcje (callbacki) powinny być podłączone do metod prezentera.
3.  **Pozostałe widoki (`FlashcardEditView`, `AIGenerateView`, `AIReviewSingleFlashcardView`)**:
    *   Dla każdego z nich stworzyć odpowiedniego prezentera i zastosować wzorzec MVP analogicznie jak dla `CardListView`.
4.  **`CardManagement/infrastructure/ui/widgets/flashcard_table.py`**:
    *   Jeśli powstanie `GenericTableWidget` w `Shared`, dostosować `FlashcardTable` do jego użycia lub dziedziczenia. W przeciwnym razie, upewnić się, że jest spójny ze standardami.
5.  **Ujednolicenie Stylów**: Przejrzeć wszystkie widgety.

### D. Moduł `DeckManagement`

1.  **`DeckManagement/application/presenters/deck_list_presenter.py`**:
    *   Stworzyć `DeckListPresenter`.
    *   Przenieść logikę i stan z `DeckListView` do tego prezentera (analogicznie do `CardListPresenter`).
    *   Komunikacja z `DeckService`.
2.  **`DeckManagement/infrastructure/ui/views/deck_list_view.py`**:
    *   Uprościć widok, przyjmować `DeckListPresenter`. Implementować interfejs widoku.
    *   Zaktualizować użycie `DeleteConfirmationDialog` na współdzieloną wersję.
3.  **Widgety (`DeckTable`, `CreateDeckDialog`)**:
    *   `DeckTable`: Analogicznie do `FlashcardTable`, rozważyć użycie `GenericTableWidget`.
    *   `CreateDeckDialog`: Rozważyć użycie `BaseDialog` jeśli istnieje. Logika tworzenia talii powinna być w `DeckListPresenter`.
4.  **Ujednolicenie Stylów**: Przejrzeć wszystkie widgety.

### E. Moduł `Study`

1.  **`StudySessionView` i `StudyPresenter`**:
    *   Ta para jest już blisko ideału. Przejrzeć ją pod kątem ewentualnych drobnych uspójnień ze zmianami wprowadzanymi w innych modułach (np. jeśli `HeaderBar` zostanie zmodyfikowany, czy użycie stylów).
    *   Upewnić się, że obsługa błędów przez `Messagebox.show_error` jest spójna z globalnym mechanizmem (np. `ToastContainer` dla mniej krytycznych błędów, `Messagebox` dla blokujących).

## 4. Obsługa Błędów

-   **Toast Notifications (`Shared.ui.widgets.toast_container.ToastContainer`)**:
    *   Używać do informowania użytkownika o wynikach operacji (sukces, informacja, drobny błąd nieblokujący).
    *   Inicjowanie toastów powinno być zlecane przez prezentery (np. `view.show_toast("Sukces", "Talia została utworzona")`).
-   **Messagebox (`ttkbootstrap.dialogs.Messagebox`)**:
    *   Używać do krytycznych błędów, które wymagają uwagi użytkownika lub gdy operacja nie może być kontynuowana (np. błąd ładowania kluczowych danych, błąd walidacji API Key uniemożliwiający zapis).
    *   Wywołania `Messagebox` również powinny być inicjowane przez prezentery.
-   **Walidacja Formularzy**:
    *   Walidacja danych wejściowych (np. w dialogach tworzenia/edycji, polach tekstowych) powinna odbywać się w prezenterach.
    *   Widok może wyświetlać informacje o błędach walidacji (np. podświetlając pole, pokazując komunikat obok pola) na podstawie informacji od prezentera.
-   **Logowanie**:
    *   Kontynuować logowanie błędów z tracebackami na poziomie serwisów i prezenterów.
    *   Logować kluczowe akcje użytkownika inicjowane w prezenterach.

## 5. Kwestie Ryzyka

1.  **Duży Zakres Zmian (MVP)**:
    *   **Ryzyko**: Wprowadzenie MVP do wielu widoków jednocześnie jest czasochłonne i może prowadzić do błędów trudnych do wyśledzenia.
    *   **Łagodzenie**: Przeprowadzać refaktoryzację moduł po module lub nawet widok po widoku. Stosować częste, małe commity. Pisać testy jednostkowe dla prezenterów.
2.  **Interfejsy Współdzielonych Komponentów**:
    *   **Ryzyko**: Niewłaściwie zaprojektowany interfejs współdzielonego komponentu (np. `ConfirmationDialog`) może nie pasować do wszystkich przypadków użycia lub być trudny w użyciu.
    *   **Łagodzenie**: Dokładnie przeanalizować wymagania przed implementacją. Zacząć od prostego interfejsu i rozszerzać w razie potrzeby.
3.  **Regresje Funkcjonalne**:
    *   **Ryzyko**: Zmiany w logice i przepływie danych mogą wprowadzić nowe błędy w działających częściach aplikacji.
    *   **Łagodzenie**: Staranne testowanie manualne każdej zrefaktoryzowanej części. Jeśli istnieją testy automatyczne, zaktualizować je i upewnić się, że przechodzą. Rozważyć pisanie testów behawioralnych dla kluczowych przepływów.
4.  **Styling i `ttkbootstrap`**:
    *   **Ryzyko**: Niespójności wizualne lub problemy z dynamiczną zmianą motywów, jeśli style nie zostaną poprawnie zastosowane.
    *   **Łagodzenie**: Testować każdy zrefaktoryzowany widok/widget z różnymi motywami `ttkbootstrap`. Stworzyć listę kontrolną standardowych stylów.
5.  **Aktualizacja Testów**:
    *   **Ryzyko**: Jeśli istnieją testy UI, będą wymagały znaczących modyfikacji.
    *   **Łagodzenie**: Zaplanować czas na aktualizację testów jako część refaktoryzacji.

## 6. Plan Wdrożenia Krok po Kroku

Zaleca się podejście iteracyjne, moduł po module.

**Faza 1: Przygotowanie Fundamentów (`Shared`)**

1.  **Implementacja `Shared.ui.widgets.confirmation_dialog.ConfirmationDialog`**:
    *   Stwórz klasę `ConfirmationDialog`.
    *   Zaimplementuj logikę wyświetlania, przycisków i callbacków.
    *   Napisz proste testy (jeśli to możliwe w izolacji) lub przykłady użycia.
2.  **(Opcjonalnie) Implementacja `Shared.ui.widgets.base_dialog.BaseDialog`**:
    *   Jeśli zdecydujesz się na ten krok, zaimplementuj podstawową funkcjonalność.
3.  **(Opcjonalnie) Implementacja `Shared.ui.widgets.generic_table_widget.GenericTableWidget` lub `BaseTableWidget`**:
    *   Przeanalizuj tabele i zdecyduj o poziomie abstrakcji. Zaimplementuj.

**Faza 2: Refaktoryzacja Modułu (np. `DeckManagement`)**

Przykład dla `DeckManagement`:

1.  **Stwórz `DeckManagement/application/presenters/deck_list_presenter.py`**:
    *   Zdefiniuj `DeckListPresenter` i interfejs `IDeckListView`.
    *   Przenieś logikę i zarządzanie stanem z `DeckListView` do prezentera.
    *   Prezenter powinien obsługiwać ładowanie talii, tworzenie nowej talii (koordynacja z `CreateDeckDialog`), usuwanie talii (koordynacja z `ConfirmationDialog`), wybór talii i nawigację.
2.  **Zrefaktoryzuj `DeckManagement/infrastructure/ui/views/deck_list_view.py`**:
    *   Widok przyjmuje `DeckListPresenter` i implementuje `IDeckListView`.
    *   Usuń starą logikę. Zdarzenia UI (kliknięcia przycisków, wybór z listy) deleguj do prezentera.
    *   Dane do wyświetlenia (lista talii) pobieraj od prezentera poprzez metody interfejsu.
3.  **Zrefaktoryzuj `DeckManagement/infrastructure/ui/widgets/create_deck_dialog.py`**:
    *   Dialog powinien być jak najprostszy. Może przyjmować callback od prezentera, który zostanie wywołany z nową nazwą talii.
    *   Logika walidacji i tworzenia talii powinna być w `DeckListPresenter`.
    *   Rozważ użycie `BaseDialog`.
4.  **Zrefaktoryzuj `DeckManagement/infrastructure/ui/widgets/deck_table.py`**:
    *   Jeśli stworzono `GenericTableWidget`, użyj go. W przeciwnym razie, upewnij się, że widget jest spójny ze standardami. Interakcje (np. wybór) powinny być komunikowane do `DeckListPresenter`.
5.  **Zastąp `DeleteConfirmationDialog`**: Użyj `Shared.ui.widgets.confirmation_dialog.ConfirmationDialog`, wywołując go z poziomu `DeckListPresenter`.
6.  **Testowanie**: Manualnie przetestuj wszystkie funkcje zarządzania taliami.

**Faza 3: Refaktoryzacja Kolejnych Modułów**

Powtórz kroki z Fazy 2 dla:
-   `CardManagement` (obejmuje `CardListView`, `FlashcardEditView`, `AIGenerateView`, `AIReviewSingleFlashcardView` oraz ich widgety i dialogi).
-   `UserProfile` (obejmuje `ProfileListView`, `SettingsView` oraz dialogi w `settings_dialogs/`).

**Faza 4: Refaktoryzacja Modułu `Study` (Przegląd i Uspójnienie)**

1.  Przejrzyj `StudySessionView` i `StudyPresenter`.
2.  Upewnij się, że użycie `HeaderBar`, stylów `ttkbootstrap`, oraz sposób komunikacji z prezenterem są spójne z nowo wprowadzonymi standardami w innych modułach.
3.  Sprawdź, czy obsługa błędów jest spójna.

**Faza 5: Ujednolicenie Stylów i `ttkbootstrap` Globalnie**

1.  Po zrefaktoryzowaniu wszystkich modułów, wykonaj globalny przegląd:
    *   Czy wszystkie widgety używają stylów `ttkbootstrap` (np. `primary.TButton`) zamiast hardkodowanych wartości tam, gdzie to możliwe?
    *   Czy czcionki i paddingi są spójne?
    *   Przetestuj dynamiczną zmianę motywów (FR-063) we wszystkich częściach aplikacji.
2.  Stwórz (jeśli jeszcze nie istnieje) dokumentację lub listę kontrolną standardowych stylów używanych w projekcie.

**Faza 6: Testowanie Końcowe i Dokumentacja**

1.  Przeprowadź kompleksowe testy manualne całej aplikacji.
2.  Zaktualizuj wszelką dokumentację deweloperską dotyczącą architektury UI.
3.  Jeśli są testy automatyczne, upewnij się, że wszystkie są zaktualizowane i przechodzą.

### Kluczowe Metody i Funkcje (Przykłady Implementacji)

*   **Interfejs Widoku (Protokół lub ABC)**:
    ```python
    # In presenter file or a dedicated interfaces file
    from typing import Protocol, List
    # from ...domain.models.some_model import SomeViewModel # Example

    class IMyView(Protocol):
        def display_items(self, items: List[SomeViewModel]) -> None: ...
        def show_loading(self, is_loading: bool) -> None: ...
        def show_error_message(self, message: str) -> None: ...
        # ... inne metody aktualizacji UI
    ```

*   **Konstruktor Prezentera**:
    ```python
    # In application/presenters/my_presenter.py
    class MyPresenter:
        def __init__(self, view: IMyView, some_service: SomeService, navigation_controller: NavigationController):
            self._view = view
            self._some_service = some_service
            self._navigation_controller = navigation_controller
            self._state = ... # Internal state of the presenter

        def load_data(self):
            self._view.show_loading(True)
            try:
                items = self._some_service.get_items()
                # Process items into view models if necessary
                self._view.display_items(items)
            except Exception as e:
                self._view.show_error_message(str(e))
            finally:
                self._view.show_loading(False)

        def handle_item_selected(self, item_id: int):
            # ... logic for item selection
            self._navigation_controller.navigate(f"/details/{item_id}")
    ```

*   **Widok Implementujący Interfejs**:
    ```python
    # In infrastructure/ui/views/my_view.py
    class MyView(ttk.Frame, IMyView): # Implement the interface
        def __init__(self, parent, presenter: MyPresenter): # Inject presenter
            super().__init__(parent)
            self._presenter = presenter
            self._setup_widgets()
            # Request initial data load
            self._presenter.load_data()

        def _setup_widgets(self):
            # ...
            # self.my_button = ttk.Button(self, text="Action", command=self._on_action_button_click)
            # ...

        def _on_action_button_click(self):
            self._presenter.handle_some_action() # Delegate to presenter

        # Implementation of IMyView methods
        def display_items(self, items: List[SomeViewModel]) -> None:
            # Logic to update Treeview or other widgets
            pass

        def show_loading(self, is_loading: bool) -> None:
            # Show/hide loading indicator
            pass

        def show_error_message(self, message: str) -> None:
            # Display error using toast or messagebox
            pass
    ```

*   **Użycie `ConfirmationDialog` z Prezentera**:
    ```python
    # In a presenter
    def attempt_delete_item(self, item_id: int, item_name: str):
        self._item_to_delete_id = item_id # Store for callback
        # Assuming self._view has a method to show the dialog, or presenter creates it directly
        # This part depends on how dialogs are shown (view method vs. presenter creating Toplevel)
        # If view shows it:
        self._view.show_delete_confirmation(
            item_name, 
            self._confirm_delete_item, 
            self._cancel_delete_item
        )

    def _confirm_delete_item(self):
        if self._item_to_delete_id is not None:
            # ... call service to delete
            # self._view.show_toast("Success", "Item deleted")
            # self.load_data() # Refresh
            pass
        self._item_to_delete_id = None

    def _cancel_delete_item(self):
        self._item_to_delete_id = None
        # self._view.show_toast("Info", "Deletion cancelled")

    # In the view (if view is responsible for creating dialog instance):
    # def show_delete_confirmation(self, item_name, on_confirm, on_cancel):
    #    dialog = ConfirmationDialog(
    #        self, "Potwierdź Usunięcie", f"Czy na pewno usunąć '{item_name}'?",
    #        "Usuń", "danger.TButton", "Anuluj",
    #        on_confirm, on_cancel
    #    )
    #    dialog.show() # Or however it's displayed
    ```
