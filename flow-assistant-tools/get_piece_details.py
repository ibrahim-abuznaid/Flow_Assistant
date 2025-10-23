#!/usr/bin/env python3
"""
Get Piece Details
Retrieves detailed information about a specific piece including all actions and triggers
"""

import json
import argparse
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection, count_collection

def print_piece_info(piece: dict, verbose: bool = False):
    """Print formatted piece information"""
    print("\n" + "="*80)
    print(f"PIECE: {piece['displayName']}")
    print("="*80)
    print(f"Name: {piece['name']}")
    print(f"Version: {piece['version']}")
    print(f"Description: {piece.get('description', 'No description')}")
    print(f"Categories: {', '.join(piece.get('categories', []))}")
    print(f"Logo URL: {piece.get('logoUrl', 'N/A')}")
    
    # Authentication
    if piece.get('auth'):
        print(f"\nAuthentication Required: Yes")
        auth = piece['auth']
        print(f"  Type: {auth.get('type', 'Unknown')}")
        print(f"  Display Name: {auth.get('displayName', 'N/A')}")
    else:
        print(f"\nAuthentication Required: No")
    
    # Actions
    actions = normalize_collection(piece.get('actions'))
    print(f"\n{'─'*80}")
    print(f"ACTIONS ({count_collection(piece.get('actions'))})")
    print('─'*80)
    
    for action_name, action in actions.items():
        print(f"\n  • {action.get('displayName', action_name)}")
        print(f"    Name: {action_name}")
        print(f"    Description: {action.get('description', 'No description')}")
        print(f"    Requires Auth: {action.get('requireAuth', False)}")
        
        if verbose and action.get('props'):
            print(f"    Properties:")
            for prop_name, prop in action['props'].items():
                print(f"      - {prop_name}: {prop.get('type', 'unknown')} "
                      f"(required: {prop.get('required', False)})")
    
    # Triggers
    triggers = normalize_collection(piece.get('triggers'))
    print(f"\n{'─'*80}")
    print(f"TRIGGERS ({count_collection(piece.get('triggers'))})")
    print('─'*80)
    
    for trigger_name, trigger in triggers.items():
        print(f"\n  • {trigger.get('displayName', trigger_name)}")
        print(f"    Name: {trigger_name}")
        print(f"    Description: {trigger.get('description', 'No description')}")
        print(f"    Type: {trigger.get('type', 'UNKNOWN')}")
        print(f"    Requires Auth: {trigger.get('requireAuth', False)}")
        
        if verbose and trigger.get('props'):
            print(f"    Properties:")
            for prop_name, prop in trigger['props'].items():
                print(f"      - {prop_name}: {prop.get('type', 'unknown')} "
                      f"(required: {prop.get('required', False)})")

def main():
    parser = argparse.ArgumentParser(
        description='Get detailed information about a specific piece'
    )
    parser.add_argument(
        'piece_name',
        help='Piece name (e.g., @activepieces/piece-slack)'
    )
    parser.add_argument(
        '--version',
        help='Specific piece version',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Output file path (JSON)',
        default=None
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all properties and details'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Output raw JSON only (no formatting)'
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    # Fetch piece details
    print(f"Fetching details for '{args.piece_name}'...")
    
    try:
        piece = client.get_piece(
            name=args.piece_name,
            version=args.version
        )
        
        if args.json_only:
            output = json.dumps(piece, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)
        else:
            print_piece_info(piece, verbose=args.verbose)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(piece, f, indent=2)
                print(f"\n\nFull JSON saved to {args.output}")
    
    except requests.exceptions.HTTPError as e:
        print(f"\nError: {e}")
        if e.response.status_code == 404:
            print(f"Piece '{args.piece_name}' not found.")
            print("\nTip: Run 'python get_all_pieces.py --summary' to see available pieces")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    import requests
    sys.exit(main())

