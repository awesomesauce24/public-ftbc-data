#!/usr/bin/env python3
"""
Scan and fix misplaced objects in objectjsons.

Uses main_realm_objects.json as the source of truth for object locations.
Moves objects to their correct realm files and updates all related fields.
"""

import json
from pathlib import Path
from typing import Dict, List, Set

def load_main_realm_objects() -> Dict[str, str]:
    """
    Load main_realm_objects.json and create a mapping of object -> realm.
    
    Returns:
        Dictionary mapping object name to realm name
    """
    path = Path('metadata/main_realm_objects.json')
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    obj_to_realm = {}
    
    # All objects in main_realm_objects are in Main Realm
    for difficulty, diff_data in data.get('main_realm_objects', {}).items():
        if isinstance(diff_data, dict) and 'objects' in diff_data:
            for obj_name in diff_data['objects']:
                obj_to_realm[obj_name] = 'Main Realm'
    
    return obj_to_realm

def load_realms_data() -> Dict[str, Dict]:
    """Load realm metadata from realms.json"""
    path = Path('metadata/realms.json')
    
    with open(path, 'r', encoding='utf-8') as f:
        realms_data = json.load(f)
    
    # Flatten all realms
    realms_map = {}
    for realm in realms_data.get('normal', []):
        if isinstance(realm, dict):
            label = realm.get('label', '')
            if label:
                realms_map[label] = realm
    
    # Add subrealms
    for subrealm_type, subrealm_list in realms_data.get('subrealms', {}).items():
        if isinstance(subrealm_list, list):
            for realm in subrealm_list:
                if isinstance(realm, dict):
                    label = realm.get('label', '')
                    if label:
                        realms_map[label] = realm
    
    return realms_map

def scan_for_misplaced() -> Dict[str, List[tuple]]:
    """
    Scan all objectjsons and find misplaced objects.
    
    Returns:
        Dictionary mapping source_realm -> [(object_name, correct_realm)]
    """
    metadata_dir = Path('metadata/objectjsons')
    canonical = load_main_realm_objects()
    
    misplaced = {}
    
    for json_file in sorted(metadata_dir.glob('*.json')):
        realm_name = json_file.stem
        
        with open(json_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        for obj_name in objects.keys():
            # Check if this object is in main_realm_objects
            if obj_name in canonical:
                correct_realm = canonical[obj_name]
                if realm_name != correct_realm:
                    if realm_name not in misplaced:
                        misplaced[realm_name] = []
                    misplaced[realm_name].append((obj_name, correct_realm))
    
    return misplaced

def fix_misplaced_objects():
    """Fix all misplaced objects by moving them to correct realm files."""
    metadata_dir = Path('metadata/objectjsons')
    canonical = load_main_realm_objects()
    realms_map = load_realms_data()
    
    # Track all objects to move
    moves = {}  # source_realm -> {object_name -> correct_realm}
    
    for json_file in sorted(metadata_dir.glob('*.json')):
        realm_name = json_file.stem
        
        with open(json_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        for obj_name in objects.keys():
            if obj_name in canonical:
                correct_realm = canonical[obj_name]
                if realm_name != correct_realm:
                    if realm_name not in moves:
                        moves[realm_name] = {}
                    moves[realm_name][obj_name] = correct_realm
    
    # Execute moves
    total_moved = 0
    
    for source_realm, objects_to_move in moves.items():
        source_file = metadata_dir / f"{source_realm}.json"
        
        # Load source realm
        with open(source_file, 'r', encoding='utf-8') as f:
            source_objects = json.load(f)
        
        # Load destination realms
        dest_objects = {}
        for obj_name, dest_realm in objects_to_move.items():
            if dest_realm not in dest_objects:
                dest_file = metadata_dir / f"{dest_realm}.json"
                with open(dest_file, 'r', encoding='utf-8') as f:
                    dest_objects[dest_realm] = json.load(f)
        
        # Move objects
        for obj_name, dest_realm in objects_to_move.items():
            if obj_name in source_objects:
                obj_data = source_objects[obj_name]
                
                # Update realm-related fields
                obj_data['realm'] = dest_realm
                
                # Update realmData
                if dest_realm in realms_map:
                    realm_info = realms_map[dest_realm]
                    obj_data['realmData'] = {
                        'label': realm_info.get('label', dest_realm),
                        'icon': realm_info.get('icon', ''),
                        'link': realm_info.get('link', dest_realm.replace(' ', '_')),
                        'image': realm_info.get('image', ''),
                        'colors': extract_colors_from_gradient(realm_info.get('gradient', '')),
                        'gradient': realm_info.get('gradient', ''),
                        'accent': realm_info.get('accent', '#ffffff')
                    }
                
                # Update categories
                difficulty = obj_data.get('difficulty', '')
                categories = [
                    'Objects',
                    f'{difficulty} Objects' if difficulty else '',
                    f'{dest_realm} Objects'
                ]
                obj_data['categories'] = [c for c in categories if c]  # Remove empty strings
                
                # Add to destination
                dest_objects[dest_realm][obj_name] = obj_data
                
                # Remove from source
                del source_objects[obj_name]
                
                total_moved += 1
                print(f"  ✓ {obj_name}: {source_realm} → {dest_realm}")
        
        # Save modified source realm
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_objects, f, indent=2, ensure_ascii=False)
        
        # Save modified destination realms
        for dest_realm, dest_data in dest_objects.items():
            dest_file = metadata_dir / f"{dest_realm}.json"
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(dest_data, f, indent=2, ensure_ascii=False)
    
    return total_moved

def extract_colors_from_gradient(gradient: str) -> list:
    """Extract hex colors from gradient string."""
    import re
    if not gradient:
        return []
    
    hex_pattern = r'#[0-9a-fA-F]{3,6}'
    colors = re.findall(hex_pattern, gradient)
    return colors

def main():
    """Main execution."""
    print("="*70)
    print("SCANNING FOR MISPLACED OBJECTS")
    print("="*70)
    
    misplaced = scan_for_misplaced()
    
    if not misplaced:
        print("\n✓ All objects are in correct realms!")
        return
    
    print(f"\nFound misplaced objects:\n")
    
    total_misplaced = 0
    for source_realm, objects in misplaced.items():
        print(f"  {source_realm}:")
        for obj_name, correct_realm in objects:
            print(f"    - {obj_name} (should be in {correct_realm})")
            total_misplaced += 1
    
    print(f"\nTotal misplaced: {total_misplaced}")
    
    print(f"\n{'='*70}")
    print("FIXING MISPLACED OBJECTS")
    print(f"{'='*70}\n")
    
    moved = fix_misplaced_objects()
    
    print(f"\n{'='*70}")
    print(f"✓ Fixed {moved} misplaced objects!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
