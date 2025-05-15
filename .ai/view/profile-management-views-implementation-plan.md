# Plan implementacji widoków Zarządzania Profilami

## 1. Przegląd
Ten dokument opisuje plan implementacji dla dwóch powiązanych widoków w aplikacji 10xCards:
1.  **ProfileListView**: Główny ekran startowy aplikacji, wyświetlający listę istniejących profili użytkowników, umożliwiający wybór profilu do zalogowania lub zainicjowanie tworzenia nowego profilu.
2.  **ProfileLoginView**: Widok wyświetlany po wybraniu profilu chronionego hasłem, służący do wprowadzenia hasła i weryfikacji tożsamości użytkownika.

Celem jest umożliwienie użytkownikom zarządzania swoimi profilami i bezpiecznego logowania się do aplikacji, zgodnie z wymaganiami PRD i User Stories (US-001, US-002, US-004). Widoki będą zbudowane przy użyciu Tkinter i ttkbootstrap, integrując się z istniejącą warstwą persystencji poprzez dedykowane serwisy aplikacyjne.

## 2. Routing widoku
-   **ProfileListView**: Dostępny pod główną ścieżką aplikacji przy starcie (np. `/profiles`). Powinien być to domyślny widok.
-   **ProfileLoginView**: Dostępny po wybraniu chronionego hasłem profilu z `ProfileListView` (np. `/profiles/login`). Wymaga przekazania informacji o wybranym profilu (`user_id`, `username`).

Nawigacja między widokami będzie zarządzana przez centralny komponent Router/ViewManager.

## 3. Struktura komponentów

```
App / Router
  ├── ToastContainer (współdzielony komponent do powiadomień)
  └── MainContentArea (Frame do przełączania widoków)
      ├── ProfileListView (`/profiles`)
      │   ├── TitleLabel (np. "Wybierz profil")
      │   ├── ProfileList (ttk.Treeview)
      │   └── ButtonBar (Frame)
      │       └── AddProfileButton (ttk.Button -> otwiera CreateProfileDialog)
      │
      ├── ProfileLoginView (`/profiles/login`)
      │   ├── TitleLabel (np. "Zaloguj do profilu: [username]")
      │   ├── PasswordEntryFrame (Frame)
      │   │   ├── PasswordLabel (ttk.Label "Hasło:")
      │   │   └── PasswordInput (ttk.Entry show="*")
      │   └── ButtonBar (Frame)
      │       ├── LoginButton (ttk.Button "Zaloguj")
      │       └── CancelButton (ttk.Button "Anuluj")
      │
      └── CreateProfileDialog (Toplevel - okno modalne, nie w MainContentArea)
          ├── PromptLabel (ttk.Label "Podaj nazwę nowego profilu:")
          ├── UsernameInput (ttk.Entry)
          ├── ErrorLabel (ttk.Label, do wyświetlania błędów walidacji)
          └── ButtonBar (Frame)
              ├── CreateButton (ttk.Button "Utwórz")
              └── CancelButton (ttk.Button "Anuluj")
```

## 4. Szczegóły komponentów

### `ProfileListView` (ttk.Frame)
-   **Opis:** Główny kontener widoku listy profili. Odpowiedzialny za pobranie listy profili, wyświetlenie ich za pomocą `ProfileList` i obsługę nawigacji (do `ProfileLoginView` lub `DeckListView`) oraz inicjowanie tworzenia nowego profilu.
-   **Główne elementy:** `TitleLabel`, `ProfileList` (Treeview), `ButtonBar` z `AddProfileButton`.
-   **Obsługiwane interakcje:**
    -   Pobranie i wyświetlenie listy profili przy załadowaniu widoku.
    -   Odbieranie zdarzenia wyboru profilu z `ProfileList`.
    -   Odbieranie zdarzenia kliknięcia `AddProfileButton`.
    -   Nawigowanie do odpowiedniego widoku na podstawie wybranego profilu lub akcji.
    -   Wyświetlanie powiadomień (Toast) o sukcesie/błędzie tworzenia profilu.
-   **Obsługiwana walidacja:** Brak (delegowana do `CreateProfileDialog` i serwisu aplikacyjnego).
-   **Typy:** `ProfileListViewState`, `UserProfileSummaryViewModel`.
-   **Properties:** `router` (instancja klasy Router/ViewManager do nawigacji), `profile_service` (instancja serwisu aplikacyjnego do operacji na profilach).

### `ProfileList` (ttk.Treeview)
-   **Opis:** Wyświetla listę profili użytkowników w formie tabeli (lub listy). Pokazuje nazwę użytkownika i ikonę kłódki, jeśli profil jest chroniony hasłem. Umożliwia wybór profilu.
-   **Główne elementy:** Skonfigurowany `ttk.Treeview` z kolumnami "Nazwa użytkownika" i "Chroniony". Użycie obrazka kłódki (`PhotoImage`) dla profili chronionych.
-   **Obsługiwane interakcje:**
    -   Wybór pojedynczego wiersza myszką (`<ButtonRelease-1>`, `<<TreeviewSelect>>`).
    -   Wybór wiersza klawiaturą (strzałki góra/dół).
    -   Aktywacja wybranego wiersza (podwójne kliknięcie `<Double-1>`, klawisz Enter `<Return>`).
    -   Emituje zdarzenie `profile_selected` z `UserProfileSummaryViewModel` wybranego profilu do rodzica (`ProfileListView`).
-   **Obsługiwana walidacja:** Brak.
-   **Typy:** Przyjmuje `List[UserProfileSummaryViewModel]`.
-   **Properties:** `profiles: List[UserProfileSummaryViewModel]`.

### `AddProfileButton` (ttk.Button wewnątrz `ButtonBar`)
-   **Opis:** Przycisk inicjujący proces tworzenia nowego profilu.
-   **Główne elementy:** `ttk.Button` z tekstem "Dodaj nowy profil".
-   **Obsługiwane interakcje:** Kliknięcie (`<Button-1>`, `command`). Emituje zdarzenie `add_profile_requested` do rodzica (`ProfileListView`).
-   **Obsługiwana walidacja:** Brak.
-   **Typy:** Brak.
-   **Properties:** Brak.

### `CreateProfileDialog` (tkinter.Toplevel)
-   **Opis:** Modalne okno dialogowe do wprowadzania nazwy nowego profilu.
-   **Główne elementy:** `PromptLabel`, `UsernameInput` (Entry), `ErrorLabel`, `ButtonBar` z `CreateButton` i `CancelButton`.
-   **Obsługiwane interakcje:**
    -   Wprowadzanie tekstu w `UsernameInput`.
    -   Kliknięcie `CreateButton`: Waliduje nazwę (niepusta, <= 30 znaków). Jeśli poprawna, emituje zdarzenie `profile_create_confirmed` z wprowadzoną nazwą do `ProfileListView` i zamyka dialog.
    -   Kliknięcie `CancelButton` lub zamknięcie okna: Zamyka dialog bez wysyłania zdarzenia.
    -   Klawisz Enter w `UsernameInput`: Traktowany jak kliknięcie `CreateButton`.
    -   Klawisz Escape: Traktowany jak kliknięcie `CancelButton`.
-   **Obsługiwana walidacja:**
    -   Nazwa nie może być pusta.
    -   Nazwa nie może przekraczać 30 znaków.
    -   *Walidacja unikalności jest wykonywana przez serwis aplikacyjny po otrzymaniu nazwy.*
-   **Typy:** `CreateProfileDialogState`.
-   **Properties:** Brak (jest to okno Toplevel).

### `ProfileLoginView` (ttk.Frame)
-   **Opis:** Główny kontener widoku logowania hasłem. Wyświetla nazwę profilu, pole do wpisania hasła i przyciski akcji.
-   **Główne elementy:** `TitleLabel`, `PasswordEntryFrame`, `ButtonBar` z `LoginButton` i `CancelButton`.
-   **Obsługiwane interakcje:**
    -   Odbieranie zdarzenia `login_attempted` z `LoginButton`.
    -   Wywołanie serwisu aplikacyjnego w celu weryfikacji hasła.
    *   Odbieranie zdarzenia `cancel_login` z `CancelButton`.
    -   Nawigowanie do `DeckListView` (sukces) lub wyświetlanie błędu (porażka) za pomocą `ToastContainer` lub dedykowanej etykiety błędu.
    -   Nawigowanie z powrotem do `ProfileListView` po anulowaniu.
-   **Obsługiwana walidacja:** Brak (delegowana do serwisu aplikacyjnego).
-   **Typy:** `ProfileLoginViewState`, `UserProfileSummaryViewModel`.
-   **Properties:** `router`, `profile_service`, `profile_to_login: UserProfileSummaryViewModel` (lub `user_id` i `username`).

### `PasswordEntryFrame` (ttk.Frame)
-   **Opis:** Komponent zawierający etykietę i pole do wprowadzania hasła.
-   **Główne elementy:** `PasswordLabel`, `PasswordInput` (`ttk.Entry(show="*")`).
-   **Obsługiwane interakcje:**
    -   Automatyczne ustawienie fokusa na `PasswordInput` przy pojawieniu się widoku.
    -   Klawisz Enter w `PasswordInput`: Emituje zdarzenie `login_attempted` do rodzica (`ProfileLoginView`).
    -   Udostępnia metodę `get_password()` zwracającą wprowadzoną wartość.
-   **Obsługiwana walidacja:** Brak.
-   **Typy:** Brak.
-   **Properties:** Brak.

### `LoginButton` (ttk.Button wewnątrz `ButtonBar`)
-   **Opis:** Przycisk inicjujący próbę zalogowania.
-   **Główne elementy:** `ttk.Button` z tekstem "Zaloguj".
-   **Obsługiwane interakcje:** Kliknięcie (`<Button-1>`, `command`). Emituje zdarzenie `login_attempted` do rodzica (`ProfileLoginView`).
-   **Obsługiwana walidacja:** Brak.
-   **Typy:** Brak.
-   **Properties:** Brak.

### `CancelButton` (ttk.Button wewnątrz `ButtonBar`)
-   **Opis:** Przycisk do anulowania logowania i powrotu do listy profili.
-   **Główne elementy:** `ttk.Button` z tekstem "Anuluj".
-   **Obsługiwane interakcje:** Kliknięcie (`<Button-1>`, `command`). Emituje zdarzenie `cancel_login` do rodzica (`ProfileLoginView`).
-   **Obsługiwana walidacja:** Brak.
-   **Typy:** Brak.
-   **Properties:** Brak.

## 5. Typy

-   **`UserProfileSummaryViewModel`**:
    ```python
    from dataclasses import dataclass

    @dataclass
    class UserProfileSummaryViewModel:
        id: int
        username: str
        is_password_protected: bool
    ```
-   **`ProfileListViewState`**:
    ```python
    from dataclasses import dataclass, field
    from typing import List, Optional

    @dataclass
    class ProfileListViewState:
        profiles: List[UserProfileSummaryViewModel] = field(default_factory=list)
        selected_profile_id: Optional[int] = None
        is_loading: bool = False
        error_message: Optional[str] = None # Błąd ładowania listy
    ```
-   **`CreateProfileDialogState`**:
    ```python
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class CreateProfileDialogState:
        username_input: str = ""
        error_message: Optional[str] = None # Błędy walidacji: pusty, za długi, istnieje
    ```
-   **`ProfileLoginViewState`**:
    ```python
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class ProfileLoginViewState:
        user_id: int
        username: str
        password_input: str = ""
        is_logging_in: bool = False
        error_message: Optional[str] = None # Błąd: nieprawidłowe hasło
    ```
-   **Domain Model (`User`)**: Zgodnie z `src/UserProfile/domain/models/user.py` (używany przez serwis aplikacyjny i repozytorium).

## 6. Zarządzanie stanem

-   Stan dla każdego widoku (`ProfileListView`, `ProfileLoginView`) i dialogu (`CreateProfileDialog`) będzie zarządzany wewnątrz odpowiednich klas tych komponentów.
-   Zostaną użyte proste zmienne instancyjne (np. przechowujące `ProfileListViewState`).
-   Zmiany stanu (np. załadowanie listy profili, wpisanie hasła) będą prowadzić do bezpośrednich aktualizacji odpowiednich widgetów (np. `ProfileList.populate(new_profiles)`, `PasswordInput.delete(0, 'end')`).
-   Tkinter Variables (`StringVar`, `BooleanVar`) mogą być użyte dla prostszych powiązań (np. `UsernameInput` w dialogu).
-   Komunikacja między komponentami będzie odbywać się za pomocą emisji zdarzeń (np. przez `widget.event_generate()`) lub bezpośredniego wywoływania metod rodzica/dziecka (jeśli struktura jest prosta).

## 7. Integracja persystencji

Integracja z warstwą persystencji odbędzie się **wyłącznie** poprzez dedykowany **Serwis Aplikacyjny** (np. `UserProfileService`), który będzie wstrzykiwany do widoków (`ProfileListView`, `ProfileLoginView`). Serwis ten będzie używał `IUserRepository`.

-   **Ładowanie listy profili (`ProfileListView`)**:
    -   **Wywołanie:** `profile_service.get_all_profiles_summary()`
    -   **Serwis:** Wywołuje `user_repository.list_all()`. Mapuje `List[User]` na `List[UserProfileSummaryViewModel]`, sprawdzając `user.hashed_password is not None` dla `is_password_protected`.
    -   **Typy:** Żądanie: brak. Odpowiedź (serwis): `List[UserProfileSummaryViewModel]`. Odpowiedź (repo): `List[User]`.
-   **Tworzenie profilu (`CreateProfileDialog` -> `ProfileListView`)**:
    -   **Wywołanie:** `profile_service.create_profile(username: str)`
    -   **Serwis:** Tworzy `User(username=username)`. Wywołuje `user_repository.add(user)`. Obsługuje `UsernameAlreadyExistsError`, `InvalidUserDataError`.
    -   **Typy:** Żądanie: `username: str`. Odpowiedź (serwis): `UserProfileSummaryViewModel` (nowo utworzony) lub wyjątek. Odpowiedź (repo): `User` lub wyjątek.
-   **Logowanie (`ProfileLoginView`)**:
    -   **Wywołanie:** `profile_service.authenticate_user(user_id: int, password: str)`
    -   **Serwis:** Wywołuje `user_repository.get_by_id(user_id)`. Jeśli użytkownik istnieje i ma hasło, porównuje `password` z `user.hashed_password` używając `bcrypt.checkpw()`. Zwraca `True` przy sukcesie, `False` przy błędnym haśle. Może rzucić `UserNotFoundError`.
    -   **Typy:** Żądanie: `user_id: int`, `password: str`. Odpowiedź (serwis): `bool` lub wyjątek.

Widoki muszą być przygotowane na obsługę wyjątków propagowanych przez serwis (np. `UsernameAlreadyExistsError`, `UserNotFoundError`, `RepositoryError`) i wyświetlanie odpowiednich komunikatów użytkownikowi.

## 8. Interakcje użytkownika

-   **Uruchomienie aplikacji:** Wyświetla `ProfileListView` z listą profili.
-   **Kliknięcie "Dodaj nowy profil":** Otwiera `CreateProfileDialog`.
-   **Wpisanie nazwy w dialogu, kliknięcie "Utwórz":**
    -   *Sukces:* Dialog znika, lista w `ProfileListView` odświeża się, pojawia się toast "Profil [nazwa] utworzony".
    -   *Błąd (walidacja):* Komunikat błędu w dialogu (np. "Nazwa nie może być pusta").
    -   *Błąd (istnieje):* Komunikat błędu w dialogu lub toast ("Nazwa profilu [nazwa] już istnieje").
-   **Kliknięcie "Anuluj" w dialogu:** Dialog znika.
-   **Wybór profilu bez hasła w `ProfileList` (klik/Enter):** Przejście do widoku `DeckListView` dla wybranego `user_id`.
-   **Wybór profilu z hasłem w `ProfileList` (klik/Enter):** Przejście do `ProfileLoginView` dla wybranego `user_id` i `username`.
-   **Wpisanie hasła w `ProfileLoginView`, kliknięcie "Zaloguj" (lub Enter):**
    -   *Sukces:* Przejście do widoku `DeckListView` dla tego `user_id`.
    -   *Błąd:* Komunikat w `ProfileLoginView` ("Nieprawidłowe hasło."), pole hasła wyczyszczone.
-   **Kliknięcie "Anuluj" w `ProfileLoginView`:** Powrót do `ProfileListView`.
-   **Nawigacja klawiaturą w `ProfileList`:** Strzałki zmieniają wybór, Enter aktywuje.
-   **Nawigacja klawiaturą w dialogach/login:** Tab przełącza pola, Enter aktywuje domyślny przycisk, Escape anuluje.

## 9. Warunki i walidacja

-   **Ładowanie listy profili (`ProfileListView`):**
    -   Warunek: Połączenie z bazą danych musi być aktywne.
    -   Walidacja: Brak po stronie UI. Błędy połączenia/repozytorium obsługiwane globalnie lub przez widok.
-   **Tworzenie profilu (`CreateProfileDialog`, `ProfileListView`):**
    -   Warunek (UI): Nazwa profilu niepusta.
    -   Walidacja (UI): Długość nazwy <= 30 znaków. Wyświetlenie błędu w dialogu.
    -   Warunek (Serwis): Nazwa profilu musi być unikalna (`UNIQUE constraint`).
    -   Walidacja (Serwis): Rzuca `UsernameAlreadyExistsError`. Widok (`ProfileListView`) obsługuje wyjątek i wyświetla błąd (toast/dialog).
-   **Logowanie (`ProfileLoginView`):**
    -   Warunek (UI): Pole hasła nie musi być sprawdzane pod kątem pustki (serwis to obsłuży).
    -   Walidacja (UI): Brak.
    -   Warunek (Serwis): Podane hasło musi pasować do hasha zapisanego dla `user_id`.
    -   Walidacja (Serwis): Zwraca `False` lub rzuca wyjątek. Widok (`ProfileLoginView`) wyświetla błąd "Nieprawidłowe hasło.".
    -   Warunek (Serwis): Użytkownik o podanym `user_id` musi istnieć.
    -   Walidacja (Serwis): Rzuca `UserNotFoundError`. Widok powinien obsłużyć (np. powrót do listy z błędem).

Komunikaty o błędach powinny być jasne i zwięzłe, wyświetlane za pomocą `ToastContainer` lub dedykowanych etykiet w odpowiednich komponentach.

## 10. Obsługa błędów

-   **Błędy połączenia z DB (`DatabaseConnectionError`, `RepositoryError`):**
    -   Podczas ładowania listy: Wyświetlić błąd w `ProfileListView` (np. "Nie można załadować profili. Błąd bazy danych.") i ewentualnie zablokować interakcje.
    -   Podczas tworzenia/logowania: Wyświetlić generyczny błąd toast ("Wystąpił błąd bazy danych."). Zalogować szczegóły.
-   **Nazwa profilu istnieje (`UsernameAlreadyExistsError`):**
    -   Wyświetlić błąd w `CreateProfileDialog` ("Nazwa profilu już istnieje.") lub toast po próbie utworzenia. Zapobiec zamknięciu dialogu lub powrócić do niego.
-   **Nieprawidłowa nazwa profilu (pusta, za długa):**
    -   Wyświetlić błąd bezpośrednio w `CreateProfileDialog` przy próbie utworzenia. Zapobiec wysłaniu do serwisu.
-   **Nieprawidłowe hasło:**
    -   Wyświetlić błąd w `ProfileLoginView` ("Nieprawidłowe hasło."). Wyczyścić pole hasła. Pozwolić na ponowną próbę.
-   **Użytkownik nie znaleziony (`UserNotFoundError`):**
    -   Podczas logowania (nie powinno się zdarzyć przy poprawnej nawigacji): Wyświetlić generyczny błąd toast i wrócić do `ProfileListView`. Zalogować błąd.
-   **Inne błędy (`Exception`):**
    -   Złapać generyczne wyjątki na poziomie serwisu lub widoku, zalogować szczegóły i wyświetlić generyczny komunikat błędu ("Wystąpił nieoczekiwany błąd.").

## 11. Kroki implementacji

1.  **Przygotowanie Serwisu Aplikacyjnego:**
    -   Utworzyć `UserProfileService` z metodami: `get_all_profiles_summary()`, `create_profile(username)`, `authenticate_user(user_id, password)`.
    -   Wstrzyknąć `IUserRepository` do serwisu.
    -   Zaimplementować logikę mapowania `User` -> `UserProfileSummaryViewModel`.
    -   Zaimplementować logikę weryfikacji hasła (`bcrypt.checkpw`).
    -   Obsłużyć i propagować wyjątki z repozytorium.
2.  **Implementacja `ProfileListView`:**
    -   Stworzyć klasę `ProfileListView(ttk.Frame)`.
    -   Dodać widgety: `TitleLabel`, `ProfileList` (Treeview), `AddProfileButton`.
    -   Skonfigurować `ProfileList` (kolumny, obsługa obrazka kłódki).
    -   W metodzie inicjalizującej lub `show()` wywołać `profile_service.get_all_profiles_summary()`.
    -   Zaimplementować metodę `populate_list(profiles: List[UserProfileSummaryViewModel])` do wypełnienia Treeview.
    -   Dodać obsługę zdarzeń dla `ProfileList` (`<<TreeviewSelect>>`, `<Double-1>`, `<Return>`) -> wywołanie metody `on_profile_selected(profile)`.
    -   Zaimplementować `on_profile_selected`: sprawdzenie `is_password_protected` i nawigacja (`router.show_login(profile)` lub `router.show_deck_list(profile.id)`).
    -   Dodać obsługę kliknięcia `AddProfileButton` -> wywołanie metody `show_create_profile_dialog()`.
3.  **Implementacja `CreateProfileDialog`:**
    -   Stworzyć klasę `CreateProfileDialog(Toplevel)`.
    -   Dodać widgety: `PromptLabel`, `UsernameInput`, `ErrorLabel`, `CreateButton`, `CancelButton`.
    -   Ustawić dialog jako modalny (`grab_set()`).
    -   Zaimplementować walidację w `on_create_clicked`: sprawdzenie pustej nazwy, długości. Wyświetlanie błędów w `ErrorLabel`.
    -   Jeśli walidacja UI przejdzie, wywołać metodę w `ProfileListView` (przekazaną np. w konstruktorze lub przez callback) z wprowadzoną nazwą i zamknąć dialog (`self.destroy()`).
    -   Obsłużyć `CancelButton`, Enter, Escape.
4.  **Aktualizacja `ProfileListView` (obsługa tworzenia):**
    -   Zaimplementować metodę `handle_profile_creation(username: str)` w `ProfileListView`.
    -   Wywołać `profile_service.create_profile(username)`.
    -   Obsłużyć sukces: odświeżyć listę profili (`refresh_profiles()`), pokazać toast sukcesu.
    -   Obsłużyć `UsernameAlreadyExistsError`: pokazać toast błędu.
    -   Obsłużyć inne błędy: pokazać generyczny toast błędu.
    -   Zaimplementować `refresh_profiles()` (ponowne wywołanie `get_all_profiles_summary` i `populate_list`).
5.  **Implementacja `ProfileLoginView`:**
    -   Stworzyć klasę `ProfileLoginView(ttk.Frame)`.
    -   Dodać widgety: `TitleLabel`, `PasswordEntryFrame`, `LoginButton`, `CancelButton`.
    -   Przechowywać `user_id` i `username` przekazane podczas nawigacji.
    -   Ustawić tekst `TitleLabel` (np. f"Zaloguj do profilu: {self.username}").
    -   Zaimplementować `PasswordEntryFrame` z automatycznym focusem na `PasswordInput`.
    -   Dodać obsługę kliknięcia `LoginButton` i Enter w `PasswordInput` -> wywołanie `on_login_attempt()`.
    -   Zaimplementować `on_login_attempt`: pobrać hasło z `PasswordInput`, wywołać `profile_service.authenticate_user(self.user_id, password)`.
    -   Obsłużyć wynik: `True` -> nawigacja `router.show_deck_list(self.user_id)`; `False` -> wyświetlić błąd ("Nieprawidłowe hasło."), wyczyścić pole hasła; wyjątek -> pokazać generyczny błąd toast.
    -   Dodać obsługę `CancelButton` -> nawigacja `router.show_profile_list()`.
6.  **Integracja z Routerem/ViewManagerem:**
    -   Upewnić się, że Router potrafi tworzyć, pokazywać i ukrywać instancje `ProfileListView` i `ProfileLoginView`.
    -   Upewnić się, że Router przekazuje niezbędne dane (`user_id`, `username`) do `ProfileLoginView`.
7.  **Implementacja ToastContainer:**
    -   Stworzyć lub dostosować globalny mechanizm powiadomień (Toast).
8.  **Testowanie:**
    -   Napisać testy jednostkowe dla `UserProfileService` (mockując `IUserRepository`).
    -   Napisać testy jednostkowe dla logiki walidacji w `CreateProfileDialog`.
    -   Rozważyć testy integracyjne dla przepływów (np. tworzenie profilu, logowanie).
9.  **Styling i Dopracowanie:**
    -   Zastosować style `ttkbootstrap` dla spójnego wyglądu.
    -   Dopracować layout i obsługę klawiatury.
    -   Dodać ikony (np. kłódka).
