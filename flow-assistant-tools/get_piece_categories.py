#!/usr/bin/env python3
"""
Get Piece Categories
Lists all available piece categories
"""

import json
import argparse
from api_client import ActivepiecesAPIClient
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(
        description='Get all available piece categories'
    )
    parser.add_argument(
        '--with-pieces',
        action='store_true',
        help='Show pieces in each category'
    )
    parser.add_argument(
        '--output',
        help='Output file path (JSON)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    print("Fetching categories...")
    
    try:
        categories = client.get_piece_categories()
        
        print(f"\nFound {len(categories)} categories:\n")
        
        if args.with_pieces:
            # Fetch all pieces to categorize them
            print("Fetching pieces...")
            pieces = client.list_pieces()
            
            # Group pieces by category
            category_pieces = defaultdict(list)
            for piece in pieces:
                for category in piece.get('categories', []):
                    category_pieces[category].append({
                        'name': piece['name'],
                        'displayName': piece['displayName'],
                        'description': piece.get('description', '')
                    })
            
            # Print categories with pieces
            for i, category in enumerate(categories, 1):
                pieces_in_cat = category_pieces.get(category, [])
                print(f"{i}. {category} ({len(pieces_in_cat)} pieces)")
                
                for piece in pieces_in_cat[:5]:  # Show first 5
                    print(f"   - {piece['displayName']}")
                
                if len(pieces_in_cat) > 5:
                    print(f"   ... and {len(pieces_in_cat) - 5} more")
                print()
            
            # Save detailed output if requested
            if args.output:
                output_data = {
                    'categories': categories,
                    'category_pieces': dict(category_pieces)
                }
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"Saved to {args.output}")
        else:
            # Just print categories
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump({'categories': categories}, f, indent=2)
                print(f"\nSaved to {args.output}")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

