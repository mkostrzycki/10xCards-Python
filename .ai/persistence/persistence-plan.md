# Plan Persystencji Danych

## 1. Struktura Bazy Danych i Schemat

-   **Strategia Przechowywania:** Aplikacja będzie korzystać z **jednego, wspólnego pliku bazy danych SQLite** dla wszystkich profili użytkowników. Plik będzie zlokalizowany wewnątrz struktury projektu, w katalogu `data/`, pod nazwą `10xcards.db` (tj. `<katalog_główny_projektu>/data/10xcards.db`). Taka strategia wymaga implementacji izolacji danych na poziomie logiki aplikacji (repozytoriów).
-   **Schemat Bazy Danych:** Schemat bazy danych zdefiniowany w plikach migracji (np. `infrastructure/persistence/sqlite/migrations/20250413174854_initial_schema.sql`) będzie stosowany do tego **pojedynczego** pliku `data/10xcards.db`.
-   **Główne Tabele i Relacje:**
    -   `Users`: Przechowuje dane **wszystkich** profili użytkowników aplikacji. Klucz główny `id`. Kluczowe kolumny to `username` (musi być `UNIQUE` globalnie), `hashed_password`, `hashed_api_key`.
    -   `Decks`: Zawiera talie fiszek należące do **różnych** użytkowników. Klucz główny `id`. Kolumna `user_id` jest **kluczowa** dla izolacji danych – jest to klucz obcy (`FOREIGN KEY`) wskazujący na tabelę `Users` z regułą `ON DELETE CASCADE`. Ograniczenie `UNIQUE (user_id, name)` zapewnia, że nazwa talii jest unikalna **w obrębie danego użytkownika**.
    -   `Flashcards`: Zawiera poszczególne fiszki należące do talii **różnych** użytkowników. Klucz główny `id`. Posiada klucz obcy `deck_id` wskazujący na tabelę `Decks` (`ON DELETE CASCADE`). Izolacja danych odbywa się pośrednio przez przynależność do talii (`Decks`), która jest powiązana z użytkownikiem (`user_id`). Przechowuje `front_text`, `back_text`, `fsrs_state`, `source`, `ai_model_name`.
-   **Relacje:**
    -   `Users` 1 -- * `Decks` (poprzez `user_id`, `ON DELETE CASCADE`)
    -   `Decks` 1 -- * `Flashcards` (poprzez `deck_id`, `ON DELETE CASCADE`)

## 2. Wzorzec Repozytorium i Interfejsy

-   **Zastosowany Wzorzec:** Warstwa persystencji będzie implementowana z użyciem wzorca **Repozytorium**. Kluczowe zasady tego wzorca w tym projekcie to:
    -   **Definicja Interfejsów:** Abstrakcyjne interfejsy repozytoriów (np. `IUserRepository`, `IDeckRepository`) są definiowane w warstwie `domain` odpowiedniego kontekstu (np. `src/UserProfile/domain/repositories/`). Określają one kontrakt operacji na danych dla danej agregacji/encji.
    -   **Implementacja w Infrastrukturze:** Konkretne implementacje tych interfejsów, wykorzystujące SQLite, znajdują się w warstwie `infrastructure` (np. `src/UserProfile/infrastructure/persistence/sqlite/repositories/UserRepositoryImpl.py`).
    -   **Enkapsulacja Logiki SQL:** Cała logika bezpośredniej interakcji z bazą danych (konstrukcja zapytań SQL, mapowanie wyników na obiekty domenowe) jest zamknięta wewnątrz klas implementujących repozytoria.
    -   **Wstrzykiwanie Zależności:** Implementacje repozytoriów otrzymują niezbędne zależności, takie jak obiekt połączenia z bazą danych lub dostawca kursorów, poprzez mechanizm wstrzykiwania zależności (np. przez konstruktor). Nie tworzą one połączenia samodzielnie.
-   **Interfejsy Repozytoriów i Kluczowe Metody (z uwzględnieniem izolacji danych):**

    **Kontekst: `UserProfile`**
    -   Interfejs: `src/UserProfile/domain/repositories/IUserRepository.py`
    -   Metody:
        -   `add(user: User) -> User`: Dodaje nowego użytkownika do tabeli `Users`. Rzuca `IntegrityError` w przypadku naruszenia unikalności `username`. Zwraca dodanego użytkownika z ID.
        -   `get_by_id(user_id: int) -> Optional[User]`: Pobiera użytkownika na podstawie jego ID.
        -   `get_by_username(username: str) -> Optional[User]`: Pobiera użytkownika na podstawie nazwy użytkownika.
        -   `list_all() -> List[User]`: Zwraca listę wszystkich użytkowników (potrzebne do ekranu logowania).
        -   `update(user: User) -> None`: Aktualizuje dane użytkownika. Rzuca wyjątek w przypadku problemów.

    **Kontekst: `DeckManagement`**
    -   Interfejs: `src/DeckManagement/domain/repositories/IDeckRepository.py`
    -   Metody (każda operująca na danych wymaga `user_id` do filtrowania):
        -   `add(deck: Deck) -> Deck`: Dodaje nową talię (obiekt `Deck` powinien zawierać `user_id`). Rzuca `IntegrityError` w przypadku naruszenia `UNIQUE(user_id, name)`.
        -   `get_by_id(deck_id: int, user_id: int) -> Optional[Deck]`: Pobiera talię o danym ID, **tylko jeśli należy do danego użytkownika**.
        -   `get_by_name(name: str, user_id: int) -> Optional[Deck]`: Pobiera talię o danej nazwie, **należącą do danego użytkownika**.
        -   `list_all(user_id: int) -> List[Deck]`: Zwraca listę wszystkich talii **należących do danego użytkownika**.
        -   `update(deck: Deck) -> None`: Aktualizuje dane talii (obiekt `Deck` musi zawierać `user_id` i `id`). Rzuca `IntegrityError` przy naruszeniu unikalności nazwy dla tego użytkownika.
        -   `delete(deck_id: int, user_id: int) -> None`: Usuwa talię o podanym ID, **tylko jeśli należy do danego użytkownika**.

    **Kontekst: `CardManagement`**
    -   Interfejs: `src/CardManagement/domain/repositories/IFlashcardRepository.py`
    -   Metody (operacje wymagają `deck_id`, a pośrednio izolacja jest zapewniona przez `user_id` na poziomie talii):
        -   `add(flashcard: Flashcard) -> Flashcard`: Dodaje nową fiszkę (obiekt `Flashcard` zawiera `deck_id`).
        -   `get_by_id(flashcard_id: int) -> Optional[Flashcard]`: Pobiera fiszkę na podstawie jej ID. (Potencjalnie wymaga sprawdzenia `user_id` talii nadrzędnej w serwisie).
        -   `list_by_deck_id(deck_id: int) -> List[Flashcard]`: Zwraca listę wszystkich fiszek dla talii o podanym ID. (Serwis wywołujący powinien upewnić się, że `deck_id` należy do zalogowanego użytkownika).
        -   `update(flashcard: Flashcard) -> None`: Aktualizuje dane istniejącej fiszki.
        -   `delete(flashcard_id: int) -> None`: Usuwa fiszkę o podanym ID.
        -   `get_fsrs_card_data_for_deck(deck_id: int) -> List[Tuple[int, Optional[str]]]`: Pobiera dane FSRS dla fiszek w talii. (Serwis musi zapewnić poprawność `deck_id`).

## 3. Implementacja Repozytoriów (SQLite)

-   **Lokalizacja:** Implementacje repozytoriów znajdują się w `src/<Context>/infrastructure/persistence/sqlite/repositories/`.
-   **Zarządzanie Połączeniem:** Implementacje repozytoriów będą otrzymywać **współdzielony** obiekt połączenia `sqlite3.Connection` (lub dostawcę kursorów) do **jedynego pliku bazy danych** (`data/10xcards.db`) poprzez wstrzykiwanie zależności.
-   **Kluczowa Rola Filtrowania:** Ponieważ wszystkie dane są w jednym pliku, **krytyczne** jest, aby **każde zapytanie** SQL w implementacjach repozytoriów `DeckRepositoryImpl` i `FlashcardRepositoryImpl` (oraz częściowo `UserRepositoryImpl`), które ma operować na danych specyficznych dla użytkownika, zawierało odpowiednią klauzulę `WHERE user_id = ?` (lub odpowiedni `JOIN` z warunkiem na `user_id`). Parametr `user_id` musi być przekazywany do metod repozytorium z warstwy aplikacji (np. z Serwisów). **Brak filtrowania po `user_id` jest poważnym błędem bezpieczeństwa i logiki.**
-   **Bezpieczeństwo Zapytań:** Należy **bezwzględnie** stosować **zapytania parametryzowane** (`?`) w celu ochrony przed SQL Injection.
-   **Transakcje:** Zarządzanie transakcjami odbywa się w warstwie Serwisów Aplikacji, gdy operacja obejmuje wiele zapisów.

## 4. Zarządzanie Połączeniem i Migracje

-   **Singleton Połączenia:** Centralny mechanizm (Singleton/zarządzany obiekt) będzie odpowiedzialny za zarządzanie połączeniem do **jedynego, wspólnego pliku** `data/10xcards.db`. Ścieżka do pliku będzie stała. Odpowiada za udostępnianie `sqlite3.Connection`, włączanie `PRAGMA foreign_keys = ON;` i zamykanie połączenia.
-   **Mechanizm Migracji:**
    -   **Lokalizacja Skryptów:** Skrypty migracji SQL są przechowywane w `infrastructure/persistence/sqlite/migrations/`.
    -   **Konwencja Nazewnictwa:** Pliki migracji nazywane są zgodnie z formatem `YYYYMMDDHHmmss_krotki_opis.sql`.
    -   **Proces Uruchamiania:** Migracje będą uruchamiane **raz, przy starcie aplikacji**, przez dedykowany komponent (`MigrationRunner`). Proces łączy się ze **wspólną bazą** `data/10xcards.db`, sprawdza `PRAGMA user_version`, porównuje z dostępnymi plikami migracji w `migrations/` i aplikuje brakujące sekwencyjnie w jednej transakcji, aktualizując na końcu `user_version`. Proces ten nie jest już zależny od wyboru profilu użytkownika.

## 5. Integralność i Walidacja Danych (na poziomie persystencji)

-   **Integralność na Poziomie Bazy Danych:** Podstawowa integralność danych jest zapewniana przez ograniczenia schematu SQL (`UNIQUE`, `NOT NULL`, `FOREIGN KEY`).
-   **Obsługa Błędów Integralności:** Repozytoria powinny obsługiwać wyjątki `sqlite3.IntegrityError` i propagować je do wyższych warstw.
-   **Krytyczna Rola Filtrowania Aplikacyjnego:** Należy ponownie podkreślić, że izolacja danych między użytkownikami w tym modelu **nie jest** zapewniana przez mechanizmy bazy danych (jak RLS), lecz **wyłącznie przez poprawną implementację filtrowania `user_id` w każdej metodzie repozytorium** operującej na danych zależnych od użytkownika (`Decks`, `Flashcards`). Błędy w tym filtrowaniu prowadzą do wycieku lub modyfikacji danych innych użytkowników.
-   **Walidacja Biznesowa:** Walidacje logiki biznesowej są realizowane w Serwisach Aplikacji *przed* wywołaniem metod repozytorium.
