# Plan implementacji funkcjonalności Integracji sesji użytkownika i autoryzacji

## 1. Przegląd
Celem tej funkcjonalności jest wprowadzenie wspólnej obsługi sesji użytkownika (logowanie, wylogowanie, przechowywanie aktualnego kontekstu użytkownika) i zapewnienie prawidłowych kontroli autoryzacji w całej aplikacji. Pozwoli to na usunięcie wszystkich hardcoded `user_id` i `TODO` w widokach (np. w `DeckListView`), a także zrealizowanie wymagań PRD dotyczących ochrony profili hasłami.

## 2. Struktura klas/komponentów

### 2.1 Shared/application/SessionService
- Odpowiada za logikę logowania/wylogowania i przechowywania bieżącego użytkownika.
- Metody:
  - `login(username: str, password: str) -> User`
  - `logout() -> None`
  - `get_current_user() -> Optional[User]`
  - `is_authenticated() -> bool`

### 2.2 Shared/domain/errors.py
- Definicja wyjątków aplikacyjnych:
  - `AuthenticationError(AppError)`
  - (opcjonalnie `AuthorizationError`)

### 2.3 Modyfikacja `main.py`
- Inicjalizacja `SessionService` wraz z `UserRepositoryImpl`.
- Przekazanie `session_service` do zależności w całej aplikacji.

### 2.4 Modyfikacja widoków użytkownika
- **ProfileListView** (`/profiles`):
  - Po kliknięciu na niechroniony profil: wywołanie `session_service.login` bez hasła i navigacja do `/decks`.
  - Po kliknięciu na chroniony profil: przekierowanie do `ProfileLoginView`.

- **ProfileLoginView** (`/profiles/login`):
  - Formularz hasła, walidacja via `session_service.login`.
  - Na sukces: `navigate("/decks")`.

### 2.5 Modyfikacja DeckListView i innych
- Dodanie parametru `session_service` w konstruktorze.
- Zamiana `user_id = 1` na `session_service.get_current_user().id`.
- Blokada wyświetlania widoku (lub przekierowanie) jeżeli `!session_service.is_authenticated()`.

## 3. Integracja z persystencją

- `SessionService` użyje `IUserRepository.get_by_username` do pobrania `User` z bazy.
- Podczas `login()`:
  - Jeżeli `user.hashed_password is None` i hasło puste – akceptuj.
  - W przeciwnym razie weryfikacja `bcrypt.checkpw`.
- `logout()` czyści stan `current_user`.
- Inne serwisy (np. `DeckService`) pozostają niezmienione: przyjmują `user_id` przekazany z warstwy UI.

## 4. Obsługa błędów

- `Login`:
  - `User` nie istnieje → `AuthenticationError("Profil nie istnieje")`.
  - Błędne hasło → `AuthenticationError("Niepoprawne hasło")`.
- Próba dostępu do chronionych widoków bez zalogowania → przekierowanie do `/profiles` + toast error.
- Wszelkie wyjątki niskopoziomowe (`sqlite3.IntegrityError`) będą logowane i przetłumaczone na komunikat użytkownika.

## 5. Kroki implementacji

1. Stwórz plik `src/Shared/application/session_service.py` i zaimplementuj klasę `SessionService`.
2. Utwórz `src/Shared/domain/errors.py` z `AuthenticationError`.
3. W `main.py`:
   - Zaimportuj i zainicjalizuj `SessionService(user_repo)`.
   - Dołącz `session_service` do słownika `dependencies`.
4. W `TenXCardsApp.__init__`:
   - Pobierz `session_service` z `dependencies`.
   - Przekaż `session_service` do `ProfileListView`, `ProfileLoginView` i `DeckListView`.
5. W `ProfileListView`:
   - Zamień dotychczasowe wywołanie na metodę logowania: 
     ```python
     session_service.login(selected_username, "")
     navigation_controller.navigate("/decks")
     ```
   - Dodaj przekierowanie do `ProfileLoginView` w przypadku chronionego profilu.
6. Stwórz plik `src/UserProfile/infrastructure/ui/views/profile_login_view.py` z formularzem hasła i wywołaniem `session_service.login(username, password)`.
7. W `DeckListView` (i analogicznie w `CardListView`):
   - Dodaj parametr `session_service` w konstruktorze.
   - Usuń hardcoded `user_id = 1` i zastąp `self.session_service.get_current_user().id`.
   - Przed metodami ładowania danych sprawdź `is_authenticated()` i ewentualnie przekieruj.
8. Usuń wszystkie `# TODO: Get current user_id` w kodzie.
9. Zaktualizuj dokumentację w README.md i ewentualnie diagramy przepływu.
