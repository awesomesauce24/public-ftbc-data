import json
from pathlib import Path
from collections import defaultdict

# Find all duplicates across realms and subrealms
object_locations = defaultdict(list)

# Collect realm objects
for realm_dir in Path('data/realms').iterdir():
    if realm_dir.is_dir():
        obj_file = realm_dir / 'objects.json'
        if obj_file.exists():
            with open(obj_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for obj in data.get('objects', []):
                obj_name = obj.get('name', '').strip()
                if obj_name:
                    object_locations[obj_name].append(('realm', realm_dir.name))

# Collect subrealm objects
for parent_dir in Path('data/subrealms').iterdir():
    if parent_dir.is_dir():
        for subrealm_dir in parent_dir.iterdir():
            if subrealm_dir.is_dir():
                obj_file = subrealm_dir / 'objects.json'
                if obj_file.exists():
                    with open(obj_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    for obj in data.get('objects', []):
                        obj_name = obj.get('name', '').strip()
                        if obj_name:
                            object_locations[obj_name].append(('subrealm', f'{parent_dir.name}/{subrealm_dir.name}'))

# Find duplicates
duplicates = {name: locs for name, locs in object_locations.items() if len(locs) > 1}

print(f"Total duplicates across realms/subrealms: {len(duplicates)}\n")
for obj_name in sorted(duplicates.keys()):
    locs = duplicates[obj_name]
    print(f"{obj_name}:")
    for type_, location in locs:
        print(f"  - {type_:10} {location}")
    print()
