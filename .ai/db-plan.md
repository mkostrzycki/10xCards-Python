# Schemat Bazy Danych SQLite dla 10xCards MVP

## 1. Definicje Tabel

### `Users`

Przechowuje informacje o profilach użytkowników.

| Kolumna           | Typ      | Ograniczenia                                  | Opis                                                                 |
| :---------------- | :------- | :-------------------------------------------- | :------------------------------------------------------------------- |
| `id`              | INTEGER  | PRIMARY KEY AUTOINCREMENT                     | Unikalny identyfikator użytkownika.                                  |
| `username`        | TEXT     | NOT NULL, UNIQUE                              | Unikalna nazwa profilu użytkownika (maks. 30 znaków, walidacja w aplikacji). |
| `hashed_password` | TEXT     | NULL                                          | Hash hasła użytkownika (bcrypt, generowany w aplikacji). Może być NULL. |
| `hashed_api_key`  | TEXT     | NULL                                          | Hash klucza API Openrouter.ai (bcrypt, generowany w aplikacji). Może być NULL. |
| `created_at`      | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas utworzenia profilu.                                        |
| `updated_at`      | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas ostatniej modyfikacji profilu (trigger do aktualizacji).   |

### `Decks`

Przechowuje informacje o taliach fiszek należących do użytkowników.

| Kolumna      | Typ      | Ograniczenia                                  | Opis                                                              |
| :----------- | :------- | :-------------------------------------------- | :---------------------------------------------------------------- |
| `id`         | INTEGER  | PRIMARY KEY AUTOINCREMENT                     | Unikalny identyfikator talii.                                     |
| `user_id`    | INTEGER  | NOT NULL, FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE | ID użytkownika, do którego należy talia. Usunięcie użytkownika usuwa jego talie. |
| `name`       | TEXT     | NOT NULL                                      | Nazwa talii (maks. 50 znaków, walidacja w aplikacji).            |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas utworzenia talii.                                     |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas ostatniej modyfikacji talii (trigger do aktualizacji).  |
|              |          | UNIQUE (user_id, name)                        | Nazwa talii musi być unikalna w obrębie danego użytkownika.       |

### `Flashcards`

Przechowuje poszczególne fiszki należące do talii.

| Kolumna         | Typ      | Ograniczenia                                  | Opis                                                                    |
| :-------------- | :------- | :-------------------------------------------- | :---------------------------------------------------------------------- |
| `id`            | INTEGER  | PRIMARY KEY AUTOINCREMENT                     | Unikalny identyfikator fiszki.                                          |
| `deck_id`       | INTEGER  | NOT NULL, FOREIGN KEY(deck_id) REFERENCES Decks(id) ON DELETE CASCADE | ID talii, do której należy fiszka. Usunięcie talii usuwa jej fiszki. |
| `front_text`    | TEXT     | NOT NULL                                      | Tekst na przedniej stronie fiszki (maks. 200 znaków, walidacja w aplikacji). |
| `back_text`     | TEXT     | NOT NULL                                      | Tekst na tylnej stronie fiszki (maks. 500 znaków, walidacja w aplikacji). |
| `fsrs_state`    | TEXT     | NULL                                          | Stan algorytmu FSRS dla fiszki, przechowywany jako JSON. Może być NULL. |
| `source`        | TEXT     | NOT NULL, CHECK (source IN ('manual', 'ai-generated', 'ai-edited')) | Źródło pochodzenia fiszki.                                           |
| `ai_model_name` | TEXT     | NULL                                          | Nazwa modelu AI użytego do generacji/edycji (jeśli dotyczy). Może być NULL. |
| `created_at`    | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas utworzenia fiszki.                                          |
| `updated_at`    | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | Data i czas ostatniej modyfikacji fiszki (trigger do aktualizacji).     |

## 2. Relacje Między Tabelami

*   **Users ‹— Decks (Jeden-do-wielu):**
    *   Jeden użytkownik (`Users`) może mieć wiele talii (`Decks`).
    *   Każda talia (`Decks`) należy do dokładnie jednego użytkownika (`Users`).
    *   Relacja wymuszona przez `FOREIGN KEY (user_id)` w tabeli `Decks`.
    *   `ON DELETE CASCADE`: Usunięcie użytkownika automatycznie usuwa wszystkie jego talie.
*   **Decks ‹— Flashcards (Jeden-do-wielu):**
    *   Jedna talia (`Decks`) może zawierać wiele fiszek (`Flashcards`).
    *   Każda fiszka (`Flashcards`) należy do dokładnie jednej talii (`Decks`).
    *   Relacja wymuszona przez `FOREIGN KEY (deck_id)` w tabeli `Flashcards`.
    *   `ON DELETE CASCADE`: Usunięcie talii automatycznie usuwa wszystkie zawarte w niej fiszki.

## 3. Indeksy

Oprócz indeksów tworzonych automatycznie dla kluczy głównych (`PRIMARY KEY`) i ograniczeń `UNIQUE`, zaleca się utworzenie indeksów na kluczach obcych w celu poprawy wydajności zapytań JOIN:

*   `idx_decks_user_id` ON `Decks` (`user_id`)
*   `idx_flashcards_deck_id` ON `Flashcards` (`deck_id`)

Dodatkowe indeksy mogą być rozważone w przyszłości, jeśli analiza wydajności wykaże taką potrzebę (np. na `Flashcards.source` lub `Flashcards.created_at`).

## 4. Zasady Bezpieczeństwa na Poziomie Wiersza (Row-Level Security - RLS)

SQLite nie posiada wbudowanego mechanizmu RLS porównywalnego do systemów takich jak PostgreSQL. Zgodnie z ustaleniami z sesji planowania i regułą `database.mdc`, **izolacja danych między użytkownikami będzie implementowana wyłącznie w warstwie aplikacji**, w ramach logiki repozytoriów. Wszystkie zapytania pobierające dane dla konkretnego użytkownika (np. talie, fiszki) muszą być filtrowane po `user_id` w klauzuli `WHERE`.

## 5. Dodatkowe Uwagi

*   **Migracje:** Schemat będzie zarządzany za pomocą prostego mechanizmu migracji opartego na `PRAGMA user_version` i skryptach SQL przechowywanych w `infrastructure/persistence/sqlite/migrations/`.
*   **Aktywacja Kluczy Obcych:** Należy pamiętać o wykonaniu `PRAGMA foreign_keys = ON;` przy każdym nowym połączeniu z bazą danych, aby wymusić ograniczenia kluczy obcych.
*   **Trigger `updated_at`:** W celu automatycznej aktualizacji kolumn `updated_at` przy każdej modyfikacji wiersza, zostaną utworzone odpowiednie triggery dla tabel `Users`, `Decks` i `Flashcards`. Przykład dla `Users`:
    ```sql
    CREATE TRIGGER update_users_updated_at
    AFTER UPDATE ON Users
    FOR EACH ROW
    BEGIN
        UPDATE Users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    ```
    Analogiczne triggery zostaną utworzone dla `Decks` i `Flashcards`.
*   **FSRS State JSON:** Przechowywanie stanu FSRS jako `TEXT` (JSON blob) upraszcza schemat, ale może utrudnić wykonywanie zapytań opartych na wewnętrznych danych tego stanu w przyszłości. Jest to świadomy kompromis na etapie MVP.
*   **Hashowanie:** Hashowanie haseł i kluczy API (bcrypt) odbywa się w warstwie aplikacji przed zapisem do bazy. Baza danych przechowuje tylko wynikowe hashe.
*   **Walidacja Danych:** Ograniczenia długości tekstu dla `username`, `Decks.name`, `Flashcards.front_text`, `Flashcards.back_text` są walidowane w warstwie aplikacji, nie w bazie danych.
