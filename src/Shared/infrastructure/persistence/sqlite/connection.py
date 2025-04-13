import sqlite3
import logging
import atexit
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SqliteConnectionProvider:
    """
    Singleton provider for SQLite database connections.
    Ensures single connection instance and proper cleanup on application exit.
    """

    _instance: Optional["SqliteConnectionProvider"] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls, db_path: str) -> "SqliteConnectionProvider":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection(db_path)
        return cls._instance

    def _init_connection(self, db_path: str) -> None:
        """
        Initialize the SQLite connection with proper settings.

        Args:
            db_path: Path to the SQLite database file
        """
        try:
            # Ensure the directory exists
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Initializing SQLite connection to {db_path}")
            self._connection = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False,  # SQLite is thread-safe for reads
            )

            # Enable foreign key support
            self._connection.execute("PRAGMA foreign_keys = ON")

            # Use Row factory for better column access
            self._connection.row_factory = sqlite3.Row

            # Register cleanup on application exit
            atexit.register(self._cleanup)

            logger.info("SQLite connection initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Failed to initialize SQLite connection: {e}", exc_info=True)
            raise RuntimeError(f"Database connection failed: {e}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get the SQLite connection instance.

        Returns:
            SQLite connection object

        Raises:
            RuntimeError: If connection is not initialized or was closed
        """
        if self._connection is None:
            logger.error("Attempting to get connection but none is initialized")
            raise RuntimeError("Database connection is not initialized")
        return self._connection

    def _cleanup(self) -> None:
        """Clean up database connection on application exit."""
        if self._connection is not None:
            try:
                logger.info("Closing SQLite connection")
                self._connection.close()
                self._connection = None
            except sqlite3.Error as e:
                logger.error(f"Error closing SQLite connection: {e}", exc_info=True)

    def __del__(self) -> None:
        """Ensure connection is closed on object destruction."""
        self._cleanup()
