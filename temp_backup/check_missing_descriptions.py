import json
from pathlib import Path

placeholder_count = 0
total_objects = 0
missing_by_realm = {}

# Check realms
realms_dir = Path('data/realms')
for realm_dir in realms_dir.iterdir():
    if not realm_dir.is_dir():
        continue
    
    # Check direct objects
    obj_file = realm_dir / 'objects.json'
    if obj_file.exists():
        with open(obj_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for obj in data.get('objects', []):
            total_objects += 1
            desc = obj.get('description', '')
            if '[PLACEHOLDER]' in desc or desc == 'PLACEHOLDER' or not desc or desc == '':
                placeholder_count += 1
                if realm_dir.name not in missing_by_realm:
                    missing_by_realm[realm_dir.name] = []
                missing_by_realm[realm_dir.name].append(obj.get('name'))
    
    # Check sub-areas
    for area_dir in realm_dir.iterdir():
        if area_dir.is_dir():
            obj_file = area_dir / 'objects.json'
            if obj_file.exists():
                with open(obj_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for obj in data.get('objects', []):
                    total_objects += 1
                    desc = obj.get('description', '')
                    if '[PLACEHOLDER]' in desc or desc == 'PLACEHOLDER' or not desc or desc == '':
                        placeholder_count += 1
                        if realm_dir.name not in missing_by_realm:
                            missing_by_realm[realm_dir.name] = []
                        missing_by_realm[realm_dir.name].append(obj.get('name'))

# Check subrealms
subrealms_dir = Path('data/subrealms')
if subrealms_dir.exists():
    for parent_dir in subrealms_dir.iterdir():
        if parent_dir.is_dir():
            for subrealm_dir in parent_dir.iterdir():
                if subrealm_dir.is_dir():
                    obj_file = subrealm_dir / 'objects.json'
                    if obj_file.exists():
                        with open(obj_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        for obj in data.get('objects', []):
                            total_objects += 1
                            desc = obj.get('description', '')
                            if '[PLACEHOLDER]' in desc or desc == 'PLACEHOLDER' or not desc or desc == '':
                                placeholder_count += 1
                                key = f"{parent_dir.name}/{subrealm_dir.name}"
                                if key not in missing_by_realm:
                                    missing_by_realm[key] = []
                                missing_by_realm[key].append(obj.get('name'))

print(f"Total objects: {total_objects}")
print(f"Missing descriptions: {placeholder_count} ({placeholder_count*100/total_objects:.1f}%)")
print(f"\nRealms/Subrealms with missing descriptions:")
for realm, objects in sorted(missing_by_realm.items()):
    print(f"\n{realm}: {len(objects)} missing")
    for obj in objects[:5]:
        print(f"  - {obj}")
    if len(objects) > 5:
        print(f"  ... and {len(objects)-5} more")
