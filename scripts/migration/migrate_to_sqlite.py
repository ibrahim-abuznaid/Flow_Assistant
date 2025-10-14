"""
Migration script: PostgreSQL to SQLite
This script exports data from PostgreSQL and imports it into SQLite
"""
import sqlite3
import json
from datetime import datetime
from db_config import get_db_cursor

# SQLite database file
SQLITE_DB = "activepieces.db"

def create_sqlite_schema(conn):
    """Create SQLite schema matching PostgreSQL structure"""
    cursor = conn.cursor()
    
    print("Creating SQLite schema...")
    
    # Pieces table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pieces (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            description TEXT,
            logo_url TEXT,
            version TEXT,
            minimum_supported_release TEXT,
            auth_type TEXT,
            categories TEXT,  -- JSON array as text
            authors TEXT,     -- JSON array as text
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT     -- JSON as text
        )
    """)
    
    # Actions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY,
            piece_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            requires_auth INTEGER,  -- 0 or 1 for boolean
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT,
            FOREIGN KEY (piece_id) REFERENCES pieces(id)
        )
    """)
    
    # Action properties table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_properties (
            id INTEGER PRIMARY KEY,
            action_id INTEGER NOT NULL,
            property_name TEXT NOT NULL,
            display_name TEXT,
            description TEXT,
            property_type TEXT NOT NULL,
            required INTEGER,
            default_value TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT,
            FOREIGN KEY (action_id) REFERENCES actions(id)
        )
    """)
    
    # Triggers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY,
            piece_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            trigger_type TEXT,
            requires_auth INTEGER,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT,
            FOREIGN KEY (piece_id) REFERENCES pieces(id)
        )
    """)
    
    # Trigger properties table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trigger_properties (
            id INTEGER PRIMARY KEY,
            trigger_id INTEGER NOT NULL,
            property_name TEXT NOT NULL,
            display_name TEXT,
            description TEXT,
            property_type TEXT NOT NULL,
            required INTEGER,
            default_value TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT,
            FOREIGN KEY (trigger_id) REFERENCES triggers(id)
        )
    """)
    
    # Property options table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS property_options (
            id INTEGER PRIMARY KEY,
            property_id INTEGER NOT NULL,
            property_type TEXT NOT NULL,
            option_label TEXT,
            option_value TEXT NOT NULL,
            created_at TEXT
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_piece_id ON actions(piece_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_properties_action_id ON action_properties(action_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_triggers_piece_id ON triggers(piece_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trigger_properties_trigger_id ON trigger_properties(trigger_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pieces_name ON pieces(name)")
    
    conn.commit()
    print("[OK] SQLite schema created")


def migrate_table(pg_cur, sqlite_conn, table_name, column_mapping):
    """
    Migrate a table from PostgreSQL to SQLite
    
    Args:
        pg_cur: PostgreSQL cursor
        sqlite_conn: SQLite connection
        table_name: Name of the table to migrate
        column_mapping: Dict mapping PostgreSQL columns to SQLite format
    """
    print(f"\nMigrating table: {table_name}")
    
    # Get columns to select
    pg_columns = list(column_mapping.keys())
    sqlite_columns = list(column_mapping.values())
    
    # Fetch data from PostgreSQL
    select_sql = f"SELECT {', '.join(pg_columns)} FROM {table_name}"
    pg_cur.execute(select_sql)
    rows = pg_cur.fetchall()
    
    if not rows:
        print(f"  No data in {table_name}")
        return
    
    # Prepare insert statement for SQLite
    placeholders = ', '.join(['?' for _ in sqlite_columns])
    insert_sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(sqlite_columns)}) VALUES ({placeholders})"
    
    # Convert and insert data
    sqlite_cur = sqlite_conn.cursor()
    converted_rows = []
    
    for row in rows:
        converted_row = []
        for pg_col, sqlite_col in column_mapping.items():
            value = row[pg_col]
            
            # Convert special types
            if value is None:
                converted_row.append(None)
            elif isinstance(value, (list, dict)):
                # Convert arrays and JSON to text
                converted_row.append(json.dumps(value))
            elif isinstance(value, bool):
                # Convert boolean to integer
                converted_row.append(1 if value else 0)
            elif isinstance(value, datetime):
                # Convert datetime to ISO format string
                converted_row.append(value.isoformat())
            else:
                converted_row.append(value)
        
        converted_rows.append(tuple(converted_row))
    
    # Batch insert
    sqlite_cur.executemany(insert_sql, converted_rows)
    sqlite_conn.commit()
    
    print(f"  [OK] Migrated {len(converted_rows)} records")


def main():
    print("=" * 60)
    print("PostgreSQL to SQLite Migration")
    print("=" * 60)
    
    # Connect to SQLite
    print(f"\nConnecting to SQLite database: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    
    # Create schema
    create_sqlite_schema(sqlite_conn)
    
    # Connect to PostgreSQL and migrate data
    try:
        with get_db_cursor() as pg_cur:
            print("\n" + "=" * 60)
            print("Starting data migration...")
            print("=" * 60)
            
            # Migrate pieces (main table)
            migrate_table(pg_cur, sqlite_conn, 'pieces', {
                'id': 'id',
                'name': 'name',
                'display_name': 'display_name',
                'description': 'description',
                'logo_url': 'logo_url',
                'version': 'version',
                'minimum_supported_release': 'minimum_supported_release',
                'auth_type': 'auth_type',
                'categories': 'categories',
                'authors': 'authors',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'metadata': 'metadata'
            })
            
            # Migrate actions
            migrate_table(pg_cur, sqlite_conn, 'actions', {
                'id': 'id',
                'piece_id': 'piece_id',
                'name': 'name',
                'display_name': 'display_name',
                'description': 'description',
                'requires_auth': 'requires_auth',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'metadata': 'metadata'
            })
            
            # Migrate action_properties
            migrate_table(pg_cur, sqlite_conn, 'action_properties', {
                'id': 'id',
                'action_id': 'action_id',
                'property_name': 'property_name',
                'display_name': 'display_name',
                'description': 'description',
                'property_type': 'property_type',
                'required': 'required',
                'default_value': 'default_value',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'metadata': 'metadata'
            })
            
            # Migrate triggers
            migrate_table(pg_cur, sqlite_conn, 'triggers', {
                'id': 'id',
                'piece_id': 'piece_id',
                'name': 'name',
                'display_name': 'display_name',
                'description': 'description',
                'trigger_type': 'trigger_type',
                'requires_auth': 'requires_auth',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'metadata': 'metadata'
            })
            
            # Migrate trigger_properties
            migrate_table(pg_cur, sqlite_conn, 'trigger_properties', {
                'id': 'id',
                'trigger_id': 'trigger_id',
                'property_name': 'property_name',
                'display_name': 'display_name',
                'description': 'description',
                'property_type': 'property_type',
                'required': 'required',
                'default_value': 'default_value',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'metadata': 'metadata'
            })
            
            # Migrate property_options (if any data exists)
            migrate_table(pg_cur, sqlite_conn, 'property_options', {
                'id': 'id',
                'property_id': 'property_id',
                'property_type': 'property_type',
                'option_label': 'option_label',
                'option_value': 'option_value',
                'created_at': 'created_at'
            })
            
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sqlite_conn.close()
        return False
    
    # Verify migration
    print("\n" + "=" * 60)
    print("Verifying migration...")
    print("=" * 60)
    
    cursor = sqlite_conn.cursor()
    tables = ['pieces', 'actions', 'action_properties', 'triggers', 'trigger_properties', 'property_options']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")
    
    sqlite_conn.close()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Migration completed successfully!")
    print("=" * 60)
    print(f"\nSQLite database created: {SQLITE_DB}")
    print("\nNext steps:")
    print("  1. Backup your PostgreSQL database (if needed)")
    print("  2. Update db_config.py to use SQLite")
    print("  3. Update requirements.txt to remove PostgreSQL")
    print("  4. Test the application with: python test_assistant.py")
    
    return True


if __name__ == "__main__":
    main()

