#!/usr/bin/env python3
"""
Search utility for FTBC Wiki Bot
Handles searching through objects database
"""

import json
from pathlib import Path


class ObjectSearcher:
    """Search through objects in realms and subrealms"""
    
    def __init__(self):
        """Initialize the searcher"""
        self.objects = []
        self._load_objects()
    
    def _load_objects(self):
        """Load all objects from realm JSON files"""
        base_path = Path(__file__).parent.parent.parent / "Realms"
        
        if not base_path.exists():
            print(f"Warning: Realms path not found: {base_path}")
            return
        
        # Load main realms
        for realm_file in base_path.glob("*.json"):
            self._parse_realm_file(realm_file, realm_file.stem)
        
        # Load subrealms
        subrealms_path = base_path / "Sub-realms"
        if subrealms_path.exists():
            for subrealm_file in subrealms_path.glob("*.json"):
                self._parse_realm_file(subrealm_file, subrealm_file.stem)
    
    def _parse_realm_file(self, file_path, realm_name):
        """Parse a realm JSON file and extract objects"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                objects = json.load(f)
                
                for obj in objects:
                    self.objects.append({
                        'name': obj.get('ObjectName', ''),
                        'difficulty': obj.get('Difficulty', ''),
                        'description': obj.get('Description', ''),
                        'realm': realm_name
                    })
        except Exception as e:
            pass
    
    def search(self, query):
        """
        Search for objects matching the query
        
        Args:
            query (str): Search term (case-insensitive)
            
        Returns:
            list: Matching objects
        """
        query_lower = query.lower()
        results = [
            obj for obj in self.objects
            if query_lower in obj['name'].lower()
        ]
        return sorted(results, key=lambda x: x['name'])


# Global searcher instance
_searcher = None


def get_searcher():
    """Get or create the global searcher instance"""
    global _searcher
    if _searcher is None:
        _searcher = ObjectSearcher()
    return _searcher


def search_objects(query):
    """
    Search for objects and return formatted results
    
    Args:
        query (str): Search term
        
    Returns:
        list: Search results
    """
    searcher = get_searcher()
    return searcher.search(query)
