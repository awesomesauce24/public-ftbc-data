#!/usr/bin/env python3
"""
Merge object descriptions back into realm/subrealm objects.json files.
1. Backup existing objects.json files
2. Merge description data from object_descriptions folder
3. Rebuild objects.json with complete data
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

def main():
    print("=" * 80)
    print("MERGING OBJECT DESCRIPTIONS INTO REALM/SUBREALM DATA")
    print("=" * 80)
    print()
    
    # Step 1: Backup existing objects.json files
    print("STEP 1: Backing up existing objects.json files...")
    backup_dir = Path('data/objects_backup')
    backup_dir.mkdir(exist_ok=True)
    
    realms_dir = Path('data/realms')
    subrealms_dir = Path('data/subrealms')
    
    backed_up = 0
    for root, dirs, files in realms_dir.walk() if hasattr(realms_dir, 'walk') else [(realms_dir, [], [])]:
        root_path = Path(root)
        for file in files:
            if file == 'objects.json':
                src = root_path / file
                rel_path = src.relative_to(realms_dir)
                dst = backup_dir / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                backed_up += 1
    
    if subrealms_dir.exists():
        for root, dirs, files in subrealms_dir.walk() if hasattr(subrealms_dir, 'walk') else [(subrealms_dir, [], [])]:
            root_path = Path(root)
            for file in files:
                if file == 'objects.json':
                    src = root_path / file
                    rel_path = src.relative_to(subrealms_dir)
                    dst = backup_dir / rel_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    backed_up += 1
    
    print(f"  ✓ Backed up {backed_up} objects.json files to {backup_dir}\n")
    
    # Step 2: Load all descriptions
    print("STEP 2: Loading descriptions from object_descriptions...")
    desc_dir = Path('object_descriptions')
    descriptions = {}
    
    if desc_dir.exists():
        for json_file in desc_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    obj_data = json.load(f)
                obj_name = obj_data.get('name')
                if obj_name:
                    descriptions[obj_name] = obj_data
            except Exception as e:
                print(f"  ERROR loading {json_file.name}: {e}")
    
    print(f"  ✓ Loaded {len(descriptions)} descriptions\n")
    
    # Step 3: Merge descriptions into realm objects
    print("STEP 3: Merging descriptions into realm objects...")
    merged_realms = 0
    merged_objects = 0
    
    for realm_dir in realms_dir.iterdir():
        if not realm_dir.is_dir():
            continue
        
        # Check for direct objects.json
        obj_file = realm_dir / 'objects.json'
        if obj_file.exists():
            with open(obj_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Merge descriptions
            for obj in data.get('objects', []):
                obj_name = obj.get('name')
                if obj_name in descriptions:
                    desc_data = descriptions[obj_name]
                    # Update fields if they're empty or to get richer data
                    if not obj.get('description'):
                        obj['description'] = desc_data.get('description', '')
                    if not obj.get('hint'):
                        obj['hint'] = desc_data.get('hint', '')
                    merged_objects += 1
            
            # Save back
            with open(obj_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            merged_realms += 1
        
        # Check for sub-areas
        for area_dir in realm_dir.iterdir():
            if area_dir.is_dir():
                obj_file = area_dir / 'objects.json'
                if obj_file.exists():
                    with open(obj_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Merge descriptions
                    for obj in data.get('objects', []):
                        obj_name = obj.get('name')
                        if obj_name in descriptions:
                            desc_data = descriptions[obj_name]
                            if not obj.get('description'):
                                obj['description'] = desc_data.get('description', '')
                            if not obj.get('hint'):
                                obj['hint'] = desc_data.get('hint', '')
                            merged_objects += 1
                    
                    # Save back
                    with open(obj_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    merged_realms += 1
    
    print(f"  ✓ Merged {merged_objects} descriptions into {merged_realms} realm files\n")
    
    # Step 4: Merge descriptions into subrealm objects
    print("STEP 4: Merging descriptions into subrealm objects...")
    merged_subrealms = 0
    merged_sub_objects = 0
    
    if subrealms_dir.exists():
        for parent_dir in subrealms_dir.iterdir():
            if parent_dir.is_dir():
                for subrealm_dir in parent_dir.iterdir():
                    if subrealm_dir.is_dir():
                        obj_file = subrealm_dir / 'objects.json'
                        if obj_file.exists():
                            with open(obj_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Merge descriptions
                            for obj in data.get('objects', []):
                                obj_name = obj.get('name')
                                if obj_name in descriptions:
                                    desc_data = descriptions[obj_name]
                                    if not obj.get('description'):
                                        obj['description'] = desc_data.get('description', '')
                                    if not obj.get('hint'):
                                        obj['hint'] = desc_data.get('hint', '')
                                    merged_sub_objects += 1
                            
                            # Save back
                            with open(obj_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            merged_subrealms += 1
    
    print(f"  ✓ Merged {merged_sub_objects} descriptions into {merged_subrealms} subrealm files\n")
    
    # Summary
    print("=" * 80)
    print(f"✓ MERGE COMPLETE")
    print(f"  Backup location: {backup_dir.absolute()}")
    print(f"  Realms updated: {merged_realms}")
    print(f"  Subrealms updated: {merged_subrealms}")
    print(f"  Objects enriched: {merged_objects + merged_sub_objects}")
    print(f"  Descriptions available: {len(descriptions)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
