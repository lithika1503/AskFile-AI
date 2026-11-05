"""SQLite connection manager with WAL mode and transaction support."""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from config import DATABASE_PATH
from utils.logging_config import logger

_local = threading.local()

def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Returns a thread-local SQLite connection."""
    conn = getattr(_local, "connection", None)
    if conn is None:
        conn = sqlite3.connect(
            str(db_path),
            timeout=30.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        # Enable Foreign Key constraints and WAL mode
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        _local.connection = conn
    return conn

@contextmanager
def get_db(db_path: Path = DATABASE_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe database transactions."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
