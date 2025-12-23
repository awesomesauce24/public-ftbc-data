"""Data loaders for realms and subrealms"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class RealmLoader:
    """Load and manage realm data"""
    
    def __init__(self, realms_path: Path):
        self.realms_path = Path(realms_path)
    
    def get_all_realms(self) -> List[str]:
        """Get list of all realm names"""
        if not self.realms_path.exists():
            return []
        
        realms = []
        for item in self.realms_path.iterdir():
            # Skip hidden directories and cache
            if item.is_dir() and not item.name.startswith('.'):
                realms.append(item.name)
        return sorted(realms)
    
    def get_realm_data(self, realm_name: str) -> Dict[str, Any]:
        """Load JSON data for a realm"""
        realm_path = self.realms_path / realm_name
        json_file = realm_path / f"{realm_name}.json"
        
        if not json_file.exists():
            return {}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {realm_name}: {e}")
            return {}
    
    def get_realm_description(self, realm_name: str) -> str:
        """Load text description for a realm"""
        realm_path = self.realms_path / realm_name
        page_file = realm_path / "page.txt"
        
        if not page_file.exists():
            return ""
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading description for {realm_name}: {e}")
            return ""
    
    def get_subrealms(self, realm_name: str) -> List[str]:
        """Get list of subrealms for a realm"""
        realm_path = self.realms_path / realm_name
        subrealms_dir = realm_path / "subrealms"
        
        if not subrealms_dir.exists():
            return []
        
        subrealms = []
        for item in subrealms_dir.iterdir():
            if item.is_dir():
                subrealms.append(item.name)
        return sorted(subrealms)


class SubrealmLoader:
    """Load and manage subrealm data"""
    
    def __init__(self, realms_path: Path):
        self.realms_path = Path(realms_path)
    
    def get_subrealm_data(self, realm_name: str, subrealm_name: str) -> Dict[str, Any]:
        """Load JSON data for a subrealm"""
        subrealm_path = self.realms_path / realm_name / "subrealms" / subrealm_name
        json_file = subrealm_path / f"{subrealm_name}.json"
        
        if not json_file.exists():
            return {}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {subrealm_name}: {e}")
            return {}
    
    def get_subrealm_description(self, realm_name: str, subrealm_name: str) -> str:
        """Load text description for a subrealm"""
        subrealm_path = self.realms_path / realm_name / "subrealms" / subrealm_name
        page_file = subrealm_path / "page.txt"
        
        if not page_file.exists():
            return ""
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading description for {subrealm_name}: {e}")
            return ""
    
    def get_all_subrealms_for_realm(self, realm_name: str) -> List[Dict[str, Any]]:
        """Get all subrealm data for a realm"""
        realm_path = self.realms_path / realm_name
        subrealms_dir = realm_path / "subrealms"
        
        if not subrealms_dir.exists():
            return []
        
        subrealms = []
        for subrealm_dir in sorted(subrealms_dir.iterdir()):
            if subrealm_dir.is_dir():
                data = self.get_subrealm_data(realm_name, subrealm_dir.name)
                description = self.get_subrealm_description(realm_name, subrealm_dir.name)
                subrealms.append({
                    'name': subrealm_dir.name,
                    'data': data,
                    'description': description,
                })
        return subrealms
