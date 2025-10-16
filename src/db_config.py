"""
Database configuration for SQLite connection to Activepieces pieces database.

Migrated from PostgreSQL to SQLite for easier deployment.
Original PostgreSQL config backed up in db_config_postgresql_backup.py
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional
import json

# SQLite database file path (updated to use new activepieces-pieces.db structure)
DB_FILE = os.getenv('SQLITE_DB_FILE', 'data/activepieces.db')


def get_connection():
    """
    Get a SQLite database connection.
    Returns a connection with Row factory for dict-like access.
    """
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        # Enable dict-like row access
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"[WARNING] Database connection failed: {e}")
        raise


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor.
    Automatically handles connection and cursor cleanup.
    
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM pieces")
            results = cur.fetchall()
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            cur.close()
            conn.close()


def dict_from_row(row) -> dict:
    """Convert a sqlite3.Row to a regular dictionary."""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def parse_json_fields(row: dict, json_fields: list) -> dict:
    """
    Parse JSON text fields back to Python objects.
    
    Args:
        row: Dictionary row from database
        json_fields: List of field names that contain JSON text
    
    Returns:
        Row dict with JSON fields parsed
    """
    if not row:
        return row
    
    result = dict(row)
    for field in json_fields:
        if field in result and result[field]:
            try:
                result[field] = json.loads(result[field])
            except (json.JSONDecodeError, TypeError):
                # Keep original value if not valid JSON
                pass
    return result


def test_connection() -> bool:
    """
    Test the database connection and return True if successful.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM pieces")
            result = cur.fetchone()
            count = result['count'] if result else 0
            print(f"[OK] Database connected successfully! Found {count} pieces.")
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


def get_database_info():
    """
    Get information about the database for diagnostics.
    """
    try:
        with get_db_cursor() as cur:
            # Get all tables
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row['name'] for row in cur.fetchall()]
            
            print(f"\n{'=' * 60}")
            print(f"SQLite Database: {DB_FILE}")
            print(f"{'=' * 60}\n")
            
            print("Tables:")
            for table in tables:
                cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cur.fetchone()['count']
                print(f"  - {table}: {count} records")
            
            # Get database size
            size_bytes = os.path.getsize(DB_FILE)
            size_mb = size_bytes / (1024 * 1024)
            print(f"\nDatabase size: {size_mb:.2f} MB")
            print(f"{'=' * 60}\n")
            
    except Exception as e:
        print(f"[ERROR] Could not get database info: {e}")


if __name__ == "__main__":
    # Test connection when run directly
    if test_connection():
        get_database_info()
