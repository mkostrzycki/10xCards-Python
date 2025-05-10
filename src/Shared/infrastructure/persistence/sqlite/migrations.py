"""Database migration management."""

import glob
import logging
import os
import sqlite3
from pathlib import Path
from typing import List, Tuple, cast

from ...config import MIGRATIONS_DIR


def get_current_version(conn: sqlite3.Connection) -> int:
    """Get the current database schema version.

    Args:
        conn: SQLite database connection.

    Returns:
        int: Current schema version from PRAGMA user_version.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version")
    return cast(int, cursor.fetchone()[0])


def set_version(conn: sqlite3.Connection, version: int) -> None:
    """Set the database schema version.

    Args:
        conn: SQLite database connection.
        version: Version number to set.
    """
    conn.execute(f"PRAGMA user_version = {version}")


def get_pending_migrations(current_version: int) -> List[Tuple[int, Path]]:
    """Get list of pending migrations ordered by version.

    Args:
        current_version: Current schema version.

    Returns:
        List[Tuple[int, Path]]: List of (version, path) tuples for pending migrations.
    """
    migrations = []
    migration_pattern = str(MIGRATIONS_DIR / "*.sql")

    for file_path in glob.glob(migration_pattern):
        # Extract version from SQL comments
        with open(file_path, "r") as f:
            content = f.read()
            version_line = next((line for line in content.split("\n") if "-- Version:" in line), None)
            if not version_line:
                logging.warning(f"Migration {file_path} has no version comment, skipping")
                continue

            try:
                version = int(version_line.split(":")[1].strip())
                if version > current_version:
                    migrations.append((version, Path(file_path)))
            except (ValueError, IndexError):
                logging.warning(f"Invalid version format in {file_path}, skipping")
                continue

    # Sort by version number
    migrations.sort(key=lambda x: x[0])
    return migrations


def run_migrations(db_path: str) -> None:
    """Run all pending database migrations.

    Args:
        db_path: Path to the SQLite database file.
    """
    if not os.path.exists(db_path):
        logging.info(f"Database file not found: {db_path}. Creating new database.")
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Create an empty database file by connecting and then closing
        conn = sqlite3.connect(db_path)
        conn.close()
        logging.info(f"Created new database at {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        current_version = get_current_version(conn)
        pending = get_pending_migrations(current_version)

        if not pending:
            logging.info("Database schema is up to date")
            return

        logging.info(f"Found {len(pending)} pending migrations")

        for version, migration_path in pending:
            logging.info(f"Running migration to version {version}: {migration_path.name}")

            try:
                # Read and execute migration SQL
                with open(migration_path, "r") as f:
                    sql = f.read()

                conn.executescript(sql)
                conn.commit()

                logging.info(f"Successfully migrated to version {version}")

            except sqlite3.Error as e:
                conn.rollback()
                logging.error(f"Migration failed: {str(e)}")
                raise

    finally:
        conn.close()
