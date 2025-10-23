#!/usr/bin/env python3
"""
Get All Pieces
Lists all available pieces in Activepieces with optional filtering
"""

import json
import argparse
from api_client import ActivepiecesAPIClient
from piece_utils import count_collection

def main():
    parser = argparse.ArgumentParser(
        description='Get all available pieces from Activepieces'
    )
    parser.add_argument(
        '--search',
        help='Search query to filter pieces',
        default=None
    )
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Include hidden pieces'
    )
    parser.add_argument(
        '--include-tags',
        action='store_true',
        help='Include piece tags'
    )
    parser.add_argument(
        '--suggestion-type',
        choices=['ACTION', 'TRIGGER', 'ACTION_AND_TRIGGER'],
        help='Filter by suggestion type'
    )
    parser.add_argument(
        '--sort-by',
        choices=['NAME', 'UPDATED', 'CREATED', 'POPULARITY'],
        help='Sort pieces by field'
    )
    parser.add_argument(
        '--order-by',
        choices=['ASC', 'DESC'],
        help='Sort order'
    )
    parser.add_argument(
        '--output',
        help='Output file path (JSON)',
        default=None
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary only (names and counts)'
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    # Fetch pieces
    print(f"Fetching pieces from {client.base_url}...")
    pieces = client.list_pieces(
        search_query=args.search,
        include_hidden=args.include_hidden,
        include_tags=args.include_tags,
        suggestion_type=args.suggestion_type,
        sort_by=args.sort_by,
        order_by=args.order_by
    )
    
    print(f"\nFound {len(pieces)} pieces")
    
    if args.summary:
        # Show summary
        print("\n" + "="*80)
        print("PIECES SUMMARY")
        print("="*80)
        for piece in pieces:
            action_count = count_collection(piece.get('actions'))
            trigger_count = count_collection(piece.get('triggers'))
            print(f"\n{piece['displayName']} ({piece['name']})")
            print(f"  Version: {piece.get('version', 'N/A')}")
            print(f"  Actions: {action_count}, Triggers: {trigger_count}")
            print(f"  Description: {piece.get('description', 'No description')[:100]}")
    else:
        # Show full output
        output_data = json.dumps(pieces, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_data)
            print(f"\nSaved to {args.output}")
        else:
            print("\n" + output_data)

if __name__ == '__main__':
    main()

