# Plan wdrożenia persystencji dla modelu Flashcard

## 1. Przegląd Modelu/Domeny
Model **Flashcard** reprezentuje pojedynczą fiszkę należącą do określonej talii użytkownika. Główne założenia:
- CRUD operacje: tworzenie, odczyt, aktualizacja, usuwanie.
- Inicjalizacja i aktualizacja stanu FSRS (algorytm `Py-FSRS`).
- Obsługa różnych źródeł fiszki (`manual`, `ai-generated`, `ai-edited`).
- Izolacja danych poprzez `deck_id`, który łączy fiszkę z talią przypisaną do użytkownika.

## 2. Model Domenowy
Plik: `src/CardManagement/domain/models/Flashcard.py`

```python
from datetime import datetime
from typing import Optional

class Flashcard:
    def __init__(
        self,
        id: Optional[int],
        deck_id: int,
        front_text: str,
        back_text: str,
        fsrs_state: Optional[str],  # JSON blob or None
        source: str,  # 'manual' | 'ai-generated' | 'ai-edited'
        ai_model_name: Optional[str],
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.deck_id = deck_id
        self.front_text = front_text
        self.back_text = back_text
        self.fsrs_state = fsrs_state
        self.source = source
        self.ai_model_name = ai_model_name
        self.created_at = created_at
        self.updated_at = updated_at
```

### Uwagi
- `fsrs_state` jako tekst JSON, deserializowany do VO w warstwie aplikacji.
- Walidacja długości pól (`front_text <= 200`, `back_text <= 500`) w serwisach aplikacji.

## 3. Struktura Bazy Danych (odniesienie)
Oparcie na specyfikacji z `.ai/db-plan.md`:

| Kolumna        | Typ        | Ograniczenia                                               |
| -------------- | ---------- | ---------------------------------------------------------- |
| `id`           | INTEGER    | PRIMARY KEY AUTOINCREMENT                                  |
| `deck_id`      | INTEGER    | NOT NULL, FK → Decks(id) ON DELETE CASCADE                 |
| `front_text`   | TEXT       | NOT NULL                                                   |
| `back_text`    | TEXT       | NOT NULL                                                   |
| `fsrs_state`   | TEXT       | NULL (JSON blob)                                           |
| `source`       | TEXT       | NOT NULL, CHECK IN ('manual','ai-generated','ai-edited')  |
| `ai_model_name`| TEXT       | NULL                                                       |
| `created_at`   | DATETIME   | NOT NULL, DEFAULT CURRENT_TIMESTAMP                        |
| `updated_at`   | DATETIME   | NOT NULL, DEFAULT CURRENT_TIMESTAMP                        |

**Indeksy rekomendowane**:
- `idx_flashcards_deck_id` ON `Flashcards(deck_id)`

## 4. Interfejs Repozytorium (`IFlashcardRepository`)
Plik: `src/CardManagement/domain/repositories/IFlashcardRepository.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.CardManagement.domain.models.Flashcard import Flashcard

class IFlashcardRepository(ABC):
    @abstractmethod
    def add(self, flashcard: Flashcard) -> Flashcard:
        """Dodaje nową fiszkę i zwraca instancję ze wstawionym 'id' oraz timestampami."""

    @abstractmethod
    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        """Pobiera fiszkę po jej ID. Zwraca None, jeśli nie istnieje."""

    @abstractmethod
    def list_by_deck_id(self, deck_id: int) -> List[Flashcard]:
        """Zwraca listę fiszek należących do podanej talii."""

    @abstractmethod
    def update(self, flashcard: Flashcard) -> None:
        """Aktualizuje istniejącą fiszkę (treść lub stan FSRS)."""

    @abstractmethod
    def delete(self, flashcard_id: int) -> None:
        """Usuwa fiszkę o podanym ID."""

    @abstractmethod
    def get_fsrs_card_data_for_deck(self, deck_id: int) -> List[Tuple[int, Optional[str]]]:
        """Pobiera krotki (flashcard_id, fsrs_state) dla wszystkich fiszek w talii."""
```

**Zasady**:
- Parametryzowane zapytania SQL (`?`) – brak f-stringów.
- Brak bezpośredniej izolacji po `user_id`; warstwa serwisowa sprawdza, że `deck_id` należy do zalogowanego użytkownika.

## 5. Implementacja Repozytorium (`FlashcardRepositoryImpl`)
Plik: `src/CardManagement/infrastructure/persistence/sqlite/repositories/FlashcardRepositoryImpl.py`

```python
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from src.CardManagement.domain.models.Flashcard import Flashcard
from src.CardManagement.domain.repositories.IFlashcardRepository import IFlashcardRepository

class FlashcardRepositoryImpl(IFlashcardRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        # PRAGMA foreign_keys = ON jest ustawiane przy inicjalizacji singletona połączenia

    def add(self, flashcard: Flashcard) -> Flashcard:
        cursor = self._conn.cursor()
        query = (
            "INSERT INTO Flashcards"
            " (deck_id, front_text, back_text, fsrs_state, source, ai_model_name)"
            " VALUES (?, ?, ?, ?, ?, ?)"
        )
        cursor.execute(
            query,
            (
                flashcard.deck_id,
                flashcard.front_text,
                flashcard.back_text,
                flashcard.fsrs_state,
                flashcard.source,
                flashcard.ai_model_name,
            ),
        )
        flashcard_id = cursor.lastrowid
        self._conn.commit()
        return self.get_by_id(flashcard_id)

    def get_by_id(self, flashcard_id: int) -> Optional[Flashcard]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM Flashcards WHERE id = ?", (flashcard_id,)
        )
        row = cursor.fetchone()
        return _row_to_flashcard(row) if row else None

    def list_by_deck_id(self, deck_id: int) -> List[Flashcard]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM Flashcards WHERE deck_id = ? ORDER BY created_at ASC", (deck_id,)
        )
        return [_row_to_flashcard(row) for row in cursor.fetchall()]

    def update(self, flashcard: Flashcard) -> None:
        cursor = self._conn.cursor()
        query = (
            "UPDATE Flashcards SET front_text = ?, back_text = ?, fsrs_state = ?, source = ?, ai_model_name = ?, updated_at = CURRENT_TIMESTAMP"
            " WHERE id = ?"
        )
        cursor.execute(
            query,
            (
                flashcard.front_text,
                flashcard.back_text,
                flashcard.fsrs_state,
                flashcard.source,
                flashcard.ai_model_name,
                flashcard.id,
            ),
        )
        self._conn.commit()

    def delete(self, flashcard_id: int) -> None:
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM Flashcards WHERE id = ?", (flashcard_id,))
        self._conn.commit()

    def get_fsrs_card_data_for_deck(self, deck_id: int) -> List[Tuple[int, Optional[str]]]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, fsrs_state FROM Flashcards WHERE deck_id = ?", (deck_id,)
        )
        return cursor.fetchall()

# ... existing code ...

def _row_to_flashcard(row: sqlite3.Row) -> Flashcard:
    return Flashcard(
        id=row[0],
        deck_id=row[1],
        front_text=row[2],
        back_text=row[3],
        fsrs_state=row[4],
        source=row[5],
        ai_model_name=row[6],
        created_at=datetime.fromisoformat(row[7]),
        updated_at=datetime.fromisoformat(row[8]),
    )
```

## 6. Mapowanie Danych
- Funkcja `_row_to_flashcard` konwertuje `sqlite3.Row` na obiekt domenowy.
- `fsrs_state` przechowywane i zwracane jako JSON-text; deserializacja odbywa się w warstwie aplikacji do VO.

## 7. Zarządzanie Transakcjami
- Pojedyncze CRUD (add/update/delete) kończą się `commit()` wewnątrz repozytorium.
- W operacjach wieloetapowych (np. generowanie wielu fiszek AI) transakcja i rollback powinny być zarządzane w warstwie serwisu aplikacji.

## 8. Obsługa Błędów
- `sqlite3.IntegrityError` (np. naruszenie unikalności lub FK) jest łapany w serwisach wyższego poziomu i propagowany jako wyjątek domenowy.
- Przy błędach komunikacji z DB, repozytorium nie wykonuje `commit()` i pozwala na rollback w warstwie serwisu.

## 9. Kroki Implementacji
1. Utworzyć klasę domenową `Flashcard` w kontekście `CardManagement/domain/models`.
2. Zdefiniować interfejs `IFlashcardRepository` w `domain/repositories`.
3. Implementować `FlashcardRepositoryImpl` według wzorca Repozytorium w `infrastructure/persistence/sqlite/repositories`.
4. Dodać funkcję pomocniczą `_row_to_flashcard` do mapowania.
5. Zapewnić, że singleton połączenia SQLite w `Shared/infrastructure` włącza `PRAGMA foreign_keys = ON;`.
6. Napisać testy jednostkowe dla wszystkich metod repozytorium, w tym scenariuszy błędów `IntegrityError`.
7. Zweryfikować migrację początkową (`initial_schema.sql`) pod kątem struktury tabeli `Flashcards`.
8. Zintegrować repozytorium z serwisami aplikacji i zaimplementować obsługę transakcji wieloetapowych.
