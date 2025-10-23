#!/usr/bin/env python3
"""
Search Pieces
Search for pieces by query with smart filtering and ranking
"""

import json
import argparse
from typing import List, Dict, Any
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection, count_collection, get_categories


def rank_search_results(pieces: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Rank search results by relevance"""
    query_lower = query.lower()
    
    def calculate_score(piece: Dict[str, Any]) -> int:
        score = 0
        
        # Exact name match (highest priority)
        if query_lower in piece['name'].lower():
            score += 100
        
        # Display name match
        if query_lower in piece.get('displayName', '').lower():
            score += 80
        
        # Description match
        if query_lower in piece.get('description', '').lower():
            score += 40
        
        # Categories match
        for category in get_categories(piece.get('categories')):
            if query_lower in category.lower():
                score += 30
        
        # Action/trigger match
        for action in normalize_collection(piece.get('actions')).values():
            if query_lower in action.get('displayName', '').lower():
                score += 20
            if query_lower in action.get('description', '').lower():
                score += 10
        
        for trigger in normalize_collection(piece.get('triggers')).values():
            if query_lower in trigger.get('displayName', '').lower():
                score += 20
            if query_lower in trigger.get('description', '').lower():
                score += 10
        
        return score
    
    # Calculate scores and sort
    for piece in pieces:
        piece['_relevance_score'] = calculate_score(piece)
    
    return sorted(pieces, key=lambda p: p['_relevance_score'], reverse=True)

def print_search_results(pieces: List[Dict[str, Any]], query: str, limit: int = None):
    """Print formatted search results"""
    print("\n" + "="*80)
    print(f"SEARCH RESULTS FOR: '{query}'")
    print("="*80)
    print(f"Found {len(pieces)} pieces\n")
    
    display_pieces = pieces[:limit] if limit else pieces
    
    for i, piece in enumerate(display_pieces, 1):
        actions = normalize_collection(piece.get('actions'))
        triggers = normalize_collection(piece.get('triggers'))

        action_count = count_collection(piece.get('actions'))
        trigger_count = count_collection(piece.get('triggers'))
        
        print(f"{i}. {piece['displayName']}")
        print(f"   Name: {piece['name']}")
        print(f"   Version: {piece.get('version', 'N/A')}")
        print(f"   Actions: {action_count}, Triggers: {trigger_count}")
        print(f"   Description: {piece.get('description', 'No description')[:150]}")
        
        if piece.get('_relevance_score'):
            print(f"   Relevance: {piece['_relevance_score']}")
        
        # Show matching actions/triggers
        matching_actions = []
        for action_name, action in actions.items():
            if query.lower() in action.get('displayName', '').lower():
                matching_actions.append(action.get('displayName', action_name))
        
        matching_triggers = []
        for trigger_name, trigger in triggers.items():
            if query.lower() in trigger.get('displayName', '').lower():
                matching_triggers.append(trigger.get('displayName', trigger_name))
        
        if matching_actions:
            print(f"   → Matching Actions: {', '.join(matching_actions[:3])}")
        if matching_triggers:
            print(f"   → Matching Triggers: {', '.join(matching_triggers[:3])}")
        
        print()
    
    if limit and len(pieces) > limit:
        print(f"... and {len(pieces) - limit} more results")

def main():
    parser = argparse.ArgumentParser(
        description='Search for pieces by query'
    )
    parser.add_argument(
        'query',
        help='Search query'
    )
    parser.add_argument(
        '--suggestion-type',
        choices=['ACTION', 'TRIGGER', 'ACTION_AND_TRIGGER'],
        help='Filter by suggestion type'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of results',
        default=None
    )
    parser.add_argument(
        '--rank',
        action='store_true',
        help='Rank results by relevance (client-side)'
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
    
    # Search pieces
    print(f"Searching for '{args.query}'...")
    
    try:
        pieces = client.list_pieces(
            search_query=args.query,
            suggestion_type=args.suggestion_type
        )
        
        # Rank results if requested
        if args.rank:
            pieces = rank_search_results(pieces, args.query)
        
        if args.json_only:
            output = json.dumps(pieces, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)
        else:
            print_search_results(pieces, args.query, limit=args.limit)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(pieces, f, indent=2)
                print(f"JSON saved to {args.output}")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

