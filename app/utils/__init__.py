"""Utilities for common operations"""

import json
from pathlib import Path
from typing import Any, Dict


class FileUtils:
    """File operation utilities"""
    
    @staticmethod
    def read_json(path: Path) -> Dict[str, Any]:
        """Read JSON file safely"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return {}
    
    @staticmethod
    def write_json(path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
        """Write JSON file safely"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent)
            return True
        except Exception as e:
            print(f"Error writing {path}: {e}")
            return False
    
    @staticmethod
    def read_text(path: Path) -> str:
        """Read text file safely"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return ""


class StringUtils:
    """String manipulation utilities"""
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize a name for URLs or filenames"""
        return name.lower().replace(' ', '-').replace('_', '-')
    
    @staticmethod
    def title_case(name: str) -> str:
        """Convert name to title case"""
        return ' '.join(word.capitalize() for word in name.split('_'))
