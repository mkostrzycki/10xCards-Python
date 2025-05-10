# Python Style & Practices Rules

-   **PEP 8:** Adhere strictly. Use `black` for formatting and `flake8` for linting before commits.
-   **Type Hinting:** Mandatory and correct (`typing`). Use `mypy` for static analysis if feasible.
-   **Exceptions:** Use custom, specific exception classes (e.g., `AIError`, `DatabaseError`, `FSRSError`, inheriting from a base `AppError` if useful) instead of generic `Exception`. Raise exceptions appropriately.
-   **Logging:** Log errors with tracebacks. Log key application events and service calls. Use standard `logging` module configured in `Shared/infrastructure`.
-   **Strings:** Prefer f-strings for formatting.
-   **Defaults:** Avoid mutable default arguments in function/method definitions (use `None` and initialize inside).
-   **Imports:** Follow PEP 8 import ordering. Use absolute imports within the `src` package. Always use full import paths (e.g., `from DeckManagement.infrastructure.ui.views.deck_list_view import DeckListView`) instead of relative imports (e.g., `from ....Shared.application.session_service import SessionService`).
-   **Naming:** Use clear, descriptive names following PEP 8 conventions (snake_case for variables/functions, PascalCase for classes).