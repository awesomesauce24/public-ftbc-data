#!/usr/bin/env python3
"""
Enrich objectjsons metadata with wiki-ready structure.

Adds:
- Realm data (icon, image, gradient, accent, colors)
- Difficulty info (icon and color)
- Auto-generated categories
- Wiki section placeholders
- Extracted colors from gradients
"""

import json
import re
from pathlib import Path
from typing import Dict, List

def load_realms_data():
    """Load realm metadata from realms.json and flatten it by realm label"""
    realms_path = Path('metadata/realms.json')
    with open(realms_path, 'r', encoding='utf-8') as f:
        realms_by_type = json.load(f)
    
    # Flatten all realms into a dict keyed by label
    realms_flat = {}
    for realm_type, realm_list in realms_by_type.items():
        if isinstance(realm_list, list):
            for realm in realm_list:
                if isinstance(realm, dict):
                    label = realm.get('label', '')
                    if label:
                        realms_flat[label] = realm
    
    return realms_flat

def load_difficulties_data():
    """Load difficulty metadata from difficulties.json"""
    difficulties_path = Path('metadata/difficulties.json')
    with open(difficulties_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create map keyed by difficulty name
    difficulties_map = {}
    for difficulty in data.get('difficulties', []):
        name = difficulty.get('name', '')
        if name:
            difficulties_map[name] = difficulty
    
    return difficulties_map

def extract_colors_from_gradient(gradient: str) -> List[str]:
    """
    Extract hex color values from a CSS gradient string.
    
    Examples:
    - "-webkit-linear-gradient(#23bd1c,#188a13)" -> ["#23bd1c", "#188a13"]
    - "-webkit-linear-gradient(#c4a747, #8b7355)" -> ["#c4a747", "#8b7355"]
    
    Args:
        gradient: CSS gradient string
        
    Returns:
        List of hex color codes found in the gradient
    """
    if not gradient:
        return []
    
    # Find all hex color codes (#RRGGBB or #RGB)
    hex_pattern = r'#[0-9a-fA-F]{3,6}'
    colors = re.findall(hex_pattern, gradient)
    
    return colors

def enrich_objectjsons():
    """Enrich all objectjsons files with wiki-ready structure"""
    metadata_dir = Path('metadata/objectjsons')
    
    # Load reference data
    realms_data = load_realms_data()
    difficulties_data = load_difficulties_data()
    
    print("Enriching objectjsons for wiki readiness...\n")
    
    total_enriched = 0
    
    for json_file in sorted(metadata_dir.glob('*.json')):
        realm_name = json_file.stem
        
        # Load objects for this realm
        with open(json_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        # Enrich each object
        for obj_name, obj_data in objects.items():
            # Get realm data
            realm_info = realms_data.get(realm_name, {})
            
            # Add realmData with colors extracted from gradient
            if 'realmData' not in obj_data:
                gradient = realm_info.get('gradient', '')
                colors = extract_colors_from_gradient(gradient)
                
                obj_data['realmData'] = {
                    'label': realm_info.get('label', realm_name),
                    'icon': realm_info.get('icon', ''),
                    'link': realm_info.get('link', realm_name.replace(' ', '_')),
                    'image': realm_info.get('image', ''),
                    'colors': colors,
                    'gradient': gradient,
                    'accent': realm_info.get('accent', '#ffffff')
                }
            else:
                # Update colors even if realmData exists
                gradient = obj_data['realmData'].get('gradient', '')
                if not obj_data['realmData'].get('colors'):
                    colors = extract_colors_from_gradient(gradient)
                    obj_data['realmData']['colors'] = colors
            
            # Add difficulty info
            if 'difficultyInfo' not in obj_data:
                difficulty = obj_data.get('difficulty', '')
                diff_data = difficulties_data.get(difficulty, {})
                
                obj_data['difficultyInfo'] = {
                    'icon': diff_data.get('icon', f'{difficulty}.png'),
                    'color': diff_data.get('color', '#ffffff')
                }
            
            # Add images array if not present
            if 'images' not in obj_data:
                obj_data['images'] = []
            
            # Add previous difficulties if not present
            if 'previousDifficulties' not in obj_data:
                obj_data['previousDifficulties'] = []
            
            # Auto-generate categories if not present
            if 'categories' not in obj_data:
                categories = ['Objects']
                
                # Add difficulty category
                if difficulty:
                    categories.append(f'{difficulty} Objects')
                
                # Add realm category
                categories.append(f'{realm_name} Objects')
                
                obj_data['categories'] = categories
            
            # Add wiki sections if not present
            if 'wiki' not in obj_data:
                obj_data['wiki'] = {
                    'info': '',
                    'obtaining': ''
                }
        
        # Save enriched objects
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(objects, f, indent=2, ensure_ascii=False)
        
        enriched_count = len(objects)
        total_enriched += enriched_count
        print(f"[OK] {realm_name:<40} [{enriched_count} objects enriched]")
    
    print(f"\n✓ All objectjsons enriched! ({total_enriched} total objects)")

if __name__ == '__main__':
    enrich_objectjsons()
