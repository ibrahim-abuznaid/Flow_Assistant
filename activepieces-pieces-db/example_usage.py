#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: How to use Activepieces database in Flow_Assistant project
"""

from activepieces_db import ActivepiecesDB

def main():
    print("=== Flow Assistant - Activepieces Integration ===\n")
    
    # Example 1: Search for pieces
    with ActivepiecesDB() as db:
        print("1. Search for email integrations:")
        pieces = db.search_pieces('email', limit=5)
        for piece in pieces:
            print(f"   • {piece['display_name']}: {piece['action_count']} actions")
        print()
        
        # Example 2: Find specific actions
        print("2. Find 'send message' actions:")
        actions = db.search_actions('send message', limit=5)
        for action in actions:
            print(f"   • {action['piece_display_name']}: {action['action_display_name']}")
        print()
        
        # Example 3: Get action details
        print("3. Gmail Send Email - Required inputs:")
        inputs = db.get_action_inputs('gmail', 'send_email')
        required_inputs = [inp for inp in inputs if inp['required']]
        for inp in required_inputs:
            print(f"   • {inp['display_name']} ({inp['type']})")
        print()
        
        # Example 4: Top integrations
        print("4. Top 10 integrations by capabilities:")
        top = db.get_top_pieces(limit=10)
        for i, piece in enumerate(top, 1):
            total = piece['action_count'] + piece['trigger_count']
            print(f"   {i}. {piece['display_name']}: {total} total capabilities")
        print()
        
        print("✅ Ready to use in Flow_Assistant!")

if __name__ == '__main__':
    main()


