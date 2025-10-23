"""
API Client for Activepieces
Handles all HTTP requests to the Activepieces API
"""

import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class ActivepiecesAPIClient:
    """Client for interacting with Activepieces API"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the API client with configuration"""
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.base_url = self.config['api_base_url']
        self.api_version = self.config['api_version']
        self.default_locale = self.config.get('default_locale', 'en')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL"""
        return f"{self.base_url}/api/{self.api_version}{endpoint}"
    
    def list_pieces(
        self,
        search_query: Optional[str] = None,
        include_hidden: bool = False,
        include_tags: bool = False,
        suggestion_type: Optional[str] = None,
        categories: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        order_by: Optional[str] = None,
        locale: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all pieces with optional filters
        
        Args:
            search_query: Search term to filter pieces
            include_hidden: Include hidden pieces
            include_tags: Include piece tags
            suggestion_type: 'ACTION', 'TRIGGER', or 'ACTION_AND_TRIGGER'
            categories: List of categories to filter by
            sort_by: 'NAME', 'UPDATED', 'CREATED', 'POPULARITY'
            order_by: 'ASC' or 'DESC'
            locale: Language locale (default: 'en')
        
        Returns:
            List of piece metadata summaries
        """
        params = {}
        
        if search_query:
            params['searchQuery'] = search_query
        if include_hidden:
            params['includeHidden'] = 'true'
        if include_tags:
            params['includeTags'] = 'true'
        if suggestion_type:
            params['suggestionType'] = suggestion_type
        if categories:
            params['categories'] = categories
        if sort_by:
            params['sortBy'] = sort_by
        if order_by:
            params['orderBy'] = order_by
        if locale or self.default_locale:
            params['locale'] = locale or self.default_locale
        
        url = self._build_url('/pieces')
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_piece(
        self,
        name: str,
        version: Optional[str] = None,
        locale: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific piece
        
        Args:
            name: Piece name (e.g., '@activepieces/piece-slack')
            version: Specific version (optional)
            locale: Language locale
        
        Returns:
            Complete piece metadata model
        """
        params = {}
        if version:
            params['version'] = version
        if locale or self.default_locale:
            params['locale'] = locale or self.default_locale
        
        url = self._build_url(f'/pieces/{name}')
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_piece_categories(self) -> List[str]:
        """
        Get all available piece categories
        
        Returns:
            List of category names
        """
        url = self._build_url('/pieces/categories')
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_piece_versions(
        self,
        name: str,
        release: str
    ) -> Dict[str, Any]:
        """
        Get available versions for a piece
        
        Args:
            name: Piece name
            release: Activepieces release version
        
        Returns:
            Dictionary of available versions
        """
        params = {
            'name': name,
            'release': release
        }
        url = self._build_url('/pieces/versions')
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

