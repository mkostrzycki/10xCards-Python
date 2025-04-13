# SQLite Persistence Layer

This module provides SQLite database connectivity for the application, implementing the Repository pattern for data access.

## Connection Management

The `SqliteConnectionProvider` class manages database connections using a Singleton pattern to ensure a single connection instance throughout the application lifecycle.

### Features

- Single connection instance (Singleton pattern)
- Automatic connection cleanup on application exit
- Foreign key support enabled by default
- Thread-safe for read operations
- Proper error handling and logging
- Row factory for convenient column access

### Usage Example

```python
from Shared.infrastructure.persistence.sqlite.connection import SqliteConnectionProvider

# Initialize the connection provider (typically done once in main.py)
db_provider = SqliteConnectionProvider("data/10xcards.db")

# Get the connection in repositories
connection = db_provider.get_connection()
```

## Repository Pattern Implementation

Each domain context has its own repository implementation in `infrastructure/persistence/sqlite/repositories/`.
Repositories use the connection provider and implement the corresponding domain interface.

### Example Repository Usage

```python
from UserProfile.infrastructure.persistence.sqlite.repositories.UserRepositoryImpl import UserRepositoryImpl
from Shared.infrastructure.persistence.sqlite.connection import SqliteConnectionProvider

# Setup
db_provider = SqliteConnectionProvider("data/10xcards.db")
user_repository = UserRepositoryImpl(db_provider)

# Use the repository
user = user_repository.get_by_username("testuser")
```

## Error Handling

The persistence layer uses custom exceptions defined in each domain's `repositories/exceptions.py`:

- `RepositoryError`: Base class for repository-related errors
- `UserNotFoundError`: When a requested user doesn't exist
- `UsernameAlreadyExistsError`: When attempting to create/update with a duplicate username

### Example Error Handling

```python
from UserProfile.domain.repositories.exceptions import UsernameAlreadyExistsError

try:
    user_repository.add(new_user)
except UsernameAlreadyExistsError as e:
    print(f"Username already taken: {e}")
except RepositoryError as e:
    print(f"Database error: {e}")
```

## Best Practices

1. Always use parameterized queries (`?` placeholders) to prevent SQL injection
2. Let the connection provider manage the connection lifecycle
3. Use appropriate repository methods instead of direct SQL
4. Handle repository-specific exceptions appropriately
5. Use transactions for operations requiring multiple writes

## Testing

For unit tests, mock the connection provider:
```python
@pytest.fixture
def mock_db_provider(mocker):
    provider = mocker.Mock(spec=DbConnectionProvider)
    provider.get_connection.return_value = mocker.Mock(spec=sqlite3.Connection)
    return provider
```

For behavioral tests, use an in-memory database:
```python
connection = sqlite3.connect(':memory:') 