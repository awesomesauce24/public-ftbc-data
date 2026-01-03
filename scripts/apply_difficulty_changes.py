#!/usr/bin/env python3
"""
Apply difficulty changes from difficultychanges.json to the enriched metadata.

Updates:
- Object difficulty to the new value
- previousDifficulties array to include the old difficulty
- difficultyInfo (icon and color) based on new difficulty
- categories based on new difficulty
"""

import json
from pathlib import Path

# Load difficulty info for reference
difficulties_path = Path('metadata/difficulties.json')
with open(difficulties_path, 'r', encoding='utf-8') as f:
    difficulties_data = json.load(f)

difficulties_map = {}
for diff in difficulties_data.get('difficulties', []):
    name = diff.get('name', '')
    if name:
        difficulties_map[name] = {
            'icon': diff.get('icon', f'{name}.png'),
            'color': diff.get('color', '#ffffff')
        }

# Load difficulty changes
changes_path = Path('metadata/difficultychanges.json')
with open(changes_path, 'r', encoding='utf-8') as f:
    changes = json.load(f)

metadata_dir = Path('metadata/objectjsons')

total_changes = 0
realms_affected = {}

# Apply changes
for realm_name, realm_changes in changes.items():
    if not realm_changes:  # Skip empty realms
        continue
    
    json_file = metadata_dir / f"{realm_name}.json"
    if not json_file.exists():
        print(f"⚠ Realm file not found: {realm_name}")
        continue
    
    # Load metadata for this realm
    with open(json_file, 'r', encoding='utf-8') as f:
        objects = json.load(f)
    
    realm_change_count = 0
    
    for obj_name, change_data in realm_changes.items():
        if obj_name not in objects:
            print(f"⚠ Object not found in {realm_name}: {obj_name}")
            continue
        
        obj = objects[obj_name]
        old_difficulty = change_data.get('previous', '')
        new_difficulty = change_data.get('new', '')
        
        # Update difficulty
        obj['difficulty'] = new_difficulty
        
        # Update previousDifficulties
        if 'previousDifficulties' not in obj:
            obj['previousDifficulties'] = []
        
        # Add old difficulty if not already present
        if old_difficulty and old_difficulty not in obj['previousDifficulties']:
            obj['previousDifficulties'].insert(0, old_difficulty)  # Insert at beginning
        
        # Update difficultyInfo
        if new_difficulty in difficulties_map:
            obj['difficultyInfo'] = difficulties_map[new_difficulty]
        
        # Update categories
        categories = obj.get('categories', [])
        # Remove old difficulty category if present
        old_cat = f"{old_difficulty} Objects"
        new_cat = f"{new_difficulty} Objects"
        
        if old_cat in categories:
            categories.remove(old_cat)
        if new_cat not in categories:
            categories.append(new_cat)
        
        obj['categories'] = sorted(categories)  # Keep sorted for consistency
        
        realm_change_count += 1
        total_changes += 1
    
    # Save updated metadata
    if realm_change_count > 0:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(objects, f, indent=2, ensure_ascii=False)
        
        realms_affected[realm_name] = realm_change_count
        print(f"[OK] {realm_name:<40} [{realm_change_count} objects updated]")

print(f"\n{'='*70}")
print(f"Difficulty changes applied!")
print(f"  Total changes: {total_changes}")
print(f"  Realms affected: {len(realms_affected)}")
print(f"{'='*70}")
