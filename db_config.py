"""
Database configuration for PostgreSQL connection to Activepieces pieces database.
"""
import os
import psycopg
from psycopg.rows import dict_row
from typing import Optional
from contextlib import contextmanager


# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5433)),
    'dbname': os.getenv('DB_NAME', 'activepieces_pieces'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '7777'),
}


def get_connection():
    """
    Get a database connection using the configured settings.
    Returns a connection with dict_row for easier result handling.
    """
    try:
        conn = psycopg.connect(
            **DB_CONFIG,
            row_factory=dict_row
        )
        return conn
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
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


if __name__ == "__main__":
    # Test connection when run directly
    test_connection()

