# Architecture Rules (Vertical Slice / Context-Based MVP + DDD Lite)

## Core Principles

-   **DDD Lite:** Use Ubiquitous Language (from PRD), Rich Domain Models (state+behavior), Repositories (interfaces in `domain`, implementations in `infrastructure`), Value Objects (immutable).
-   **MVP:** Model (`domain`/`application`), View (`infrastructure/ui`), Presenter (`application/presenters`). Views are passive. Layers exist *within* each context/feature slice.
-   **SOLID:** Apply strictly.
-   **Dependency Injection:** Use manual constructor/method injection. No direct dependency instantiation within classes.
-   **Separation of Concerns:** Enforce boundaries between contexts and between layers within each context.
-   **High Cohesion:** Keep code related to a specific feature/context together within its slice.

## Directory Structure (`src/`)

Organize the codebase into vertical slices based on Bounded Contexts or major features:

```
src/
|-- UserProfile/
|   |-- domain/ (Models: UserProfile, Repos: IUserProfileRepository)
|   |-- application/ (Services: ProfileService, Presenters: ProfilePresenter)
|   |-- infrastructure/ (Persistence: UserProfileRepositoryImpl, UI: ProfileView)
|   +-- __init__.py
|
|-- DeckManagement/
|   |-- domain/ (Models: Deck, Repos: IDeckRepository)
|   |-- application/ (Services: DeckService, Presenters: DeckPresenter)
|   |-- infrastructure/ (Persistence: DeckRepositoryImpl, UI: DeckListView)
|   +-- __init__.py
|
|-- CardManagement/
|   |-- domain/ (Models: Flashcard, VOs: FlashcardContent, Repos: IFlashcardRepository)
|   |-- application/ (Services: CardService, AIService?, Presenters: CardPresenter)
|   |-- infrastructure/ (Persistence: FlashcardRepositoryImpl, UI: CardView, API: AIClient)
|   +-- __init__.py
|
|-- Study/
|   |-- domain/ (Models: StudySession, ReviewLog, Services?: FSRSInterface)
|   |-- application/ (Services: StudyOrchestrationService, Presenters: StudyPresenter)
|   |-- infrastructure/ (FSRSAdapter, UI: StudyView)
|   +-- __init__.py
|
|-- Shared/ # Or Common - Cross-cutting concerns
|   |-- domain/ # Shared value objects, base classes?
|   |-- infrastructure/ # DB Connection Singleton, Logging setup?
|   |-- ui/ # Common UI utilities, base views?
|   +-- __init__.py
|
|-- main.py             # Application entry point, DI setup
+-- __init__.py
```

_(Note: The specific contents within domain/application/infrastructure for each slice are examples and will evolve.)_

## Layer Dependencies (within each slice)

-   `domain`: No dependencies on `application` or `infrastructure` from *any* slice.
-   `application`: Depends on its own `domain`. May depend on `domain` from `Shared`. Avoid direct dependencies on other slices' `application` or `infrastructure`.
-   `infrastructure`: Implements `domain` interfaces. Depends on its own `domain`, potentially `application` DTOs. Depends on `Shared/infrastructure` for common utilities.

## Inter-Context Communication

-   Keep dependencies between contexts minimal.
-   Prefer communication through application services or domain events (if used).
-   Avoid direct calls between presenters or infrastructure components of different contexts.

## Testing Structure (`tests/`)

-   Mirror the `src/` structure, separating tests by context and then by layer (unit) or type (integration, behavioral).
    -   `tests/UserProfile/unit/domain/`
    -   `tests/DeckManagement/integration/`
    -   `tests/behavioral/`

## Configuration

-   `requirements.txt`: Dependencies.
-   `pyproject.toml`: Tooling config (black, flake8, pytest).
