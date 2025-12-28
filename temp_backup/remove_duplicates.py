#!/usr/bin/env python3
"""Remove duplicate objects that appear in both realms and subrealms."""

import json
from pathlib import Path

# Objects to remove from subrealms
duplicates_to_remove = {
    "Classic Paradise/Starter Place": ["2009 Firey"],
    "Classic Paradise/Classic Insanity": ["Administratory", "Veterany"],
}

for location, obj_names in duplicates_to_remove.items():
    parent_realm, subrealm_name = location.split("/")
    obj_file = Path(f"data/subrealms/{parent_realm}/{subrealm_name}/objects.json")
    
    if not obj_file.exists():
        print(f"❌ File not found: {obj_file}")
        continue
    
    # Load current objects
    with open(obj_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data.get("objects", []))
    
    # Remove duplicates
    remaining_objects = [
        obj for obj in data.get("objects", [])
        if obj.get("name") not in obj_names
    ]
    
    # Save updated file
    data["objects"] = remaining_objects
    with open(obj_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    removed_count = original_count - len(remaining_objects)
    print(f"✓ {location:40} {removed_count} duplicate(s) removed ({original_count} → {len(remaining_objects)})")

print("\n✅ Duplicate removal complete!")
