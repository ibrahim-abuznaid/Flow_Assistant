#!/usr/bin/env python3
"""
Pieces Toolkit - Programmatic API Wrapper
High-level wrapper for easy integration into Python applications
"""

from typing import List, Dict, Any, Optional
from api_client import ActivepiecesAPIClient
from piece_utils import normalize_collection, count_collection, get_categories
import json

class PiecesToolkit:
    """High-level toolkit for working with Activepieces pieces"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize toolkit with API client"""
        self.client = ActivepiecesAPIClient(config_path)
        self._pieces_cache = None
        self._piece_details_cache = {}
    
    def get_all_pieces(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get all pieces with caching
        
        Args:
            force_refresh: Force refresh from API (ignore cache)
        
        Returns:
            List of all piece metadata
        """
        if self._pieces_cache is None or force_refresh:
            self._pieces_cache = self.client.list_pieces(include_tags=True)
        return self._pieces_cache
    
    def search_pieces(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search pieces by query with ranking
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching pieces sorted by relevance
        """
        pieces = self.client.list_pieces(search_query=query)
        
        # Rank by relevance
        query_lower = query.lower()
        for piece in pieces:
            score = 0
            if query_lower in piece['name'].lower():
                score += 100
            if query_lower in piece.get('displayName', '').lower():
                score += 80
            if query_lower in piece.get('description', '').lower():
                score += 40
            piece['_relevance_score'] = score
        
        pieces.sort(key=lambda p: p['_relevance_score'], reverse=True)
        
        return pieces[:limit] if limit else pieces
    
    def get_piece(self, name: str) -> Dict[str, Any]:
        """
        Get detailed piece information
        
        Args:
            name: Piece name
        
        Returns:
            Complete piece metadata
        """
        if name not in self._piece_details_cache:
            self._piece_details_cache[name] = self.client.get_piece(name)
        return self._piece_details_cache[name]
    
    def get_piece_actions(self, name: str) -> Dict[str, Any]:
        """
        Get all actions for a piece
        
        Args:
            name: Piece name
        
        Returns:
            Dictionary of actions
        """
        piece = self.get_piece(name)
        return normalize_collection(piece.get('actions'))
    
    def get_piece_triggers(self, name: str) -> Dict[str, Any]:
        """
        Get all triggers for a piece
        
        Args:
            name: Piece name
        
        Returns:
            Dictionary of triggers
        """
        piece = self.get_piece(name)
        return normalize_collection(piece.get('triggers'))
    
    def get_action_details(self, piece_name: str, action_name: str) -> Dict[str, Any]:
        """
        Get details about a specific action
        
        Args:
            piece_name: Piece name
            action_name: Action name
        
        Returns:
            Action metadata
        """
        actions = self.get_piece_actions(piece_name)
        return actions.get(action_name, {})
    
    def get_trigger_details(self, piece_name: str, trigger_name: str) -> Dict[str, Any]:
        """
        Get details about a specific trigger
        
        Args:
            piece_name: Piece name
            trigger_name: Trigger name
        
        Returns:
            Trigger metadata
        """
        triggers = self.get_piece_triggers(piece_name)
        return triggers.get(trigger_name, {})
    
    def find_pieces_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Find all pieces in a specific category
        
        Args:
            category: Category name
        
        Returns:
            List of pieces in category
        """
        pieces = self.get_all_pieces()
        return [
            p for p in pieces
            if category in get_categories(p.get('categories'))
        ]
    
    def find_pieces_with_action(self, action_keyword: str) -> List[Dict[str, Any]]:
        """
        Find pieces that have actions matching a keyword
        
        Args:
            action_keyword: Keyword to search in action names/descriptions
        
        Returns:
            List of pieces with matching actions
        """
        pieces = self.get_all_pieces()
        matching = []
        
        keyword_lower = action_keyword.lower()
        
        for piece in pieces:
            actions = normalize_collection(piece.get('actions'))
            detailed_piece = piece

            if not actions and count_collection(piece.get('actions')):
                detailed_piece = self.get_piece(piece['name'])
                actions = normalize_collection(detailed_piece.get('actions'))

            for action_name, action in actions.items():
                if (keyword_lower in action_name.lower() or
                    keyword_lower in action.get('displayName', '').lower() or
                    keyword_lower in action.get('description', '').lower()):
                    matching.append(detailed_piece)
                    break
        
        return matching
    
    def find_pieces_with_trigger(self, trigger_keyword: str) -> List[Dict[str, Any]]:
        """
        Find pieces that have triggers matching a keyword
        
        Args:
            trigger_keyword: Keyword to search in trigger names/descriptions
        
        Returns:
            List of pieces with matching triggers
        """
        pieces = self.get_all_pieces()
        matching = []
        
        keyword_lower = trigger_keyword.lower()
        
        for piece in pieces:
            triggers = normalize_collection(piece.get('triggers'))
            detailed_piece = piece

            if not triggers and count_collection(piece.get('triggers')):
                detailed_piece = self.get_piece(piece['name'])
                triggers = normalize_collection(detailed_piece.get('triggers'))

            for trigger_name, trigger in triggers.items():
                if (keyword_lower in trigger_name.lower() or
                    keyword_lower in trigger.get('displayName', '').lower() or
                    keyword_lower in trigger.get('description', '').lower()):
                    matching.append(detailed_piece)
                    break
        
        return matching
    
    def get_action_properties(self, piece_name: str, action_name: str) -> Dict[str, Any]:
        """
        Get properties/inputs for a specific action
        
        Args:
            piece_name: Piece name
            action_name: Action name
        
        Returns:
            Dictionary of action properties
        """
        action = self.get_action_details(piece_name, action_name)
        return action.get('props', {})
    
    def format_piece_summary(self, piece: Dict[str, Any]) -> str:
        """
        Format piece as human-readable summary
        
        Args:
            piece: Piece metadata
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"{piece['displayName']} ({piece['name']})")
        lines.append(f"  Version: {piece.get('version', 'N/A')}")
        lines.append(f"  Description: {piece.get('description', 'No description')}")
        lines.append(f"  Actions: {count_collection(piece.get('actions'))}")
        lines.append(f"  Triggers: {count_collection(piece.get('triggers'))}")
        return "\n".join(lines)
    
    def format_action_summary(self, action: Dict[str, Any], action_name: str) -> str:
        """
        Format action as human-readable summary
        
        Args:
            action: Action metadata
            action_name: Action name
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"{action.get('displayName', action_name)}")
        lines.append(f"  Name: {action_name}")
        lines.append(f"  Description: {action.get('description', 'No description')}")
        lines.append(f"  Requires Auth: {action.get('requireAuth', False)}")
        lines.append(f"  Properties: {len(action.get('props', {}))}")
        return "\n".join(lines)
    
    def export_to_json(self, data: Any, filepath: str):
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available pieces
        
        Returns:
            Dictionary with statistics
        """
        pieces = self.get_all_pieces()
        
        total_actions = sum(count_collection(p.get('actions')) for p in pieces)
        total_triggers = sum(count_collection(p.get('triggers')) for p in pieces)
        
        # Count by category
        categories = {}
        for piece in pieces:
            for cat in get_categories(piece.get('categories')):
                categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_pieces': len(pieces),
            'total_actions': total_actions,
            'total_triggers': total_triggers,
            'pieces_with_auth': len([p for p in pieces if p.get('auth')]),
            'categories': categories,
            'avg_actions_per_piece': total_actions / len(pieces) if pieces else 0,
            'avg_triggers_per_piece': total_triggers / len(pieces) if pieces else 0
        }


# Example usage
if __name__ == '__main__':
    # Initialize toolkit
    toolkit = PiecesToolkit()
    
    # Get statistics
    print("=== Activepieces Statistics ===")
    stats = toolkit.get_statistics()
    print(f"Total Pieces: {stats['total_pieces']}")
    print(f"Total Actions: {stats['total_actions']}")
    print(f"Total Triggers: {stats['total_triggers']}")
    print(f"\nTop Categories:")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {cat}: {count}")
    
    # Search example
    print("\n=== Search Example: 'slack' ===")
    results = toolkit.search_pieces('slack', limit=3)
    for piece in results:
        print(f"\n{toolkit.format_piece_summary(piece)}")
    
    # Get actions example
    if results:
        print(f"\n=== Actions for {results[0]['displayName']} ===")
        actions = toolkit.get_piece_actions(results[0]['name'])
        for action_name, action in list(actions.items())[:3]:
            print(f"\n{toolkit.format_action_summary(action, action_name)}")

