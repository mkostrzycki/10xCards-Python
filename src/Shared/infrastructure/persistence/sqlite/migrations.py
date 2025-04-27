import sqlite3
import logging


def run_initial_migration_if_needed(db_path: str, migration_sql_path: str, target_version: int = 1) -> None:
    """
    Runs the initial migration SQL if the database schema version is less than target_version.
    Uses PRAGMA user_version for version tracking.
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA user_version;")
        (current_version,) = cur.fetchone()
        if current_version < target_version:
            logging.info(f"Running initial migration from {migration_sql_path} (current version: {current_version})")
            with open(migration_sql_path, encoding="utf-8") as f:
                sql = f.read()
            cur.executescript(sql)
            conn.commit()
            logging.info("Migration applied successfully.")
        else:
            logging.info("Migration already applied, skipping.")
    except Exception as e:
        logging.error(f"Migration failed: {e}", exc_info=True)
        raise
    finally:
        conn.close()
