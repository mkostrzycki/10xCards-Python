# Persistence Implementation Plan for Deck/DeckManagement

This document provides a comprehensive guide for implementing persistence mechanisms for the `Deck` model in the DeckManagement context. It follows the Repository Pattern, SQLite guidelines, and the project's architectural rules.

---

## 1. Przegląd Modelu/Domeny

**Kontekst:** DeckManagement

**Zakres:** Zarządzanie taliami fiszek dla zalogowanego użytkownika.

**Kluczowe operacje (FR):**
- FR-008: Tworzenie nowej talii (nazwa talii, walidacja długości).
- FR-009: Wyświetlanie listy talii przypisanych do danego użytkownika.
- FR-010: Usuwanie istniejącej talii wraz ze wszystkimi fiszkami (ON DELETE CASCADE).
- FR-011: Pobieranie szczegółów jednej talii (przegląd zawartości).

---

## 2. Model Domenowy

**Lokalizacja:** `src/DeckManagement/domain/models/Deck.py`

**Klasa:**
```python
class Deck:
    def __init__(self, id: int, user_id: int, name: str, created_at: datetime, updated_at: datetime):
        self.id = id
        self.user_id = user_id
        self.name = name  # max 50 chars
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create_new(cls, user_id: int, name: str) -> 'Deck':
        # business-level validation (length, non-empty)
        return cls(id=None, user_id=user_id, name=name.strip(),
                   created_at=None, updated_at=None)
```

**Uwagi:** Walidacja ograniczeń długości i pustego ciągu powinna odbywać się w warstwie aplikacji przed wywołaniem repozytorium.

---

## 3. Struktura Bazy Danych (odniesienie)

Tabela: **Decks** (opis w `@db-plan.md`)

| Kolumna      | Typ       | Ograniczenia                                                            |
|--------------|-----------|--------------------------------------------------------------------------|
| `id`         | INTEGER   | PRIMARY KEY AUTOINCREMENT                                                |
| `user_id`    | INTEGER   | NOT NULL, FOREIGN KEY → Users(id) ON DELETE CASCADE                      |
| `name`       | TEXT      | NOT NULL, max 50 znaków, UNIQUE(user_id, name)                           |
| `created_at` | DATETIME  | NOT NULL, DEFAULT CURRENT_TIMESTAMP                                      |
| `updated_at` | DATETIME  | NOT NULL, DEFAULT CURRENT_TIMESTAMP (trigger do automatycznej aktualizacji)|

**Indeksy:**
- `idx_decks_user_id` ON `Decks(user_id)`

---

## 4. Interfejs Repozytorium (IDeckRepository)

**Lokalizacja:** `src/DeckManagement/domain/repositories/IDeckRepository.py`

```python
from typing import List, Optional
from DeckManagement.domain.models.Deck import Deck

class IDeckRepository:
    def add(self, deck: Deck) -> Deck:
        """Dodaje nową talię. Zwraca obiekt z wypełnionym ID i znacznikami czasu."""
        raise NotImplementedError

    def get_by_id(self, deck_id: int, user_id: int) -> Optional[Deck]:
        """Pobiera talię po ID, tylko dla danego użytkownika."""
        raise NotImplementedError

    def get_by_name(self, name: str, user_id: int) -> Optional[Deck]:
        """Pobiera talię po nazwie, tylko dla danego użytkownika."""
        raise NotImplementedError

    def list_all(self, user_id: int) -> List[Deck]:
        """Zwraca wszystkie talie dla danego użytkownika."""
        raise NotImplementedError

    def update(self, deck: Deck) -> None:
        """Aktualizuje istniejącą talię (nazwa), wymagany user_id w obiekcie."""
        raise NotImplementedError

    def delete(self, deck_id: int, user_id: int) -> None:
        """Usuwa talię po ID, tylko dla danego użytkownika."""
        raise NotImplementedError
```

---

## 5. Implementacja Repozytorium (DeckRepositoryImpl)

**Lokalizacja:** `src/DeckManagement/infrastructure/persistence/sqlite/repositories/DeckRepositoryImpl.py`

**Główne założenia:**
- Otrzymuje współdzielony `sqlite3.Connection` przez wstrzykiwanie.
- Bezpośrednia logika SQL ukryta w tej klasie.
- Wyłącznie zapytania parametryzowane (`?`).
- Filtr `user_id = ?` we wszystkich metodach dot. danego użytkownika.
- Automatyczne commity w metodach (pojedyncze operacje).

```python
import sqlite3
from typing import List, Optional
from DeckManagement.domain.models.Deck import Deck
from DeckManagement.domain.repositories.IDeckRepository import IDeckRepository

class DeckRepositoryImpl(IDeckRepository):
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def add(self, deck: Deck) -> Deck:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Decks (user_id, name) VALUES (?, ?)",
            (deck.user_id, deck.name)
        )
        deck.id = cursor.lastrowid
        deck.created_at, deck.updated_at = self._fetch_timestamps(deck.id)
        self.conn.commit()
        return deck

    def get_by_id(self, deck_id: int, user_id: int) -> Optional[Deck]:
        row = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at"
            " FROM Decks WHERE id = ? AND user_id = ?",
            (deck_id, user_id)
        ).fetchone()
        return DeckMapper.from_row(row) if row else None

    def get_by_name(self, name: str, user_id: int) -> Optional[Deck]:
        row = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at"
            " FROM Decks WHERE name = ? AND user_id = ?",
            (name, user_id)
        ).fetchone()
        return DeckMapper.from_row(row) if row else None

    def list_all(self, user_id: int) -> List[Deck]:
        rows = self.conn.execute(
            "SELECT id, user_id, name, created_at, updated_at"
            " FROM Decks WHERE user_id = ? ORDER BY name",
            (user_id,)
        ).fetchall()
        return [DeckMapper.from_row(r) for r in rows]

    def update(self, deck: Deck) -> None:
        self.conn.execute(
            "UPDATE Decks SET name = ? WHERE id = ? AND user_id = ?",
            (deck.name, deck.id, deck.user_id)
        )
        self.conn.commit()

    def delete(self, deck_id: int, user_id: int) -> None:
        self.conn.execute(
            "DELETE FROM Decks WHERE id = ? AND user_id = ?",
            (deck_id, user_id)
        )
        self.conn.commit()

    def _fetch_timestamps(self, deck_id: int):
        row = self.conn.execute(
            "SELECT created_at, updated_at FROM Decks WHERE id = ?",
            (deck_id,)
        ).fetchone()
        return row[0], row[1]  # type: ignore
```

---

## 6. Mapowanie Danych

**Mapper:** `src/DeckManagement/infrastructure/persistence/sqlite/mappers/DeckMapper.py`

```python
from DeckManagement.domain.models.Deck import Deck

class DeckMapper:
    @staticmethod
    def from_row(row: tuple) -> Deck:
        id, user_id, name, created_at, updated_at = row
        return Deck(id=id, user_id=user_id, name=name,
                    created_at=created_at, updated_at=updated_at)
```

---

## 7. Zarządzanie Transakcjami

- Każda metoda repozytorium wywołuje `conn.commit()` po zakończonej operacji.
- Operacje składające się z wielu kroków (np. migracje) powinny być zarządzane w warstwie aplikacji przez `connection` lub dedykowany `TransactionManager`.

---

## 8. Obsługa Błędów

- **IntegrityError**: Rzucane przy naruszeniu `UNIQUE(user_id, name)` lub FK. Repozytorium nie przechwytuje – propaguje do serwisu aplikacji.
- **OperationalError**: Błędy SQL, można logować i opakować w niestandardowe wyjątki warstwy domenowej.
- **Brak wyniku**: `get_*` metody zwracają `None`.

**Zasady:**
- Logowanie błędów zgodnie z FR-036.
- Propagacja wyjątków do warstwy aplikacji, gdzie można je obsłużyć i wyświetlić komunikat użytkownikowi.

---

## 9. Kroki Implementacji

1. Utworzyć interfejs `IDeckRepository` w `domain/repositories`.
2. Dodać model `Deck` w `domain/models` i ewentualny VO dla nazwy.
3. Utworzyć klasę `DeckRepositoryImpl` w `infrastructure/persistence/sqlite/repositories`.
4. Zaimplementować metody CRUD z parametryzowanymi zapytaniami SQL i filtrem `user_id`.
5. Napisać mapper `DeckMapper` w `infrastructure/persistence/sqlite/mappers`.
6. Zarejestrować repozytorium w konfiguracji DI (np. w `main.py`).
7. Utworzyć testy jednostkowe dla wszystkich metod repozytorium (symulacja w pamięci lub testowa baza).
8. Zweryfikować migrację: sprawdzić istniejące skrypty w `migrations/` i strukturę tabeli `Decks`.
9. Dodać indeks `idx_decks_user_id` w migracjach, jeśli brak.
10. Przejść przez scenariusze błędów i zaktualizować logowanie.

---

*Końcowy plan powinien zostać zaimplementowany zgodnie z zasadami architektury, repozytorium oraz zabezpieczeniem izolacji danych użytkowników.*
