import sqlite3
import json
import logging
from typing import List, Dict, Any, Protocol, Optional
from datetime import datetime

from Study.domain.repositories.IReviewLogRepository import IReviewLogRepository

logger = logging.getLogger(__name__)


class DbConnectionProvider(Protocol):
    """Protocol defining the required interface for database connection providers."""

    def get_connection(self) -> sqlite3.Connection:
        """Returns a SQLite connection object."""
        ...


class ReviewLogRepositoryImpl(IReviewLogRepository):
    """Implementation of the IReviewLogRepository interface for SQLite."""

    def __init__(self, db_provider: DbConnectionProvider):
        """Initialize the repository with a database connection provider.

        Args:
            db_provider: Provider for SQLite database connections.
        """
        self._db_provider = db_provider

    def add(
        self,
        user_id: int,
        flashcard_id: int,
        review_log_data: Dict[str, Any],
        rating: int,
        reviewed_at: datetime,
        scheduler_params_json: str,
    ) -> None:
        """Add a new review log entry.

        Args:
            user_id: The ID of the user who performed the review.
            flashcard_id: The ID of the flashcard that was reviewed.
            review_log_data: The serialized FSRS ReviewLog data as a dictionary.
            rating: The rating given by the user (1-4).
            reviewed_at: The datetime when the review was performed.
            scheduler_params_json: JSON string of the FSRS scheduler parameters used for this review.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            conn = self._db_provider.get_connection()
            # Convert review_log_data to JSON string
            review_log_json = json.dumps(review_log_data)
            # Convert datetime to ISO format string
            reviewed_at_str = reviewed_at.isoformat()

            query = """
                INSERT INTO ReviewLogs (
                    user_profile_id, flashcard_id, review_log_data, 
                    fsrs_rating, reviewed_at, scheduler_params_at_review
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (user_id, flashcard_id, review_log_json, rating, reviewed_at_str, scheduler_params_json)

            cursor = self._execute_query(query, params)
            conn.commit()

            logger.debug(f"Added review log for user {user_id}, flashcard {flashcard_id}, rating {rating}")
        except Exception as e:
            conn = self._db_provider.get_connection()
            conn.rollback()
            error_msg = f"Failed to add review log: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def get_review_logs_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all review logs for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            List of dictionaries containing review log data.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            query = """
                SELECT * FROM ReviewLogs
                WHERE user_profile_id = ?
                ORDER BY reviewed_at DESC
            """
            cursor = self._execute_query(query, (user_id,))

            result = []
            for row in cursor.fetchall():
                review_log = self._row_to_dict(row)
                result.append(review_log)

            return result
        except Exception as e:
            error_msg = f"Failed to get review logs for user {user_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def get_review_logs_for_flashcard(self, user_id: int, flashcard_id: int) -> List[Dict[str, Any]]:
        """Get all review logs for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            List of dictionaries containing review log data.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            query = """
                SELECT * FROM ReviewLogs
                WHERE user_profile_id = ? AND flashcard_id = ?
                ORDER BY reviewed_at DESC
            """
            cursor = self._execute_query(query, (user_id, flashcard_id))

            result = []
            for row in cursor.fetchall():
                review_log = self._row_to_dict(row)
                result.append(review_log)

            return result
        except Exception as e:
            error_msg = f"Failed to get review logs for user {user_id}, flashcard {flashcard_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def get_last_review_log_for_flashcard(self, user_id: int, flashcard_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent review log for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            Dictionary containing review log data, or None if no logs exist.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            query = """
                SELECT * FROM ReviewLogs
                WHERE user_profile_id = ? AND flashcard_id = ?
                ORDER BY reviewed_at DESC LIMIT 1
            """
            cursor = self._execute_query(query, (user_id, flashcard_id))

            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        except Exception as e:
            error_msg = f"Failed to get last review log for user {user_id}, flashcard {flashcard_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def delete_review_logs_for_flashcard(self, user_id: int, flashcard_id: int) -> int:
        """Delete all review logs for a specific flashcard for a user.

        Args:
            user_id: The ID of the user.
            flashcard_id: The ID of the flashcard.

        Returns:
            Number of deleted rows.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            conn = self._db_provider.get_connection()
            query = """
                DELETE FROM ReviewLogs
                WHERE user_profile_id = ? AND flashcard_id = ?
            """
            cursor = self._execute_query(query, (user_id, flashcard_id))
            conn.commit()

            deleted_count = cursor.rowcount
            logger.debug(f"Deleted {deleted_count} review logs for user {user_id}, flashcard {flashcard_id}")
            return deleted_count
        except Exception as e:
            conn = self._db_provider.get_connection()
            conn.rollback()
            error_msg = f"Failed to delete review logs for user {user_id}, flashcard {flashcard_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def delete_review_logs_for_user(self, user_id: int) -> int:
        """Delete all review logs for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            Number of deleted rows.

        Raises:
            RepositoryError: If the operation fails.
        """
        try:
            conn = self._db_provider.get_connection()
            query = """
                DELETE FROM ReviewLogs
                WHERE user_profile_id = ?
            """
            cursor = self._execute_query(query, (user_id,))
            conn.commit()

            deleted_count = cursor.rowcount
            logger.debug(f"Deleted {deleted_count} review logs for user {user_id}")
            return deleted_count
        except Exception as e:
            conn = self._db_provider.get_connection()
            conn.rollback()
            error_msg = f"Failed to delete review logs for user {user_id}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg) from e

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a SQLite row to a dictionary with proper type conversions.

        Args:
            row: SQLite row object.

        Returns:
            Dictionary with review log data.
        """
        result = dict(row)
        # Parse JSON fields
        if "review_log_data" in result and result["review_log_data"]:
            result["review_log_data"] = json.loads(result["review_log_data"])
        return result

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
            # Enable row factory to get column names
            conn.row_factory = sqlite3.Row

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


class RepositoryError(Exception):
    """Base exception for repository errors."""

    pass


class DatabaseConnectionError(RepositoryError):
    """Exception raised when database connection fails."""

    pass
