#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activepieces SQLite Database Helper
Standalone module for querying Activepieces pieces database.

Usage:
    from activepieces_db import ActivepiecesDB
    
    with ActivepiecesDB() as db:
        pieces = db.search_pieces('email')
        for piece in pieces:
            print(piece['display_name'])
"""

import sqlite3
import json
import sys
import os
from typing import List, Dict, Any, Optional

# Ensure UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class ActivepiecesDB:
    """Helper class for querying the Activepieces pieces database."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file. If None, looks for 
                     'activepieces-pieces.db' in the same directory as this script.
        """
        if db_path is None:
            # Default to database in same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, 'activepieces-pieces.db')
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return results as dictionaries
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def search_pieces(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search pieces using full-text search.
        
        Args:
            query: Search query (e.g., 'email', 'slack OR discord')
            limit: Maximum number of results
            
        Returns:
            List of matching pieces with their details
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.name,
                p.display_name,
                p.description,
                p.auth_type,
                (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) as action_count,
                (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) as trigger_count
            FROM pieces_fts
            JOIN pieces p ON pieces_fts.rowid = p.id
            WHERE pieces_fts MATCH ?
            LIMIT ?
        """, (query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_actions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search actions using full-text search.
        
        Args:
            query: Search query (e.g., 'send email', 'create task')
            limit: Maximum number of results
            
        Returns:
            List of matching actions with piece information
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.name as piece_name,
                p.display_name as piece_display_name,
                a.name as action_name,
                a.display_name as action_display_name,
                a.description,
                a.requires_auth
            FROM actions_fts
            JOIN actions a ON actions_fts.rowid = a.id
            JOIN pieces p ON a.piece_id = p.id
            WHERE actions_fts MATCH ?
            LIMIT ?
        """, (query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_piece_details(self, piece_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete details for a specific piece.
        
        Args:
            piece_name: Name of the piece (e.g., 'gmail', 'slack')
            
        Returns:
            Piece details including actions and triggers
        """
        cursor = self.conn.cursor()
        
        # Get piece info
        cursor.execute("""
            SELECT * FROM pieces WHERE name = ?
        """, (piece_name,))
        
        piece = cursor.fetchone()
        if not piece:
            return None
        
        piece_dict = dict(piece)
        
        # Parse JSON fields
        if piece_dict.get('categories'):
            piece_dict['categories'] = json.loads(piece_dict['categories'])
        if piece_dict.get('authors'):
            piece_dict['authors'] = json.loads(piece_dict['authors'])
        
        # Get actions
        cursor.execute("""
            SELECT name, display_name, description, requires_auth
            FROM actions
            WHERE piece_id = ?
        """, (piece_dict['id'],))
        piece_dict['actions'] = [dict(row) for row in cursor.fetchall()]
        
        # Get triggers
        cursor.execute("""
            SELECT name, display_name, description, trigger_type, requires_auth
            FROM triggers
            WHERE piece_id = ?
        """, (piece_dict['id'],))
        piece_dict['triggers'] = [dict(row) for row in cursor.fetchall()]
        
        return piece_dict
    
    def get_action_inputs(self, piece_name: str, action_name: str) -> List[Dict[str, Any]]:
        """
        Get input properties for a specific action.
        
        Args:
            piece_name: Name of the piece (e.g., 'gmail')
            action_name: Name of the action (e.g., 'send_email')
            
        Returns:
            List of input properties with their details
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ap.name,
                ap.display_name,
                ap.description,
                ap.type,
                ap.required,
                ap.default_value
            FROM pieces p
            JOIN actions a ON p.id = a.piece_id
            JOIN action_properties ap ON a.id = ap.action_id
            WHERE p.name = ? AND a.name = ?
            ORDER BY ap.required DESC, ap.display_name
        """, (piece_name, action_name))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_top_pieces(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the most capable pieces (by action + trigger count).
        
        Args:
            limit: Maximum number of pieces to return
            
        Returns:
            List of pieces ordered by total capabilities
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                display_name,
                auth_type,
                action_count,
                trigger_count,
                (action_count + trigger_count) as total_capabilities
            FROM pieces_with_capabilities
            WHERE action_count > 0 OR trigger_count > 0
            ORDER BY total_capabilities DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_pieces(self) -> List[Dict[str, Any]]:
        """Get all pieces with their action and trigger counts."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                name,
                display_name,
                auth_type,
                action_count,
                trigger_count
            FROM pieces_with_capabilities
            ORDER BY display_name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pieces_by_auth_type(self, auth_type: str) -> List[Dict[str, Any]]:
        """
        Get pieces by authentication type.
        
        Args:
            auth_type: Authentication type (e.g., 'OAuth2', 'ApiKey', 'SecretText')
            
        Returns:
            List of pieces with that auth type
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT display_name, action_count, trigger_count
            FROM pieces_with_capabilities
            WHERE auth_type = ?
            ORDER BY (action_count + trigger_count) DESC
        """, (auth_type,))
        
        return [dict(row) for row in cursor.fetchall()]


def main():
    """Example usage of the ActivepiecesDB class."""
    
    print("🤖 Activepieces Database - Python Example\n")
    
    with ActivepiecesDB() as db:
        # Example 1: Search for pieces related to email
        print("📧 Example 1: Search for email-related pieces")
        print("-" * 50)
        email_pieces = db.search_pieces('email', limit=5)
        for piece in email_pieces:
            print(f"  • {piece['display_name']}")
            print(f"    {piece['action_count']} actions, {piece['trigger_count']} triggers")
        print()
        
        # Example 2: Search for "send email" actions
        print("✉️ Example 2: Find 'send email' actions")
        print("-" * 50)
        send_actions = db.search_actions('send email', limit=5)
        for action in send_actions:
            print(f"  • {action['piece_display_name']}: {action['action_display_name']}")
        print()
        
        # Example 3: Get Gmail piece details
        print("📬 Example 3: Gmail piece details")
        print("-" * 50)
        gmail = db.get_piece_details('gmail')
        if gmail:
            print(f"  Name: {gmail['display_name']}")
            print(f"  Auth Type: {gmail['auth_type']}")
            print(f"  Actions: {len(gmail['actions'])}")
            print(f"  Triggers: {len(gmail['triggers'])}")
        print()
        
        # Example 4: Get inputs for Gmail Send Email action
        print("📝 Example 4: Gmail Send Email inputs")
        print("-" * 50)
        inputs = db.get_action_inputs('gmail', 'send_email')
        for inp in inputs[:5]:  # Show first 5
            required = "✓" if inp['required'] else " "
            print(f"  [{required}] {inp['display_name']} ({inp['type']})")
        print()
        
        print("✅ All examples completed successfully!")


if __name__ == '__main__':
    main()

