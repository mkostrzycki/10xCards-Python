# Testing Rules

-   **Frameworks:** Use `pytest` for unit and integration tests. Use `behave` for behavioral (BDD) tests.
-   **Structure:** Organize tests in the `tests/` directory, mirroring the `src/` structure by context and layer (e.g., `tests/unit/UserProfile/domain/`). Behavioral tests reside in `tests/behavioral/` (`features/`, `steps/`).
-   **Unit Tests (`pytest`):**
    -   Focus on testing individual classes/functions in isolation.
    -   Use `pytest` fixtures for setup/teardown.
    -   Use clear `assert` statements.
    -   Mock external dependencies (DB, API, FSRS, other services/contexts) using `pytest-mock` (for general mocking) and `requests-mock` (specifically for HTTP requests to AI API).
-   **Behavioral Tests (`behave`):**
    -   Write scenarios in `.feature` files using Gherkin syntax (Given/When/Then) based on User Stories (PRD).
    -   Implement step definitions in `tests/behavioral/steps/` that exercise the application logic, potentially through application services or presenters.
-   **Coverage:** Aim for high test coverage of critical domain logic, application services, and presenter logic. Use tools like `pytest-cov` to monitor coverage.
-   **Naming:** Test functions should start with `test_`. Test files should start with `test_` or end with `_test.py`. 
-   **Testing Exceptions:**
    -   When testing code that uses exception chaining (`raise ExceptionA from ExceptionB`), standard `pytest.raises()` might not work correctly.
    -   For chained exceptions, use direct `try/except` with type name checking: `assert type(e).__name__ == "ExpectedExceptionName"` instead of `isinstance(e, ExpectedExceptionClass)`. 