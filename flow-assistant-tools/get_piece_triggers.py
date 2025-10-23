#!/usr/bin/env python3
"""
Get Piece Triggers
Lists all triggers for a specific piece with their properties
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
    
    # Handle nested properties
    if prop.get('properties'):
        lines.append(f"{ind}  Nested Properties:")
        for nested_name, nested_prop in prop['properties'].items():
            lines.append(format_property(nested_name, nested_prop, indent + 2))
    
    return "\n".join(lines)

def print_triggers(piece_name: str, triggers: dict, show_properties: bool = False):
    """Print formatted triggers information"""
    print("\n" + "="*80)
    print(f"TRIGGERS FOR: {piece_name}")
    print("="*80)
    print(f"Total Triggers: {len(triggers)}\n")
    
    for i, (trigger_name, trigger) in enumerate(triggers.items(), 1):
        print(f"{i}. {trigger.get('displayName', trigger_name)}")
        print(f"   Name: {trigger_name}")
        print(f"   Description: {trigger.get('description', 'No description')}")
        print(f"   Type: {trigger.get('type', 'UNKNOWN')}")
        print(f"   Requires Auth: {trigger.get('requireAuth', False)}")
        
        if show_properties:
            props = trigger.get('props', {})
            if props:
                print(f"   Properties ({len(props)}):")
                for prop_name, prop in props.items():
                    print(format_property(prop_name, prop, indent=2))
            else:
                print(f"   Properties: None")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Get all triggers for a specific piece'
    )
    parser.add_argument(
        'piece_name',
        help='Piece name (e.g., @activepieces/piece-slack)'
    )
    parser.add_argument(
        '--show-properties',
        action='store_true',
        help='Show all properties for each trigger'
    )
    parser.add_argument(
        '--trigger-name',
        help='Filter to specific trigger name',
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
    print(f"Fetching triggers for '{args.piece_name}'...")
    
    try:
        piece = client.get_piece(name=args.piece_name)
        triggers = normalize_collection(piece.get('triggers'))
        
        # Filter to specific trigger if requested
        if args.trigger_name:
            if args.trigger_name in triggers:
                triggers = {args.trigger_name: triggers[args.trigger_name]}
            else:
                print(f"\nError: Trigger '{args.trigger_name}' not found in piece '{args.piece_name}'")
                print(f"\nAvailable triggers: {', '.join(triggers.keys())}")
                return 1
        
        if args.json_only:
            output = json.dumps(triggers, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)
        else:
            print_triggers(
                piece.get('displayName', args.piece_name),
                triggers,
                show_properties=args.show_properties
            )
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(triggers, f, indent=2)
                print(f"JSON saved to {args.output}")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

