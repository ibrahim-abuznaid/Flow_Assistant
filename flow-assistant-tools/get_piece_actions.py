#!/usr/bin/env python3
"""
Get Piece Actions
Lists all actions for a specific piece with their properties
"""

import json
import argparse
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection

def format_property(prop_name: str, prop: dict, indent: int = 0) -> str:
    """Format a property for display"""
    ind = "  " * indent
    lines = []
    
    lines.append(f"{ind}• {prop_name}")
    lines.append(f"{ind}  Type: {prop.get('type', 'unknown')}")
    lines.append(f"{ind}  Required: {prop.get('required', False)}")
    
    if prop.get('displayName'):
        lines.append(f"{ind}  Display Name: {prop['displayName']}")
    if prop.get('description'):
        lines.append(f"{ind}  Description: {prop['description']}")
    if prop.get('defaultValue'):
        lines.append(f"{ind}  Default: {prop['defaultValue']}")
    
    # Handle nested properties (for objects, dynamics, etc.)
    if prop.get('properties'):
        lines.append(f"{ind}  Nested Properties:")
        for nested_name, nested_prop in prop['properties'].items():
            lines.append(format_property(nested_name, nested_prop, indent + 2))
    
    return "\n".join(lines)

def print_actions(piece_name: str, actions: dict, show_properties: bool = False):
    """Print formatted actions information"""
    print("\n" + "="*80)
    print(f"ACTIONS FOR: {piece_name}")
    print("="*80)
    print(f"Total Actions: {len(actions)}\n")
    
    for i, (action_name, action) in enumerate(actions.items(), 1):
        print(f"{i}. {action.get('displayName', action_name)}")
        print(f"   Name: {action_name}")
        print(f"   Description: {action.get('description', 'No description')}")
        print(f"   Requires Auth: {action.get('requireAuth', False)}")
        
        if show_properties:
            props = action.get('props', {})
            if props:
                print(f"   Properties ({len(props)}):")
                for prop_name, prop in props.items():
                    print(format_property(prop_name, prop, indent=2))
            else:
                print(f"   Properties: None")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Get all actions for a specific piece'
    )
    parser.add_argument(
        'piece_name',
        help='Piece name (e.g., @activepieces/piece-slack)'
    )
    parser.add_argument(
        '--show-properties',
        action='store_true',
        help='Show all properties for each action'
    )
    parser.add_argument(
        '--action-name',
        help='Filter to specific action name',
        default=None
    )
    parser.add_argument(
        '--output',
        help='Output file path (JSON)',
        default=None
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Output raw JSON only'
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    # Fetch piece details
    print(f"Fetching actions for '{args.piece_name}'...")
    
    try:
        piece = client.get_piece(name=args.piece_name)
        actions = normalize_collection(piece.get('actions'))
        
        # Filter to specific action if requested
        if args.action_name:
            if args.action_name in actions:
                actions = {args.action_name: actions[args.action_name]}
            else:
                print(f"\nError: Action '{args.action_name}' not found in piece '{args.piece_name}'")
                print(f"\nAvailable actions: {', '.join(actions.keys())}")
                return 1
        
        if args.json_only:
            output = json.dumps(actions, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)
        else:
            print_actions(
                piece.get('displayName', args.piece_name),
                actions,
                show_properties=args.show_properties
            )
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(actions, f, indent=2)
                print(f"JSON saved to {args.output}")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

