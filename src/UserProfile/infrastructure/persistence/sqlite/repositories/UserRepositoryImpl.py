import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Protocol

from UserProfile.domain.models.user import User
from UserProfile.domain.repositories.IUserRepository import IUserRepository
from UserProfile.domain.repositories.exceptions import (
    RepositoryError,
    DatabaseConnectionError,
    DatabaseIntegrityError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
    InvalidUserDataError,
)

logger = logging.getLogger(__name__)


class DbConnectionProvider(Protocol):
    """Protocol defining the required interface for database connection providers."""

    def get_connection(self) -> sqlite3.Connection:
        """Returns a SQLite connection object."""
        ...


class UserRepositoryImpl(IUserRepository):
    """
    SQLite implementation of the IUserRepository interface.
    Handles all database operations for User entities.
    """

    def __init__(self, db_provider: DbConnectionProvider):
        """
        Initialize the repository with a database connection provider.

        Args:
            db_provider: Object providing SQLite database connections
        """
        self._db_provider = db_provider
        logger.debug("UserRepositoryImpl initialized with database provider")

    def _map_row_to_user(self, row: sqlite3.Row) -> User:
        """
        Maps a database row to a User domain entity.

        Args:
            row: SQLite row containing user data

        Returns:
            User domain entity

        Raises:
            InvalidUserDataError: If row data is invalid or missing required fields
        """
        try:
            return User(
                id=row["id"],
                username=row["username"],
                hashed_password=row["hashed_password"] if "hashed_password" in row.keys() else None,
                encrypted_api_key=row["encrypted_api_key"] if "encrypted_api_key" in row.keys() else None,
                default_llm_model=row["default_llm_model"] if "default_llm_model" in row.keys() else None,
                app_theme=row["app_theme"] if "app_theme" in row.keys() else None,
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        except (KeyError, ValueError) as e:
            error_msg = f"Failed to map database row to User: {e}"
            logger.error(error_msg)
            raise InvalidUserDataError(error_msg) from e

    def _execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Executes a SQL query with error handling.

        Args:
            query: SQL query string with ? placeholders
            params: Query parameters

        Returns:
            SQLite cursor

        Raises:
            DatabaseConnectionError: If connection fails or is not initialized
            RepositoryError: If query execution fails
        """
        try:
            conn = self._db_provider.get_connection()
            # Enable foreign key support for each connection
            conn.execute("PRAGMA foreign_keys = ON")
            logger.debug(f"Executing query: {query} with params: {params}")
            return conn.execute(query, params)
        except (RuntimeError, sqlite3.OperationalError) as e:
            error_msg = f"Database connection error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg) from e
        except sqlite3.Error as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def add(self, user: User) -> User:
        """
        Adds a new user to the repository.

        Args:
            user: User entity to persist (without id)

        Returns:
            User entity with assigned id and timestamps

        Raises:
            InvalidUserDataError: If user data is invalid
            UsernameAlreadyExistsError: If username is not unique
            DatabaseConnectionError: If connection fails
            RepositoryError: If operation fails for other reasons
        """
        if not user.username:
            raise InvalidUserDataError("Username is required")

        query = """
            INSERT INTO Users (username, hashed_password, encrypted_api_key, default_llm_model, app_theme)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            logger.info(f"Adding new user with username: {user.username}")
            conn = self._db_provider.get_connection()
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute(query, (
                user.username, 
                user.hashed_password, 
                user.encrypted_api_key,
                user.default_llm_model,
                user.app_theme
            ))
            conn.commit()

            # Get the newly created user with timestamps
            created_user = self.get_by_id(cursor.lastrowid)  # type: ignore[arg-type]
            if created_user is None:  # This should never happen
                raise RepositoryError("Failed to retrieve newly created user")

            logger.info(f"Successfully created user with id: {created_user.id}")
            return created_user

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: Users.username" in str(e):
                error_msg = f"Username '{user.username}' already exists"
                logger.warning(error_msg)
                raise UsernameAlreadyExistsError(user.username) from e
            error_msg = f"Database integrity error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseIntegrityError(error_msg) from e
        except (RuntimeError, sqlite3.OperationalError) as e:
            error_msg = f"Database connection error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg) from e
        except sqlite3.Error as e:
            error_msg = f"Failed to add user: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            User entity if found, None otherwise

        Raises:
            DatabaseConnectionError: If connection fails
            RepositoryError: If query fails
            InvalidUserDataError: If retrieved data is invalid
        """
        query = """
            SELECT id, username, hashed_password, encrypted_api_key, default_llm_model, app_theme, created_at, updated_at
            FROM Users
            WHERE id = ?
        """
        try:
            logger.debug(f"Fetching user by id: {user_id}")
            cursor = self._execute_query(query, (user_id,))
            row = cursor.fetchone()

            if row is None:
                logger.debug(f"No user found with id: {user_id}")
                return None

            user = self._map_row_to_user(row)
            logger.debug(f"Successfully fetched user: {user.username}")
            return user

        except (DatabaseConnectionError, InvalidUserDataError):
            raise
        except Exception as e:
            error_msg = f"Failed to get user by id {user_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by their username.

        Args:
            username: The unique username to search for

        Returns:
            User entity if found, None otherwise

        Raises:
            DatabaseConnectionError: If connection fails
            RepositoryError: If query fails
            InvalidUserDataError: If retrieved data is invalid
        """
        query = """
            SELECT id, username, hashed_password, encrypted_api_key, default_llm_model, app_theme, created_at, updated_at
            FROM Users
            WHERE username = ?
        """
        try:
            logger.debug(f"Fetching user by username: {username}")
            cursor = self._execute_query(query, (username,))
            row = cursor.fetchone()

            if row is None:
                logger.debug(f"No user found with username: {username}")
                return None

            user = self._map_row_to_user(row)
            logger.debug(f"Successfully fetched user: {user.username}")
            return user

        except (DatabaseConnectionError, InvalidUserDataError):
            raise
        except Exception as e:
            error_msg = f"Failed to get user by username '{username}': {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def list_all(self) -> List[User]:
        """
        Retrieves all users from the repository.

        Returns:
            List of all User entities

        Raises:
            DatabaseConnectionError: If connection fails
            RepositoryError: If query fails
            InvalidUserDataError: If retrieved data is invalid
        """
        query = """
            SELECT id, username, hashed_password, encrypted_api_key, default_llm_model, app_theme, created_at, updated_at
            FROM Users
            ORDER BY username
        """
        try:
            logger.debug("Fetching all users")
            cursor = self._execute_query(query)
            users = [self._map_row_to_user(row) for row in cursor.fetchall()]
            logger.debug(f"Successfully fetched {len(users)} users")
            return users

        except (DatabaseConnectionError, InvalidUserDataError):
            raise
        except Exception as e:
            error_msg = f"Failed to list users: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def update(self, user: User) -> None:
        """
        Updates an existing user's data.

        Args:
            user: User entity with updated data (must have id)

        Raises:
            InvalidUserDataError: If user data is invalid
            UserNotFoundError: If user with given id doesn't exist
            UsernameAlreadyExistsError: If new username is not unique
            DatabaseConnectionError: If connection fails
            RepositoryError: If operation fails for other reasons
        """
        if user.id is None:
            raise InvalidUserDataError("Cannot update user without id")

        if not user.username:
            raise InvalidUserDataError("Username is required")

        # First check if user exists
        if self.get_by_id(user.id) is None:
            raise UserNotFoundError(user.id)

        query = """
            UPDATE Users
            SET username = ?,
                hashed_password = ?,
                encrypted_api_key = ?,
                default_llm_model = ?,
                app_theme = ?
            WHERE id = ?
        """
        try:
            logger.info(f"Updating user {user.id} with username: {user.username}")
            logger.info(
                f"User object dump: id={user.id}, username={user.username}, "
                f"has_password={'YES' if user.hashed_password else 'NO'}, "
                f"has_api_key={'YES' if user.encrypted_api_key else 'NO'}, "
                f"default_llm_model={user.default_llm_model}, "
                f"app_theme={user.app_theme}"
            )

            conn = self._db_provider.get_connection()
            conn.execute("PRAGMA foreign_keys = ON")

            # Log detailed information about the values being saved
            logger.info(
                f"User {user.id} preferences - default_llm_model: {user.default_llm_model}, app_theme: {user.app_theme}"
            )

            # Add specific logging for API key
            api_key_status = "NOT SET"
            if user.encrypted_api_key is not None:
                api_key_status = f"SET (length: {len(user.encrypted_api_key)}, type: {type(user.encrypted_api_key)})"
                # Try to convert the key to hex for debugging
                try:
                    hex_sample = user.encrypted_api_key[:10].hex() if hasattr(user.encrypted_api_key, "hex") else "N/A"
                    logger.info(f"API key start (hex): {hex_sample}...")
                except Exception as e:
                    logger.error(f"Could not convert API key to hex: {str(e)}")
            logger.info(f"User {user.id} encrypted_api_key: {api_key_status}")

            # Prepare parameters, ensuring proper type conversion
            params = [
                user.username,
                user.hashed_password,
                user.encrypted_api_key,  # This might need explicit conversion
                user.default_llm_model,
                user.app_theme,
                user.id,
            ]

            # Ensure encrypted_api_key is bytes or None
            if params[2] is not None and not isinstance(params[2], bytes):
                logger.error(f"API key has wrong type: {type(params[2])}, converting to bytes")
                try:
                    if isinstance(params[2], str):
                        params[2] = params[2].encode("utf-8")
                    else:
                        params[2] = bytes(params[2])
                except Exception as e:
                    logger.error(f"Failed to convert API key to bytes: {str(e)}")
                    params[2] = None

            # Log parameter types for debugging
            logger.debug(
                f"Parameter types: username={type(params[0])}, "
                f"hashed_password={type(params[1])}, "
                f"encrypted_api_key={type(params[2])}, "
                f"default_llm_model={type(params[3])}, "
                f"app_theme={type(params[4])}, "
                f"id={type(params[5])}"
            )

            cursor = conn.execute(query, params)
            conn.commit()

            row_count = cursor.rowcount
            logger.info(f"Update affected {row_count} rows")

            if row_count == 0:  # Should never happen as we checked existence
                error_msg = f"Failed to update user {user.id}"
                logger.error(error_msg)
                raise RepositoryError(error_msg)

            logger.info(f"Successfully updated user {user.id}")

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: Users.username" in str(e):
                error_msg = f"Username '{user.username}' already exists"
                logger.warning(error_msg)
                raise UsernameAlreadyExistsError(user.username) from e
            error_msg = f"Database integrity error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseIntegrityError(error_msg) from e
        except (RuntimeError, sqlite3.OperationalError) as e:
            error_msg = f"Database connection error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg) from e
        except sqlite3.Error as e:
            error_msg = f"Failed to update user: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def delete(self, user_id: int) -> None:
        """
        Deletes a user by their ID.

        Args:
            user_id: The unique identifier of the user to delete

        Raises:
            UserNotFoundError: If user with given id doesn't exist
            DatabaseConnectionError: If connection fails
            RepositoryError: If operation fails for other reasons
        """
        # First check if user exists
        if self.get_by_id(user_id) is None:
            raise UserNotFoundError(user_id)

        query = "DELETE FROM Users WHERE id = ?"
        try:
            logger.info(f"Deleting user with id: {user_id}")
            conn = self._db_provider.get_connection()
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute(query, (user_id,))
            conn.commit()

            if cursor.rowcount == 0:  # Should never happen as we checked existence
                error_msg = f"Failed to delete user {user_id}"
                logger.error(error_msg)
                raise RepositoryError(error_msg)

            logger.info(f"Successfully deleted user {user_id}")

        except (RuntimeError, sqlite3.OperationalError) as e:
            error_msg = f"Database connection error: {e}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg) from e
        except sqlite3.Error as e:
            error_msg = f"Failed to delete user: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e
