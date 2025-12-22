"""Parsers for extracting structured data from wiki content"""

import re
from typing import Dict, List, Any, Optional


class RealmParser:
    """Parse realm data and extract structured information"""
    
    @staticmethod
    def extract_objects_from_description(description: str) -> List[Dict[str, Any]]:
        """Extract object information from realm description"""
        objects = []
        
        # Pattern to find object entries
        # Matches: [[File:Icon.png|18px]] '''[[ObjectName]]'''
        pattern = r"\[\[File:([^\]]+)\|([^\]]+)\]\]\s+'''?\[\[([^\]]+)\]\]'''?"
        
        for match in re.finditer(pattern, description):
            icon, size, name = match.groups()
            objects.append({
                'name': name.strip(),
                'icon': icon.strip(),
                'size': size.strip(),
            })
        
        return objects
    
    @staticmethod
    def extract_difficulty_section(description: str) -> Dict[str, List[str]]:
        """Extract difficulty sections from description"""
        difficulties = {}
        
        # Pattern to find difficulty headers and their contents
        pattern = r"=+\s*(.+?)\s*=+.*?(?=^=|$)"
        
        for match in re.finditer(pattern, description, re.MULTILINE | re.DOTALL):
            section = match.group(1).strip()
            if section.lower() not in ['objects', 'info', 'how to enter']:
                continue
            
            # This is simplified - actual parsing would be more complex
            difficulties[section.lower()] = []
        
        return difficulties


class ObjectParser:
    """Parse object data from wiki format"""
    
    @staticmethod
    def extract_from_line(line: str) -> Optional[Dict[str, Any]]:
        """Extract object information from a wiki line"""
        # Pattern: [[File:Icon.png|18px]] '''[[Name]]'''
        pattern = r"\[\[File:([^\]]+)\]\]\s+'''?\[\[([^\]]+)\]\]'''?"
        match = re.search(pattern, line)
        
        if match:
            icon, name = match.groups()
            return {
                'icon': icon.strip(),
                'name': name.strip(),
            }
        return None
    
    @staticmethod
    def clean_wiki_markup(text: str) -> str:
        """Remove wiki markup from text"""
        # Remove links
        text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", text)
        # Remove bold/italic
        text = re.sub(r"'''([^']+)'''", r"\1", text)
        text = re.sub(r"''([^']+)''", r"\1", text)
        # Remove templates
        text = re.sub(r"\{\{[^}]+\}\}", "", text)
        return text
