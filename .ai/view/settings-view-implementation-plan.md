# Plan implementacji widoku SettingsView

## 1. Przegląd
Widok `SettingsView` (Panel Ustawień Użytkownika) jest centralnym miejscem w aplikacji 10xCards, gdzie zalogowany użytkownik może zarządzać ustawieniami swojego profilu oraz globalnymi preferencjami aplikacji. Umożliwia zmianę nazwy profilu, zarządzanie hasłem, konfigurację klucza API OpenRouter, wybór domyślnego modelu LLM oraz personalizację wyglądu aplikacji poprzez wybór schematu kolorystycznego. Dostęp do panelu jest możliwy po zalogowaniu, a poszczególne opcje konfiguracyjne otwierane są w dedykowanych oknach dialogowych.

## 2. Routing widoku
Widok `SettingsView` powinien być dostępny pod umowną ścieżką, np. `/settings`. Nawigacja do tego widoku następuje po kliknięciu przycisku "Ustawienia" dostępnego w głównym interfejsie aplikacji po zalogowaniu użytkownika (np. na górnym pasku w widoku listy talii).

## 3. Struktura komponentów
```
AppWindow (Główne okno aplikacji, np. klasa dziedzicząca po tk.Tk lub ttk.Window)
  └── MainApplicationFrame (Ramka główna aplikacji po zalogowaniu)
      ├── TopBar (np. ttk.Frame, zawiera przycisk "Ustawienia")
      │   └── SettingsButton (ttk.Button, nawiguje do SettingsView)
      └── ContentView (ttk.Frame, dynamicznie zmieniająca zawartość)
          └── SettingsView (ttk.Frame, wyświetlany gdy aktywna ścieżka to /settings)
              ├── TitleLabel (ttk.Label, "Panel Ustawień")
              ├── ChangeUsernameButton (ttk.Button, "Zmień nazwę profilu")
              ├── ManagePasswordButton (ttk.Button, "Zarządzaj hasłem")
              ├── ManageApiKeyButton (ttk.Button, "Klucz API OpenRouter")
              ├── SelectLlmModelButton (ttk.Button, "Domyślny model LLM")
              ├── SelectThemeButton (ttk.Button, "Schemat kolorystyczny")
              ├── BackButton (ttk.Button, "Wróć")
```
Okna dialogowe (będące instancjami `tk.Toplevel`):
- `ChangeUsernameDialog`
- `ManagePasswordDialog`
- `ManageApiKeyDialog`
- `SelectLlmModelDialog`
- `SelectThemeDialog`

Komponent `ToastContainer` (lub jego funkcjonalność) będzie używany do wyświetlania powiadomień (np. o sukcesie lub błędzie operacji) i może być zarządzany na poziomie głównego okna aplikacji.

## 4. Szczegóły komponentów

### `SettingsView` (Frame)
- **Opis komponentu:** Główny kontener Panelu Ustawień. Wyświetla przyciski nawigacyjne do poszczególnych sekcji ustawień oraz przycisk powrotu do poprzedniego widoku.
- **Główne elementy:**
    - `ttk.Label` z tytułem "Panel Ustawień".
    - `ttk.Button` "Zmień nazwę profilu": Otwiera `ChangeUsernameDialog`.
    - `ttk.Button` "Zarządzaj hasłem": Otwiera `ManagePasswordDialog`.
    - `ttk.Button` "Klucz API OpenRouter": Otwiera `ManageApiKeyDialog`.
    - `ttk.Button` "Domyślny model LLM": Otwiera `SelectLlmModelDialog`.
    - `ttk.Button` "Schemat kolorystyczny": Otwiera `SelectThemeDialog`.
    - `ttk.Button` "Wróć": Nawiguje do poprzedniego widoku (np. listy talii).
- **Obsługiwane interakcje:** Kliknięcie każdego z przycisków.
- **Obsługiwana walidacja:** Brak bezpośredniej; delegowana do dialogów.
- **Typy:** Wymaga dostępu do `SettingsViewModel` (lub poszczególnych jego części) do przekazania do dialogów.
- **Properties:** `app_controller` (lub referencja do głównego kontrolera/okna aplikacji do nawigacji i otwierania dialogów), `user_service` (do pobierania aktualnych danych użytkownika i inicjalizacji `SettingsViewModel`), `config_service` (do pobierania list modeli LLM i motywów).

### `ChangeUsernameDialog` (Toplevel)
- **Opis komponentu:** Okno dialogowe umożliwiające użytkownikowi zmianę nazwy swojego profilu.
- **Główne elementy:**
    - `ttk.Label` "Aktualna nazwa: [nazwa]".
    - `ttk.Label` "Nowa nazwa profilu:".
    - `ttk.Entry` `new_username_entry` na nową nazwę.
    - `ttk.Button` "Zapisz".
    - `ttk.Button` "Anuluj".
- **Obsługiwane interakcje:** Wprowadzanie tekstu, kliknięcie "Zapisz", kliknięcie "Anuluj".
- **Obsługiwana walidacja:**
    - Nowa nazwa nie może być pusta.
    - Nowa nazwa max. 30 znaków.
    - Nowa nazwa musi być unikalna (sprawdzane przez `UserService`).
- **Typy:** `ChangeUsernameDTO` (do przekazania do `UserService`).
- **Properties:** `parent` (okno nadrzędne), `user_service`, `current_username: str`.

### `ManagePasswordDialog` (Toplevel)
- **Opis komponentu:** Okno dialogowe do ustawiania, zmiany lub usuwania hasła profilu.
- **Główne elementy:**
    - (Warunkowo) `ttk.Label` "Aktualne hasło:", `ttk.Entry` `current_password_entry` (show='*') - jeśli hasło jest już ustawione.
    - `ttk.Label` "Nowe hasło (zostaw puste by usunąć):", `ttk.Entry` `new_password_entry` (show='*').
    - `ttk.Label` "Potwierdź nowe hasło:", `ttk.Entry` `confirm_password_entry` (show='*').
    - `ttk.Button` "Zapisz".
    - `ttk.Button` "Anuluj".
- **Obsługiwane interakcje:** Wprowadzanie tekstu, kliknięcie "Zapisz", kliknięcie "Anuluj".
- **Obsługiwana walidacja:**
    - Jeśli hasło jest ustawione: `current_password` musi pasować do zapisanego hasła (weryfikacja przez `UserService` przy użyciu bcrypt).
    - Jeśli ustawiane/zmieniane: `new_password` i `confirm_password` muszą być identyczne.
    - `new_password` może być puste tylko jeśli usuwamy hasło (i `current_password` jest poprawne).
- **Typy:** `SetUserPasswordDTO` (do przekazania do `UserService`).
- **Properties:** `parent`, `user_service`, `has_password_set: bool`.

### `ManageApiKeyDialog` (Toplevel)
- **Opis komponentu:** Okno dialogowe do zarządzania kluczem API OpenRouter.
- **Główne elementy:**
    - `ttk.Label` "Klucz API OpenRouter:".
    - `ttk.Entry` `api_key_entry` (wyświetla zamaskowany klucz, jeśli istnieje; pozwala na wpisanie nowego).
    - `ttk.Button` "Zapisz".
    - `ttk.Button` "Usuń klucz" (jeśli klucz istnieje).
    - `ttk.Button` "Anuluj".
    - (Opcjonalnie) `ttk.Checkbutton` do przełączania widoczności klucza.
- **Obsługiwane interakcje:** Wprowadzanie tekstu, kliknięcie "Zapisz", "Usuń klucz", "Anuluj".
- **Obsługiwana walidacja:**
    - Przy zapisie: Walidacja online klucza API przez `UserService` (np. testowe zapytanie do OpenRouter).
- **Typy:** `UpdateUserApiKeyDTO` (do przekazania do `UserService`).
- **Properties:** `parent`, `user_service`, `current_api_key_masked: Optional[str]`.

### `SelectLlmModelDialog` (Toplevel)
- **Opis komponentu:** Okno dialogowe do wyboru domyślnego modelu LLM.
- **Główne elementy:**
    - `ttk.Label` "Wybierz domyślny model LLM:".
    - `ttk.Combobox` `llm_model_combobox` ( wartości z `available_llm_models`, stan `readonly`).
    - `ttk.Button` "Zapisz".
    - `ttk.Button` "Anuluj".
- **Obsługiwane interakcje:** Wybór z Combobox, kliknięcie "Zapisz", "Anuluj".
- **Obsługiwana walidacja:** Wybrany model musi być jednym z `available_llm_models`.
- **Typy:** `UpdateUserPreferencesDTO` (do przekazania częściowo do `UserService`).
- **Properties:** `parent`, `user_service`, `config_service`, `current_llm_model: Optional[str]`.

### `SelectThemeDialog` (Toplevel)
- **Opis komponentu:** Okno dialogowe do wyboru schematu kolorystycznego aplikacji.
- **Główne elementy:**
    - `ttk.Label` "Wybierz schemat kolorystyczny:".
    - `ttk.Combobox` `theme_combobox` (wartości z `available_app_themes`, stan `readonly`).
    - `ttk.Button` "Zastosuj".
    - `ttk.Button` "Anuluj".
- **Obsługiwane interakcje:** Wybór z Combobox, kliknięcie "Zastosuj", "Anuluj".
- **Obsługiwana walidacja:** Wybrany schemat musi być jednym z `available_app_themes`.
- **Typy:** `UpdateUserPreferencesDTO` (do przekazania częściowo do `UserService`).
- **Properties:** `parent`, `user_service`, `config_service`, `app_controller` (do natychmiastowej zmiany motywu), `current_app_theme: str`.

## 5. Typy

### Modele Domeny (rozszerzenie istniejącego)
**`User`** (w `src/UserProfile/domain/models/user.py`)
- `id: Optional[int]`
- `username: str`
- `hashed_password: Optional[str]`
- `encrypted_api_key: Optional[bytes]` (dla zaszyfrowanego klucza Fernet)
- `default_llm_model: Optional[str]` (np. "openai/gpt-4o-mini")
- `app_theme: Optional[str]` (np. "litera", "darkly")
- `created_at: Optional[datetime]`
- `updated_at: Optional[datetime]`

### ViewModels
**`SettingsViewModel`** (używany do inicjalizacji i przekazywania danych do dialogów)
- `user_id: int`
- `current_username: str`
- `has_password_set: bool`
- `current_api_key_masked: Optional[str]` (np. "sk-xxxx...xxxx" lub "Nie ustawiono")
- `current_llm_model: Optional[str]`
- `current_app_theme: str`
- `available_llm_models: List[str]` (ładowane z `src/Shared/infrastructure/config.py`)
- `available_app_themes: List[str]` (ładowane z `src/Shared/infrastructure/config.py`)

### Data Transfer Objects (DTOs)
**`UpdateUserProfileDTO`**
- `user_id: int`
- `new_username: str`

**`SetUserPasswordDTO`**
- `user_id: int`
- `current_password: Optional[str]` (plaintext, do weryfikacji z hashem)
- `new_password: Optional[str]` (plaintext, do hashowania; jeśli None, oznacza usunięcie hasła)

**`UpdateUserApiKeyDTO`**
- `user_id: int`
- `api_key: Optional[str]` (plaintext; jeśli None, oznacza usunięcie klucza)

**`UpdateUserPreferencesDTO`**
- `user_id: int`
- `default_llm_model: Optional[str]` (opcjonalne, jeśli tylko to jest zmieniane)
- `app_theme: Optional[str]` (opcjonalne, jeśli tylko to jest zmieniane)

## 6. Zarządzanie stanem
- Stan główny `SettingsView` (i dane dla dialogów) będzie pochodził z załadowanego obiektu `User` (przez `UserService`) i przekształcony w `SettingsViewModel`.
- Każde okno dialogowe będzie zarządzać swoim lokalnym stanem (np. wartości w polach `Entry` za pomocą `tk.StringVar`).
- Po pomyślnym zapisie zmian przez `UserService`, `SettingsViewModel` w `SettingsView` (lub odpowiednie jego części) powinien zostać odświeżony, jeśli to konieczne, lub aplikacja może polegać na ponownym załadowaniu danych przy następnym wejściu do widoku.
- Zmiana motywu (`app_theme`) powinna być zastosowana natychmiast do aktywnego okna przez wywołanie `app_controller.set_theme(new_theme_name)` i zapisana. `app_controller` powinien przechowywać aktualnie wybrany motyw, aby nowe okna mogły go używać.
- Informacje o dostępnych modelach LLM i motywach będą ładowane z pliku `src/Shared/infrastructure/config.py` za pośrednictwem `ConfigService`.

## 7. Integracja z persystencją
Integracja z persystencją będzie odbywać się poprzez `UserService` (warstwa aplikacyjna), który z kolei będzie korzystał z `IUserRepository`. Kluczowe znaczenie ma również `SessionService`, który dostarcza informacje o aktualnie zalogowanym użytkowniku.

- **Odczyt:**
    - Przy wejściu do `SettingsView`, aktualne dane użytkownika (w tym `username`, `encrypted_api_key`, `default_llm_model`, `app_theme` oraz informacja, czy `hashed_password` istnieje) będą pobierane poprzez `SessionService.get_current_user()`. Zwrócony obiekt `User` będzie źródłem danych do inicjalizacji `SettingsViewModel`.
    - Jeśli potrzebne jest odświeżenie danych użytkownika (np. po zmianie w innym miejscu lub dla pewności), można użyć `SessionService.refresh_current_user()` przed pobraniem danych.
    - `ConfigService` dostarczy listy modeli LLM i motywów.
- **Zapis:**
    - Identyfikator użytkownika (`user_id`) potrzebny do DTOs operacji zapisu będzie pobierany z obiektu `User` dostarczonego przez `SessionService.get_current_user().id`.
    - **Zmiana nazwy profilu:** `UserService.update_username(dto: UpdateUserProfileDTO)` -> `IUserRepository.update(user)`.
        - Żądanie: `UpdateUserProfileDTO(user_id, new_username)`
        - Odpowiedź (UserService): `User` (zaktualizowany) lub wyjątek. Po pomyślnej operacji należy wywołać `SessionService.refresh_current_user()`.
    - **Zarządzanie hasłem:** `UserService.set_user_password(dto: SetUserPasswordDTO)` -> `IUserRepository.update(user)`.
        - Żądanie: `SetUserPasswordDTO(user_id, current_password, new_password)`
        - Odpowiedź (UserService): `bool` (sukces) lub wyjątek. Wymaga weryfikacji `current_password` z `user.hashed_password` i hashowania `new_password` (bcrypt). Po pomyślnej operacji należy wywołać `SessionService.refresh_current_user()`.
    - **Zarządzanie kluczem API:** `UserService.update_api_key(dto: UpdateUserApiKeyDTO)` -> `IUserRepository.update(user)`.
        - Żądanie: `UpdateUserApiKeyDTO(user_id, api_key)`
        - Odpowiedź (UserService): `bool` (sukces walidacji i zapisu) lub wyjątek. Wymaga walidacji online klucza i szyfrowania (Fernet) przed zapisem `user.encrypted_api_key`. Sól Fernet z `config.py`. Po pomyślnej operacji należy wywołać `SessionService.refresh_current_user()`.
    - **Wybór modelu LLM/Motywu:** `UserService.update_user_preferences(dto: UpdateUserPreferencesDTO)` -> `IUserRepository.update(user)`.
        - Żądanie: `UpdateUserPreferencesDTO(user_id, default_llm_model?, app_theme?)`
        - Odpowiedź (UserService): `User` (zaktualizowany) lub wyjątek. Po pomyślnej operacji należy wywołać `SessionService.refresh_current_user()`.

## 8. Interakcje użytkownika
- **Nawigacja do Panelu Ustawień:** Kliknięcie przycisku "Ustawienia" w głównym UI.
- **Wybór opcji w Panelu:** Kliknięcie jednego z przycisków ("Zmień nazwę...", "Zarządzaj hasłem" itd.) otwiera odpowiednie okno dialogowe.
- **Wprowadzanie danych w dialogach:** Użytkownik wprowadza tekst w polach `Entry`, wybiera opcje z `Combobox`.
- **Zapis zmian:** Kliknięcie przycisku "Zapisz" / "Zastosuj" w dialogu inicjuje proces walidacji i zapisu.
    - Wyświetlany jest wskaźnik postępu/oczekiwania (jeśli operacja może potrwać, np. walidacja API key).
    - Po zakończeniu operacji wyświetlany jest komunikat `Toast` (sukces/błąd).
    - Dialog jest zamykany po sukcesie.
- **Anulowanie:** Kliknięcie "Anuluj" w dialogu zamyka go bez zapisywania zmian.
- **Usuwanie klucza API:** Kliknięcie "Usuń klucz" usuwa klucz API po potwierdzeniu.
- **Powrót:** Kliknięcie "Wróć" w `SettingsView` nawiguje do poprzedniego widoku.
- **Zmiana motywu:** Wybór motywu i kliknięcie "Zastosuj" natychmiast zmienia wygląd aktywnego okna.

## 9. Warunki i walidacja
- **Nazwa profilu (FR-044b):**
    - Niepusta: Sprawdzane w `ChangeUsernameDialog` przed wysłaniem.
    - Max. 30 znaków: Sprawdzane w `ChangeUsernameDialog`.
    - Unikalna: Sprawdzane przez `UserService` (zapytanie do `IUserRepository`).
    - Efekt: Komunikat błędu w dialogu, blokada zapisu.
- **Hasło (FR-045, FR-046):**
    - Zgodność aktualnego hasła: Sprawdzane przez `UserService` z hashem w DB.
    - Zgodność nowego hasła i potwierdzenia: Sprawdzane w `ManagePasswordDialog`.
    - Efekt: Komunikat błędu w dialogu, blokada zapisu.
- **Klucz API (FR-051, FR-052):**
    - Walidacja online: Przeprowadzana przez `UserService` (np. testowe zapytanie do OpenRouter).
    - Efekt: Komunikat o statusie walidacji w `ManageApiKeyDialog`, blokada zapisu przy niepoprawnym kluczu.
- **Długość tekstu fiszek (poza tym widokiem, ale związane z API Key i LLM):**
    - Minimalna (1000) i maksymalna (10000) długość tekstu do generowania fiszek (FR-012).
- **Limity znaków dla fiszek (FR-015, FR-021):**
    - Przód: max 200 znaków.
    - Tył: max 500 znaków.
- **Maskowanie klucza API (FR-053):** `ManageApiKeyDialog` powinien wyświetlać klucz w formie zamaskowanej (np. `sk-xxxx...xxxx`).
- **Niedostępność domyślnego modelu LLM (FR-059):**
    - Przy ładowaniu `SettingsView` lub przy próbie użycia AI, jeśli zapisany w DB `user.default_llm_model` nie istnieje na liście z `config.py`:
        - Aplikacja używa pierwszego dostępnego modelu z listy jako zastępczego.
        - Użytkownik jest informowany (jednorazowy komunikat/toast).
        - Wartość w DB jest aktualizowana na `null` lub faktycznie używany model zastępczy.
        - `SelectLlmModelDialog` powinien odzwierciedlać aktualnie używany (potencjalnie zastępczy) model.

## 10. Obsługa błędów
- **Błędy walidacji (lokalne):** Wyświetlanie komunikatów bezpośrednio w oknach dialogowych (np. pod odpowiednim polem `Entry` lub w dedykowanej etykiecie błędu).
- **Błędy komunikacji z serwisem/API (np. walidacja API key online):**
    - Wyświetlanie komunikatów w oknach dialogowych.
    - Użycie `ToastContainer` do informowania o ogólnych błędach operacji (np. "Nie udało się zapisać zmian. Spróbuj ponownie.").
- **Błędy zapisu do bazy danych:** Ogólny komunikat błędu przez `ToastContainer`.
- **Brak klucza API przy próbie generowania fiszek AI (FR-054):** Aplikacja powinna wyświetlić użytkownikowi komunikat o braku klucza i niemożności wykonania operacji, sugerując jego konfigurację w Panelu Ustawień.
- **Błędy ładowania konfiguracji (np. brak pliku `config.py`):** Aplikacja powinna obsłużyć taki przypadek, np. używając wartości domyślnych i logując błąd. Dostępne modele/motywy będą puste, co UI powinno obsłużyć (np. wyłączając opcje).
- **Logowanie (FR-034 do FR-037a):**
    - Błędy komunikacji z API AI.
    - Błędy operacji na bazie danych.
    - Zmiany istotnych ustawień użytkownika (zmiana klucza API, domyślnego modelu LLM).

## 11. Kroki implementacji

1.  **Aktualizacja modelu domeny i repozytorium:**
    *   Dodać pola `default_llm_model: Optional[str]` i `app_theme: Optional[str]` do dataclassy `User` w `src/UserProfile/domain/models/user.py`.
    *   Upewnić się, że pole `encrypted_api_key` ma typ `Optional[bytes]`.
    *   Zaktualizować implementację `IUserRepository` (np. `SqliteUserRepository`) oraz schemat bazy danych (migracje), aby uwzględnić nowe pola.
2.  **Utworzenie DTOs:**
    *   Zdefiniować wszystkie DTO (`UpdateUserProfileDTO`, `SetUserPasswordDTO`, `UpdateUserApiKeyDTO`, `UpdateUserPreferencesDTO`) w odpowiednim module, np. `src/UserProfile/application/dtos.py`.
3.  **Rozbudowa `UserService` (lub utworzenie nowego serwisu dla ustawień):**
    *   Implementacja metod:
        *   `get_user_settings(user_id: int) -> SettingsViewModel` (lub metoda zwracająca `User` i transformacja w UI).
        *   `update_username(dto: UpdateUserProfileDTO)`.
        *   `set_user_password(dto: SetUserPasswordDTO)` (z logiką bcrypt).
        *   `update_api_key(dto: UpdateUserApiKeyDTO)` (z walidacją online i szyfrowaniem Fernet).
        *   `update_user_preferences(dto: UpdateUserPreferencesDTO)`.
    *   Integracja z `IUserRepository`.
    *   Implementacja logiki walidacji online dla klucza API (np. testowe zapytanie do OpenRouter używając `litellm`).
    *   Implementacja szyfrowania/odszyfrowywania klucza API przy użyciu Fernet (sól z `config.py`).
4.  **Implementacja `ConfigService`:**
    *   Serwis do odczytu list (modele LLM, schematy kolorystyczne, sól Fernet) z `src/Shared/infrastructure/config.py`.
5.  **Implementacja UI - `SettingsView`:**
    *   Stworzenie ramki `SettingsView` z przyciskami nawigacyjnymi i przyciskiem "Wróć".
    *   Podłączenie akcji do przycisków otwierających odpowiednie dialogi.
    *   Implementacja logiki ładowania `SettingsViewModel` przy wejściu do widoku.
6.  **Implementacja UI - Okna Dialogowe:**
    *   Dla każdego ustawienia (`ChangeUsernameDialog`, `ManagePasswordDialog`, `ManageApiKeyDialog`, `SelectLlmModelDialog`, `SelectThemeDialog`):
        *   Stworzyć klasę dziedziczącą po `tk.Toplevel`.
        *   Zaimplementować layout z wymaganymi widgetami (`Label`, `Entry`, `Combobox`, `Button`).
        *   Powiązać widgety z `tk.StringVar` itp.
        *   Implementacja logiki przycisków "Zapisz"/"Zastosuj" (walidacja, wywołanie `UserService`, obsługa odpowiedzi, zamknięcie dialogu, wyświetlenie toasta).
        *   Implementacja logiki przycisku "Anuluj".
        *   Przekazywanie odpowiednich danych (np. `current_username`) przy tworzeniu dialogu.
7.  **Implementacja natychmiastowej zmiany motywu:**
    *   W `SelectThemeDialog`, po kliknięciu "Zastosuj" i pomyślnym zapisie, wywołać metodę w głównym kontrolerze aplikacji (`app_controller.set_theme(new_theme_name)`), która użyje `style.theme_use(new_theme_name)`.
    *   Główny kontroler aplikacji powinien przechowywać aktualny motyw i stosować go przy tworzeniu nowych okien.
8.  **Maskowanie i obsługa klucza API:**
    *   W `ManageApiKeyDialog` wyświetlać zapisany klucz w formie zamaskowanej.
    *   Implementacja opcjonalnego przycisku "Pokaż/Ukryj klucz".
9.  **Obsługa niedostępnego modelu LLM (FR-059):**
    *   W logice ładowania `SettingsViewModel` lub w `UserService.get_user_settings`, sprawdzić czy zapisany `default_llm_model` jest na liście z `config.py`. Jeśli nie, zastosować logikę zastępczą i poinformować użytkownika.
10. **Integracja `ToastContainer`:** Zapewnić mechanizm wyświetlania powiadomień toast z poziomu dialogów/`SettingsView`.
11. **Nawigacja:**
    *   Implementacja przycisku "Ustawienia" w głównym UI, który przełącza `ContentView` na `SettingsView`.
    *   Implementacja przycisku "Wróć" w `SettingsView`.
12. **Testowanie:**
    *   Testy jednostkowe dla logiki w `UserService` (walidacja, hashowanie, szyfrowanie).
    *   Testy UI (manualne lub z użyciem narzędzi, jeśli są w projekcie) dla wszystkich interakcji i scenariuszy błędów w `SettingsView` i dialogach.
13. **Logowanie:** Zaimplementować logowanie zdarzeń zgodnie z FR-034 do FR-037a.
