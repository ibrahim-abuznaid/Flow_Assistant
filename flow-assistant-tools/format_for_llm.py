#!/usr/bin/env python3
"""
Format for LLM
Formats pieces data into a context-optimized format for LLM assistants
"""

import json
import argparse
from typing import List, Dict, Any
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection, count_collection, get_categories

def format_piece_for_llm(piece: Dict[str, Any], verbose: bool = False) -> str:
    """Format a single piece for LLM context"""
    lines = []
    
    # Header
    lines.append(f"## {piece['displayName']} ({piece['name']})")
    lines.append(f"**Version:** {piece.get('version', 'N/A')}")
    lines.append(f"**Description:** {piece.get('description', 'No description')}")
    
    # Categories
    categories = get_categories(piece.get('categories'))
    if categories:
        lines.append(f"**Categories:** {', '.join(categories)}")
    
    # Authentication
    if piece.get('auth'):
        auth = piece['auth']
        lines.append(f"**Authentication:** Required ({auth.get('type', 'Unknown')})")
    else:
        lines.append("**Authentication:** Not required")
    
    # Actions
    raw_actions = piece.get('actions')
    actions = normalize_collection(raw_actions)
    action_count = count_collection(raw_actions)

    if action_count:
        lines.append(f"\n### Actions ({action_count})")
        if actions:
            for action_name, action in actions.items():
                lines.append(f"- **{action.get('displayName', action_name)}** (`{action_name}`)")
                lines.append(f"  - {action.get('description', 'No description')}")

                if verbose and action.get('props'):
                    lines.append(f"  - Properties:")
                    for prop_name, prop in action['props'].items():
                        required = "required" if prop.get('required', False) else "optional"
                        lines.append(
                            f"    - `{prop_name}` ({prop.get('type', 'unknown')}, {required}): "
                            f"{prop.get('description', 'No description')}"
                        )
        else:
            lines.append("- Action details unavailable")

    # Triggers
    raw_triggers = piece.get('triggers')
    triggers = normalize_collection(raw_triggers)
    trigger_count = count_collection(raw_triggers)

    if trigger_count:
        lines.append(f"\n### Triggers ({trigger_count})")
        if triggers:
            for trigger_name, trigger in triggers.items():
                lines.append(f"- **{trigger.get('displayName', trigger_name)}** (`{trigger_name}`)")
                lines.append(f"  - {trigger.get('description', 'No description')}")
                lines.append(f"  - Type: {trigger.get('type', 'UNKNOWN')}")

                if verbose and trigger.get('props'):
                    lines.append(f"  - Properties:")
                    for prop_name, prop in trigger['props'].items():
                        required = "required" if prop.get('required', False) else "optional"
                        lines.append(
                            f"    - `{prop_name}` ({prop.get('type', 'unknown')}, {required}): "
                            f"{prop.get('description', 'No description')}"
                        )
        else:
            lines.append("- Trigger details unavailable")
    
    return "\n".join(lines)

def format_all_pieces_for_llm(pieces: List[Dict[str, Any]], verbose: bool = False) -> str:
    """Format all pieces for LLM context"""
    lines = []
    
    # Header
    lines.append("# Activepieces Integration Catalog")
    lines.append(f"\nTotal Pieces: {len(pieces)}")
    lines.append("\n---\n")
    
    # Group by category
    from collections import defaultdict
    categorized = defaultdict(list)
    
    for piece in pieces:
        categories = get_categories(piece.get('categories')) or ['Uncategorized']
        for category in categories:
            categorized[category].append(piece)
    
    # Output by category
    for category in sorted(categorized.keys()):
        category_pieces = categorized[category]
        lines.append(f"\n# Category: {category} ({len(category_pieces)} pieces)\n")
        
        for piece in category_pieces:
            lines.append(format_piece_for_llm(piece, verbose))
            lines.append("\n---\n")
    
    return "\n".join(lines)

def format_compact_for_llm(pieces: List[Dict[str, Any]]) -> str:
    """Format pieces in compact format for smaller context"""
    lines = []
    
    lines.append("# Activepieces Integration Catalog (Compact)\n")
    
    for piece in pieces:
        actions = normalize_collection(piece.get('actions'))
        triggers = normalize_collection(piece.get('triggers'))
        action_count = count_collection(piece.get('actions'))
        trigger_count = count_collection(piece.get('triggers'))
        
        lines.append(f"**{piece['displayName']}** ({piece['name']})")
        lines.append(f"  {piece.get('description', 'No description')}")
        
        if action_count:
            action_names = list(actions.keys())
            if action_names:
                lines.append(f"  Actions: {', '.join(action_names[:5])}")
                if len(action_names) > 5:
                    lines.append(f"  ... and {len(action_names) - 5} more")
            else:
                lines.append("  Actions: details unavailable")
        
        if trigger_count:
            trigger_names = list(triggers.keys())
            if trigger_names:
                lines.append(f"  Triggers: {', '.join(trigger_names[:3])}")
                if len(trigger_names) > 3:
                    lines.append(f"  ... and {len(trigger_names) - 3} more")
            else:
                lines.append("  Triggers: details unavailable")
        
        lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description='Format pieces data for LLM context'
    )
    parser.add_argument(
        '--output',
        help='Output file path',
        required=True
    )
    parser.add_argument(
        '--format',
        choices=['full', 'compact', 'json'],
        default='full',
        help='Output format'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Include all properties and details (only for full format)'
    )
    parser.add_argument(
        '--search',
        help='Filter pieces by search query',
        default=None
    )
    parser.add_argument(
        '--categories',
        nargs='+',
        help='Filter by categories',
        default=None
    )
    parser.add_argument(
        '--suggestion-type',
        choices=['ACTION', 'TRIGGER', 'ACTION_AND_TRIGGER'],
        help='Filter by suggestion type'
    )
    
    args = parser.parse_args()
    
    # Initialize API client
    client = ActivepiecesAPIClient()
    
    # Fetch pieces
    print("Fetching pieces...")
    pieces = client.list_pieces(
        search_query=args.search,
        suggestion_type=args.suggestion_type,
        include_tags=True
    )
    
    # Filter by categories if specified
    if args.categories:
        pieces = [
            p for p in pieces
            if any(cat in p.get('categories', []) for cat in args.categories)
        ]
    
    print(f"Processing {len(pieces)} pieces...")

    if args.format in {"full", "compact"}:
        detailed_pieces: List[Dict[str, Any]] = []

        for piece in pieces:
            if isinstance(piece.get('actions'), dict) and isinstance(piece.get('triggers'), dict):
                detailed_pieces.append(piece)
            else:
                detailed_pieces.append(client.get_piece(piece['name']))

        pieces = detailed_pieces
    
    # Format based on selected format
    if args.format == 'json':
        output = json.dumps(pieces, indent=2)
    elif args.format == 'compact':
        output = format_compact_for_llm(pieces)
    else:  # full
        output = format_all_pieces_for_llm(pieces, verbose=args.verbose)
    
    # Save to file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\nFormatted data saved to: {args.output}")
    print(f"Format: {args.format}")
    print(f"Total pieces: {len(pieces)}")
    
    # Show file size
    import os
    size_kb = os.path.getsize(args.output) / 1024
    print(f"File size: {size_kb:.2f} KB")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

