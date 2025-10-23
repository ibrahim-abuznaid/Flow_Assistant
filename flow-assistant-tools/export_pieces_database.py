#!/usr/bin/env python3
"""
Export Pieces Database
Exports all pieces data to various formats (JSON, CSV, SQLite)
"""

import json
import csv
import argparse
from typing import List, Dict, Any
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection, count_collection, get_categories

def export_to_json(pieces: List[Dict[str, Any]], output_path: str):
    """Export pieces to JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pieces, f, indent=2)
    print(f"Exported {len(pieces)} pieces to JSON: {output_path}")

def export_to_csv(pieces: List[Dict[str, Any]], output_path: str):
    """Export pieces to CSV (flattened)"""
    rows = []
    
    for piece in pieces:
        # Flatten piece data for CSV
        base_row = {
            'name': piece['name'],
            'displayName': piece.get('displayName', ''),
            'version': piece.get('version', ''),
            'description': piece.get('description', ''),
            'logoUrl': piece.get('logoUrl', ''),
            'categories': ','.join(get_categories(piece.get('categories'))),
            'requiresAuth': 'Yes' if piece.get('auth') else 'No',
            'authType': piece.get('auth', {}).get('type', '') if piece.get('auth') else '',
            'actionCount': count_collection(piece.get('actions')),
            'triggerCount': count_collection(piece.get('triggers'))
        }
        rows.append(base_row)
    
    if rows:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported {len(rows)} pieces to CSV: {output_path}")

def _ensure_detailed_piece(
    piece: Dict[str, Any],
    client: ActivepiecesAPIClient,
    cache: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Ensure the piece contains detailed action/trigger data."""

    name = piece['name']

    if isinstance(piece.get('actions'), dict) and isinstance(piece.get('triggers'), dict):
        cache[name] = piece
        return piece

    if name not in cache:
        cache[name] = client.get_piece(name)

    return cache[name]


def export_actions_to_csv(
    pieces: List[Dict[str, Any]],
    output_path: str,
    client: ActivepiecesAPIClient,
    cache: Dict[str, Dict[str, Any]]
):
    """Export all actions to CSV"""
    rows = []
    
    for piece in pieces:
        actions = normalize_collection(piece.get('actions'))

        if not actions and count_collection(piece.get('actions')):
            detailed_piece = _ensure_detailed_piece(piece, client, cache)
            actions = normalize_collection(detailed_piece.get('actions'))

        for action_name, action in actions.items():
            row = {
                'pieceName': piece['name'],
                'pieceDisplayName': piece.get('displayName', ''),
                'actionName': action_name,
                'actionDisplayName': action.get('displayName', ''),
                'description': action.get('description', ''),
                'requiresAuth': 'Yes' if action.get('requireAuth', False) else 'No',
                'propertyCount': len(action.get('props', {}))
            }
            rows.append(row)
    
    if rows:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported {len(rows)} actions to CSV: {output_path}")

def export_triggers_to_csv(
    pieces: List[Dict[str, Any]],
    output_path: str,
    client: ActivepiecesAPIClient,
    cache: Dict[str, Dict[str, Any]]
):
    """Export all triggers to CSV"""
    rows = []
    
    for piece in pieces:
        triggers = normalize_collection(piece.get('triggers'))

        if not triggers and count_collection(piece.get('triggers')):
            detailed_piece = _ensure_detailed_piece(piece, client, cache)
            triggers = normalize_collection(detailed_piece.get('triggers'))

        for trigger_name, trigger in triggers.items():
            row = {
                'pieceName': piece['name'],
                'pieceDisplayName': piece.get('displayName', ''),
                'triggerName': trigger_name,
                'triggerDisplayName': trigger.get('displayName', ''),
                'description': trigger.get('description', ''),
                'type': trigger.get('type', ''),
                'requiresAuth': 'Yes' if trigger.get('requireAuth', False) else 'No',
                'propertyCount': len(trigger.get('props', {}))
            }
            rows.append(row)
    
    if rows:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported {len(rows)} triggers to CSV: {output_path}")

def export_to_sqlite(
    pieces: List[Dict[str, Any]],
    output_path: str,
    client: ActivepiecesAPIClient,
    cache: Dict[str, Dict[str, Any]]
):
    """Export pieces to SQLite database"""
    import sqlite3
    import json as json_lib
    from datetime import datetime
    
    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Create pieces table with full schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pieces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            description TEXT,
            logo_url TEXT,
            version TEXT,
            minimum_supported_release TEXT,
            auth_type TEXT,
            categories TEXT,
            authors TEXT,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piece_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            requires_auth INTEGER DEFAULT 0,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
            UNIQUE(piece_id, name)
        )
    ''')
    
    # Create triggers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piece_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            trigger_type TEXT,
            requires_auth INTEGER DEFAULT 0,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
            UNIQUE(piece_id, name)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pieces_name ON pieces(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_piece_id ON actions(piece_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_name ON actions(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_triggers_piece_id ON triggers(piece_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_triggers_name ON triggers(name)')
    
    # Create FTS tables
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS pieces_fts USING fts5(
            name, display_name, description,
            content='pieces', content_rowid='id'
        )
    ''')
    
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS actions_fts USING fts5(
            name, display_name, description,
            content='actions', content_rowid='id'
        )
    ''')
    
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS triggers_fts USING fts5(
            name, display_name, description,
            content='triggers', content_rowid='id'
        )
    ''')
    
    # Create FTS triggers
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS pieces_ai AFTER INSERT ON pieces BEGIN
            INSERT INTO pieces_fts(rowid, name, display_name, description)
            VALUES (new.id, new.name, new.display_name, new.description);
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS actions_ai AFTER INSERT ON actions BEGIN
            INSERT INTO actions_fts(rowid, name, display_name, description)
            VALUES (new.id, new.name, new.display_name, new.description);
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS triggers_ai AFTER INSERT ON triggers BEGIN
            INSERT INTO triggers_fts(rowid, name, display_name, description)
            VALUES (new.id, new.name, new.display_name, new.description);
        END
    ''')
    
    # Create views
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS pieces_with_capabilities AS
        SELECT 
            p.*,
            (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) as action_count,
            (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) as trigger_count
        FROM pieces p
    ''')
    
    # Insert pieces
    for piece in pieces:
        # Get categories
        categories = get_categories(piece.get('categories', []))
        categories_json = json_lib.dumps(categories) if categories else '[]'
        
        # Get authors
        authors = piece.get('authors', [])
        authors_json = json_lib.dumps(authors) if authors else '[]'
        
        # Get auth type
        auth_type = None
        if piece.get('auth'):
            auth_type = piece.get('auth', {}).get('type', '')
        
        cursor.execute('''
            INSERT OR REPLACE INTO pieces 
            (name, display_name, description, logo_url, version, minimum_supported_release,
             auth_type, categories, authors, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            piece['name'],
            piece.get('displayName', ''),
            piece.get('description', ''),
            piece.get('logoUrl', ''),
            piece.get('version', ''),
            piece.get('minimumSupportedRelease', ''),
            auth_type,
            categories_json,
            authors_json,
            json_lib.dumps({}),  # metadata
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Get piece_id
        cursor.execute('SELECT id FROM pieces WHERE name = ?', (piece['name'],))
        piece_id = cursor.fetchone()[0]
        
        # Insert actions
        actions = normalize_collection(piece.get('actions'))

        if not actions and count_collection(piece.get('actions')):
            detailed_piece = _ensure_detailed_piece(piece, client, cache)
            actions = normalize_collection(detailed_piece.get('actions'))

        for action_name, action in actions.items():
            cursor.execute('''
                INSERT INTO actions (piece_id, name, display_name, description, requires_auth, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                piece_id,
                action_name,
                action.get('displayName', ''),
                action.get('description', ''),
                1 if action.get('requireAuth', False) else 0,
                json_lib.dumps({}),  # metadata
                datetime.now().isoformat()
            ))
        
        # Insert triggers
        triggers = normalize_collection(piece.get('triggers'))

        if not triggers and count_collection(piece.get('triggers')):
            detailed_piece = _ensure_detailed_piece(piece, client, cache)
            triggers = normalize_collection(detailed_piece.get('triggers'))

        for trigger_name, trigger in triggers.items():
            cursor.execute('''
                INSERT INTO triggers (piece_id, name, display_name, description, trigger_type, requires_auth, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                piece_id,
                trigger_name,
                trigger.get('displayName', ''),
                trigger.get('description', ''),
                trigger.get('type', ''),
                1 if trigger.get('requireAuth', False) else 0,
                json_lib.dumps({}),  # metadata
                datetime.now().isoformat()
            ))
    
    conn.commit()
    conn.close()
    print(f"Exported {len(pieces)} pieces to SQLite: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Export pieces database to various formats'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'csv-actions', 'csv-triggers', 'sqlite', 'all'],
        default='json',
        help='Export format'
    )
    parser.add_argument(
        '--output',
        help='Output file/directory path',
        default='pieces_export'
    )
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Include hidden pieces'
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    # Fetch all pieces
    print("Fetching all pieces...")
    pieces = client.list_pieces(
        include_hidden=args.include_hidden,
        include_tags=True
    )
    
    print(f"Fetched {len(pieces)} pieces")

    detail_cache: Dict[str, Dict[str, Any]] = {}
    
    # Export based on format
    if args.format == 'json' or args.format == 'all':
        export_to_json(pieces, f"{args.output}.json" if args.format == 'json' else f"{args.output}_pieces.json")
    
    if args.format == 'csv' or args.format == 'all':
        export_to_csv(pieces, f"{args.output}.csv" if args.format == 'csv' else f"{args.output}_pieces.csv")
    
    if args.format == 'csv-actions' or args.format == 'all':
        export_actions_to_csv(
            pieces,
            f"{args.output}.csv" if args.format == 'csv-actions' else f"{args.output}_actions.csv",
            client,
            detail_cache
        )
    
    if args.format == 'csv-triggers' or args.format == 'all':
        export_triggers_to_csv(
            pieces,
            f"{args.output}.csv" if args.format == 'csv-triggers' else f"{args.output}_triggers.csv",
            client,
            detail_cache
        )
    
    if args.format == 'sqlite' or args.format == 'all':
        export_to_sqlite(
            pieces,
            f"{args.output}.db" if args.format == 'sqlite' else f"{args.output}_pieces.db",
            client,
            detail_cache
        )
    
    print("\nExport complete!")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

