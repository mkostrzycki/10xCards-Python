# Database (SQLite) Rules

-   **Repository Pattern:**
    -   Define repository interfaces in the `domain/repositories/` directory of the relevant context (e.g., `src/DeckManagement/domain/repositories/IDeckRepository.py`).
    -   Implement concrete repositories using SQLite in `infrastructure/persistence/sqlite/repositories/` (e.g., `src/DeckManagement/infrastructure/persistence/sqlite/repositories/DeckRepositoryImpl.py`).
    -   Repositories encapsulate all SQL logic.
    -   Inject the database connection/cursor provider into repositories.
-   **SQL Queries:** Use **parameterized queries** exclusively (`?` placeholders) to prevent SQL injection vulnerabilities. Do NOT use string formatting (f-strings, `%`, `.format()`) to build SQL queries with user data.
-   **Connection Management:** Implement a **Singleton** pattern for managing the SQLite database connection (`sqlite3.Connection`). This can reside in `Shared/infrastructure/persistence/sqlite/` or a similar shared location. Ensure proper connection closing on application exit.
-   **Migrations:**
    -   Place migration SQL scripts in `infrastructure/persistence/sqlite/migrations/`.
    -   Follow this naming convention: `YYYYMMDDHHmmss_short_description.sql` where YYYY, MM, DD, HH, mm and ss are year, month, day, hour, minutes and seconds.
    -   Implement a mechanism (e.g., in `main.py` or a dedicated script) to apply pending migrations sequentially on application startup by tracking the current schema version (e.g., using `PRAGMA user_version`).
-   **Transactions:** Use transactions (`connection.commit()`, `connection.rollback()`) for operations involving multiple database writes to ensure atomicity.
