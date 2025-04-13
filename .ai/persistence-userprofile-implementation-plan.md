# Plan Implementacji Persystencji dla Domeny: UserProfile

## 1. Przegląd Modelu/Domeny

Domena `UserProfile` odpowiada za zarządzanie profilami użytkowników aplikacji. Obejmuje tworzenie, uwierzytelnianie (opcjonalne hasło) oraz przechowywanie podstawowych informacji o użytkowniku, takich jak nazwa i klucz API. Dane użytkownika są centralnym punktem, do którego odnoszą się inne dane w systemie (np. talie).

## 2. Model Domenowy

Zgodnie z zasadami DDD Lite i strukturą projektu (`src/UserProfile/domain/models/user.py`):

```python
# src/UserProfile/domain/models/user.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]  # None before saving to DB
    username: str
    hashed_password: Optional[str] = None
    hashed_api_key: Optional[str] = None
    # created_at, updated_at can be handled by DB/repo or added if needed in domain logic
```

## 3. Struktura Bazy Danych (odniesienie)

Persystencja modelu `User` opiera się na tabeli `Users` zdefiniowanej w `@db-plan.md`. Kluczowe kolumny to `id`, `username` (UNIQUE), `hashed_password`, `hashed_api_key`, `created_at`, `updated_at`.

## 4. Interfejs Repozytorium (`IUserRepository`)

Zgodnie z zasadami architektury, interfejs zostanie zdefiniowany w `src/UserProfile/domain/repositories/IUserRepository.py`.

```python
# src/UserProfile/domain/repositories/IUserRepository.py
from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.user import User

class IUserRepository(ABC):

    @abstractmethod
    def add(self, user: User) -> User:
        """Adds a new user to the repository. Returns the user with the assigned ID."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieves a user by their ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        """Retrieves a list of all users (or basic user info needed for selection)."""
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        """Updates an existing user's data (identified by user.id)."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Deletes a user by their ID."""
        pass

```

## 5. Implementacja Repozytorium (`UserRepositoryImpl`)

Implementacja zostanie umieszczona w `src/UserProfile/infrastructure/persistence/sqlite/repositories/UserRepositoryImpl.py`.

-   **Zależności:** Implementacja będzie przyjmować w konstruktorze dostawcę połączenia/kursora do **współdzielonej bazy danych** SQLite (`data/10xcards.db`).
-   **Zapytania SQL:** Wszystkie zapytania SQL **muszą** używać **parametryzacji (`?`)**, aby zapobiec SQL Injection.
-   **Izolacja Danych:** Tabela `Users` przechowuje dane **wszystkich** użytkowników. W przeciwieństwie do repozytoriów `Deck` czy `Flashcard`, **operacje w `UserRepositoryImpl` generalnie nie wymagają filtrowania po `user_id`**, ponieważ:
    -   `add` tworzy nowego, globalnego użytkownika.
    -   `get_by_id` i `get_by_username` z natury rzeczy pobierają konkretnego użytkownika.
    -   `list_all` ma na celu zwrócenie listy wszystkich profili.
    -   `update` i `delete` operują na użytkowniku identyfikowanym przez `id`.
    Izolacja danych w systemie jest osiągana przez filtrowanie `user_id` w repozytoriach operujących na danych podrzędnych (np. `DeckRepositoryImpl`).
-   **Przykładowe Zapytania SQL (szkielet):**
    -   `add`: `INSERT INTO Users (username, hashed_password, hashed_api_key) VALUES (?, ?, ?) RETURNING id;` (lub `SELECT last_insert_rowid();`)
    -   `get_by_id`: `SELECT id, username, hashed_password, hashed_api_key FROM Users WHERE id = ?;`
    -   `get_by_username`: `SELECT id, username, hashed_password, hashed_api_key FROM Users WHERE username = ?;`
    -   `list_all`: `SELECT id, username FROM Users ORDER BY username;` (Zwracamy tylko potrzebne dane dla listy wyboru)
    -   `update`: `UPDATE Users SET username = ?, hashed_password = ?, hashed_api_key = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;`
    -   `delete`: `DELETE FROM Users WHERE id = ?;`

## 6. Mapowanie Danych

Mapowanie między obiektem `User` a wierszem tabeli `Users` jest bezpośrednie.
-   Implementacja repozytorium będzie odpowiedzialna za tworzenie obiektów `User` z danych pobranych z bazy (wyników zapytań `SELECT`).
-   Przy zapisie (`add`, `update`), dane z obiektu `User` zostaną użyte jako parametry w zapytaniach `INSERT` lub `UPDATE`.
-   **Hashowanie** haseł i kluczy API odbywa się **poza** repozytorium (np. w serwisie aplikacyjnym) przed przekazaniem obiektu `User` do zapisu. Repozytorium operuje na już zahashowanych wartościach lub `None`.

## 7. Zarządzanie Transakcjami

Standardowe operacje CRUD na pojedynczym użytkowniku (`add`, `get_*`, `update`, `delete`) są zazwyczaj atomowe na poziomie pojedynczego zapytania SQL. Jawne zarządzanie transakcjami (`connection.commit()`, `connection.rollback()`) w `UserRepositoryImpl` nie jest wymagane dla tych podstawowych metod. Jeśli operacje biznesowe wyższego poziomu (w serwisach aplikacyjnych) będą wymagały atomowego wykonania wielu operacji (np. dodanie użytkownika i jego domyślnej talii), transakcja powinna być zarządzana przez ten serwis, obejmując wywołania wielu repozytoriów.

## 8. Obsługa Błędów

Implementacja repozytorium musi być przygotowana na obsługę i propagację błędów SQLite:
-   `sqlite3.IntegrityError`: Szczególnie ważne przy `add` i `update` w kontekście naruszenia ograniczenia `UNIQUE` na `username`. Repozytorium powinno przechwycić ten błąd i albo rzucić go dalej, albo opakować w bardziej specyficzny wyjątek domenowy (np. `UsernameAlreadyExistsError`).
-   `sqlite3.Error` (lub inne podklasy): Ogólne błędy połączenia, składni SQL itp. Powinny być logowane i propagowane w górę stosu wywołań.
-   Metody `get_*` zwracające `Optional[User]` powinny zwracać `None`, jeśli użytkownik nie zostanie znaleziony.

## 9. Kroki Implementacji

1.  Zdefiniuj klasę `User` w `src/UserProfile/domain/models/user.py`.
2.  Zdefiniuj interfejs `IUserRepository` w `src/UserProfile/domain/repositories/IUserRepository.py`.
3.  Utwórz plik implementacji `src/UserProfile/infrastructure/persistence/sqlite/repositories/UserRepositoryImpl.py`.
4.  Zaimplementuj klasę `UserRepositoryImpl`, dziedzicząc po `IUserRepository`.
5.  Wstrzyknij zależność do dostawcy połączenia/kursora SQLite w konstruktorze `UserRepositoryImpl`.
6.  Zaimplementuj metody interfejsu, używając **parametryzowanych zapytań SQL** do interakcji z tabelą `Users`.
7.  Zaimplementuj logikę mapowania danych między wierszami tabeli a obiektami `User`.
8.  Dodaj obsługę błędów, w szczególności `sqlite3.IntegrityError` dla `UNIQUE(username)`.
9.  Napisz testy jednostkowe dla `UserRepositoryImpl` (wymaga mockowania połączenia/kursora i wyników zapytań) w `tests/unit/UserProfile/infrastructure/persistence/sqlite/repositories/`.
10. Rozważ testy integracyjne sprawdzające poprawność interakcji z rzeczywistą (testową) bazą danych.
