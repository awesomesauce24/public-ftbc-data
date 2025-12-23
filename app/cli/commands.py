"""CLI command implementations"""

from core.loader import RealmLoader, SubrealmLoader
from core.config import Config
from pathlib import Path
from typing import List, Optional


class RealmCommands:
    """Commands for viewing realm information"""
    
    def __init__(self):
        self.loader = RealmLoader(Config.REALMS_PATH)
        self.subrealm_loader = SubrealmLoader(Config.REALMS_PATH)
    
    def list_realms(self) -> List[str]:
        """List all realms"""
        return self.loader.get_all_realms()
    
    def show_realm(self, realm_name: str) -> dict:
        """Display information for a specific realm"""
        data = self.loader.get_realm_data(realm_name)
        description = self.loader.get_realm_description(realm_name)
        subrealms = self.loader.get_subrealms(realm_name)
        
        return {
            'name': realm_name,
            'data': data,
            'description': description,
            'subrealms': subrealms,
        }
    
    def list_subrealms(self, realm_name: str) -> List[str]:
        """List subrealms for a realm"""
        return self.loader.get_subrealms(realm_name)
    
    def show_subrealm(self, realm_name: str, subrealm_name: str) -> dict:
        """Display information for a specific subrealm"""
        data = self.subrealm_loader.get_subrealm_data(realm_name, subrealm_name)
        description = self.subrealm_loader.get_subrealm_description(realm_name, subrealm_name)
        
        return {
            'name': subrealm_name,
            'parent_realm': realm_name,
            'data': data,
            'description': description,
        }


class SearchCommands:
    """Commands for searching content"""
    
    def __init__(self):
        self.loader = RealmLoader(Config.REALMS_PATH)
        self.subrealm_loader = SubrealmLoader(Config.REALMS_PATH)
    
    def search_realms(self, query: str) -> List[str]:
        """Search for realms by name"""
        realms = self.loader.get_all_realms()
        query_lower = query.lower()
        return [r for r in realms if query_lower in r.lower()]
    
    def search_subrealms(self, query: str) -> List[tuple]:
        """Search for subrealms by name (returns list of (realm, subrealm) tuples)"""
        realms = self.loader.get_all_realms()
        results = []
        query_lower = query.lower()
        
        for realm in realms:
            subrealms = self.loader.get_subrealms(realm)
            for sub in subrealms:
                if query_lower in sub.lower():
                    results.append((realm, sub))
        
        return results


class ExportCommands:
    """Commands for exporting data"""
    
    def __init__(self):
        self.loader = RealmLoader(Config.REALMS_PATH)
        self.subrealm_loader = SubrealmLoader(Config.REALMS_PATH)
    
    def export_realm_list(self, format: str = 'text') -> str:
        """Export list of all realms"""
        realms = self.loader.get_all_realms()
        
        if format == 'json':
            import json
            return json.dumps(realms, indent=2)
        else:  # text
            return '\n'.join([f"• {r}" for r in realms])
    
    def export_realm_structure(self, realm_name: str, format: str = 'json') -> str:
        """Export complete structure of a realm including subrealms"""
        realm_data = self.loader.get_realm_data(realm_name)
        subrealms = []
        
        for sub_name in self.loader.get_subrealms(realm_name):
            sub_data = self.subrealm_loader.get_subrealm_data(realm_name, sub_name)
            subrealms.append({
                'name': sub_name,
                'data': sub_data,
            })
        
        structure = {
            'realm': realm_name,
            'data': realm_data,
            'subrealms': subrealms,
        }
        
        if format == 'json':
            import json
            return json.dumps(structure, indent=2)
        else:
            return str(structure)
